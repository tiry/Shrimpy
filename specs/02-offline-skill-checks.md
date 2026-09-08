# 02 — Offline skill checks

| | |
|---|---|
| **ID** | 02 |
| **Severity** | High |
| **Status** | **Done** |
| **Affected files** | `tests/conftest.py`, `tests/test_frontmatter.py`, `tests/test_system_prompt.py`, `tests/test_references.py`, `tests/test_harness.py`, `harness/inspect.py` |
| **Depends on** | [`01`](01-standalone-agent-repo.md) — needs the ephemeral home and prompt assembly |

## Problem

A Hermes skill can be entirely absent from the agent's world while every file on disk looks
correct, the agent boots, and nothing logs an error. There are two documented ways
(`tairy-agent/profiles/README.md:99-135`), both of which had already been hit:

**Descriptions are truncated at 60 characters.** `agent/skill_utils.py:1182`:

```python
if len(desc) > SKILL_PROMPT_DESC_LIMIT:
    return desc[:SKILL_PROMPT_DESC_LIMIT - 3] + "..."
```

The index line is the only thing the model sees when deciding whether to open a skill, so a
long trigger-rich description is mostly invisible. A 971-character one became
`"Operating profile and runbook for Tiry's two freshwater t..."`.

**An unquoted `": "` in a description is invalid YAML.** `description: Tiry's aquariums:
shrimp, guppies` makes the second colon a nested mapping. Frontmatter parsing falls back to
a naive line reader, `platforms` comes back as the *string* `"[linux, macos, windows]"`,
platform matching fails (`skill_utils.py:227`), and **the skill is dropped from the index
entirely** — while still parsing, and logging nothing.

## Why it matters

Both failures present identically to a working agent: it answers, fluently, from the
persona alone, about tanks it no longer knows anything about. There is no error to notice
and no log line to grep. The only symptom is subtly worse answers.

## Constraints

1. **The skill index has no hook.** `agent/prompt_builder.py:1769-1827` builds it with no
   `invoke_hook`, no callback, no event. Post-hoc parsing of the assembled prompt is the
   only way to observe it — which is what upstream does internally
   (`agent/context_breakdown.py:103-121`).
2. **A skills tool must be in the toolset** or the block is empty
   (`agent/system_prompt.py:619`), so an inspection agent has to request one.
3. **Checks must cost nothing.** They run on every edit; anything that calls a model won't
   be run often enough to matter.
4. **Hermes' frontmatter parser is deliberately tolerant.** It is the component that
   *succeeds* on the bad YAML above. A check that reuses it cannot detect the bug.

## Proposed change

### Assemble the real prompt offline

`harness/inspect.py` builds an `AIAgent` with dummy credentials — the same trick
`hermes prompt-size` uses (`hermes_cli/prompt_size.py:50-80`) — and calls
`build_system_prompt()`. No request leaves the machine and no API key is needed.

The index is extracted with the delimiter upstream uses
(`hermes_cli/prompt_size.py:23`): `<available_skills>.*?</available_skills>`.

### Delegate conventions to Hermes' own linter

`tools/skill_linter.py` ships with Hermes and **is importable from the installed package**
(`tools` is in `pyproject.toml:585`'s `packages.find`). Twelve checks including
`description-length`, `name-dir-mismatch`, `platforms-value`, `dangling-reference` and
`missing-section`. Delegating keeps the conventions correct as upstream moves instead of
drifting against a hand-rolled copy.

It is advisory by design (`skill_linter.py:17-20`) and every rule is WARNING severity, so
the suite fails on ERROR and surfaces warnings as skips.

Worth recording: the linter exists but is **not wired to anything** — not CI, not a
`hermes skills` subcommand. Its only in-tree caller is `skill_manager_tool.py:1059` on the
skill-creation path.

### Keep strict YAML hand-rolled

The linter reads frontmatter through Hermes' tolerant parser. Parsing the same bytes
*strictly* is what catches the `": "` trap, so `tests/conftest.py::frontmatter` uses
`yaml.safe_load` and raises. This is deliberately stricter than the runtime.

### Assert on what the model receives

| Check | Catches |
|---|---|
| `SOUL.md` phrases present in the prompt | persona replaced by `DEFAULT_AGENT_IDENTITY` |
| `<available_skills>` non-empty | every skill silently dropped |
| every skill and category indexed | one skill dropped |
| category description rendered **byte-identical** | truncation reaching category descriptions |
| specific trigger phrases present | truncation losing the phrases that matter |
| skill body **absent** from the prompt | progressive disclosure broken; 600 lines on every turn |
| `references/*` content absent | support files leaking into the index |

## Options considered

| Option | Why not |
|---|---|
| Reimplement the frontmatter rules | Drifts against upstream the moment a convention changes. |
| Use only the upstream linter | Cannot catch the `": "` trap — it uses the parser that has the bug. |
| Both, split by what each can prove | **Chosen.** |

## Acceptance criteria

- [x] Runs with no API key, no network, in ~1 s
- [x] Introducing an unquoted `": "` turns the suite red and makes
      `./shrimpy prompt --skills` say so explicitly
- [x] Introducing an over-long description fails `description-length`
- [x] Gutting `SOUL.md` fails
- [x] Adding an orphan `references/*.md` fails
- [x] `tools/skill_linter.py` reports zero findings on the shipped skill

## Verification

**Negative-tested by injection**, because a suite that cannot fail is worthless. Each fault
was introduced, the failure observed, and the file restored:

| Injected | Result |
|---|---|
| unquoted `": "` in `description` | 10 failures; `prompt --skills` printed `NO SKILL INDEX RENDERED` |
| description over 60 chars | `test_description_survives_truncation` |
| `SOUL.md` truncated to 3 lines | `test_soul_is_loaded`, `test_soul_is_not_the_hermes_placeholder` |
| orphan `references/orphan.md` | `test_no_orphan_references` |

## Out of scope

Whether the agent *follows* the skill once it is loaded — that is
[`03`](03-behavioural-evals.md). These checks prove only that the prompt is assembled
correctly.

## Open questions

None. The `## When to Use` advisory the linter raised was resolved by adding the section.
