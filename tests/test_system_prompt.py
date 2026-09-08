"""The assembled system prompt — what the model actually receives.

Every other test in this directory reads files on disk. This one builds the real
prompt through Hermes' own code path (offline, dummy credentials, no network) and
asserts on the result. It is the only check that can catch a persona or a skill
being present in the repo but absent from the agent.
"""

from __future__ import annotations

from conftest import REPO_ROOT, frontmatter, skill_files

# Informational ceiling. The whole prompt is re-sent on every turn, so growth
# here is a recurring token cost, not a one-off.
SYSTEM_PROMPT_SOFT_LIMIT = 40_000


def test_soul_is_loaded(assembled):
    """SOUL.md must be in the prompt.

    Hermes substitutes a generic DEFAULT_AGENT_IDENTITY whenever SOUL.md fails to
    load (agent/system_prompt.py:472-487) — including under --safe-mode and
    --ignore-rules. The agent still answers, competently, as nobody in particular.
    """
    soul = (REPO_ROOT / "SOUL.md").read_text(encoding="utf-8")
    # A distinctive sentence rather than the whole file: the prompt builder may
    # truncate on context length.
    assert "You are Shrimpy" in assembled["prompt"], "SOUL.md did not make it into the prompt"
    for phrase in ("living animals", "Never invent a number", "Always know which tank"):
        assert phrase in assembled["prompt"], f"SOUL.md truncated before {phrase!r}"
    assert soul.strip(), "SOUL.md is empty"


def test_soul_is_not_the_hermes_placeholder():
    """`hermes profile create` seeds a DEFAULT_SOUL_MD placeholder. Catch a
    clobbered file before it ships."""
    soul = (REPO_ROOT / "SOUL.md").read_text(encoding="utf-8")
    assert "You are Shrimpy" in soul
    assert len(soul.strip()) > 1000, "SOUL.md looks like a stub"


def test_skill_index_is_not_empty(assembled):
    """The single highest-value assertion in the suite.

    An empty index is what an invalid-YAML frontmatter looks like from the
    outside: the agent boots, answers, and simply does not know it has skills.
    """
    assert assembled["index"], (
        "no <available_skills> block was rendered — every skill was dropped. "
        "Check frontmatter validity and that a skills tool is in the toolset."
    )


def test_every_skill_is_indexed(assembled):
    indexed = assembled["parsed"]["skills"]
    for skill_md in skill_files():
        name = frontmatter(skill_md)["name"]
        assert name in indexed, (
            f"{name} exists on disk but is absent from the skill index: {sorted(indexed)}"
        )


def test_every_category_is_indexed(assembled):
    indexed = assembled["parsed"]["categories"]
    for category in (p for p in (REPO_ROOT / "skills").iterdir() if p.is_dir()):
        assert category.name in indexed, (
            f"category {category.name} is missing from the index: {sorted(indexed)}"
        )


def test_category_description_is_rendered_in_full(assembled):
    """The reason categories exist here.

    A skill's own description is truncated at 60 chars; a category's is not. If
    that ever changed upstream, the trigger phrases would vanish and the only
    symptom would be Shrimpy failing to notice aquarium questions.
    """
    for category in (p for p in (REPO_ROOT / "skills").iterdir() if p.is_dir()):
        expected = frontmatter(category / "DESCRIPTION.md")["description"].strip()
        rendered = assembled["parsed"]["categories"][category.name]
        assert rendered == expected, (
            f"{category.name} description was altered in the index.\n"
            f"  expected {len(expected)} chars\n"
            f"  rendered {len(rendered)} chars\n"
            f"  rendered: {rendered}"
        )


def test_trigger_phrases_reach_the_model(assembled):
    """Spot-check the casual phrasings the DESCRIPTION.md explicitly promises to
    trigger on. These are the ones most likely to be lost to truncation."""
    for phrase in ("my shrimp look weird", "is 6.6 too low", "lost a guppy overnight"):
        assert phrase in assembled["index"], f"trigger phrase {phrase!r} is not in the prompt"


def test_skill_body_is_not_inlined(assembled):
    """Only the index line belongs in the prompt; the body is loaded on demand.

    If SKILL.md content appeared here, every turn would carry 600 lines of tank
    documentation whether or not the conversation is about the aquarium.
    """
    assert "## 2. Dosing" not in assembled["prompt"], (
        "SKILL.md body was inlined into the system prompt instead of being "
        "loaded on demand via skill_view"
    )


def test_prompt_size_is_reasonable(assembled):
    size = len(assembled["prompt"])
    assert size < SYSTEM_PROMPT_SOFT_LIMIT, (
        f"system prompt is {size} chars (soft limit {SYSTEM_PROMPT_SOFT_LIMIT}). "
        "This is paid for on every turn — check whether a skill body is being inlined."
    )
