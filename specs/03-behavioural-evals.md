# 03 — Behavioural evals

| | |
|---|---|
| **ID** | 03 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `evals/runner.py`, `evals/cases/aquarium.yaml`, `harness/agent.py`, `harness/cli.py` |
| **Depends on** | [`01`](01-standalone-agent-repo.md) |

## Problem

[`02`](02-offline-skill-checks.md) proves the persona and skill index are *assembled*
correctly. It says nothing about whether they are *acted on*. The failures that matter to
an aquarium keeper are all behavioural:

- giving a dose without asking which of two tanks differing 6× in volume
- accepting ORP as a proxy for an ammonia test, which the skill spends 20 lines refuting
  and which the user has been told elsewhere
- applying a caution outside its stated scope
- stating an unmeasured number as fact

None of these are visible in a prompt. They need real model calls.

## Why it matters

`SOUL.md:7` states the stakes: *"panicking a keeper into unnecessary intervention kills
more animals than neglect does."* The skill exists to prevent specific mistakes, and the
only way to know it does is to make them available and check.

## Constraints

1. **`opens_skills` cannot be recovered from the final text.** Hermes has no field for it;
   a skill is loaded by the model calling `skill_view` (`tools/skills_tool.py`), so it must
   be read out of the tool calls.
2. **`skill_view` failures look like successes.** The model routinely tries the *category*
   name first, which returns `{"error": "Skill 'aquarium' not found."}`
   (`tools/skills_tool.py:1438`). Counting that as a load makes an eval pass on a miss.
3. **Each case is a fresh session.** `session_db=None` means no history, so a case worded as
   a follow-up has no antecedent.
4. **Cost and variance are real.** Every case is a live call.

## Proposed change

### Declarative cases, each traceable to a stated rule

`evals/cases/*.yaml`, with a **required `why:` field** citing the rule in `SOUL.md` or
`SKILL.md` that the case defends. A case that does not trace back to a stated rule is
testing the model, not the agent; `tests/test_harness.py` enforces the field's presence.

Assertions: `opens_skills`, `matches_any`, `matches_all`, `not_matches`, `max_chars`,
`attempts_no_commands`, and a `judge:` rubric.

### Two grading mechanisms, chosen per property

**Regex** for facts with one right answer — a dose is 2.5 mL or it is not.

**A rubric graded by a cheaper second model** for semantic properties: *"does it avoid
presenting an unmeasured number as fact"*. A substring match there is either brittle or
meaningless.

### Structural detection of what was opened

Parse `skill_view` calls out of the assistant messages, pair each with its tool response by
`tool_call_id`, and exclude failures by **parsing the JSON envelope for an `error` key** —
never by scanning the response body. See Verification for why that distinction is not
pedantic.

## Options considered

| Option | Why not |
|---|---|
| `on_skill_lifecycle` hook (`plugins.py:225`) | `skill_view` has a dedup stub (`skills_tool.py:2155`) that returns early on a repeat view, so **no event fires the second time**. Raw tool-call parsing has no such blind spot. |
| LLM judge for everything | Slow, expensive, and vague where a regex is exact. |
| Regex for everything | Cannot express "avoid presenting an unmeasured number as fact". |
| Per-case toolsets and homes | `activate()` mutates process-wide environment; parallel cases would race. One home per batch, isolated by a fresh agent with no session store. |

## Acceptance criteria

- [x] Cases are data, not code, and each carries a `why:`
- [x] `skills_opened` reflects successful loads only
- [x] Failures name the assertion and show what matched
- [x] Results append to `evals/results/<timestamp>.jsonl` for diffing
- [x] `--case`, `--no-judge`, `-j`, `-v` supported
- [x] Ten starter cases covering triggering, the two-tank rule, proxies, rule scope, the
      cabinet, and voice

## Verification

**Live, twice.** The first pass was 6/10, and **all four failures were case-design bugs —
the agent was right every time.** That is the finding worth carrying forward:

| Case | Why it failed |
|---|---|
| `dose-display` | forbade `3.2 mL`; the agent named it *in order to correct it*: "2.5 mL … not the 3.2 mL you'd get from treating it as 32 gallons" |
| `coral-scope` | forbade "do not add"; the agent correctly scoped the caution — "This caution is specific to staging. Do not add coral to the display tank." |
| `dose-staging` | worded as a follow-up ("And for the little quarantine tank?") with no history |
| `brevity` | asserted `opens_skills`, but the answer was already in the category description |

**Forbidding a substring forbids the right answer too.** The semantic cases moved to a
rubric judge; `dose-staging` was made self-contained; `brevity` dropped the assertion that
was not the property under test.

Second pass: 12/12.

**One harness bug this surfaced.** `contextlib.redirect_stdout` is process-global, so with
parallel cases the last thread to exit restored a dead buffer and **silently swallowed the
entire results table**. Replaced with a per-thread stdout router.

**A second, worse one**, found later when [`04`](04-access-boundary.md) edited the skill:
`skills_opened` used to treat any response containing `"not found"` as a failed lookup.
`SKILL.md` §7 contains the phrase `command not found`, so every *successful* `skill_view`
of the aquarium skill scored as a miss and **eight of twelve evals failed on a documentation
edit**. Skill content is input to the harness; parse the envelope, never scan the body.
Pinned by `test_skill_view_detection_is_structural`.

## Out of scope

Cost and determinism — [`05`](05-eval-snapshots.md). Terminal-dependent cases —
[`04`](04-access-boundary.md).

## Open questions

- **Model drift.** Cases are pinned to `anthropic/claude-sonnet-5`. If OpenRouter silently
  moves that alias, the evals measure a different model without saying so.
