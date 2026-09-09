"""Transcript rendering and publishing.

Two of these guard bugs that ``../mvp-bootstrap`` shipped to production and
documented afterwards: a renderer that silently dropped half a transcript, and a
prune that sorted by mtime after a shallow clone and therefore deleted
near-arbitrary runs. Both are cheap to test and expensive to find in the wild.
"""

from __future__ import annotations

import json
import subprocess

import pytest
from conftest import REPO_ROOT

SKILL_MD = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor" / "SKILL.md"
PUBLISH = REPO_ROOT / "scripts" / "publish-transcripts.sh"


# --------------------------------------------------------------------------- #
# fences — the bug that breaks a whole page
# --------------------------------------------------------------------------- #

def test_embedded_fences_are_escaped():
    """`skill_view` returns whole files, and SKILL.md is full of ``` blocks.

    Rendered naively inside a fence, the first embedded ``` closes the block and
    the rest of the page renders as garbage. The zero-width space is invisible
    and stops that.
    """
    from harness.transcript import fence

    content = SKILL_MD.read_text(encoding="utf-8")
    assert "```" in content, "this test is pointless if SKILL.md has no fences"

    rendered = fence(content)
    # Exactly two unescaped fences: the ones this function opened and closed.
    assert rendered.count("```") - rendered.count("\u200b```") == 2
    assert rendered.startswith("```text\n")
    assert rendered.endswith("\n```")


def test_a_rendered_case_has_balanced_fences():
    """The property that actually matters: the page is valid markdown."""
    from harness.transcript import render_case

    tool_response = SKILL_MD.read_text(encoding="utf-8")
    markdown = render_case(
        {"id": "x", "why": "because", "expect": {"opens_skills": ["s"]}},
        {
            "case_id": "x",
            "passed": True,
            "messages": [
                {"role": "user", "content": "what?"},
                {"role": "assistant", "content": "```python\nprint(1)\n```"},
                {"role": "tool", "name": "skill_view", "content": tool_response},
            ],
        },
    )
    unescaped = markdown.count("```") - markdown.count("\u200b```")
    assert unescaped % 2 == 0, "unbalanced fences — the page will render as garbage"


# --------------------------------------------------------------------------- #
# redaction — the repo is public
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "secret",
    [
        "sk-or-v1-a36f00bbaaccddeeff0011223344556677",
        "sk-ant-api03-AAAABBBBCCCCDDDD",
        "ghp_0123456789abcdefghijklmnopqrstuvwxyz",
        "github_pat_11ABCDEFG0123456789_abcdefgh",
        "AKIAIOSFODNN7EXAMPLE",
    ],
)
def test_provider_keys_are_scrubbed(secret):
    """Nothing key-shaped reaches a transcript. Scrubbed on the way in, because
    the repo is public and forgetting once costs a rotated key."""
    from harness.agent import redact

    payload = {
        "role": "tool",
        "content": f"OPENROUTER_API_KEY={secret}\nnext line",
        "nested": [{"deep": secret}],
    }
    cleaned = redact(payload)
    blob = json.dumps(cleaned)
    assert secret not in blob
    assert "[redacted]" in blob
    # Structure survives.
    assert cleaned["role"] == "tool"
    assert "next line" in cleaned["content"]


def test_redaction_leaves_ordinary_text_alone():
    """Over-eager redaction would quietly destroy the evidence it protects."""
    from harness.agent import redact

    text = "pH 6.86 on the kactoily probe; run `aqua status --tank display`"
    assert redact(text) == text


# --------------------------------------------------------------------------- #
# readability
# --------------------------------------------------------------------------- #

def test_long_tool_responses_collapse_but_stay_complete():
    """A 13 KB skill dump inline drowns the page; truncated it stops being
    evidence. Collapsed, it is both readable and whole."""
    from harness.transcript import COLLAPSE_OVER_BYTES, render_conversation

    payload = "x" * (COLLAPSE_OVER_BYTES + 500)
    markdown = render_conversation(
        [{"role": "tool", "name": "skill_view", "content": payload}]
    )
    assert "<details>" in markdown
    assert payload in markdown, "the response was truncated"


