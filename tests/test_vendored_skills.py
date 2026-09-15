"""Vendored skills — spec 11.

Two skills are copied out of `vendor/hermes-agent/skills/` into this repo so the
profile is self-describing: `create-profile.sh` copies `skills/` wholesale, so
what is here is what the agent gets, with no install step at provision time.

Copying has two failure modes and this module covers both.

**A capability the container cannot deliver.** `productivity/pdf` was the third
candidate and was rejected on evidence: `pymupdf`, `pdfplumber`, `pypdf` and
`reportlab` are in neither hermes's `[all]` extra nor `tools/lazy_deps.py`, and
the skill declares no `required_commands` — so `skill_view` would report it
available, the model would offer to read a PDF, and every script would die on
import. Nothing in hermes checks this.

**Silent drift.** The submodule is pinned, but it will be bumped. A vendored copy
that quietly diverges from upstream is a fork nobody decided to maintain.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib

import pytest
from conftest import REPO_ROOT

UPSTREAM = REPO_ROOT / "vendor" / "hermes-agent"
SKILLS = REPO_ROOT / "skills"

# skills/<category>/<skill> here -> the same path under the submodule.
VENDORED = {
    "research/grounded-citations": "research/grounded-citations",
    "media/youtube-content": "media/youtube-content",
}

# Import names that differ from their distribution name, for the few that matter.
DIST_ALIASES = {
    "youtube_transcript_api": "youtube-transcript-api",
    "dateutil": "python-dateutil",
    "yaml": "pyyaml",
    "fitz": "pymupdf",
    "PIL": "pillow",
}


def vendored_dirs() -> list:
    return [SKILLS / rel for rel in sorted(VENDORED)]


def _ids(path) -> str:
    return str(path.relative_to(SKILLS))


# --------------------------------------------------------------------------- #
# what the deployment can actually satisfy
# --------------------------------------------------------------------------- #

def _pyproject() -> dict:
    return tomllib.loads((UPSTREAM / "pyproject.toml").read_text(encoding="utf-8"))


def _satisfiable_distributions() -> set[str]:
    """Every package the deployment image can import.

    The image builds with `uv sync ... --extra all --extra messaging ...`
    (vendor/hermes-agent/Dockerfile:267), so core dependencies plus everything
    reachable from `[all]`. `tools/lazy_deps.py` adds packages that install
    themselves on first use, which counts as satisfiable.
    """
    data = _pyproject()
    project = data.get("project", {})
    optional = project.get("optional-dependencies", {})

    names: set[str] = set()

    def add(spec: str) -> None:
        # "httpx>=0.28.1,<1" -> httpx ; "hermes-agent[cron]" -> recurse
        inner = re.fullmatch(r"hermes-agent\[([\w-]+)\]", spec.strip())
        if inner:
            for nested in optional.get(inner.group(1), []):
                add(nested)
            return
        name = re.split(r"[<>=!~\[; ]", spec.strip(), maxsplit=1)[0]
        if name:
            names.add(name.lower().replace("_", "-"))

    for spec in project.get("dependencies", []):
        add(spec)
    for spec in optional.get("all", []):
        add(spec)

    # Lazy-installed on first use — tools/lazy_deps.py
    lazy = (UPSTREAM / "tools" / "lazy_deps.py").read_text(encoding="utf-8")
    for spec in re.findall(r'"([A-Za-z0-9_.-]+)[=<>~]{1,2}[^"]*"', lazy):
        names.add(spec.lower().replace("_", "-"))

    # hermes-agent's own top-level modules. Not distributions, but importable in
    # the image because the agent itself is installed there -- `hermes_constants`
    # is how a bundled skill finds HERMES_HOME.
    for entry in UPSTREAM.iterdir():
        if entry.suffix == ".py" and not entry.name.startswith("_"):
            names.add(entry.stem.lower().replace("_", "-"))
        elif entry.is_dir() and (entry / "__init__.py").is_file():
            names.add(entry.name.lower().replace("_", "-"))

    return names


def _third_party_imports(path) -> set[str]:
    """Top-level imported module names that are not stdlib and not local."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import, local to the skill
                continue
            if node.module:
                found.add(node.module.split(".")[0])
    local = {p.stem for p in path.parent.glob("*.py")}
    return {
        name
        for name in found
        if name not in sys.stdlib_module_names and name not in local
    }


