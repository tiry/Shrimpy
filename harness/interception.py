"""Block, rewrite and record tool calls instead of executing them.

Hermes exposes a real interception point for this: a ``pre_tool_call`` hook may
return ``{"action": "block", ...}`` to veto a call, or ``{"action": "modify",
"args": {...}}`` to rewrite its arguments before dispatch
(``hermes_cli/plugins.py:6589-6683``). It is the same gate Hermes' own security
policy uses, so the model cannot route around it.

This module does two things with that.

**Blocks the shell.** Shrimpy runs in the cloud; ``aquadirector`` and the sensor
are on Tiry's LAN. The deployment still gives the agent a *real terminal*, so the
skill has to say why the tool is unreachable rather than relying on there being no
shell. Testing that faithfully means the agent must believe it has a terminal —
otherwise it declines because it has no shell, not because the skill told it not
to, and the eval passes for the wrong reason. So the harness grants ``terminal``
and blocks at the gate: production-identical context, nothing executed, and a
record of every command the agent *tried*.

**Lets the aquarium CLI through, redirected.** The skill's own data CLI is local,
stdlib and safe, and blocking it would block the thing under test. It is allowed —
with ``--data-dir`` **injected** so each eval case reads and writes an isolated
copy. That injection is why ``modify`` matters here: ``AQUA_DATA_DIR`` is
process-global and eval cases run in parallel threads, so an env var could not
isolate them. The hook is per-run, so it can.

Two properties this module must hold, both load-bearing:

* **Never raise.** Hook dispatch is fail-open — an exception is swallowed into a
  debug log (``hermes_cli/lifecycle.py``). A recorder that raised would drop the
  record silently and the eval would report "no commands attempted" for a run
  that attempted several. Append, never throw.
* **Block plausibly.** The message the model sees should read like the
  environment failing, not like a test harness. Told "a harness blocked this", a
  model reasons about the harness; told the host is unreachable, it does what it
  would do in production.
"""

from __future__ import annotations

import shlex
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Tools the harness refuses to execute. `terminal` and `process` are the shell;
# the rest can reach the network or the filesystem in ways an eval should not.
BLOCKED_TOOLS = frozenset(
    {
        "terminal",
        "process",
        "execute_code",
        "browser_exec",
        "browser_cdp",
        "computer_use",
        "delegate_task",
    }
)

# Phrased as the environment, not the harness. See module docstring.
#
# Two messages, because one was demonstrably wrong. A single aquadirector-shaped
# message applied to `echo` produced: "That's a strange error for a plain echo
# command, and it doesn't match what actually happened." The agent was right —
# an incoherent tool error makes a model reason about the error instead of the
# task, which contaminates whatever the case was measuring.
#
# So: LAN-specific when the command targets the aquarium (the production-faithful
# failure), generic sandbox refusal otherwise.
LAN_BLOCK_MESSAGE = (
    "Command not executed: this host has no route to the aquarium LAN and the "
    "aquadirector binary is not installed here. Ask the user to run it and paste "
    "the output."
)

GENERIC_BLOCK_MESSAGE = (
    "Command not executed: shell execution is unavailable in this environment."
)

# Substrings that mark a command as aiming at the aquarium rather than the host.
_LAN_MARKERS = ("aquadirector", "kactoily", "smartlife", "tuya", "eheim")

# A command containing any of these is refused outright rather than parsed. Shell
# composition would let an allowed prefix carry an arbitrary payload.
#
# `|` is deliberately NOT here. Models routinely append `2>&1 | head -100` to a
# terminal call, and in production that works — so refusing it would make the
# eval diverge from the behaviour it is meant to measure. Pipelines are allowed
# when every stage after the first is a pure text filter. `2>&1` is stripped
# before this scan for the same reason.
_FORBIDDEN_CHARACTERS = (";", "&", "`", "$", ">", "<", "\n")

# Read-only text filters. Nothing here can write a file, spawn a process or open
# a socket, so an allowed pipeline cannot become an arbitrary one.
_SAFE_FILTERS = frozenset(
    {"head", "tail", "cat", "wc", "grep", "egrep", "fgrep", "sort", "uniq",
     "cut", "tr", "nl", "jq", "column", "rev", "tee"}
    - {"tee"}  # tee writes; excluded explicitly so the omission is deliberate
)

AQUA_SCRIPT_SUFFIX = ("scripts", "aqua.py")


