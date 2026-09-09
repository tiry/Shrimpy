"""Behavioural evals: prompt in, assertions out.

Complements tests/, which proves the persona and skill index are *assembled*
correctly. This proves they are *acted on* — which needs real model calls, so it
costs money and is not part of `./shrimpy test`.

Two grading mechanisms, deliberately:

  * regex assertions for facts with a single right answer (a dose is 2.5 mL or
    it is not);
  * a rubric graded by a second model for properties that are semantic ("does it
    avoid presenting an unmeasured number as fact"), where a substring match
    would be either brittle or meaningless.

Results are appended to evals/results/<timestamp>.jsonl so a regression can be
diffed against an earlier run.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

from harness import transcript

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "evals" / "cases"
RESULTS_DIR = REPO_ROOT / "evals" / "results"
TRANSCRIPTS_DIR = REPO_ROOT / ".work" / "transcripts"

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

# A run can fail because the provider is unavailable rather than because the
# agent misbehaved. Those are different answers and must not share an exit code:
# a red build should mean "Shrimpy is wrong", not "OpenRouter was down at 3am".
PROVIDER_ERROR_MARKERS = (
    "402",
    "429",
    "500",
    "502",
    "503",
    "504",
    "insufficient",
    "credits",
    "rate limit",
    "rate-limit",
    "overloaded",
    "timeout",
    "timed out",
    "connection",
    "temporarily unavailable",
    "service unavailable",
    "authentication",
    "unauthorized",
    "invalid api key",
)


def _commit() -> str:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        ).stdout.strip() or "?"
    except Exception:  # noqa: BLE001
        return "?"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def is_provider_error(error: str | None) -> bool:
    lowered = (error or "").lower()
    return any(marker in lowered for marker in PROVIDER_ERROR_MARKERS)

# Hold the real stdout: harness.agent replaces sys.stdout with a per-thread
# router to mute agent runs, and the report must not go through it.
_STDOUT = sys.stdout


def out_write(line: str = "") -> None:
    """Print a report line immediately — a long eval should stream, not batch."""
    _STDOUT.write(line + "\n")
    _STDOUT.flush()


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    reply: str = ""
    skills_opened: list[str] = field(default_factory=list)
    tokens: int = 0
    cost_usd: float | None = None
    wall_s: float = 0.0
    judge_note: str = ""
    error: str | None = None
    cached: bool = False
    messages: list = field(default_factory=list)
    system_prompt: str = ""
    model: str = ""
    blocked_commands: list[str] = field(default_factory=list)
    aqua_calls: list[str] = field(default_factory=list)


def load_cases(path: Path | None = None, only: list[str] | None = None) -> list[dict]:
    files = [path] if path else sorted(CASES_DIR.glob("*.yaml"))
    cases: list[dict] = []
    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
        for case in data.get("cases", []):
            case["_file"] = file.name
            cases.append(case)
    if only:
        wanted = set(only)
        cases = [c for c in cases if c.get("id") in wanted]
        missing = wanted - {c.get("id") for c in cases}
        if missing:
            raise SystemExit(f"no such case(s): {sorted(missing)}")
    return cases


def check(case: dict, result) -> list[str]:
    """Deterministic assertions. Returns a list of failure descriptions."""
    expect = case.get("expect") or {}
    reply = result.final
    failures: list[str] = []

    for skill in expect.get("opens_skills") or []:
        if skill not in result.skills_opened:
            failures.append(
                f"did not open skill {skill!r} "
                f"(opened: {result.skills_opened or 'nothing'})"
            )

    for pattern in expect.get("matches_all") or []:
        if not re.search(pattern, reply, re.IGNORECASE):
            failures.append(f"missing required /{pattern}/")

    any_patterns = expect.get("matches_any") or []
    if any_patterns and not any(re.search(p, reply, re.IGNORECASE) for p in any_patterns):
        failures.append(f"none of {any_patterns} matched")

    for pattern in expect.get("not_matches") or []:
        found = re.search(pattern, reply, re.IGNORECASE)
        if found:
            failures.append(f"matched forbidden /{pattern}/ -> {found.group(0)!r}")

    limit = expect.get("max_chars")
    if limit and len(reply) > limit:
        failures.append(f"reply is {len(reply)} chars, limit {limit}")

    if expect.get("attempts_no_commands") and result.blocked_commands:
        failures.append(
            f"attempted {len(result.blocked_commands)} shell command(s): "
            f"{result.blocked_commands[:3]}"
        )

    for verb in expect.get("runs_aqua") or []:
        if not any(f" {verb}" in call for call in result.aqua_calls):
            failures.append(
                f"did not run `aqua {verb}` (ran: "
                + (", ".join(_aqua_verb(c) for c in result.aqua_calls) or "nothing")
                + ")"
            )

    alternatives = expect.get("runs_any_aqua") or []
    if alternatives and not any(
        f" {verb}" in call for verb in alternatives for call in result.aqua_calls
    ):
        failures.append(
            f"ran none of `aqua {'|'.join(alternatives)}` (ran: "
            + (", ".join(_aqua_verb(c) for c in result.aqua_calls) or "nothing")
            + ")"
        )

    if expect.get("runs_no_aqua") and result.aqua_calls:
        failures.append(f"ran the CLI when it should not have: {result.aqua_calls[:2]}")

    return failures


def _aqua_verb(command: str) -> str:
    """The subcommand from a full aqua invocation, for readable failure messages."""
    parts = command.split()
    for index, token in enumerate(parts):
        if token.endswith("aqua.py"):
            rest = [p for p in parts[index + 1:] if not p.startswith("-")]
            # skip the injected --data-dir value
            return rest[1] if len(rest) > 1 and "/" in rest[0] else (rest[0] if rest else "?")
    return "?"


def run_case(
    case: dict, *, home, model: str | None, use_judge: bool,
    use_snapshot: bool, force_live: bool,
) -> CaseResult:
    from harness import agent as agent_mod

    started = time.monotonic()
    result = agent_mod.run(
        case["prompt"],
        model=model,
        home=home,
        toolsets=case.get("toolsets"),
        use_snapshot=use_snapshot,
        force_live=force_live,
        case_id=case["id"],
    )

    if result.failed or not result.final:
        return CaseResult(
            case_id=case["id"],
            passed=False,
            failures=["agent run failed"],
            error=result.error or "empty response",
            wall_s=time.monotonic() - started,
            blocked_commands=result.blocked_commands,
            messages=result.messages,
            system_prompt=result.system_prompt,
            model=result.model,
        )

    failures = check(case, result)
    judge_note = ""
    rubric = case.get("judge")
    if rubric and use_judge:
        try:
            ok, note = agent_mod.judge(
                case["prompt"], result.final, rubric,
                use_snapshot=use_snapshot, force_live=force_live,
            )
            judge_note = note
            if not ok:
                failures.append(f"judge: {note.splitlines()[-1][:160]}")
        except Exception as exc:  # noqa: BLE001
            judge_note = f"judge unavailable: {type(exc).__name__}: {exc}"

    return CaseResult(
        case_id=case["id"],
        passed=not failures,
        failures=failures,
        reply=result.final,
        skills_opened=result.skills_opened,
        tokens=result.total_tokens,
        cost_usd=result.cost_usd,
        wall_s=result.wall_s,
        judge_note=judge_note,
        cached=result.cached,
        blocked_commands=result.blocked_commands,
        aqua_calls=result.aqua_calls,
        messages=result.messages,
        system_prompt=result.system_prompt,
        model=result.model,
    )


def main(args) -> int:
    from harness import agent as agent_mod
    from harness import home as home_mod

    cases = load_cases(Path(args.file) if args.file else None, args.case)
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2

    model = home_mod.resolve_model(getattr(args, "model", None))
    # One home for the whole batch: activate() is process-wide, so per-case homes
    # would race. Cases stay isolated because each gets a fresh agent with no
    # session store.
    home = agent_mod.prepare(model=model, ephemeral=True)


    use_judge = not args.no_judge
    use_snapshot = not getattr(args, "no_snapshot", False)
    force_live = getattr(args, "live", False)

    mode = "live" if force_live else ("snapshot" if use_snapshot else "no-cache")
    out_write(f"{DIM}{len(cases)} cases · {model} · {args.jobs} parallel · {mode}{RESET}\n")

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(
            pool.map(
                lambda c: run_case(
                    c,
                    home=home,
                    model=model,
                    use_judge=use_judge,
                    use_snapshot=use_snapshot,
                    force_live=force_live,
                ),
                cases,
            )
        )

    width = max(len(r.case_id) for r in results)
    spent = 0.0
    recorded = 0.0
    for res in results:
        mark = f"{GREEN}PASS{RESET}" if res.passed else f"{RED}FAIL{RESET}"
        cost = res.cost_usd or 0.0
        recorded += cost
        if not res.cached:
            spent += cost
        # A cached pass must never be mistaken for a fresh one — otherwise a
        # green board says nothing about the model's current behaviour.
        tag = f" {DIM}(cached){RESET}" if res.cached else "         "
        blocked = (
            f"  blocked: {len(res.blocked_commands)}" if res.blocked_commands else ""
        )
        aqua = (
            "  aqua: " + ",".join(_aqua_verb(c) for c in res.aqua_calls)
            if res.aqua_calls else ""
        )
        out_write(
            f"{mark}{tag}  {res.case_id.ljust(width)}  "
            f"{DIM}{res.tokens:>6} tok  ${cost:.4f}  {res.wall_s:>5.1f}s"
            f"  skills: {','.join(res.skills_opened) or '-'}{aqua}{blocked}{RESET}"
        )
        for failure in res.failures:
            out_write(f"      {YELLOW}· {failure}{RESET}")
        for command in res.blocked_commands:
            out_write(f"      {DIM}⊘ blocked: {command}{RESET}")
        if args.verbose and res.reply:
            indented = "\n".join("      " + ln for ln in res.reply.splitlines())
            out_write(f"{DIM}{indented}{RESET}\n")

    passed = sum(1 for r in results if r.passed)
    cached = sum(1 for r in results if r.cached)
    unreachable = [r for r in results if not r.passed and is_provider_error(r.error)]
    misbehaved = [r for r in results if not r.passed and not is_provider_error(r.error)]
    colour = GREEN if passed == len(results) else RED
    # Per-row cost is what the run cost when it was recorded; the total is what
    # this invocation actually spent. Conflating them makes a free run look
    # expensive and, worse, an expensive one look free.
    tail = f"  ·  {DIM}{cached}/{len(results)} cached (${recorded:.4f} recorded){RESET}" if cached else ""
    out_write(f"\n{colour}{passed}/{len(results)} passed{RESET}  ·  ${spent:.4f} spent{tail}")
    if cached == len(results):
        out_write(f"{DIM}all cached — nothing was measured live. --live to re-record.{RESET}")

    if unreachable:
        out_write(
            f"\n{YELLOW}{len(unreachable)} case(s) could not reach the provider{RESET} — "
            "not an agent failure:"
        )
        for res in unreachable:
            out_write(f"  {DIM}{res.case_id}: {(res.error or '')[:120]}{RESET}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%fZ")
    out = RESULTS_DIR / f"{stamp}.jsonl"
    with out.open("w", encoding="utf-8") as handle:
        for res in results:
            handle.write(json.dumps({"model": model, **res.__dict__}) + "\n")
    out_write(f"{DIM}{out.relative_to(REPO_ROOT)}{RESET}")

    # Rendered transcripts. Fail-open: a report is worth less than a result, so
    # nothing here may raise into the caller. See specs/08.
    try:
        target = Path(os.environ.get("SHRIMPY_TRANSCRIPT_DIR") or (TRANSCRIPTS_DIR / stamp))
        transcript.write_run(
            target,
            meta={
                "run_label": os.environ.get("SHRIMPY_RUN_LABEL") or stamp,
                "model": model,
                "started": stamp,
                "commit": _commit(),
            },
            cases={c["id"]: c for c in cases},
            results=[r.__dict__ for r in results],
        )
        out_write(f"{DIM}{_display_path(target)}/index.md{RESET}")
    except Exception as exc:  # noqa: BLE001
        out_write(f"{YELLOW}transcripts not written: {exc}{RESET}")

    # Exit codes are the contract CI reads:
    #   0  every case passed
    #   1  the agent behaved wrongly — a real regression
    #   3  the provider was unreachable, so nothing was proven either way
    if passed == len(results):
        return 0
    return 1 if misbehaved else 3
