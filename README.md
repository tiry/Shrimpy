<img src="avatar.png" alt="Shrimpy" width="140" align="right">

# Shrimpy

[![CI](https://github.com/tiry/Shrimpy/actions/workflows/ci.yml/badge.svg)](https://github.com/tiry/Shrimpy/actions/workflows/ci.yml)

The agent definition for **Shrimpy**, an aquarium keeper's assistant built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent) — plus a harness for
running and testing it locally with nothing else attached.

This repo is the source of truth for the persona and its skills. The
[tairy-agent](https://github.com/tiry/tairy-agent) deployment consumes them; it
is not where they are edited.

```
SOUL.md                     the persona
DISPLAYNAME  avatar.png     Matrix identity
skills/aquarium/
  DESCRIPTION.md            category description — trigger phrases, rendered in full
  aquarium-supervisor/
    SKILL.md                decision rules and the CLI contract — no facts
    references/*.md         chemistry, products, livestock, triage — mechanisms, not values
    scripts/aqua.py         the live-data CLI, stdlib only
    assets/reference.json   species tolerances, label formulas, conversions
    assets/initial/         a one-time migration payload
```

**The facts are not in the skill.** Measurements, livestock and supplies live at
`$HERMES_HOME/workspace/aquarium/` on the deployment volume, and the agent reads
and writes them through `scripts/aqua.py`. See
[`specs/06`](specs/06-live-data-and-reporting.md), and **read
[`AGENTS.md`](AGENTS.md#consuming-this-repo) before deploying** — that data exists
nowhere else, so the backup story is part of the contract.

That layout is deliberate: it is exactly what `tairy-agent/scripts/create-profile.sh`
copies out of a `profiles/<name>/` directory, so this repo can be dropped in as one.
`tests/test_profile_layout.py` fails if it drifts.

## Specs

Planned and completed work lives in [`specs/`](specs/README.md), numbered in execution
order — the same convention as `tairy-agent/specs`. [`06`](specs/06-live-data-and-reporting.md)
is the open one: live data the agent can update, replacing the ~150 hand-restated facts in
the skill, eight of which have already contradicted each other.

[`AGENTS.md`](AGENTS.md) holds the working notes, including the contract a deployment must
satisfy to consume this repo.

## Quick start

```bash
./shrimpy setup                  # uv, .venv, hermes-agent — a few minutes, once
$EDITOR .env                     # OPENROUTER_API_KEY

./shrimpy test                   # 136 offline checks, ~2.5s, no API key, no cost
./shrimpy prompt --skills        # what the model sees when deciding to open a skill
./shrimpy ask -v "is 6.6 too low"
./shrimpy chat                   # interactive REPL as Shrimpy
./shrimpy eval                   # behavioural evals — cached; ~$0.42 on a cold run
./shrimpy snapshots              # inspect or clear the eval cache
```

## What the harness is

Hermes adopts a persona from one directory: `$HERMES_HOME` holding `SOUL.md`,
`config.yaml` and `skills/`. That is the whole mechanism. Everything here is
scaffolding around it — no Matrix, no Synapse, no Hindsight, no Caddy, no
docker-compose, no gateway.

A run builds a throwaway `HERMES_HOME` whose `SOUL.md` and skill categories are
**symlinks into this repo**, so editing a `SKILL.md` takes effect on the next run
with no sync step. Runtime state lives in `.work/` or a temp dir and is
gitignored; nothing is ever written back into the definition.

Runs go through the Python API (`AIAgent.run_conversation`) rather than
`hermes -z`, because `-z` prints only the final text — and "did it open the
aquarium skill?" is the single most important question to ask about a
skill-driven persona.

## The two silent failures

A Hermes skill can be entirely absent from the agent's world while every file on
disk looks fine and nothing logs an error:

- **Descriptions are truncated at 60 characters** in the skill index
  (`SKILL_PROMPT_DESC_LIMIT`). A long, trigger-rich `description` is mostly
  invisible. This is why trigger phrases live in the category `DESCRIPTION.md`,
  which is rendered in full.
- **An unquoted `": "` in a description is invalid YAML.** Frontmatter parsing
  falls back to a naive line reader, `platforms` comes back as a string, platform
  matching fails, and **the skill is dropped from the index entirely** — while
  still parsing, and logging nothing.

Both are assertions in `tests/`. Introducing either one turns the suite red and
makes `./shrimpy prompt --skills` say so explicitly.

The first is checked by **Hermes' own linter** — `tools/skill_linter.py` is
importable from the installed package, so the conventions stay correct as upstream
moves rather than drifting against a hand-rolled copy. The second cannot be: the
linter reads frontmatter through Hermes' *tolerant* parser, which is precisely the
one that succeeds on bad YAML and drops the skill. Parsing the same bytes strictly
is what catches it.

## Offline checks — `./shrimpy test`

No API key, no network, no cost, ~1 second. Builds the real system prompt through
Hermes' own code path with dummy credentials and asserts on it.

| file | what it protects |
|---|---|
| `test_frontmatter.py` | **Hermes' own `tools/skill_linter.py`** (12 checks: description length, name/dir match, dangling references, …) plus what it does not cover: strict YAML, `platforms` is a list, every category has a `DESCRIPTION.md` |
| `test_system_prompt.py` | SOUL.md is loaded, every skill and category is indexed, the category description is rendered untruncated, trigger phrases reach the model, skill bodies are *not* inlined |
| `test_references.py` | cited reference files exist, no orphans, support files stay out of the prompt |
| `test_profile_layout.py` | the layout contract with the deployment; no runtime state committed |
| `test_harness.py` | toolset names are real, memory is off, no incidental LLM calls, eval cases assert something, the interceptor never raises, snapshots invalidate on a skill edit |

## Behavioural evals — `./shrimpy eval`

Real model calls. Proves the persona and skills are *acted on*, not merely
assembled. Twelve cases in `evals/cases/aquarium.yaml`, each traceable to a rule
written down in `SOUL.md` or `SKILL.md` via a required `why:` field — a case that
does not trace back to a stated rule is testing the model, not the agent.

Two grading mechanisms: regexes for facts with one right answer (a dose is
2.5 mL or it is not), and a rubric graded by a cheaper second model for semantic
properties ("does it avoid presenting an unmeasured number as fact").

```bash
./shrimpy eval                            # all cases (cached where possible)
./shrimpy eval --case coral-scope -v      # one case, with the full reply
./shrimpy eval --live                     # ignore the cache and re-record
./shrimpy eval --no-judge                 # regex assertions only, cheaper
```

Results append to `evals/results/<timestamp>.jsonl` so a regression can be diffed
against an earlier run.

### Snapshots

A cold pass costs about **$1.05** and takes ~40s, and every run draws a fresh
sample — so a real regression and ordinary model variance look identical. Results
are therefore cached on a hash of **everything that legitimately changes the
answer**:

```
prompt · model · provider · toolsets · SOUL.md · skills/** · config.template.yaml
```

Edit a skill and every snapshot invalidates, which is exactly when you want to
re-measure. Tweak a regex or a judge rubric and nothing does — the common case.
A cached pass is **~0.3s and $0**, and is always labelled `(cached)`: a green
board that measured nothing must never look like one that did. Judge verdicts are
cached separately on `(rubric, reply, model)`.

Snapshots live in `.work/` and are gitignored — a local cache, not a fixture to
review in a diff. `./shrimpy snapshots --clear` empties it.

Rejected alternative: recording provider responses under Hermes'
`llm_execution` middleware — the equivalent of LangGraph's `wrap_model_call`.
It's a real, well-built seam, but the request carries three volatile regions (the
ephemeral `HERMES_HOME` path, live git status, the session date), so keying on it
needs a normaliser plus response serialisation. That complexity only pays if you
need to intercept *within* a turn. Nothing here does.

**Design a case against behaviour, not against wording.** Three of the first ten
cases initially failed on correct answers: the agent named 3.2 mL *in order to
correct it*, and scoped the coral caution to the display tank with a sentence
containing "do not add". Forbidding a substring forbids the right answer too.

## Live data

The skill used to carry every fact as prose. ~150 of ~400 facts were restatements,
and **eight had already contradicted each other** — the ammonia gap asserted both
open and closed in six places each, a live `3.2 mL` dose in the emergency runbook
that two other files called a 30% overdose, and a "do not add coral" caution
applied to the tank that needed coral. Two passing evals were testing behaviour
the skill contradicted elsewhere in its own text.

So the facts moved into a database and the arithmetic moved into code:

```bash
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ph 6.94 --tank display -i kactoily
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank staging
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py report
```

Three tiers, and the split is the design:

| Tier | Where | Owner | On re-provision |
|---|---|---|---|
| **Reference** — species tolerances, label formulas, conversions | `assets/reference.json` | git | replaced |
| **Instance** — tanks, animals, readings, supplies | `$HERMES_HOME/workspace/aquarium/` | the agent | **untouched** |
| **Fixtures** — deterministic eval data | `evals/fixtures/aquarium/` | git | n/a |

`workspace/` is the only location protected on every axis — in `_PROFILE_DIRS`, in
`USER_OWNED_EXCLUDE`, in the distribution hard-exclude list, and chowned at boot.
Notably **not** `assets/`, which the update path will `rmtree`, and not the skill
directory, which `create-profile.sh:74` deletes on every provision.

`aqua` is stdlib-only, so installing the skill is the whole installation. Charts
use Pillow, which is a core Hermes dependency; there is no openpyxl, pandas or
matplotlib in the container, so spreadsheets are CSV and plots are hand-drawn PNGs.

**The arithmetic moving into code is the point.** `aqua dose prime --tank display`
returns `2.4 mL — standard dose for 24.2 gal computed water volume`. Implementing
it turned up a ninth contradiction: the prose claimed "≈24–26 gal" and dosed on
"~25", while its own subtraction gave 24.0–24.5.

## The access boundary

Shrimpy runs in the cloud. The `aquadirector` CLI, the Kactoily sensor and the
feeder are on Tiry's LAN and unreachable from there. The deployment does give the
agent a real terminal, so the skill has to say *why* it cannot use the tool —
otherwise the model tries, gets `command not found`, and reasons from the wrong
premise. SKILL.md states this in the core rules and again in §7, and §7 reframes
every command as one to **ask Tiry to run**, not to execute.

Testing that faithfully needs the same terminal production has, or the agent
declines because it has no shell rather than because the skill told it not to —
a case passing for the wrong reason.

So the harness **grants `terminal` to every run and neutralises it at the gate.**
Hermes lets a `pre_tool_call` hook return `{"action": "block"}`, which vetoes the
call and hands a message to the model as the tool result
(`plugins.py:6589`) — the same mechanism its own security policy uses, so the
model cannot route around it. `harness/interception.py` registers one: shell-capable
tools are blocked and recorded, never executed. The agent's context is identical
to production, nothing runs, and cases can assert `attempts_no_commands: true`.

Two properties that turned out to be load-bearing:

- **The recorder must never raise.** Hook dispatch is fail-open — an exception is
  swallowed into a debug log, so a throwing recorder would report "no commands
  attempted" for a run that attempted several.
- **The block message must be coherent for the command given.** One
  aquadirector-shaped message for every block produced this, given a plain `echo`:
  *"That's a strange error for a plain echo command, and it doesn't match what
  actually happened."* The agent spent the turn reasoning about the error instead
  of the task. There are now two messages — LAN-specific and generic — and a test
  that neither mentions the harness.

## Cost note

Opening the skill costs ~29k tokens (~$0.06 with Sonnet); answering from the
index alone costs ~5k (~$0.01). The category description is detailed enough to
answer some questions outright — which is correct and cheaper, so `opens_skills`
is not asserted on cases whose answer is already in the index.

## Configuration

`.env` (gitignored, from `.env.example`):

| variable | default | |
|---|---|---|
| `OPENROUTER_API_KEY` | — | required for `ask`, `chat`, `eval` |
| `SHRIMPY_MODEL` | `google/gemini-3.8-flash` | also `-m` on any subcommand |
| `SHRIMPY_JUDGE_MODEL` | `google/gemini-3.8-flash` | rubric grading |

**The model was chosen by measurement, not by price.** The full suite was run
against three candidates:

| model | result | cost |
|---|---|---|
| `anthropic/claude-sonnet-5` | 16/16 | $1.95 |
| **`google/gemini-3.8-flash`** | **16/16** | **$0.42** |
| `google/gemini-2.5-flash` | 13/16 | $0.06 |

`2.5-flash` was rejected on behaviour, not cost: it failed `salt-never` (asked
which tank instead of refusing salt outright — salt is wrong in *both*),
`cannot-check-sensor` (never said it could not reach the sensor), and it narrated
tool output, which `SOUL.md` forbids. As a **judge** it was worse: given five
deliberately-bad replies it passed one that should have failed. A silently
permissive judge is worse than none. `3.8-flash` catches all five.

Set `SHRIMPY_MODEL` to whatever the deployment runs. If the two diverge, the
evals stop measuring the agent you actually ship.

`harness/config.template.yaml` is harness-only and never shipped: the deployment
generates its own `config.yaml` on the volume. It pins memory off, disables
auto-titling, background review and the curator, and blocks lazy pip installs.

`vendor/hermes-agent` is pinned to `29112be` (v0.21.0) — the same commit the
deployment runs, so local behaviour matches.

## What Hermes does and does not give you

Worth recording, since it drove the design:

**No test harness.** `tests/` is 3,594 files but excluded from the package
(`pyproject.toml:585`) and `setup.py:34` hard-blocks wheel builds — so no fixtures
are importable. `evals/` is four bespoke harnesses with no shared code and no
`__init__.py`. There is no fake LLM provider and no VCR/replay, not even as a dev
dependency. The documented way to test a skill is, verbatim: *"Run the skill and
verify the agent follows the instructions correctly."*

**But a real middleware system**, close to LangGraph's: `llm_execution` ≈
`wrap_model_call`, `tool_execution` ≈ `wrap_tool_call`, plus 43 plugin hook events
and a shell-hook bridge. `pre_tool_call` is what makes the terminal interception
above possible. What has *no* hook is skill indexing (`prompt_builder.py:1769`) —
so the offline prompt assembly in `tests/` is the only way to assert on the index,
and that is what upstream does internally too.

Reusable off the shelf: `tools/skill_linter.py`, `hermes prompt-size --json`,
`hermes approvals test --json`, `hermes -z`.

## Known gaps

- Memory is off. The deployment runs Hindsight with a per-user bank.
- No CI yet. `./shrimpy test` is designed to run on every push; `./shrimpy eval`
  on demand.
- `tairy-agent` still holds its own copy of these files. Making it consume this
  repo is the next structural step.
- `./shrimpy chat` execs the real `hermes` binary, which does not load the
  harness — so the terminal it grants is a **real** terminal. Interception applies
  to `ask` and `eval` only.
- Snapshots are keyed on the definition, not on model version. If OpenRouter
  silently moves `anthropic/claude-sonnet-5`, a cached pass will not notice.
  `--live` on a schedule is the answer.
