"""Command dispatch for ./shrimpy. Not intended to be imported."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import REPO_ROOT, home as home_mod


# --------------------------------------------------------------------------- #
# prompt — offline
# --------------------------------------------------------------------------- #

def cmd_prompt(args) -> int:
    """Print what the model will actually see. No API call, no key required."""
    from . import inspect as insp

    hermes_home = home_mod.build_home(ephemeral=True, model=args.model)
    home_mod.activate(hermes_home)

    agent = insp.build_inspection_agent(model=home_mod.resolve_model(args.model))
    prompt = insp.system_prompt(agent)
    block = insp.skills_index(prompt)

    if args.skills:
        if not block:
            print(
                "NO SKILL INDEX RENDERED.\n"
                "Every skill was dropped. The usual cause is invalid YAML frontmatter — "
                "an unquoted ': ' in a description makes `platforms` parse as a string "
                "and the skill vanishes silently. Run ./shrimpy test.",
                file=sys.stderr,
            )
            return 1
        print(block)
        return 0

    if args.size:
        parts = insp.system_prompt_parts(agent)
        parsed = insp.parse_index(block)
        report = {
            "model": home_mod.resolve_model(args.model),
            "system_prompt_chars": len(prompt),
            "skills_index_chars": len(block),
            "sections": {k: len(v or "") for k, v in parts.items()},
            "categories": {k: len(v) for k, v in parsed["categories"].items()},
            "skills": parsed["skills"],
            "soul_loaded": "Shrimpy" in prompt,
        }
        print(json.dumps(report, indent=2))
        return 0

    print(prompt)
    return 0


# --------------------------------------------------------------------------- #
# ask — one shot
# --------------------------------------------------------------------------- #

def cmd_ask(args) -> int:
    from . import agent as agent_mod

    question = " ".join(args.question).strip()
    if not question:
        print("nothing to ask", file=sys.stderr)
        return 2

    result = agent_mod.run(
        question,
        model=args.model,
        ephemeral=not args.keep,
        max_iterations=args.max_iterations,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 1 if result.failed else 0

    if result.error:
        print(f"error: {result.error}", file=sys.stderr)
    if result.final:
        print(result.final)
    if args.verbose:
        cost = f"${result.cost_usd:.4f}" if result.cost_usd is not None else "?"
        print(
            f"\n\033[2m— skills: {', '.join(result.skills_opened) or 'none'}"
            f" | tools: {', '.join(result.tool_calls) or 'none'}"
            f" | {result.api_calls} calls, {result.total_tokens} tok, {cost}"
            f", {result.wall_s:.1f}s\033[0m",
            file=sys.stderr,
        )
    return 1 if result.failed else 0


# --------------------------------------------------------------------------- #
# chat — interactive REPL
# --------------------------------------------------------------------------- #

def cmd_chat(args) -> int:
    """Hand off to the real Hermes REPL with HERMES_HOME pointed at the persona.

    Uses the persistent .work/home so sessions survive restarts. SOUL.md and the
    skill tree are symlinks into the repo, so edits take effect on the next turn
    without leaving the REPL.
    """
    from . import agent as agent_mod

    hermes_home = agent_mod.persistent_home(model=args.model)
    env = dict(os.environ)
    env["HERMES_HOME"] = str(hermes_home)
    if args.yolo:
        env["HERMES_YOLO_MODE"] = "1"

    hermes_bin = REPO_ROOT / ".venv" / "bin" / "hermes"
    if not hermes_bin.exists():
        print("hermes not installed — run: ./shrimpy setup", file=sys.stderr)
        return 1

    print(f"\033[2mShrimpy · {home_mod.resolve_model(args.model)} · {hermes_home}\033[0m",
          file=sys.stderr)
    argv = [str(hermes_bin), "chat", *args.rest]
    os.execve(str(hermes_bin), argv, env)  # noqa: S606 — deliberate handoff


# --------------------------------------------------------------------------- #
# eval
# --------------------------------------------------------------------------- #

def cmd_eval(args) -> int:
    from evals.runner import main as eval_main

    return eval_main(args)


def cmd_snapshots(args) -> int:
    """Inspect or clear the eval result cache."""
    from . import snapshot

    if args.clear:
        removed = snapshot.clear()
        print(f"cleared {removed} cached file(s)")
        return 0

    counts = snapshot.stats()
    print(f"runs:       {counts['runs']}")
    print(f"judgements: {counts['judgements']}")
    print(f"definition: {snapshot.definition_sha()[:16]}")
    print(
        "\nSnapshots key on the agent definition, so editing SOUL.md or any skill\n"
        "invalidates all of them — which is when you want to re-measure anyway."
    )
    return 0


# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="shrimpy", add_help=True)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("-m", "--model", default=None, help="override SHRIMPY_MODEL")
        return p

    p = add("prompt", "print the assembled system prompt (offline)")
    p.add_argument("--skills", action="store_true", help="only the <available_skills> block")
    p.add_argument("--size", action="store_true", help="JSON size/structure report")
    p.set_defaults(func=cmd_prompt)

    p = add("ask", "ask one question")
    p.add_argument("question", nargs="+")
    p.add_argument("-v", "--verbose", action="store_true", help="skills, tools, tokens, cost")
    p.add_argument("--json", action="store_true", help="full structured result")
    p.add_argument("--keep", action="store_true", help="use .work/home instead of a temp dir")
    p.add_argument("--max-iterations", type=int, default=20)
    p.set_defaults(func=cmd_ask)

    p = add("chat", "interactive REPL as Shrimpy")
    p.add_argument("--yolo", action="store_true", help="auto-approve tool use")
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_chat)

    p = add("eval", "run behavioural evals")
    p.add_argument("--case", action="append", default=None, help="case id (repeatable)")
    p.add_argument("--file", default=None, help="a specific evals/cases/*.yaml")
    p.add_argument("-j", "--jobs", type=int, default=4, help="parallel cases")
    p.add_argument("--no-judge", action="store_true", help="skip rubric grading")
    p.add_argument(
        "--live",
        action="store_true",
        help="ignore snapshots and re-record (a full pass costs real money)",
    )
    p.add_argument(
        "--no-snapshot",
        action="store_true",
        help="neither read nor write snapshots",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="print full replies")
    p.set_defaults(func=cmd_eval)

    p = add("snapshots", "inspect or clear the eval result cache")
    p.add_argument("--clear", action="store_true", help="delete every snapshot")
    p.set_defaults(func=cmd_snapshots)

    args = parser.parse_args(argv)

    # The .env must be read before anything imports run_agent.
    home_mod.load_env()
    sys.path.insert(0, str(REPO_ROOT))
    return args.func(args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