@dataclass
class Interceptor:
    """Records blocked and rewritten tool calls for one agent run.

    Scoped by ``session_id``, not by thread. Hermes dispatches tool calls on a
    different thread from the one that called ``run_conversation`` — proven by an
    eval where the agent reported the block message while the interceptor had
    recorded nothing, because the call arrived on an unowned thread. ``session_id``
    is unique per ``AIAgent`` and travels with the hook payload
    (``hermes_cli/plugins.py:6640``), so it survives whatever thread the call
    lands on.
    """

    aqua_data_dir: Path | None = None
    session_id: str | None = None
    blocked: list[dict[str, Any]] = field(default_factory=list)
    allowed: list[str] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __call__(self, **kwargs) -> dict[str, Any] | None:
        """The ``pre_tool_call`` callback.

        Returns a block directive for a blocked tool, a modify directive for an
        allowed aqua invocation, and ``None`` otherwise so every other tool
        dispatches normally. Wrapped end to end: a bug here must degrade to "tool
        runs" rather than "record silently lost".
        """
        try:
            tool_name = kwargs.get("tool_name") or ""
            if tool_name not in BLOCKED_TOOLS:
                return None
            args = kwargs.get("args")
            args = args if isinstance(args, dict) else {}
            command = _describe(tool_name, args)

            rewritten = self._rewrite_aqua(tool_name, command)
            if rewritten is not None:
                with self._lock:
                    self.allowed.append(rewritten)
                return {"action": "modify", "args": {"command": rewritten}}

            with self._lock:
                self.blocked.append(
                    {"tool": tool_name, "command": command, "args": args}
                )
            return {"action": "block", "message": block_message(command)}
        except Exception:  # noqa: BLE001 — see module docstring
            return None

    def _rewrite_aqua(self, tool_name: str, command: str) -> str | None:
        """Return the command with ``--data-dir`` injected, or None if not allowed."""
        if tool_name != "terminal" or self.aqua_data_dir is None:
            return None
        stages = split_aqua_pipeline(command)
        if stages is None:
            return None
        if "--data-dir" in stages[0]:
            return None  # already scoped; leave it alone rather than double-flag
        head = stages[0]
        # Before the subcommand's own arguments, so argparse binds it to the
        # top-level parser rather than the subparser.
        stages[0] = [*head[:2], "--data-dir", str(self.aqua_data_dir), *head[2:]]
        return " | ".join(shlex.join(stage) for stage in stages)

    @property
    def commands(self) -> list[str]:
        with self._lock:
            return [entry["command"] for entry in self.blocked if entry["command"]]

    @property
    def aqua_calls(self) -> list[str]:
        with self._lock:
            return list(self.allowed)

    def records(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.blocked)


def split_aqua_pipeline(command: str) -> list[list[str]] | None:
    """Parse an aqua invocation, optionally piped into read-only filters.

    Returns the parsed stages, or None if this is not an allowed aqua command.

    Deliberately strict about what it accepts and deliberately permissive about
    pipelines. A substring match on "aqua.py" would let ``rm -rf / # aqua.py``
    through; refusing every pipe would block ``aqua.py status 2>&1 | head``,
    which is what models actually write and what production actually runs.
    """
    text = (command or "").strip()
    if not text:
        return None
    # `2>&1` is the one redirection worth allowing: it merges streams, it cannot
    # write a file, and models add it reflexively.
    text = text.replace("2>&1", " ")
    if any(token in text for token in _FORBIDDEN_CHARACTERS):
        return None

    stages: list[list[str]] = []
    for index, segment in enumerate(text.split("|")):
        try:
            parts = shlex.split(segment)
        except ValueError:
            return None
        if not parts:
            return None
        if index == 0:
            if len(parts) < 2:
                return None
            if not Path(parts[0]).name.startswith("python"):
                return None
            if Path(parts[1]).parts[-2:] != AQUA_SCRIPT_SUFFIX:
                return None
        elif Path(parts[0]).name not in _SAFE_FILTERS:
            return None
        stages.append(parts)
    return stages


def is_aqua_command(command: str) -> bool:
    """Is this exactly an invocation of the skill's own data CLI?"""
    return split_aqua_pipeline(command) is not None


