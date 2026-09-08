"""Reference-file integrity.

The aquarium skill is built on progressive disclosure: SKILL.md holds identity
and decision rules, and defers species biology, chemistry, inventory and triage
to references/, which are loaded on demand and never indexed
(agent/skill_utils.py:1210, SKILL_SUPPORT_DIRS).

That design breaks quietly in two directions — a SKILL.md pointing at a file that
was renamed, and a reference file nothing points at. Both leave the agent unable
to answer questions it was supposed to be able to answer, with no error anywhere.
"""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT, body

# Matches `references/triage.md`, `` `references/chemistry.md` ``, etc.
REFERENCE_RE = re.compile(r"`?references/([A-Za-z0-9._/-]+\.md)`?")

SUPPORT_DIRS = ("references", "templates", "assets", "scripts")


def _cited(skill_md) -> set[str]:
    return set(REFERENCE_RE.findall(body(skill_md)))


def _present(skill_md) -> set[str]:
    ref_dir = skill_md.parent / "references"
    if not ref_dir.is_dir():
        return set()
    return {str(p.relative_to(ref_dir)) for p in ref_dir.rglob("*.md")}


def test_cited_references_exist(skill_md):
    missing = sorted(_cited(skill_md) - _present(skill_md))
    assert not missing, (
        f"{skill_md.parent.name} cites reference files that do not exist: {missing}. "
        "The model will try to read them and get nothing."
    )


def test_no_orphan_references(skill_md):
    """A reference nothing links to is a reference the model never finds.

    References are not in the skill index, so the ONLY way the model learns a
    file exists is a mention in SKILL.md (or in another reference).
    """
    present = _present(skill_md)
    if not present:
        pytest.skip("no references/")
    cited = _cited(skill_md)
    for ref in present:
        cited |= set(REFERENCE_RE.findall((skill_md.parent / "references" / ref).read_text("utf-8")))
    orphans = sorted(present - cited)
    assert not orphans, (
        f"{skill_md.parent.name} has reference files nothing points to: {orphans}. "
        "Mention them in SKILL.md or delete them."
    )


def test_references_not_in_the_index(assembled):
    """Support files must stay out of the system prompt.

    If a references/*.md were indexed — or worse, inlined — progressive
    disclosure has broken and the prompt is carrying hundreds of lines of
    chemistry on every single turn.
    """
    index = assembled["index"]
    prompt = assembled["prompt"]
    for skill_dir in (p.parent for p in (REPO_ROOT / "skills").glob("*/*/SKILL.md")):
        for support in SUPPORT_DIRS:
            support_dir = skill_dir / support
            if not support_dir.is_dir():
                continue
            for ref in sorted(support_dir.rglob("*.md")):
                assert ref.name not in index, (
                    f"{support}/{ref.name} was indexed as a skill; support directories "
                    "are meant to be excluded (SKILL_SUPPORT_DIRS)"
                )
                # A distinctive slice of the body, to catch inlining rather than
                # a filename mention.
                sample = _sample(ref)
                assert sample not in prompt, (
                    f"{support}/{ref.name} content was inlined into the system prompt"
                )


def _sample(path, length: int = 160) -> str:
    """A contiguous chunk of prose from the middle of a file."""
    lines = [ln.strip() for ln in path.read_text("utf-8").splitlines()]
    prose = [ln for ln in lines if len(ln) > length and not ln.startswith(("#", "|", "-", "*"))]
    if prose:
        return prose[len(prose) // 2][:length]
    return "".join(lines)[len(lines) // 2:][:length] or path.name
