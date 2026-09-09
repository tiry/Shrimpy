#!/usr/bin/env python3
"""Rebuild the rolling README at the root of the eval-transcripts branch.

Reads every run's ``entries.json`` — the machine-readable index, which is
shipped precisely so this script does not have to parse markdown back out. The
reference implementation deletes theirs and then regex-parses two incompatible
table formats to recover the same numbers.

Stdlib only, and invoked against the branch checkout rather than the repo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RUN_DIR_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2}|\d{8}T\S+?)__run-(?P<num>\d+)__(?P<model>.+)$")


def load_runs(workdir: Path) -> list[dict]:
    runs = []
    for entry in sorted((workdir / "runs").glob("*/entries.json")):
        try:
            payload = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        entries = payload.get("entries") or []
        meta = payload.get("meta") or {}
        name = entry.parent.name
        match = RUN_DIR_RE.match(name)
        runs.append(
            {
                "dir": name,
                "number": int(match.group("num")) if match else 0,
                "date": match.group("date") if match else meta.get("started", "?"),
                "model": meta.get("model") or (match.group("model") if match else "?"),
                "total": len(entries),
                "passed": sum(1 for e in entries if e.get("passed")),
                "cost": sum(e.get("cost_usd") or 0 for e in entries if not e.get("cached")),
                "commit": meta.get("commit", "?"),
            }
        )
    runs.sort(key=lambda r: r["number"], reverse=True)
    return runs


def render(runs: list[dict]) -> str:
    lines = [
        "# Eval transcripts",
        "",
        "Rendered transcripts from `./shrimpy eval --live`, newest first. Each run holds",
        "`index.md`, `cases/<case>.md` with the assertions beside the conversation, and",
        "`cases/<case>.json` with the raw messages so a renderer fix can re-render an",
        "archived run.",
        "",
        "Written by `scripts/publish-transcripts.sh`. Do not edit by hand.",
        "",
    ]
    if not runs:
        lines += ["_No runs published yet._", ""]
        return "\n".join(lines)

    green = sum(1 for r in runs if r["total"] and r["passed"] == r["total"])
    lines += [
        f"**{len(runs)} runs kept** · {green} fully green · "
        f"${sum(r['cost'] for r in runs):.2f} spent in total",
        "",
        "| Run | Date | Model | Result | Cost | Commit | Read |",
        "|---|---|---|---|--:|---|---|",
    ]
    for run in runs:
        result = f"{run['passed']}/{run['total']}"
        if run["total"] and run["passed"] < run["total"]:
            result = f"**{result}**"
        lines.append(
            f"| {run['number']} | {run['date']} | `{run['model']}` | {result} "
            f"| ${run['cost']:.4f} | `{run['commit']}` | [open](runs/{run['dir']}/index.md) |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    workdir = Path(argv[1] if len(argv) > 1 else ".")
    if not (workdir / "runs").is_dir():
        print("no runs/ directory; nothing to render", file=sys.stderr)
        return 0
    (workdir / "README.md").write_text(render(load_runs(workdir)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
