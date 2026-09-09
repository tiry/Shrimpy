"""The eval case format — defined once, validated strictly.

The format is **bespoke**. The nearest real standard is promptfoo, whose YAML
`tests`/`assert` blocks map cleanly onto the text assertions here:

    matches_any   -> {type: contains-any}
    matches_all   -> {type: contains-all}
    not_matches   -> {type: not-regex}
    max_chars     -> {type: javascript}
    judge         -> {type: llm-rubric}

It was not adopted because the assertions that carry the weight in this repo have
no equivalent in it — `opens_skills`, `runs_aqua`, `runs_any_aqua` and
`attempts_no_matching` assert on *what the agent did*, not on what it said, and
recovering that needs the tool-call introspection in harness/agent.py. Under
promptfoo they would each become a custom `python:` assertion, so the logic would
still be ours, wrapped in a Node toolchain this repo otherwise has no use for.

What a schema *was* buying that we lacked is validation. Every assertion was read
with `expect.get(...)`, so a misspelled key was silently ignored and the case
passed having asserted nothing:

    expect:
      match_any: ["impossible"]     # typo: matches_any
      opens_skils: [aquarium]       # typo: opens_skills

Both of those reported zero failures. That is the same silent-pass class as the
toolset typo already guarded against, and it is worse, because a green eval is
read as evidence.

Validation is hand-rolled rather than `jsonschema`: it is fifty lines, and the
`skill` CI job installs only pytest and pyyaml so that it can prove the skill
needs nothing else. `schema.json` is generated from these same definitions for
editor autocomplete, and a test fails if the two drift.
"""

from __future__ import annotations

from typing import Any

# field -> (python type, json-schema fragment, help shown on a bad value)
CASE_FIELDS: dict[str, tuple[type | tuple, dict, str]] = {
    "id": (str, {"type": "string", "minLength": 1}, "a unique identifier"),
    "prompt": (str, {"type": "string", "minLength": 1}, "what the user says"),
    "why": (
        str,
        {"type": "string", "minLength": 1},
        "the rule in SOUL.md or SKILL.md this case defends — a case that traces "
        "back to nothing is testing the model, not the agent",
    ),
    "expect": (dict, {"type": "object"}, "deterministic assertions"),
    "judge": (str, {"type": "string"}, "a rubric graded by a second model"),
    "toolsets": (
        list,
        {"type": "array", "items": {"type": "string"}},
        "override the default toolset for this case",
    ),
}

REQUIRED_CASE_FIELDS = ("id", "prompt", "why")

EXPECT_FIELDS: dict[str, tuple[type | tuple, dict, str]] = {
    "opens_skills": (list, {"type": "array", "items": {"type": "string"}},
                     "skills the model must have loaded with skill_view"),
    "matches_all": (list, {"type": "array", "items": {"type": "string"}},
                    "every regex must match the reply"),
    "matches_any": (list, {"type": "array", "items": {"type": "string"}},
                    "at least one regex must match"),
    "not_matches": (list, {"type": "array", "items": {"type": "string"}},
                    "none may match — always pair with a judge, see test_harness"),
    "max_chars": ((int,), {"type": "integer", "minimum": 1}, "reply length ceiling"),
    "attempts_no_commands": (bool, {"type": "boolean"},
                             "no shell command may be attempted at all"),
    "attempts_no_matching": (list, {"type": "array", "items": {"type": "string"}},
                             "no attempted command may match these"),
    "runs_aqua": (list, {"type": "array", "items": {"type": "string"}},
                  "CLI subcommands the agent must ALL have run"),
    "runs_any_aqua": (list, {"type": "array", "items": {"type": "string"}},
                      "at least one of these subcommands"),
    "runs_no_aqua": (bool, {"type": "boolean"}, "the CLI must not be used"),
}


class CaseError(Exception):
    """A malformed case. Raised at load time, before any model is called."""


def _check(where: str, payload: dict, fields: dict, required: tuple = ()) -> list[str]:
    problems: list[str] = []
    for name in required:
        if not payload.get(name):
            problems.append(f"{where}: missing required field {name!r} — {fields[name][2]}")

    for key, value in payload.items():
        if key.startswith("_"):
            continue  # runner bookkeeping, e.g. _file
        if key not in fields:
            near = _closest(key, fields)
            hint = f" Did you mean {near!r}?" if near else ""
            problems.append(
                f"{where}: unknown field {key!r}.{hint} "
                f"Known: {', '.join(sorted(fields))}"
            )
            continue
        expected = fields[key][0]
        # bool is a subclass of int; an int field must not silently accept True.
        if expected is not bool and isinstance(value, bool):
            problems.append(f"{where}: {key!r} should not be a boolean")
        elif not isinstance(value, expected):
            names = expected if isinstance(expected, tuple) else (expected,)
            wanted = " or ".join(t.__name__ for t in names)
            problems.append(
                f"{where}: {key!r} should be {wanted}, got {type(value).__name__}"
            )
    return problems


def _closest(key: str, fields: dict) -> str | None:
    """A suggestion for a misspelling, so the error is actionable."""
    import difflib

    matches = difflib.get_close_matches(key, list(fields), n=1, cutoff=0.6)
    return matches[0] if matches else None


def validate_case(case: dict, source: str = "?") -> list[str]:
    where = f"{source}:{case.get('id', '<no id>')}"
    problems = _check(where, case, CASE_FIELDS, REQUIRED_CASE_FIELDS)
    expect = case.get("expect")
    if isinstance(expect, dict):
        problems += _check(f"{where}.expect", expect, EXPECT_FIELDS)
    if not expect and not case.get("judge"):
        problems.append(f"{where}: asserts nothing — it would pass on any reply")
    return problems


def validate_cases(cases: list[dict]) -> None:
    """Raise on the first malformed case, reporting every problem found."""
    problems: list[str] = []
    seen: set[str] = set()
    for case in cases:
        problems += validate_case(case, str(case.get("_file", "?")))
        case_id = case.get("id")
        if case_id in seen:
            problems.append(f"duplicate case id {case_id!r}")
        if isinstance(case_id, str):
            seen.add(case_id)
    if problems:
        raise CaseError(
            "eval cases are malformed:\n\n  " + "\n  ".join(problems)
            + "\n\nA misspelled assertion is silently ignored, so the case would "
            "pass having asserted nothing."
        )


def json_schema() -> dict[str, Any]:
    """The same definitions as JSON Schema, for editors."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/tiry/Shrimpy/evals/cases/schema.json",
        "title": "Shrimpy behavioural eval cases",
        "description": (
            "Bespoke. See evals/schema.py for why promptfoo was not adopted. "
            "Generated from CASE_FIELDS/EXPECT_FIELDS — edit those, not this file."
        ),
        "type": "object",
        "required": ["cases"],
        "additionalProperties": False,
        "properties": {
            "cases": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": list(REQUIRED_CASE_FIELDS),
                    "additionalProperties": False,
                    "properties": {
                        name: {**fragment, "description": help_}
                        for name, (_, fragment, help_) in CASE_FIELDS.items()
                    }
                    | {
                        "expect": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                name: {**fragment, "description": help_}
                                for name, (_, fragment, help_) in EXPECT_FIELDS.items()
                            },
                        }
                    },
                },
            }
        },
    }
