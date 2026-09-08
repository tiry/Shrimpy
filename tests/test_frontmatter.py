"""Skill frontmatter and structure — using Hermes' own linter.

`tools/skill_linter.py` ships with Hermes and is importable from the installed
package. It encodes upstream's authoring standards: `description-length`,
`name-dir-mismatch`, `platforms-value`, `dangling-reference`, `missing-section`
and more. Delegating to it means the conventions stay correct as upstream moves,
instead of drifting against a hand-rolled copy.

What stays hand-rolled here is only what the linter does not cover:

* **Category `DESCRIPTION.md`.** The linter validates a skill, not the category
  directory above it — and the category is where Shrimpy's trigger phrases live,
  because a skill's own description is truncated to 60 characters.
* **Strict YAML.** The linter reads frontmatter through Hermes' tolerant parser,
  which is the point: that parser *succeeds* on `description: a: b` and silently
  yields `platforms` as a string, dropping the skill from the index. Parsing the
  same bytes strictly is what catches it.
"""

from __future__ import annotations

import pytest

from conftest import SKILL_PROMPT_DESC_LIMIT, frontmatter


def test_upstream_linter_passes(skill_md):
    """Hermes' own linter, failing on ERROR severity.

    Warnings are reported but do not fail: they are advisory conventions, and a
    persona repo is entitled to differ from upstream's house style. Errors are
    structural and would break the skill.
    """
    from tools.skill_linter import format_findings, has_errors, lint_skill

    findings = lint_skill(skill_md)
    errors = [f for f in findings if f.severity == "ERROR"]
    assert not has_errors(findings), (
        f"{skill_md.parent.name} fails Hermes' skill linter:\n"
        + format_findings(errors)
    )


def test_upstream_linter_warnings(skill_md, request):
    """Surface advisory findings without failing the suite.

    Run with `-rs` to see them. Kept separate from the ERROR check so a new
    upstream convention shows up as a skip note rather than a red build.
    """
    from tools.skill_linter import format_findings, lint_skill

    warnings = [f for f in lint_skill(skill_md) if f.severity != "ERROR"]
    if warnings:
        pytest.skip(f"{skill_md.parent.name} advisory:\n{format_findings(warnings)}")


def test_frontmatter_is_valid_yaml(skill_md):
    """Strict YAML parse — deliberately stricter than Hermes' own parser.

    `description: Tiry's aquariums: shrimp, guppies` is not valid YAML: the
    second colon starts a nested mapping. Hermes does not error. It falls back to
    a naive line reader, `platforms` comes back as the *string*
    "[linux, macos, windows]", platform matching fails, and the skill is dropped
    from the index entirely — while still parsing, and logging nothing.

    Quote any description containing ": ".
    """
    frontmatter(skill_md)  # raises with a useful message on failure


def test_platforms_is_a_list(skill_md):
    """The observable symptom of that fallback."""
    data = frontmatter(skill_md)
    if "platforms" not in data:
        pytest.skip("no platforms constraint")
    assert isinstance(data["platforms"], list), (
        f"`platforms` parsed as {type(data['platforms']).__name__}, not a list — "
        "the frontmatter is not valid YAML and the skill will be silently dropped"
    )
    assert "linux" in data["platforms"], (
        "the deployment runs Linux; a skill excluding it never loads"
    )


def test_category_has_description_md(category_dir):
    """Every category carries the trigger phrases the skill description cannot.

    Not covered by the linter, which validates skills rather than the category
    directory. A category DESCRIPTION.md is rendered untruncated
    (agent/prompt_builder.py:1988), which is the only place a long trigger list
    is actually read by the model.
    """
    desc_md = category_dir / "DESCRIPTION.md"
    assert desc_md.is_file(), (
        f"{category_dir.name}/DESCRIPTION.md is missing — without it the category "
        "renders with no description and triggering relies on the 60-char skill line"
    )
    data = frontmatter(desc_md)
    text = data.get("description")
    assert isinstance(text, str) and text.strip(), "DESCRIPTION.md has no `description`"


def test_category_description_carries_triggers(category_dir):
    """A category description short enough to fit in a skill line is not doing
    the job the split exists for."""
    data = frontmatter(category_dir / "DESCRIPTION.md")
    assert len(data["description"]) > SKILL_PROMPT_DESC_LIMIT, (
        f"{category_dir.name}/DESCRIPTION.md is only {len(data['description'])} chars. "
        "If it fits in a skill description there is no reason for the category split; "
        "this is where trigger phrases go."
    )
