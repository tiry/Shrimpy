"""Assemble Shrimpy's system prompt offline and pull the skill index out of it.

This is the cheap half of the harness. It builds a real ``AIAgent`` with dummy
credentials — the same trick ``hermes prompt-size`` uses (hermes_cli/prompt_size.py:50)
— so no request ever leaves the machine and no API key is needed.

It exists because the two ways a Hermes skill fails are both invisible at
runtime:

  * a ``description`` over 60 chars is truncated in the index
    (``SKILL_PROMPT_DESC_LIMIT``, agent/skill_utils.py:1182), so trigger phrases
    the model never sees;
  * a ``description`` containing an unquoted ``": "`` is invalid YAML, frontmatter
    parsing falls back to a naive line reader, ``platforms`` comes back as a
    string, platform matching fails, and **the skill is dropped from the index
    entirely** — while still parsing, and logging nothing.

Both are assertions here rather than something you notice when the agent
mysteriously stops knowing about the aquarium.
"""

from __future__ import annotations

import re
from typing import Any

# The index is emitted as a delimited block (hermes_cli/prompt_size.py:23).
SKILLS_BLOCK_RE = re.compile(r"<available_skills>.*?</available_skills>", re.DOTALL)

# A skills tool must be in the toolset or the whole block is omitted
# (agent/system_prompt.py:619). Everything else is irrelevant for inspection.
INSPECT_TOOLSETS = ["skills"]


def build_inspection_agent(model: str = "anthropic/claude-sonnet-5", toolsets=None):
    """An AIAgent that can assemble a prompt but cannot call anything.

    Import is deferred: ``run_agent`` binds HERMES_HOME at import time, so the
    caller must have run ``home.activate()`` first.
    """
    from run_agent import AIAgent

    return AIAgent(
        model=model,
        provider="openrouter",
        api_key="inspect-only-not-a-real-key",
        base_url="https://openrouter.ai/api/v1",
        quiet_mode=True,
        platform="cli",
        enabled_toolsets=list(toolsets or INSPECT_TOOLSETS),
        skip_memory=True,
        skip_background_review=True,
        session_db=None,
    )


def system_prompt(agent=None, **kwargs) -> str:
    from agent.system_prompt import build_system_prompt

    return build_system_prompt(agent or build_inspection_agent(**kwargs))


def system_prompt_parts(agent=None, **kwargs) -> dict[str, str]:
    """The three prompt-cache tiers: stable / context / volatile."""
    from agent.system_prompt import build_system_prompt_parts

    return build_system_prompt_parts(agent or build_inspection_agent(**kwargs))


def skills_index(prompt: str) -> str:
    """The <available_skills> block, or '' when no skill was indexed at all."""
    match = SKILLS_BLOCK_RE.search(prompt)
    return match.group(0) if match else ""


def parse_index(block: str) -> dict[str, Any]:
    """Split the rendered index into categories and skills.

    Rendered shape (agent/prompt_builder.py:1988, hermes_cli/prompt_size.py:27):

        <available_skills>
          aquarium: <full untruncated category description>
            - aquarium-supervisor: Tiry's aquariums: shrimp, guppies, ...
        </available_skills>

    Category lines are indented two spaces, skill lines four and prefixed '- '.
    """
    categories: dict[str, str] = {}
    skills: dict[str, str] = {}
    current: str | None = None
    for line in block.splitlines():
        if line.strip() in ("<available_skills>", "</available_skills>") or not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            name, _, desc = stripped[2:].partition(":")
            skills[name.strip()] = desc.strip()
        elif line.startswith("  ") and ":" in stripped:
            name, _, desc = stripped.partition(":")
            current = name.strip()
            categories[current] = desc.strip()
    return {"categories": categories, "skills": skills}