def test_short_tool_responses_are_not_collapsed():
    from harness.transcript import render_conversation

    markdown = render_conversation([{"role": "tool", "name": "aqua", "content": "ok"}])
    assert "<details>" not in markdown
    assert "ok" in markdown


def test_tool_calls_show_their_arguments():
    """"Which tool, with what" is the question a transcript exists to answer."""
    from harness.transcript import render_conversation

    markdown = render_conversation([
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "skill_view",
                                         "arguments": '{"name": "aquarium-supervisor"}'}}],
        }
    ])
    assert "skill_view" in markdown
    assert "aquarium-supervisor" in markdown


def test_every_turn_is_rendered():
    """The reference implementation twice dropped half a transcript, because
    unrecognised roles fell through to a default branch and emitted bodiless
    rows. Count the turns."""
    from harness.transcript import render_conversation

    messages = [
        {"role": "system", "content": "ignored — stored once per run"},
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
        {"role": "tool", "name": "t", "content": "c"},
        {"role": "assistant", "content": "d"},
        {"role": "wat", "content": "unknown role"},
    ]
    markdown = render_conversation(messages)
    assert markdown.count("### Turn ") == 5, "a turn went missing"
    assert "unknown role" in markdown, "an unrecognised role lost its content"
    assert "ignored" not in markdown, "the system prompt should not repeat per case"


def test_a_missing_transcript_says_so():
    from harness.transcript import render_conversation

    assert "No transcript" in render_conversation([])


# --------------------------------------------------------------------------- #
# the run tree
# --------------------------------------------------------------------------- #

def _sample_results():
    return [
        {
            "case_id": "salt-never", "passed": True, "failures": [], "tokens": 100,
            "cost_usd": 0.02, "wall_s": 1.0, "model": "m", "skills_opened": ["s"],
            "aqua_calls": ["a"], "blocked_commands": [], "cached": False,
            "system_prompt": "SYSTEM",
            "messages": [{"role": "user", "content": "q"},
                         {"role": "assistant", "content": "no salt"}],
        },
        {
            "case_id": "which-tank", "passed": False, "failures": ["did not ask"],
            "tokens": 50, "cost_usd": 0.01, "wall_s": 1.0, "model": "m",
            "skills_opened": [], "aqua_calls": [], "blocked_commands": [],
            "cached": False, "system_prompt": "SYSTEM", "messages": [],
        },
    ]


def test_write_run_produces_the_expected_tree(tmp_path):
    from harness.transcript import write_run

    write_run(
        tmp_path / "run",
        meta={"run_label": "r", "model": "m", "started": "s", "commit": "c"},
        cases={"salt-never": {"id": "salt-never", "why": "w"},
               "which-tank": {"id": "which-tank", "why": "w"}},
        results=_sample_results(),
    )
    root = tmp_path / "run"
    for name in ("index.md", "entries.json", "system-prompt.md"):
        assert (root / name).is_file(), f"{name} missing"
    for case in ("salt-never", "which-tank"):
        assert (root / "cases" / f"{case}.md").is_file()
        assert (root / "cases" / f"{case}.json").is_file()


def test_the_index_names_what_failed(tmp_path):
    from harness.transcript import write_run

    write_run(tmp_path / "run", meta={}, cases={}, results=_sample_results())
    index = (tmp_path / "run" / "index.md").read_text(encoding="utf-8")
    assert "1/2 passed" in index
    assert "which-tank" in index and "did not ask" in index


def test_entries_json_is_shipped_and_excludes_the_bulk(tmp_path):
    """It is exactly what a dashboard wants. The reference deletes theirs and
    then regex-parses markdown back out to rebuild it."""
    from harness.transcript import write_run

    write_run(tmp_path / "run", meta={"model": "m"}, cases={}, results=_sample_results())
    payload = json.loads((tmp_path / "run" / "entries.json").read_text(encoding="utf-8"))
    assert payload["meta"]["model"] == "m"
    assert {e["case_id"] for e in payload["entries"]} == {"salt-never", "which-tank"}
    # The transcript lives in cases/*.json; duplicating it here would double the size.
    assert "messages" not in payload["entries"][0]


