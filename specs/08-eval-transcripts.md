# 08 — Eval transcripts published to a branch

| | |
|---|---|
| **ID** | 08 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `harness/transcript.py` (new), `harness/agent.py`, `harness/snapshot.py`, `harness/cli.py`, `evals/runner.py`, `scripts/publish-transcripts.sh` (new), `.github/workflows/ci.yml`, `tests/test_transcripts.py` (new), `.gitignore` |
| **Depends on** | [`03`](03-behavioural-evals.md), [`05`](05-eval-snapshots.md), [`07`](07-ci-and-lint.md) |
| **Creates** | the `eval-transcripts` orphan branch |

## Problem

A live run reports `16/16`, or:

```
FAIL  salt-never   judge: the assistant treats aquarium salt as a neutral option
```

and nothing else. It cannot show what the agent actually said, which tools it called, what
those tools returned, or which assertion the judge was applying.

**That gap is expensive in this repo specifically.** Three times during development the
harness was wrong and the agent was right:

| case | the assertion | what the agent did |
|---|---|---|
| `dose-display` | forbade `3.2 mL` | named it *in order to correct it* |
| `coral-scope` | forbade "do not add" | correctly scoped the caution to the other tank |
| `no-recall-of-stale-numbers` | required `aqua status` | used `readings`, which is more targeted |

Each was diagnosable only by reading the reply. Every one of those diagnoses happened
locally, by hand, with a Python one-liner over `evals/results/*.jsonl` — and that file does
not contain the conversation either, only the final text.

`harness/agent.py:378` reads the full `messages` list to extract tool-call names and then
**discards it**.

There is also a small lie to fix: the live job's upload step is named *"Keep the
transcripts"* and uploads `evals/results/`, which contains no transcripts.

## Why it matters

`SOUL.md` asks the agent to distinguish measured from inferred, to scope its cautions, and
to refuse a dose it cannot derive. Those are judgements. Judging whether the agent made
them correctly — or whether the *case* is wrong, which it was three times out of three —
requires reading the exchange. A pass/fail bit cannot carry that.

The failing runs are the ones worth reading, and those are exactly the runs where a human is
not sitting at the terminal.

## Constraints

1. **The repo is public.** Anything published is world-readable.
2. **`skill_view` returns whole files.** `SKILL.md` is 13.2 KB and a reference read up to
   10 KB, so a case's transcript is 25–35 KB and a run is roughly 1 MB.
3. **`SKILL.md` contains fenced code blocks.** Rendering a tool response that contains
   ` ``` ` inside a fence breaks the page.
4. **Secrets must not reach `pull_request` code** — [`07`](07-ci-and-lint.md).
5. **Sixteen cases run in parallel threads** and share one process.
6. **Rendering must never fail a run.** A broken renderer is a lost report, not a lost
   result.

## What the reference implementation got right, and wrong

`../mvp-bootstrap` publishes e2e artefacts to an orphan branch. Its mechanism is worth
copying almost verbatim; its data policy is not.

**Copy:** the `$RUNNER_TEMP` clone → `cp -r` → rebase-retry → push shape, with no third-party
action, no Pages and no deploy key; orphan self-bootstrap on first push; `if: always()` so
failed runs publish; the raw log committed beside the rendered view; rendering to the step
summary as well.

**Do not copy — four documented scars:**

| their bug | consequence |
|---|---|
| Published live SQLite DBs | tip tree **2.4 GiB**, one blob **94.6 MB** — 6% from GitHub's hard limit |
| Pruned by `mtime` after a `--depth=1` clone | every archived directory shares the clone's mtime, so the sort is near-arbitrary |
| Deleted `entries.json` before publishing | forced the dashboard to regex-parse markdown back out, across two incompatible table formats |
| `git checkout <branch>` in the workspace | wiped `src/` mid-job; `ModuleNotFoundError` they never fixed, only worked around |

Their renderer also silently dropped half a transcript **twice** — turns rendering as bare
`### Turn N · '?'` — because unrecognised event types fell through to a default branch. Both
times the data was intact in the raw log and only the rendering was wrong, which is the
argument for committing the raw log beside the rendered file.

## Proposed change

### Capture

`RunResult` gains `messages`; the run gains one `system_prompt`, stored once rather than
sixteen times because it is identical across cases bar the ephemeral home path.

**Redaction before storage.** Nothing key-shaped appears in `messages` today. The repo is
public and a future tool could echo an environment variable, so anything matching a provider
key pattern is scrubbed on the way in, not on the way out.

`snapshot.SCHEMA` bumps, invalidating snapshots — a one-off $0.42 on the next local run.
Transcripts live **inside** the snapshot, so a cached run still renders a readable
transcript rather than an empty one.

### Render — `harness/transcript.py`