def block_message(command: str) -> str:
    """The tool result the model sees. Must be coherent for the command given."""
    lowered = (command or "").lower()
    if any(marker in lowered for marker in _LAN_MARKERS):
        return LAN_BLOCK_MESSAGE
    return GENERIC_BLOCK_MESSAGE


def _describe(tool_name: str, args: dict[str, Any]) -> str:
    """A one-line rendering of what the model tried to run."""
    for key in ("command", "cmd", "code", "script", "task", "prompt"):
        value = args.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().splitlines()[0][:300]
    return tool_name


def install(interceptor: Interceptor) -> None:
    """Route this thread's tool calls through ``interceptor``.

    A single process-global router is registered on the plugin manager, and it
    dispatches to whichever interceptor owns the calling thread.

    The indirection is not decoration. ``manager._hooks["pre_tool_call"]`` is one
    list for the whole process, and Hermes invokes **every** callback in it for
    **every** tool call. Registering one interceptor per parallel eval case
    therefore made each of them record all the others' commands — a green board
    where `casual-trigger` reported running `dose`, which it never did, and where
    a `runs_aqua` assertion could pass on a different case's work.

    Fails safe: a tool call arriving on a thread with no registered interceptor is
    blocked, not executed. If Hermes ever dispatches tools on a pool thread, evals
    break loudly instead of quietly running a shell.
    """
    _router.register(interceptor)


def uninstall(interceptor: Interceptor) -> None:
    """Stop routing this thread's calls. Safe to call twice."""
    _router.unregister(interceptor)


class _Router:
    """One hook, many interceptors, dispatched by session id."""

    def __init__(self) -> None:
        self._by_session: dict[str, Interceptor] = {}
        self._by_thread: dict[int, Interceptor] = {}
        self._lock = threading.Lock()
        self._installed = False

    def register(self, interceptor: Interceptor) -> None:
        with self._lock:
            if interceptor.session_id:
                self._by_session[interceptor.session_id] = interceptor
            # Thread is a fallback for calls that arrive without a session id.
            self._by_thread[threading.get_ident()] = interceptor
            if not self._installed:
                self._install_once()
                self._installed = True

    def unregister(self, interceptor: Interceptor) -> None:
        with self._lock:
            if interceptor.session_id:
                self._by_session.pop(interceptor.session_id, None)
            for ident, registered in list(self._by_thread.items()):
                if registered is interceptor:
                    self._by_thread.pop(ident, None)

    def _resolve(self, session_id: str | None) -> Interceptor | None:
        with self._lock:
            if session_id and session_id in self._by_session:
                return self._by_session[session_id]
            found = self._by_thread.get(threading.get_ident())
            if found is not None:
                return found
            # Single-run callers (`ask`) have exactly one interceptor and may
            # dispatch on any thread. With several registered we cannot tell them
            # apart, so fall through to the block below rather than guess.
            if len(self._by_session) == 1 and not session_id:
                return next(iter(self._by_session.values()))
            return None

    def _install_once(self) -> None:
        from hermes_cli.plugins import get_plugin_manager

        # Direct mutation of `manager._hooks` is the same path Hermes' own
        # shell-hook bridge uses (agent/shell_hooks.py:320). The public
        # register_hook is only reachable from a plugin's register(ctx), which
        # would mean shipping a plugin directory to do one thing.
        manager = get_plugin_manager()
        callbacks = manager._hooks.setdefault("pre_tool_call", [])
        if self not in callbacks:
            callbacks.append(self)

    def __call__(self, **kwargs) -> dict[str, Any] | None:
        try:
            interceptor = self._resolve(kwargs.get("session_id"))
            if interceptor is not None:
                return interceptor(**kwargs)
            if (kwargs.get("tool_name") or "") in BLOCKED_TOOLS:
                # Unattributable call: refuse rather than let a shell through.
                # Recorded nowhere by definition, so if this fires the eval will
                # show a block the interceptor did not log - which is exactly how
                # the thread-scoping bug was found.
                return {"action": "block", "message": GENERIC_BLOCK_MESSAGE}
            return None
        except Exception:  # noqa: BLE001 — hook dispatch is fail-open
            return None


_router = _Router()


def rebind(interceptor: Interceptor, session_id: str | None) -> None:
    """Attach an already-installed interceptor to an agent's session id.

    Called once the AIAgent exists, since its session id is only known then.
    """
    _router.unregister(interceptor)
    interceptor.session_id = session_id
    _router.register(interceptor)