def test_raw_json_re_renders_identically(tmp_path):
    """What makes a renderer fix applicable to already-archived runs."""
    from harness.transcript import render_case, write_run

    write_run(
        tmp_path / "run",
        meta={},
        cases={"salt-never": {"id": "salt-never", "why": "w"}},
        results=_sample_results()[:1],
    )
    rendered = (tmp_path / "run" / "cases" / "salt-never.md").read_text(encoding="utf-8")
    raw = json.loads((tmp_path / "run" / "cases" / "salt-never.json").read_text(encoding="utf-8"))
    assert render_case(raw["case"], raw["result"]) == rendered


def test_rendering_failure_loses_the_report_not_the_run(tmp_path):
    """A report is worth less than a result."""
    from harness.transcript import write_run

    broken = _sample_results()[:1]
    broken[0]["messages"] = [{"role": "assistant", "content": object()}]  # unserialisable
    write_run(tmp_path / "run", meta={}, cases={}, results=broken)
    # Still produced an index, and said so in the case file.
    assert (tmp_path / "run" / "index.md").is_file()
    body = (tmp_path / "run" / "cases" / "salt-never.md").read_text(encoding="utf-8")
    assert "salt-never" in body


def test_a_cached_run_says_it_was_not_measured(tmp_path):
    """A transcript replayed from cache must not read as fresh evidence."""
    from harness.transcript import render_case

    result = _sample_results()[0]
    result["cached"] = True
    assert "cache" in render_case({"id": "x"}, result).lower()


# --------------------------------------------------------------------------- #
# publishing
# --------------------------------------------------------------------------- #

def _prune(tmp_path, names, keep):
    runs = tmp_path / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    for name in names:
        (runs / name).mkdir()
    subprocess.run(
        ["bash", str(PUBLISH), "--prune-only", str(tmp_path), str(keep)],
        check=True, capture_output=True, text=True,
    )
    return sorted(p.name for p in runs.iterdir())


def test_pruning_keeps_the_highest_run_numbers(tmp_path):
    """Sorted by run number parsed from the name, NOT by mtime.

    After `git clone --depth=1` every archived directory carries the clone's
    mtime, so an mtime sort is near-arbitrary — the reference implementation
    prunes that way and deletes effectively at random.
    """
    names = [f"2026-01-01__run-{n}__m" for n in (7, 12, 3, 100, 42)]
    kept = _prune(tmp_path, names, keep=3)
    assert kept == sorted(["2026-01-01__run-100__m",
                           "2026-01-01__run-42__m",
                           "2026-01-01__run-12__m"])


def test_pruning_is_a_no_op_below_the_limit(tmp_path):
    names = [f"2026-01-01__run-{n}__m" for n in (1, 2)]
    assert len(_prune(tmp_path, names, keep=50)) == 2


def test_pruning_leaves_unparseable_directories_alone(tmp_path):
    """Deleting something we cannot identify is worse than keeping it."""
    names = ["2026-01-01__run-1__m", "2026-01-01__run-2__m", "not-a-run-dir"]
    assert "not-a-run-dir" in _prune(tmp_path, names, keep=1)


def test_publish_script_is_executable_and_shellchecked():
    assert PUBLISH.is_file()
    result = subprocess.run(["bash", "-n", str(PUBLISH)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_workflow_publishes_even_when_the_evals_fail():
    """`if: always()` on the publish step. A failing run is the one worth
    reading, and it is the run where nobody is watching the terminal."""
    import yaml

    workflow = yaml.safe_load(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["live"]["steps"]
    publish = [s for s in steps if "publish" in (s.get("name") or "").lower()]
    assert publish, "no publish step in the live job"
    assert all(s.get("if") == "always()" for s in publish), (
        "the publish step must run on failure — that is the run worth reading"
    )


def test_the_live_job_can_write_to_the_repo():
    import yaml

    workflow = yaml.safe_load(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    )
    assert workflow["jobs"]["live"].get("permissions", {}).get("contents") == "write"
    # And the default for every other job stays read-only.
    assert workflow["permissions"]["contents"] == "read"
