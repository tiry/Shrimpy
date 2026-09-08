"""Shared fixtures for the offline checks.

Everything in tests/ runs without an API key, without network, and without cost.
The expensive behavioural checks live in evals/.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

SKILLS_DIR = REPO_ROOT / "skills"

# agent/skill_utils.py:1182 — the index line is the ONLY thing the model sees
# when deciding whether to open a skill, and anything past this is cut.
SKILL_PROMPT_DESC_LIMIT = 60

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter *strictly*.

    Hermes is forgiving here and falls back to a naive line reader when the YAML
    is invalid — which is precisely the bug that makes a skill vanish from the
    index without an error. These tests are deliberately stricter than the
    runtime so the failure surfaces at commit time instead of at answer time.
    """
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise AssertionError(f"{path.relative_to(REPO_ROOT)} has no YAML frontmatter block")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise AssertionError(f"{path.relative_to(REPO_ROOT)} frontmatter is not a mapping")
    return data


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


def skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/*/SKILL.md"))


def category_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()) if SKILLS_DIR.is_dir() else []


def _id(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def pytest_generate_tests(metafunc):
    if "skill_md" in metafunc.fixturenames:
        files = skill_files()
        metafunc.parametrize("skill_md", files, ids=[_id(p) for p in files])
    if "category_dir" in metafunc.fixturenames:
        dirs = category_dirs()
        metafunc.parametrize("category_dir", dirs, ids=[p.name for p in dirs])


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def assembled():
    """The real system prompt Hermes would send, built offline with dummy creds.

    Session-scoped: building it costs ~2s and imports the whole agent.
    """
    from harness import home as home_mod
    from harness import inspect as insp

    hermes_home = home_mod.build_home(ephemeral=True)
    home_mod.activate(hermes_home)
    agent = insp.build_inspection_agent()
    prompt = insp.system_prompt(agent)
    block = insp.skills_index(prompt)
    return {
        "prompt": prompt,
        "index": block,
        "parsed": insp.parse_index(block),
        "home": hermes_home,
    }
