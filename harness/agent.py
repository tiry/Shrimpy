"""Run Shrimpy against a prompt and return a structured result.

Uses the Python library path (``AIAgent.run_conversation``) rather than shelling
out to ``hermes -z``, for three reasons:

  * ``-z`` prints only the final text, so "did it open the aquarium skill?" —
    the single most important thing to assert about a skill-driven persona —
    is unanswerable from its output;
  * it opens a ``state.db`` and fires an auto-title LLM call per run;
  * it exits via ``os._exit()`` (hermes_cli/main.py:117), which is awkward to
    wrap.

Never pass ``skip_context_files=True`` / ``--safe-mode`` / ``--ignore-rules``
here: all three drop SOUL.md and silently substitute Hermes' generic identity
(agent/system_prompt.py:472-487), so the persona under test would not be running.
"""

from __future__ import annotations

import io
import json
import re
import shutil
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import REPO_ROOT, interception, snapshot
from . import home as home_mod

# Deterministic aquarium data for evals. Not the live data, not the skill's
# bundled migration payload - a third, fixed copy so a case's assertions do not
# move when someone logs a real reading.
AQUA_FIXTURES = REPO_ROOT / "evals" / "fixtures" / "aquarium"

# Tool exposure for a real run. `skills` is mandatory — without it the skill
# index is never rendered into the prompt and the persona has no aquarium
# knowledge at all. `file` lets Shrimpy read its own reference files, which is
# how the aquarium skill is designed to work: SKILL.md defers detail to
# references/ and expects to load them on demand.
#
# `terminal` is granted deliberately. The deployment gives Shrimpy a real shell,
# and SKILL.md tells it not to use one for aquadirector — a rule that cannot be
# tested against an agent that has no shell to decline. Nothing actually runs:
# harness/interception.py blocks shell-capable tools at Hermes' pre_tool_call
# gate and records the attempt.
#
# Must stay in sync with platform_toolsets in config.template.yaml so `ask` and
# `chat` exercise the same agent. Names come from toolsets.TOOLSETS; an unknown
# one is only a warning, so a typo silently removes a capability.
RUN_TOOLSETS = ["skills", "file", "terminal"]

CLARIFY_ANSWER = (
    "[automated harness: no human is available. "
    "State your assumption explicitly and continue.]"
)


class _StdoutRouter(io.TextIOBase):
    """A ``sys.stdout`` replacement that can be muted per-thread.

    ``contextlib.redirect_stdout`` swaps a process-global, so with parallel eval
    cases the last thread to exit restores whatever it happened to capture — and
    every subsequent print in the process disappears into a dead buffer. That is
    not a hypothetical: it silently swallowed the entire eval results table.

    This routes writes through thread-local state instead, so muting one run
    never affects another thread or the caller.
    """

    def __init__(self, real):
        self._real = real
        self._local = threading.local()

    @property
    def _target(self):
        return getattr(self._local, "sink", None) or self._real

    def mute(self):
        self._local.sink = io.StringIO()

    def unmute(self):
        self._local.sink = None

    def write(self, text):  # noqa: D102
        return self._target.write(text)

    def flush(self):  # noqa: D102
        try:
            return self._target.flush()
        except ValueError:
            return None

    def isatty(self):  # noqa: D102
        return self._real.isatty()

    def fileno(self):  # noqa: D102
        return self._real.fileno()

    @property
    def encoding(self):  # noqa: D102
        return getattr(self._real, "encoding", "utf-8")


_router: _StdoutRouter | None = None


@contextmanager
def _muted_stdout():
    """Silence this thread's stdout for the duration of an agent run.

    quiet_mode plus nulled progress callbacks removes the known sources, but a
    stray print from a tool would still corrupt `ask --json` and the eval table.
    """
    global _router
    if _router is None:
        _router = _StdoutRouter(sys.stdout)
        sys.stdout = _router
    _router.mute()
    try:
        yield
    finally:
        _router.unmute()


@dataclass
class RunResult:
    prompt: str
    final: str
    skills_opened: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)
    aqua_calls: list[str] = field(default_factory=list)
    api_calls: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None
    wall_s: float = 0.0
    failed: bool = False
    completed: bool = True
    error: str | None = None
    model: str = ""
    cached: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "final": self.final,
            "skills_opened": self.skills_opened,
            "tool_calls": self.tool_calls,
            "blocked_commands": self.blocked_commands,
            "aqua_calls": self.aqua_calls,
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "wall_s": round(self.wall_s, 1),
            "failed": self.failed,
            "completed": self.completed,
            "error": self.error,
            "model": self.model,
            "cached": self.cached,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RunResult:
        known = {f for f in cls.__dataclass_fields__}  # noqa: F821
        return cls(**{k: v for k, v in payload.items() if k in known})


def _tool_calls(messages: list) -> list[dict]:
    out = []
    for message in messages or []:
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            if isinstance(call, dict) and isinstance(call.get("function"), dict):
                out.append({**call["function"], "_id": call.get("id")})
    return out


