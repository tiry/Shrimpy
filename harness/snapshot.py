"""Turn-level result cache, so re-running evals is free and deterministic.

Two problems this solves. A full eval pass costs about a dollar, which makes
tuning an assertion expensive. And every run draws a fresh sample, so a real
regression and ordinary model variance look identical.

Both go away if a run is memoised on **everything that legitimately changes the
answer**:

    prompt · model · provider · toolsets · SOUL.md · skills/** · config template

Edit a skill and every snapshot invalidates — which is exactly when you want to
re-measure. Tweak a regex or a judge rubric and nothing invalidates, which is
the common case.

Rejected alternative: recording provider responses under Hermes'
``llm_execution`` middleware, the equivalent of LangGraph's ``wrap_model_call``.
It is a real and well-built seam, but the request carries three volatile
regions — the ephemeral HERMES_HOME path, live git status, and the session date —
so keying on it needs a normaliser, plus response serialisation and a streaming
spike. It only earns that complexity if you need to intercept *within* a turn,
which nothing here does. Cache the turn.

Snapshots live under `.work/` and are gitignored: a local cache, not a fixture
to review in a diff.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from . import REPO_ROOT

SNAPSHOT_DIR = REPO_ROOT / ".work" / "snapshots"
JUDGE_DIR = REPO_ROOT / ".work" / "judgements"

# Bump to invalidate every snapshot after a change to what a RunResult contains.
SCHEMA = 3  # bumped when RunResult gained aqua_calls


def definition_sha() -> str:
    """A digest of the agent definition and the harness config that runs it.

    Covers SOUL.md, every file under skills/ (including references/, the CLI and
    its bundled data), config.template.yaml, and the eval fixtures. Paths are
    included so a rename invalidates, not just a content edit.

    Fixtures are in here because they change the answer: a case that reads
    `aqua status` gets a different reply if the fixture's readings change, and a
    cached pass would otherwise keep reporting the old one.
    """
    sha = hashlib.sha256()
    sha.update(f"schema={SCHEMA}\n".encode())
    paths = [REPO_ROOT / "SOUL.md", REPO_ROOT / "harness" / "config.template.yaml"]
    for tree in (REPO_ROOT / "skills", REPO_ROOT / "evals" / "fixtures"):
        if tree.is_dir():
            paths.extend(
                sorted(
                    p for p in tree.rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts
                )
            )
    for path in paths:
        if not path.is_file():
            continue
        sha.update(str(path.relative_to(REPO_ROOT)).encode())
        sha.update(path.read_bytes())
    return sha.hexdigest()


def run_key(prompt: str, *, model: str, provider: str, toolsets, definition: str) -> str:
    payload = json.dumps(
        {
            "prompt": prompt,
            "model": model,
            "provider": provider,
            "toolsets": sorted(toolsets or []),
            "definition": definition,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def judge_key(question: str, answer: str, rubric: str, model: str) -> str:
    payload = json.dumps(
        {"q": question, "a": answer, "r": rubric, "m": model}, sort_keys=True
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _read(directory: Path, key: str) -> dict[str, Any] | None:
    path = directory / f"{key}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt entry is a cache miss, never a crash.
        return None


def _write(directory: Path, key: str, payload: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    tmp = directory / f"{key}.json.tmp"
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(directory / f"{key}.json")


def load_run(key: str) -> dict[str, Any] | None:
    entry = _read(SNAPSHOT_DIR, key)
    return entry.get("result") if entry else None


def save_run(key: str, *, result: dict[str, Any], case_id: str, definition: str) -> None:
    _write(
        SNAPSHOT_DIR,
        key,
        {
            "case_id": case_id,
            "definition_sha": definition,
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result": result,
        },
    )


def load_judge(key: str) -> tuple[bool, str] | None:
    entry = _read(JUDGE_DIR, key)
    if not entry:
        return None
    return bool(entry.get("passed")), str(entry.get("note") or "")


def save_judge(key: str, *, passed: bool, note: str) -> None:
    _write(
        JUDGE_DIR,
        key,
        {
            "passed": passed,
            "note": note,
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )


def clear() -> int:
    """Delete every snapshot and judgement. Returns how many files went."""
    removed = 0
    for directory in (SNAPSHOT_DIR, JUDGE_DIR):
        if not directory.is_dir():
            continue
        for path in directory.glob("*.json"):
            path.unlink()
            removed += 1
    return removed


def stats() -> dict[str, int]:
    def count(directory: Path) -> int:
        return len(list(directory.glob("*.json"))) if directory.is_dir() else 0

    return {"runs": count(SNAPSHOT_DIR), "judgements": count(JUDGE_DIR)}
