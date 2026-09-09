"""Render an eval run as markdown a human can read.

A run currently reports ``16/16``, or ``FAIL salt-never — judge: treats salt as a
neutral option``, and nothing more. Three times during development the *case* was
wrong and the agent was right, and each was diagnosable only by reading the
reply. This turns a run into something you can read.

Three details here are lifted from ``../mvp-bootstrap``, which publishes e2e
artefacts the same way and has the scars to show for it:

* **Fenced content must be escaped.** ``skill_view`` returns whole files, and
  ``SKILL.md`` contains ``` fences. Rendered naively inside a fence, the page
  breaks at the first one. A zero-width space before the backticks is invisible
  and stops the fence closing early.
* **The raw log goes beside the rendered file.** Their renderer twice dropped
  half a transcript — unrecognised turn types falling through to a default
  branch and emitting bodiless ``### Turn N · '?'`` rows. Both times the data was
  intact and only the rendering was wrong, which is recoverable exactly when the
  raw log was kept.
* **Ship the machine-readable index.** They delete theirs before publishing and
  then regex-parse the markdown back out to build a dashboard, across two
  incompatible table formats. Documented regret.

Everything here is fail-open: a report is worth less than a result, so a renderer
error must never fail an eval.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

# Above this, a tool response is folded into <details>. A skill_view response is
# 13 KB of SKILL.md; inline it drowns everything around it, and truncated it
# stops being evidence.
COLLAPSE_OVER_BYTES = 2000

ROLE_LABELS = {
    "user": "user",
    "assistant": "assistant",
    "tool": "tool result",
    "system": "system",
}


# --------------------------------------------------------------------------- #
# markdown primitives
# --------------------------------------------------------------------------- #

def fence(text: str, lang: str = "text") -> str:
    """Wrap text in a fenced block, escaping any fence it already contains.

    The zero-width space renders as nothing and stops ``` closing the block
    early. Without it, one `skill_view` response ends the fence a third of the
    way through and the rest of the page renders as garbage.
    """
    escaped = str(text).replace("```", "\u200b```")
    return f"```{lang}\n{escaped}\n```"


def details(summary: str, body: str) -> str:
    """A collapsed block. The blank lines are required or GitHub renders the
    markdown inside as literal text."""
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


def _pretty(value: Any) -> str:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return value
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def _size(text: str) -> str:
    n = len(text.encode("utf-8", "replace"))
    return f"{n / 1024:.1f} KB" if n >= 1024 else f"{n} B"


# --------------------------------------------------------------------------- #
# one case
# --------------------------------------------------------------------------- #

def render_case(case: dict, result: dict) -> str:
    """A single case: verdict, assertions, then the whole conversation."""
    case_id = case.get("id", "?")
    passed = result.get("passed")
    failures = result.get("failures") or []
    mark = "PASS" if passed else "FAIL"
    lines: list[str] = [f"# {case_id} — {mark}", ""]

    if result.get("cached"):
        lines += ["> Replayed from cache; the model was not called for this run.", ""]

    cost = result.get("cost_usd")
    lines += [
        "| | |",
        "|---|---|",
        f"| Outcome | **{mark}** |",
        f"| Model | `{result.get('model') or '?'}` |",
        f"| Tokens | {result.get('tokens') or 0:,} |",
        f"| Cost | ${cost:.4f} |" if isinstance(cost, (int, float)) else "| Cost | — |",
        f"| Wall | {result.get('wall_s') or 0:.1f}s |",
        f"| Skills opened | {', '.join(result.get('skills_opened') or []) or '—'} |",
        f"| CLI calls | {len(result.get('aqua_calls') or [])} |",
        f"| Blocked commands | {len(result.get('blocked_commands') or [])} |",
        "",
    ]

    # Why the case exists, in the author's words. Without it a reader has to
    # guess which rule a failure violated.
    if case.get("why"):
        lines += ["## Why this case exists", "", str(case["why"]).strip(), ""]

    lines += ["## Verdict", ""]
    if failures:
        for failure in failures:
            lines.append(f"- **{failure}**")
    else:
        lines.append("- every assertion held")
    lines.append("")

    expect = case.get("expect") or {}
    if expect or case.get("judge"):
        lines += ["<details><summary>What was asserted</summary>", ""]
        if expect:
            lines += [fence(_pretty(expect), "json"), ""]
        if case.get("judge"):
            lines += ["Rubric:", "", "> " + str(case["judge"]).strip().replace("\n", "\n> "), ""]
        lines += ["</details>", ""]

    if result.get("judge_note"):
        lines += ["## Judge", "", fence(result["judge_note"]), ""]

    if result.get("error"):
        lines += ["## Error", "", fence(str(result["error"])), ""]

    blocked = result.get("blocked_commands") or []
    if blocked:
        lines += ["## Commands blocked at the gate", ""]
        lines += [f"- `{command}`" for command in blocked]
        lines += ["", "_Nothing was executed. See specs/04._", ""]

    lines += ["## Conversation", ""]
    lines.append(render_conversation(result.get("messages") or [], result.get("prompt")))
    return "\n".join(lines).rstrip() + "\n"


def render_conversation(messages: list[dict], prompt: str | None = None) -> str:
    """Numbered turns, with tool calls and their results shown as their own turns."""
    if not messages:
        note = "_No transcript was captured for this run._"
        if prompt:
            return "\n".join([f"**Prompt**\n\n{fence(prompt)}", "", note])
        return note

    lines: list[str] = []
    turn = 0
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "?")
        # The system prompt is stored once per run, not repeated per case.
        if role == "system":
            continue
        turn += 1
        lines += _render_turn(turn, role, message)
    return "\n".join(lines)


def _render_turn(turn: int, role: str, message: dict) -> list[str]:
    label = ROLE_LABELS.get(role, role)
    lines = [f"### Turn {turn} · {label}", ""]

    content = message.get("content")
    if isinstance(content, list):
        # Some providers return content as a list of parts.
        content = "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    content = (content or "").strip()

    if role == "tool":
        name = message.get("name") or "tool"
        if len(content.encode("utf-8", "replace")) > COLLAPSE_OVER_BYTES:
            lines.append(
                details(f"<code>{name}</code> returned {_size(content)}", fence(content))
            )
        else:
            lines += [f"`{name}`", "", fence(content)]
        lines.append("")
        return lines

    if content:
        lines += [fence(content), ""]

    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        function = call.get("function") or {}
        name = function.get("name", "?")
        arguments = _pretty(function.get("arguments") or {})
        lines += [f"**calls `{name}`**", "", fence(arguments, "json"), ""]

    if not content and not (message.get("tool_calls") or []):
        lines += ["_(empty)_", ""]
    return lines


# --------------------------------------------------------------------------- #
# a whole run
# --------------------------------------------------------------------------- #

def render_index(meta: dict, entries: list[dict]) -> str:
    """The run's front page: headline numbers, then a row per case."""
    passed = sum(1 for e in entries if e.get("passed"))
    total = len(entries)
    spent = sum(e.get("cost_usd") or 0 for e in entries if not e.get("cached"))
    tokens = sum(e.get("tokens") or 0 for e in entries)
    cached = sum(1 for e in entries if e.get("cached"))

    lines = [
        f"# Eval run — {meta.get('run_label', 'local')}",
        "",
        "| | |",
        "|---|---|",
        f"| Result | **{passed}/{total} passed** |",
        f"| Model | `{meta.get('model', '?')}` |",
        f"| Spent | ${spent:.4f} |",
        f"| Tokens | {tokens:,} |",
        f"| Started | {meta.get('started', '?')} |",
        f"| Commit | `{meta.get('commit', '?')}` |",
    ]
    if cached:
        lines.append(f"| Cached | {cached}/{total} — those were not measured live |")
    lines += ["", "## Cases", ""]
    lines += [
        "| Case | Result | Skills | CLI calls | Tokens | Cost | Transcript |",
        "|---|---|---|---|--:|--:|---|",
    ]
    for entry in entries:
        cid = entry.get("case_id", "?")
        mark = "PASS" if entry.get("passed") else "**FAIL**"
        cost = entry.get("cost_usd") or 0
        lines.append(
            f"| {cid} | {mark} | {', '.join(entry.get('skills_opened') or []) or '—'} "
            f"| {len(entry.get('aqua_calls') or [])} | {entry.get('tokens') or 0:,} "
            f"| ${cost:.4f} | [read](cases/{cid}.md) |"
        )
    lines += ["", "Raw messages for each case sit beside the rendered file as "
              "`cases/<case>.json`, so a renderer fix can re-render an archived run.", ""]

    failures = [e for e in entries if not e.get("passed")]
    if failures:
        lines += ["## What failed", ""]
        for entry in failures:
            lines.append(f"### {entry.get('case_id')}")
            lines.append("")
            for failure in entry.get("failures") or []:
                lines.append(f"- {failure}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_run(
    out_dir: Path,
    *,
    meta: dict,
    cases: dict[str, dict],
    results: list[dict],
) -> Path:
    """Write the whole tree. Returns the directory written.

    Fail-open by construction: each case is rendered in its own try, so one bad
    message cannot cost the whole report, and the caller never sees an exception.
    """
    out_dir = Path(out_dir)
    cases_dir = out_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for result in results:
        case_id = result.get("case_id") or "unknown"
        case = cases.get(case_id, {})
        # The raw log first, so it survives a renderer that does not.
        with contextlib.suppress(Exception):
            (cases_dir / f"{case_id}.json").write_text(
                json.dumps({"case": case, "result": result}, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        try:
            (cases_dir / f"{case_id}.md").write_text(
                render_case(case, result), encoding="utf-8"
            )
        except Exception as exc:  # noqa: BLE001
            (cases_dir / f"{case_id}.md").write_text(
                f"# {case_id}\n\nRendering failed: `{exc}`.\n\n"
                f"The raw exchange is intact in `{case_id}.json`.\n",
                encoding="utf-8",
            )
        entries.append({k: v for k, v in result.items() if k not in ("messages", "system_prompt")})

    # Shipped, not deleted: it is exactly what a dashboard wants, and parsing
    # markdown back out to recover it is the mistake the reference made.
    (out_dir / "entries.json").write_text(
        json.dumps({"meta": meta, "entries": entries}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "index.md").write_text(render_index(meta, entries), encoding="utf-8")

    system_prompt = next(
        (r.get("system_prompt") for r in results if r.get("system_prompt")), ""
    )
    if system_prompt:
        (out_dir / "system-prompt.md").write_text(
            "# System prompt\n\nIdentical across cases apart from the ephemeral home "
            "path, so it is recorded once.\n\n" + fence(system_prompt) + "\n",
            encoding="utf-8",
        )
    return out_dir