@pytest.mark.parametrize("skill_dir", vendored_dirs(), ids=_ids)
def test_a_vendored_skill_imports_nothing_the_image_lacks(skill_dir):
    """The check that rejected `productivity/pdf`.

    A vendored skill whose scripts import a package the deployment does not have
    is worse than an absent skill: `skill_view` reports it available, the model
    offers the capability, and the failure lands on the user as a traceback.
    Hermes has no readiness check for this unless the skill declares
    `required_commands`, and these do not.
    """
    satisfiable = _satisfiable_distributions()
    problems: list[str] = []
    for script in sorted(skill_dir.rglob("*.py")):
        for module in sorted(_third_party_imports(script)):
            dist = DIST_ALIASES.get(module, module).lower().replace("_", "-")
            if dist not in satisfiable:
                problems.append(
                    f"{script.relative_to(SKILLS)} imports {module!r} "
                    f"(distribution {dist!r})"
                )
    assert not problems, (
        "vendored skill imports something the deployment image cannot provide:\n\n  "
        + "\n  ".join(problems)
        + "\n\nIt is in neither hermes-agent's [all] extra nor tools/lazy_deps.py, "
        "so the script dies on import while `skill_view` still reports the skill "
        "as available. This is why productivity/pdf was not vendored."
    )


def test_the_import_guard_would_have_rejected_pdf():
    """A guard that cannot fire is not a guard.

    Uses the real skill that failed this check, read from the submodule rather
    than from a fixture, so it keeps testing the actual rejection reason.
    """
    pdf = UPSTREAM / "skills" / "productivity" / "pdf"
    if not pdf.is_dir():
        pytest.skip("upstream pdf skill not present in this checkout")

    satisfiable = _satisfiable_distributions()
    unsatisfiable = {
        DIST_ALIASES.get(m, m).lower().replace("_", "-")
        for script in pdf.rglob("*.py")
        for m in _third_party_imports(script)
    } - satisfiable
    assert unsatisfiable, (
        "the pdf skill's imports now all resolve — either hermes added the "
        "dependencies, in which case reconsider vendoring it, or this guard has "
        "stopped working"
    )


# --------------------------------------------------------------------------- #
# drift from upstream
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("skill_dir", vendored_dirs(), ids=_ids)
def test_a_vendored_skill_matches_upstream(skill_dir):
    """A vendored copy that diverges is a fork nobody chose to maintain.

    `vendor/hermes-agent` is pinned, so this passes until the submodule is
    bumped. When it is, this fails and the choice — re-vendor, or keep the old
    copy deliberately — gets made by a person instead of by inattention.
    """
    rel = str(skill_dir.relative_to(SKILLS))
    upstream_dir = UPSTREAM / "skills" / VENDORED[rel]
    if not upstream_dir.is_dir():
        pytest.skip(f"upstream no longer ships {rel}")

    def tree(root):
        return {
            p.relative_to(root): p.read_bytes()
            for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
        }

    ours, theirs = tree(skill_dir), tree(upstream_dir)
    only_ours = sorted(str(p) for p in ours.keys() - theirs.keys())
    only_theirs = sorted(str(p) for p in theirs.keys() - ours.keys())
    changed = sorted(str(p) for p in ours.keys() & theirs.keys() if ours[p] != theirs[p])

    assert not (only_ours or only_theirs or changed), (
        f"the vendored copy of {rel} no longer matches "
        f"vendor/hermes-agent/skills/{VENDORED[rel]}:\n"
        f"  only here:     {only_ours}\n"
        f"  only upstream: {only_theirs}\n"
        f"  differing:     {changed}\n\n"
        "Re-vendor with `cp -r`, or record deliberately why the copy diverges."
    )


def test_every_vendored_skill_is_declared():
    """A skill copied in without being added to VENDORED gets neither guard."""
    declared = {SKILLS / rel for rel in VENDORED}
    found = {
        p.parent for p in SKILLS.glob("*/*/SKILL.md")
        if p.parent.parent.name != "aquarium"
    }
    undeclared = sorted(str(p.relative_to(SKILLS)) for p in found - declared)
    assert not undeclared, (
        f"skills present but not declared in VENDORED: {undeclared}. "
        "They would be checked for neither unsatisfiable imports nor drift."
    )