def _tool_results(messages: list) -> dict[str, str]:
    """tool_call_id -> the tool's response text."""
    out: dict[str, str] = {}
    for message in messages or []:
        if isinstance(message, dict) and message.get("role") == "tool":
            call_id = message.get("tool_call_id")
            if call_id:
                out[call_id] = str(message.get("content") or "")
    return out


def _tool_failed(response: str) -> bool:
    """Did a tool call fail?

    Hermes returns failures as a JSON payload with an ``error`` key
    (tools/skills_tool.py:1438). Detect that structurally. A substring search for
    "not found" is wrong and was actively harmful here: SKILL.md §7 contains the
    phrase "command not found", so every successful skill_view of the aquarium
    skill looked like a failed one and every eval asserting on skills_opened
    broke at once.
    """
    text = (response or "").strip()
    if not text:
        return True
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        payload = None
    if isinstance(payload, dict):
        return bool(payload.get("error"))
    return bool(re.match(r"^(Error:|Skill '[^']*' not found)", text))


def _skills_opened(functions: list[dict], results: dict[str, str]) -> list[str]:
    """Which skills the model actually *read*.

    Hermes has no field for this — a skill is "loaded" by the model calling the
    ``skill_view`` tool (tools/skills_tool.py), so the answer has to be recovered
    from the tool calls. Failed lookups are excluded: models routinely try the
    category name first ("aquarium"), which is not a skill and returns an error.
    Counting that as a load would make an eval pass on a miss.
    """
    names = []
    for fn in functions:
        if fn.get("name") != "skill_view":
            continue
        try:
            args = json.loads(fn.get("arguments") or "{}")
        except (ValueError, TypeError):
            continue
        name = args.get("name") or args.get("skill")
        if not name or name in names:
            continue
        if _tool_failed(results.get(fn.get("_id") or "", "")):
            continue
        names.append(name)
    return names


def prepare(
    *, model: str | None = None, provider: str | None = None, ephemeral: bool = True
) -> Path:
    """Build and activate a home once, for a batch of runs.

    ``activate()`` mutates process-wide environment, so a parallel eval must not
    have each case build its own home. Cases are isolated by construction
    instead: every run gets a fresh ``AIAgent`` with ``session_db=None``, so
    nothing is shared but the read-only persona on disk.
    """
    home_mod.load_env()
    model = home_mod.resolve_model(model)
    provider = home_mod.resolve_provider(provider)
    home_mod.require_api_key()
    hermes_home = home_mod.build_home(ephemeral=ephemeral, model=model, provider=provider)
    home_mod.activate(hermes_home)
    return hermes_home