Per case: outcome header, **the assertions with their pass/fail reasons**, then the
conversation — numbered turns, tool calls with pretty-printed arguments, tool responses.
Responses over ~2 KB collapse into `<details>`: complete, but a 13 KB skill dump does not
drown the page.

Fenced content is escaped with a zero-width space before the backticks — invisible when
rendered, and the fence no longer closes early.

Every rendered `<case>.md` gets a `<case>.json` beside it, and `entries.json` is **shipped,
not deleted**.

### Publish

An orphan `eval-transcripts` branch, written by `scripts/publish-transcripts.sh` so the
logic is testable outside CI. `permissions: contents: write` on the `live` job only.

Pruning is **by run number parsed from the directory name**, not by mtime.

```
eval-transcripts (orphan)
  README.md                          rolling: recent runs, pass rate, cost
  runs/2026-10-01__run-42__gemini-3.8-flash/
    index.md · entries.json · system-prompt.md
    cases/<case>.md · cases/<case>.json
    artifacts/ph-trend.png · report.html · csv/
```

### Local

`./shrimpy eval` writes the same tree to `.work/transcripts/` and prints the path.

## Options considered

| Decision | Options | Chosen |
|---|---|---|
| Renderer | Hermes' `sessions export --format md` · our own | **ours** — theirs needs `session_db`, which we pass as `None`; sixteen parallel cases would share one `state.db`; and decisively it cannot interleave *our* assertion results, which is the point |
| Transport | GitHub Pages · a third-party action · plain git | **plain git** — no Pages setup, no action to keep current, and the branch is browsable as-is |
| Long tool responses | full inline · `<details>` · truncated | **`<details>`** — complete but readable; truncation loses the evidence |
| Where transcripts live | results file only · in the snapshot too | **in the snapshot** — otherwise a cached run renders nothing |

## Acceptance criteria

- [x] A live run publishes a readable transcript per case, with assertions beside the conversation
- [ ] A **failing** run publishes — this is the `if: always()` path and the whole point
- [x] A tool response containing ` ``` ` renders without breaking the page
- [x] Raw JSON beside every rendered file, and re-rendering it reproduces the markdown
- [x] `entries.json` is on the branch
- [x] Pruning keeps the 50 highest run numbers, correct after a shallow clone
- [x] Anything key-shaped is redacted before it is written
- [x] Rendering failure degrades to a missing report, never to a failed eval
- [x] `./shrimpy eval` writes the same tree locally
- [x] The branch bootstraps itself as an orphan on first push

## Verification

**Offline:** fence escaping against a real `SKILL.md` tool response, redaction, the
`<details>` threshold, a raw-JSON round trip, and the prune arithmetic — which is where
their bug lives, so it is tested directly rather than trusted.

**Local:** one live case (~$0.03), then read the output and confirm it is legible. A
transcript nobody can read is the failure mode this spec exists to prevent, and it is not
detectable by assertion.

**CI:** dispatched with `live=true`. The orphan branch was created, run 11 published 16/16
for $0.4290, and the tree is 2.0 MB — 44 files, sixteen rendered transcripts with their raw
JSON, the chart, the HTML report and the CSVs.

### Two defects the runner found that local runs had not

1. **No git identity.** The orphan bootstrap commits to create the branch, and it did so
   before the script set `user.name`. A hosted runner has no `~/.gitconfig`, so the first
   live run rendered its transcripts, passed 16/16, and then died with
   `fatal: empty ident name`. It passed locally because this machine has a global identity.
   Fixed with `GIT_AUTHOR_*` exported at the top of the script, so there is no ordering to
   get wrong. The regression test blanks `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `HOME`
   to reproduce a runner rather than trust the fix.

   **This is the second time in two days the runner was the honest environment and this
   machine the misleading one** — the first was Pillow, which system `python3` happens to
   have here and does not have there.

2. **A push cancelled a dispatched run.** The concurrency group keyed only on workflow and
   ref, so a push landing seconds after a dispatch shared the group and one was cancelled.
   A live run costs money; a routine push must not be able to kill it. The group now
   includes `github.event_name` and only pushes cancel their predecessors.

## Out of scope

Trend analysis across runs beyond the rolling README. Publishing the ephemeral `HERMES_HOME`
— that stays in the 30-day zip, and is precisely what made the reference implementation's
branch 2.4 GiB. Serving any of this over GitHub Pages.

## Open questions

1. **Pruned directories stay in history.** At ~1 MB a month that is fine for a decade; a
   quarterly orphan reset is the escape hatch if the cadence ever increases.
2. **`git add -A` on the orphan branch ignores master's `.gitignore`** — the branch carries
   none. The copy list is therefore explicit rather than a wildcard.
3. **Transcripts are public.** They contain tank data and skill content that are already
   public in this repo. If a future case ever carries something private, this decision has
   to be revisited before that case is written.
