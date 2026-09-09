# 07 — CI, and a lint baseline for it to enforce

| | |
|---|---|
| **ID** | 07 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `.github/workflows/ci.yml` (new), `ruff.toml` (new), `harness/home.py`, `.env.example`, `evals/runner.py`, `tests/test_harness.py`, `tests/test_aqua_cli.py`, `scripts/demo-trend.sh` (new), `skills/aquarium/aquarium-supervisor/` |
| **Depends on** | [`02`](02-offline-skill-checks.md), [`03`](03-behavioural-evals.md), [`06`](06-live-data-and-reporting.md) — CI runs what those built |

**Retroactive, and it breaks this repo's own rule.** [`AGENTS.md`](../AGENTS.md) says the
retroactive specs `01`–`05` exist because the reasoning was worth keeping, and not to add
more. This is one more, for one reason: the model-selection evidence below cost real money
to obtain, contradicts the obvious cheap answer, and would otherwise survive only in a
commit message. Recording it here is the difference between "we chose this" and "we measured
this". No further retroactive specs.

## Problem

Nothing ran on push. The 136 offline checks existed and were green, and stayed green only
for as long as somebody remembered to run them. There was also no lint configuration at all
— no `pyproject.toml`, no `ruff.toml` — across 21 Python files in four directories.

Separately, [`05`](05-eval-snapshots.md) left an open question with no answer:

> Snapshots are keyed on the definition, not on model version. If OpenRouter silently moves
> `anthropic/claude-sonnet-5`, a cached pass will not notice. `--live` on a schedule is the
> answer, and there is no schedule yet.

## Why it matters

An offline suite that is cheap to run is worthless if it is not run, and the two silent
failure modes it guards ([`02`](02-offline-skill-checks.md)) produce an agent that answers
fluently about tanks it no longer knows anything about. That is not a failure anyone
notices by eye.

## Constraints

1. **Secrets must never reach `pull_request` code.** A live job triggered by a PR would
   expose the key to whatever that PR contains.
2. **The submodule is large.** A full clone of `vendor/hermes-agent` is gigabytes; a shallow
   clone at the pinned tag is 253 MB and about 4 seconds.
3. **A live run can fail because the provider is down.** That is not a regression and must
   not read as one.
4. **The skill claims to be stdlib-only.** `test_cli_is_stdlib_only` enforces that
   statically; nothing proved it at runtime.

## Proposed change

### `ruff.toml` — a baseline chosen by measurement

`E,W,F,I,UP,B,SIM` at **line-length 120**. The threshold is not arbitrary:

| line-length | `E501` violations |
|---|---|
| 100 | 20 — every one a long f-string, none prose |
| **120** | **1** — a genuinely too-long 139-char line in `delta_phrase` |

Twenty violations auto-fixed, three by hand. `SIM108` disabled: its single hit wants a
120-character ternary in place of a readable four-line `if/else`.

`ruff.toml` rather than `pyproject.toml` because the repo root is a Hermes *profile*, not a
Python package, and a `pyproject.toml` there invites someone to try installing it.

### Three jobs, cheapest first

| job | what | why it is separate |
|---|---|---|
| `lint` | ruff, pinned version, no submodule, no venv | ~7 s |
| `skill` | the aquarium CLI on Python 3.11/3.12/3.13, no submodule, no venv, only `pytest` and `pyyaml` | makes "stdlib-only" falsifiable |
| `test` | `./shrimpy setup` then `./shrimpy test`, then the prompt canary and a rendered chart | ~35 s |
| `live` | the full behavioural suite against a real model | monthly and on demand |

There is no build artifact in this repo, so **`./shrimpy setup` succeeding is the build
check**. The `test` job ends on `./shrimpy prompt --skills`, which exits 1 when the skill
index is empty — a canary for the failure that logs nothing.

### The live job's exit-code contract

| code | meaning | CI |
|---|---|---|
| 0 | every case passed | notice |
| 1 | the agent behaved wrongly | **red** |
| 3 | the provider was unreachable | warning, stays green |

A red badge must mean "Shrimpy is wrong", not "OpenRouter was down at 3am".

### The model moves to `google/gemini-3.8-flash`

Chosen by running the full suite against three candidates, not by reading a price list:

| model | result | cost |
|---|---|---|
| `anthropic/claude-sonnet-5` | 16/16 | $1.95 |
| **`google/gemini-3.8-flash`** | **16/16** | **$0.42** |
| `google/gemini-2.5-flash` | 13/16 | $0.06 |

**`2.5-flash` was rejected on behaviour, not cost.** It failed `salt-never` by asking which
tank instead of refusing salt outright — salt is wrong in *both* tanks, so asking applies
"always know which tank" where it does not belong and stalls a safety answer. It failed
`cannot-check-sensor` by giving a stale reading without ever saying it could not reach the
sensor. It also narrated tool output, which `SOUL.md` forbids.

**As a judge it was worse.** Given five deliberately-bad replies it passed one that should
have failed. A silently permissive judge is worse than no judge, because it makes a broken
agent look fine. `3.8-flash` catches all five, including a fabricated *"I ran it, the
dashboard shows pH 7.02"*.

The first check of the judge — 13/13 agreement with `3.7-flash` — was **worthless**, because
every case in it was a PASS. A judge that always says PASS scores 13/13 too. Only grading
known-bad replies discriminates.

## Options considered

| Decision | Options | Chosen |
|---|---|---|
| Live cadence | per push · weekly · monthly · manual only | **monthly + dispatch** — model drift is a slow failure; per-push spends on README commits |
| Live scope | one smoke case · three representative · full suite | **full suite** — at $0.42 the cheaper options save nothing worth the coverage |
| Failure semantics | any failure red · separate provider errors | **separate** — an unattended job that cries wolf gets ignored |
| Lint strictness | defaults · curated · curated + `ruff format` | **curated, no formatter** — `ruff format` would reflow 17 of 21 files for no correctness gain |

## Acceptance criteria

- [x] `ruff check` clean, pinned version, runs on every push
- [x] The skill's CLI passes on 3.11, 3.12 and 3.13 with hermes-agent absent
- [x] `./shrimpy setup` and `./shrimpy test` run from a clean checkout
- [x] `prompt --skills` canary fails when the index is empty
- [x] A pH trend chart is rendered and uploaded on every push
- [x] The live job runs monthly and on dispatch, never on `pull_request`
- [x] Provider errors report distinctly from agent failures
- [x] `16/16` against the live model in CI

## Verification

**Rehearsed locally before pushing**, including a clean-room simulation of the `skill` job:
a fresh clone with no submodule and a venv holding only `pytest` and `pyyaml` — 63 passed,
1 skipped (the PNG test, correctly skipping without Pillow).

**Live in CI:** 16/16 against `gemini-3.8-flash`, $0.4186, every case exercising the CLI in
the shape it was designed for.

### Four defects CI found that local runs had not

1. **`astral-sh/setup-uv@v10` does not resolve.** They publish moving major tags only to
   `v7`, though the latest release is `v10.0.1`. The evidence was already in hand — the
   `v10` *branch* 404'd while the `v10.0.1` *tag* returned the file — and it was misread:
   the action's *inputs* were checked, the *ref* was not. Now pinned exactly, and every
   `uses:` ref is verified to fetch before pushing.
2. **The chart artifact had a hole in it.** `demo-trend.sh` invoked the CLI with system
   `python3`, which on the runner has no Pillow, so the chart degraded to SVG and the glob
   for a `.png` matched nothing. `upload-artifact` does not error when *some* of several
   paths match, so it went green over a missing file. Missed locally because this machine's
   system python is conda's and happens to have Pillow. **The runner was the honest
   environment.**
3. **The demo series was dated into the future** — it used UTC while the CLI stamps local
   time — and interleaved with the seeded readings, producing a sawtooth.
4. **Three deprecation waves.** `checkout@v4`, `setup-python@v5` and later
   `upload-artifact@v5` all target Node 20. Fixed while warnings, not failures.

## Out of scope

Publishing eval transcripts — [`08`](08-eval-transcripts.md). Release or publish workflows;
there is nothing to publish.

## Open questions

1. **The evals now measure a different model from the one the deployment runs.** That only
   stays honest if the deployment moves to `gemini-3.8-flash` too. Flagged in `README.md`
   and `AGENTS.md`; `SHRIMPY_MODEL` overrides it for a Sonnet run at any time.
2. **A monthly cron will not notice a model retirement for up to 31 days.** Acceptable for a
   slow failure; the answer if it stops being acceptable is weekly, at 4× the cost.