def run(
    prompt: str,
    *,
    model: str | None = None,
    provider: str | None = None,
    ephemeral: bool = True,
    max_iterations: int = 20,
    budget_seconds: float = 300.0,
    toolsets: list[str] | None = None,
    keep_home: bool = False,
    home: Path | None = None,
    intercept: bool = True,
    use_snapshot: bool = False,
    force_live: bool = False,
    case_id: str = "",
) -> RunResult:
    """Ask Shrimpy one question. Returns a RunResult; does not raise on model failure.

    Pass ``home=`` from ``prepare()`` to reuse an already-activated home; the
    caller then owns its lifetime.

    ``intercept`` blocks shell-capable tools at Hermes' ``pre_tool_call`` gate and
    records what was attempted, so the agent can be given a production-identical
    toolset without anything actually running.

    ``use_snapshot`` memoises the result on the agent definition — see
    harness/snapshot.py.
    """
    model = home_mod.resolve_model(model)
    provider = home_mod.resolve_provider(provider)
    effective_toolsets = list(toolsets or RUN_TOOLSETS)

    # A per-run copy of the eval fixtures, so parallel cases cannot see each
    # other's writes. AQUA_DATA_DIR is process-global; the interceptor is not,
    # so the data dir is injected per tool call instead of exported.
    aqua_dir: Path | None = None
    aqua_tmp: Path | None = None
    if intercept:
        aqua_tmp = Path(tempfile.mkdtemp(prefix="shrimpy-aqua-"))
        aqua_dir = aqua_tmp / "aquarium"
        if AQUA_FIXTURES.is_dir():
            shutil.copytree(AQUA_FIXTURES, aqua_dir)
        else:
            aqua_dir.mkdir(parents=True)

    key = None
    if use_snapshot:
        definition = snapshot.definition_sha()
        key = snapshot.run_key(
            prompt,
            model=model,
            provider=provider,
            toolsets=effective_toolsets,
            definition=definition,
        )
        if not force_live:
            cached = snapshot.load_run(key)
            if cached is not None:
                result = RunResult.from_dict(cached)
                result.cached = True
                return result

    owned = home is None
    hermes_home = home if home is not None else prepare(
        model=model, provider=provider, ephemeral=ephemeral
    )

    interceptor = interception.Interceptor(aqua_data_dir=aqua_dir) if intercept else None
    started = time.monotonic()
    try:
        from run_agent import AIAgent  # after activate(): binds HERMES_HOME at import

        if interceptor is not None:
            interception.install(interceptor)

        agent = AIAgent(
            model=model,
            provider=provider,
            quiet_mode=True,
            enabled_toolsets=effective_toolsets,
            # SOUL.md and the skills index stay ON. Only memory and the
            # post-turn self-improvement fork are suppressed.
            skip_memory=True,
            skip_background_review=True,
            session_db=None,  # no state.db, and no auto-title LLM call
            max_iterations=max_iterations,
            run_budget_seconds=budget_seconds,
            platform="cli",
            tool_progress_mode="off",
            clarify_callback=lambda *a, **k: CLARIFY_ANSWER,
        )
        # quiet_mode alone still emits tool-progress lines on stdout, which would
        # be interleaved with the answer. Same teardown cli.py does for -Q
        # (cli.py:22128).
        for attr in (
            "stream_delta_callback",
            "tool_gen_callback",
            "reasoning_callback",
            "tool_progress_callback",
            "tool_start_callback",
            "tool_complete_callback",
        ):
            if hasattr(agent, attr):
                setattr(agent, attr, None)
        agent.suppress_status_output = True

        # Scope the interceptor to this agent's session before any tool can fire.
        # Hermes dispatches tool calls off-thread, so session_id is the only key
        # that reliably identifies which run a call belongs to.
        if interceptor is not None:
            interception.rebind(interceptor, getattr(agent, "session_id", None))

        with _muted_stdout():
            raw = agent.run_conversation(prompt)

        functions = _tool_calls(raw.get("messages") or [])
        results = _tool_results(raw.get("messages") or [])
        result = RunResult(
            prompt=prompt,
            final=raw.get("final_response") or "",
            skills_opened=_skills_opened(functions, results),
            tool_calls=[fn.get("name", "?") for fn in functions],
            blocked_commands=interceptor.commands if interceptor else [],
            aqua_calls=interceptor.aqua_calls if interceptor else [],
            api_calls=raw.get("api_calls") or 0,
            total_tokens=raw.get("total_tokens") or 0,
            cost_usd=raw.get("estimated_cost_usd"),
            wall_s=time.monotonic() - started,
            failed=bool(raw.get("failed")),
            completed=bool(raw.get("completed")),
            error=raw.get("error"),
            model=raw.get("model") or model,
        )
        # Only record a run that actually produced an answer: caching a
        # transport error would make one bad network moment permanent.
        if key and not result.failed and result.final:
            snapshot.save_run(
                key,
                result=result.to_dict(),
                case_id=case_id,
                definition=snapshot.definition_sha(),
            )
        return result
    except Exception as exc:  # noqa: BLE001 — a harness reports failures, it does not crash
        return RunResult(
            prompt=prompt,
            final="",
            blocked_commands=interceptor.commands if interceptor else [],
            aqua_calls=interceptor.aqua_calls if interceptor else [],
            wall_s=time.monotonic() - started,
            failed=True,
            completed=False,
            error=f"{type(exc).__name__}: {exc}",
            model=model,
        )
    finally:
        if interceptor is not None:
            interception.uninstall(interceptor)
        if aqua_tmp is not None:
            shutil.rmtree(aqua_tmp, ignore_errors=True)
        if owned and ephemeral and not keep_home:
            shutil.rmtree(hermes_home, ignore_errors=True)


def judge(
    question: str,
    answer: str,
    rubric: str,
    *,
    model: str | None = None,
    use_snapshot: bool = False,
    force_live: bool = False,
) -> tuple[bool, str]:
    """Grade an answer against a rubric with a cheap second model.

    Used only for cases where the property under test is semantic ("does it avoid
    presenting an unmeasured number as fact") and a substring match would be
    either brittle or meaningless.

    Cached separately from the run, keyed on (question, answer, rubric, model):
    editing a regex assertion should not re-pay for judging, and neither should
    a run that came back from a snapshot.
    """
    import os

    from openai import OpenAI

    model = home_mod.resolve_judge_model(model)

    key = None
    if use_snapshot:
        key = snapshot.judge_key(question, answer, rubric, model)
        if not force_live:
            cached = snapshot.load_judge(key)
            if cached is not None:
                return cached

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    reply = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You grade an aquarium assistant's reply against one criterion. "
                    "Answer with exactly 'PASS' or 'FAIL' on the first line, then one "
                    "short sentence of justification. Judge only the stated criterion."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"USER ASKED:\n{question}\n\n"
                    f"ASSISTANT REPLIED:\n{answer}\n\n"
                    f"CRITERION:\n{rubric}"
                ),
            },
        ],
    )
    text = (reply.choices[0].message.content or "").strip()
    passed = text.upper().startswith("PASS")
    if key:
        snapshot.save_judge(key, passed=passed, note=text)
    return passed, text


def persistent_home(model: str | None = None, provider: str | None = None) -> Path:
    """The .work/home used by `chat` and by `ask --keep`, rebuilt from the repo."""
    home_mod.load_env()
    return home_mod.build_home(
        ephemeral=False,
        model=home_mod.resolve_model(model),
        provider=home_mod.resolve_provider(provider),
    )
