"""Layout contract with the tairy-agent deployment.

`scripts/create-profile.sh` in the deployment repo copies exactly three things
out of a profile directory: SOUL.md, skills/*, and (via set-matrix-identity.sh)
DISPLAYNAME + avatar.png. This repo is laid out so it can *be* that directory —
as a submodule, a copy, or a sync target.

These tests fail if the layout drifts away from what the deployment can consume.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import REPO_ROOT

# scripts/set-matrix-identity.sh enforces a 2 MB cap on the avatar.
AVATAR_MAX_BYTES = 2 * 1024 * 1024


def test_profile_files_are_at_the_repo_root():
    for name in ("SOUL.md", "DISPLAYNAME", "avatar.png"):
        assert (REPO_ROOT / name).is_file(), (
            f"{name} must sit at the repo root for tairy-agent/profiles/<name>/ compatibility"
        )
    assert (REPO_ROOT / "skills").is_dir()


def test_displayname_is_one_line():
    text = (REPO_ROOT / "DISPLAYNAME").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    assert len(lines) == 1, "DISPLAYNAME must be a single line"
    assert lines[0].strip() == "Shrimpy"


def test_avatar_is_under_the_matrix_cap():
    size = (REPO_ROOT / "avatar.png").stat().st_size
    assert size <= AVATAR_MAX_BYTES, (
        f"avatar.png is {size} bytes; set-matrix-identity.sh caps uploads at 2 MB"
    )


def test_skills_tree_is_two_levels():
    """skills/<category>/<skill>/SKILL.md.

    create-profile.sh copies category directories as the unit, and the category
    layer is what makes an untruncated description possible. A SKILL.md directly
    under skills/ has no category and loses its trigger phrases.
    """
    stray = list((REPO_ROOT / "skills").glob("*/SKILL.md"))
    assert not stray, (
        f"SKILL.md found directly in a category dir: {[str(p) for p in stray]}. "
        "Expected skills/<category>/<skill>/SKILL.md."
    )
    assert list((REPO_ROOT / "skills").glob("*/*/SKILL.md")), "no skills found"


def test_no_runtime_state_is_committed():
    """Files Hermes generates must never be tracked in the tree the deployment copies.

    config.yaml and .env hold per-deployment values and secrets; the deployment
    generates its own on the volume (profiles/README.md). A committed one would
    either leak a key or silently override the deployment's model choice.

    Checked against git rather than the filesystem: a local, gitignored .env is
    exactly what setup.sh creates and is fine.
    """
    tracked = set(
        subprocess.run(
            ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
    )
    forbidden = {"config.yaml", ".env", "state.db", ".skills_prompt_snapshot.json"}
    offenders = sorted(p for p in tracked if Path(p).name in forbidden)
    assert not offenders, f"runtime state is committed: {offenders}"


def test_skills_tree_contains_only_definition_files():
    """Nothing but the skill definition, its scripts and their data inside skills/.

    `.json` and `.ndjson` are here because the skill ships reference data and a
    one-time migration payload under `assets/`. Live data is NOT here — it goes to
    `$HERMES_HOME/workspace/aquarium/`, because `create-profile.sh` does
    `rm -rf "${home}/skills"` on every provision.
    """
    allowed = {".md", ".png", ".jpg", ".yaml", ".yml", ".sh", ".py", ".json", ".ndjson"}
    strays = [
        str(p.relative_to(REPO_ROOT))
        for p in (REPO_ROOT / "skills").rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix not in allowed
    ]
    assert not strays, f"unexpected files in skills/: {strays}"


def test_no_live_data_inside_the_skill():
    """The live data directory must never appear under skills/.

    `create-profile.sh:74` destroys that tree on every provision, by explicit
    design. The bundled `memento-flashcards` skill stores its data there; that
    pattern would lose everything here on the next deploy.
    """
    skill_data = list((REPO_ROOT / "skills").rglob("workspace")) + [
        p for p in (REPO_ROOT / "skills").rglob("data") if p.is_dir()
    ]
    assert not skill_data, (
        f"live-data-shaped directory inside skills/: {[str(p) for p in skill_data]}. "
        "Live data belongs in $HERMES_HOME/workspace/aquarium/."
    )
