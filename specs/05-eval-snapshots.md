# 05 — Eval result snapshots

| | |
|---|---|
| **ID** | 05 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `harness/snapshot.py`, `harness/agent.py`, `harness/cli.py`, `evals/runner.py`, `shrimpy` |
| **Depends on** | [`03`](03-behavioural-evals.md) |

## Problem

A full eval pass costs **$1.06** and takes ~40 s. Two consequences:

**Tuning an assertion is expensive.** Adjusting a regex or a judge rubric re-runs twelve
live cases to re-read replies that have not changed.

**Every run draws a fresh sample.** A genuine regression and ordinary model variance are
indistinguishable. `brevity` opened the skill on one run and answered from the category
description on the next — same case, same prompt, 8438 vs 5158 tokens. With no cached
baseline there is nothing to say which run was the anomaly.

## Why it matters

An eval suite that is expensive to run is an eval suite that is not run. The failure is not
a wrong answer; it is the suite quietly falling out of the loop.

## Constraints

1. **The cache must invalidate on anything that changes the answer** — the persona, any
   skill file, the model, the toolset. Missing an invalidation is worse than no cache: a
   green board reporting the behaviour of an agent that no longer exists.
2. **It must not invalidate on things that don't** — assertion text, case metadata — or the
   saving is zero.
3. **A cached pass must never look like a fresh one.**
4. **Parallel cases share a process**, so any per-run state must not be global.

## What upstream provides, and why it was rejected

Hermes has `llm_execution` middleware — the equivalent of LangGraph's `wrap_model_call`
(`hermes_cli/middleware.py:20-34`, fired at `agent/conversation_loop.py:3331-3358`). It
wraps the real provider call inside the retry loop and sees the full kwargs. Recording
responses there is the textbook cassette design.

**Three findings killed it.** The request carries volatile regions that change every run,
so a request hash would never match:

| Region | Example |
|---|---|
| ephemeral home path | `Other profiles live under /tmp/shrimpy-home-lwiruh4m/profiles/` |
| live git state | `Root: /home/tiry/dev/shrimpy, Branch: master, Status: 31 staged` |
| session date | `Conversation started: Monday, September 07, 2026` |

Keying on it needs a normaliser stripping three regions, plus response serialisation and a
streaming spike. That complexity only pays if you need to intercept **within** a turn —
mocking a tool response mid-loop, say. Nothing here does.

## Proposed change

### Cache the turn, not the model call

```
key = sha256(prompt, model, provider, toolsets, SOUL.md, skills/**, config.template.yaml)
```

Everything that legitimately changes the answer, nothing that doesn't. `.work/snapshots/`,
gitignored — a local cache, not a fixture to review in a diff.

Default: **replay if present, else call and record.** `--live` re-records, `--no-snapshot`
bypasses. Judge verdicts cache separately on `(question, answer, rubric, model)`, so
changing a regex does not re-pay for judging.

### Label cached results, and separate spent from recorded

Every cached row prints `(cached)`, and a fully-cached run prints
`all cached — nothing was measured live`.

The summary distinguishes **spent this run** from **recorded**. The first implementation
conflated them and reported `$1.0626` for a run that spent nothing — exactly the lie the
feature exists to prevent.

### Never cache a failure

Only runs that produced an answer are recorded. Caching a transport error would make one
bad network moment permanent.

## Options considered

| Option | Why not |
|---|---|
| `llm_execution` cassettes | Three volatile regions, response serialisation, streaming risk. Buys sub-turn fidelity nothing needs. |
| Key on the prompt only | A skill edit would not invalidate — the exact failure that matters. |
| Key on a manual version number | Someone forgets to bump it. |
| Turn-level hash of the definition | **Chosen.** ~40 lines, no coupling to Hermes internals. |

## Acceptance criteria

- [x] Cold run records; re-run replays
- [x] Editing any skill file or `SOUL.md` invalidates every snapshot
- [x] Editing an assertion invalidates nothing
- [x] Cached rows labelled; fully-cached runs say so
- [x] Summary separates spent from recorded
- [x] `--live`, `--no-snapshot`, `./shrimpy snapshots [--clear]`
- [x] A corrupt snapshot is a miss, not a crash

## Verification

All four behaviours, end to end:

| | |
|---|---|
| cold run | 12/12, **$1.0626 spent**, ~40 s |
| re-run | 12/12, **$0.0000 spent**, **0.34 s**, every row `(cached)` |
| append a comment to `SKILL.md` | sha `baa30074` → `dde968b6`; case goes **live** |
| revert | **cached** again |

**Two defects found and fixed.** The results file used second-granularity timestamps, so two
runs in the same second overwrote each other — now microsecond. And the misleading total
described above.

## Out of scope

Sub-turn replay. Mocking tool responses. Both would need the middleware path, which is
recorded here so the reasoning is not rediscovered.

## Open questions

- **Snapshots are keyed on the definition, not on model version.** If OpenRouter silently
  moves `anthropic/claude-sonnet-5`, a cached pass will not notice. `--live` on a schedule
  is the answer, and there is no schedule yet.
