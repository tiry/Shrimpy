# 06 — Live data and reporting

| | |
|---|---|
| **ID** | 06 |
| **Severity** | High |
| **Status** | **Done** |
| **Affected files** | `skills/aquarium/aquarium-supervisor/scripts/` (new), `.../assets/` (new), `.../SKILL.md`, `.../references/*.md`, `skills/aquarium/DESCRIPTION.md`, `SOUL.md`, `harness/interception.py`, `harness/snapshot.py`, `evals/fixtures/` (new), `evals/cases/aquarium.yaml`, `tests/`, `README.md`, `AGENTS.md` (new) |
| **Depends on** | [`02`](02-offline-skill-checks.md), [`03`](03-behavioural-evals.md), [`04`](04-access-boundary.md), [`05`](05-eval-snapshots.md) — this rewrites most of the skill; the existing checks are the safety net |
| **Imposes a deployment requirement** | Yes — see [Consuming this repo](../AGENTS.md) |

## Problem

Every fact about the tanks is prose, written by hand, in more than one place. There is no
way for the agent to record a new reading, a death, or a bottle running out. The skill is a
snapshot of 5 September 2026 that can only be updated by editing markdown.

**The duplication has already drifted.** An inventory of the 1,522-line skill corpus found
~380–420 discrete facts, of which **~150 are restatements**. Eight have diverged:

| | |
|---|---|
| **Ammonia gap** | asserted **open** in six places (`SKILL.md:394-400,477`, `chemistry.md:43`, `inventory.md:81`, `triage.md:40,117`) and **closed** in six others (`SKILL.md:187,204,241`, `inventory.md:105,232`) |
| **"32 gallons"** | the figure `SKILL.md:63` calls wrong is the operative volume at `triage.md:27,101,106` and `livestock.md:98,141` — plus `livestock.md:78` "121 L", which *is* 32 gal in metric |
| **3.2 mL Prime** | `triage.md:44` still instructs "dose Prime (~3.2 mL)" — the exact error `SKILL.md:163` and `chemistry.md:102` call a ~30% overdose |
| **Coral scope** | `triage.md:139-144` says coral went into **both** tanks 28–29 Aug and "Do not add coral yet", contradicting `SKILL.md:73-77`, which scopes that caution to the display tank and says staging *needs* coral |
| **Product table** | duplicated at `SKILL.md:454-470` and `inventory.md:15-32`. BACNUNN is "Routine" in one, "Backup" in the other; zeolite "Emergency only" vs "Never". The Advatec kit — **the primary test method** — is missing from the SKILL table entirely |
| **5 Sep liquid test** | reported twice (`SKILL.md:202-208`, `:234-239`) with different phosphate values, 0–0.5 vs 0–0.25 |
| **Open question 1** | "GH/KH in both tanks — unverified" (`SKILL.md:644`) is answered at `SKILL.md:263-266`, 380 lines earlier in the same file |

Worst copy counts: staging volume **16**, display volume **14**, display GH/KH **13**,
livestock roster **8**, Prime dose table **5**.

**Two passing evals test behaviour the skill contradicts elsewhere.** `dose-display`
asserts 2.5 mL while `triage.md:44` says 3.2 mL. `coral-scope` asserts coral is correct for
staging while `triage.md:141` says do not add. They pass because the model reads
`SKILL.md`, not because the skill agrees with itself.

## Why it matters

`SOUL.md:13` is *"Never invent a number. Distinguish what was measured, what was estimated,
and what you inferred."* A corpus that states the ammonia gap as both open and closed makes
that instruction unfollowable — whichever the model picks, half the document disagrees.

`SOUL.md:7` sets the stakes: these are living animals and the errors are asymmetric in both
directions. `triage.md:44`'s 3.2 mL is a live wrong dose sitting in the emergency runbook.

And the volatile data is the data that matters. A pH reading is worth something for days.
The current design can only carry facts that were true when someone last edited a file.

## Constraints

Established by inspection of the pinned submodule and the deployment.

1. **`create-profile.sh:74` does `rm -rf "${home}/skills"`** on every provision, by explicit
   design. Data inside the skill directory is destroyed. The bundled `memento-flashcards`
   skill stores data there (`optional-skills/productivity/memento-flashcards/scripts/memento_cards.py:18-20`);
   that pattern is unsafe in *this* deployment.
2. **`assets/` is not protected either.** Absent from `_PROFILE_DIRS`
   (`hermes_cli/profiles.py:54-69`), absent from `USER_OWNED_EXCLUDE`
   (`hermes_cli/profile_distribution.py:101-120`), and `rmtree`-able at `:587`. It is the
   desktop UI's avatar store (`tui_gateway/methods_profiles.py:1021-1047`), as
   `tairy-agent/scripts/set-matrix-identity.sh:10-12` notes.
3. **`workspace/` is protected on every axis** — in `_PROFILE_DIRS` (`profiles.py:62`), in
   `USER_OWNED_EXCLUDE` (`:112`), in the docs' user-owned table
   (`profile-distributions.md:270`) and hard-exclude list (`:699`), chowned at boot
   (`docker/stage2-hook.sh:250`). No code path in either repo deletes inside it.
4. **`${HERMES_SKILL_DIR}` is the only correct invocation form.** Substituted before the
   model sees the text (`agent/skill_preprocessing.py:15,56`), on by default
   (`config_defaults.py:2261-2265`). The `maps` and `grounded-citations` skills hardcode
   `~/.hermes/...` and are **broken under named profiles**.
5. **`TERMINAL_CWD` resolves to `/opt/data`** — the *default* profile's home — for every
   multiplexed profile (`gateway/run.py:2953-2968`, `gateway/cwd_placeholder.py:40-42`).
   Relative paths land in the wrong profile. `HERMES_HOME` *is* correctly scoped per turn
   into subprocesses (`tools/environments/local.py:631-640`).
6. **No spreadsheet library exists in the container.** `openpyxl`, `xlsxwriter`, `pandas`,
   `odfpy`, `numpy`, `matplotlib` all absent — verified by live import probe. The venv is
   root-owned read-only and `HERMES_DISABLE_LAZY_INSTALLS=1` (`Dockerfile:388`). The
   bundled `xlsx` skill is non-functional there as shipped.
7. **Pillow 12.3.0 *is* a core dependency** (`pyproject.toml:245`) and is importable. Python
   is 3.13.5, venv first on `PATH`.
8. **The linter's `platforms-gating` rule** (`skill_linter.py:291-324`) flags `fcntl`,
   `os.setsid`, `/proc/`, `apt-get` and others in `scripts/*.py`. `dangling-reference`
   explicitly exempts `scripts/` (`:262-265`).
9. **A stray `.md` under a non-support subdir collides** with `skill_view`'s `rglob`
   (`tools/skills_tool.py:1319-1325`). `data/` is not in `SKILL_SUPPORT_DIRS`
   (`skill_utils.py:51`); `assets/` and `scripts/` are.
10. **The backup tar is not quiesced.** `tairy-agent/scripts/backup.sh:29-30` — file-level
    tars are inconsistent; a non-atomic JSON rewrite can be captured torn.

## Proposed change

### Three tiers of ownership

| Tier | Location | Owner | On re-provision | In git |
|---|---|---|---|---|
| **Reference** — species tolerances, label dose formulas, unit conversions, default target bands | `<skill>/assets/reference.json` | git | replaced (correct) | yes |
| **Instance** — tanks, animals, readings, supplies, events, questions | `${HERMES_HOME}/workspace/aquarium/` | the agent | **untouched** | no |
| **Fixtures** — deterministic eval data | `evals/fixtures/aquarium/` | git | n/a | yes |

"Prime's label says 5 mL per 200 L" is reference. "I have 500 mL of Prime, opened 12 Aug" is
instance. Updating the skill never touches the data; the data never needs reviewing in a PR.

Instance files: `tanks.json`, `livestock.json`, `inventory.json`, `readings.ndjson`,
`events.ndjson`, `questions.json`, `.schema_version`.

**Nothing derived is stored.** Volumes, doses, the spectator-ion figure, swap projections,
deltas and threshold flags are computed at call time. This is what makes the 3.2 mL and
32-gallon classes of error structurally impossible rather than something an eval hopes to
catch.

### A stdlib CLI shipped inside the skill

`<skill>/scripts/` — `aqua.py` (CLI and domain logic), `_store.py` (schema, atomic IO,
migration), `_report.py` (CSV, PNG, HTML). Invoked as
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py`.

```
read    status [--tank] · tanks · livestock · inventory · questions
        readings METRIC [--tank] [--since] · dose PRODUCT --tank [--scenario] · check
write   log METRIC VALUE --tank [--instrument] [--at] [--note] · log --paste
        livestock add|remove|move|note · inventory use|restock|open|set-class
        event add TYPE · question add|answer|close · tank set KEY VALUE --tank
out     export --format csv [--out] · report [--out] [--since] · plot METRIC [--tank]
admin   init [--force] · migrate · doctor
```

Three behaviours move judgment out of the model:

- **`log` answers with context** — `logged. prior 6.86 (5 Sep 16:06), Δ+0.05 over 2d,
  inside band 6.77–6.87`. `SOUL.md:15`'s *"one reading is not a trend"* becomes mechanical.
- **`dose` shows its basis** — `0.4 mL (~8 drops) — 4.0 gal measured volume`.
- **`status` flags staleness** — `latest reading 94 days old`. Without this the migration
  snapshot ages silently into a lie.

Durability: temp file + `os.replace()` in the same directory, per constraint 10. NDJSON
appends are single-line writes and readers tolerate a truncated final line. No `fcntl`, per
constraint 8. `.schema_version` and `aqua migrate` from day one — the CLI is replaced on
re-provision but the data is not, so a newer CLI will meet older data.

### One-time migration, not a mirror

`assets/initial/*.json` holds the state currently in the prose. `aqua init` copies it **only
if the data directory is empty**, stamps provenance, and never runs again. Auto-invoked on
first use so the agent cannot forget.

It goes stale by design; `status` reporting staleness is what keeps that honest.

The eight contradictions are resolved during extraction, from the evidence:

| | Resolution |
|---|---|
| Ammonia gap | **closed** — Advatec kit owned, 0 ppm both tanks 5 Sep |
| Staging coral | **3 Sep** — `triage.md`'s "both tanks, 28–29 Aug" is wrong |
| Display volume | **~25 gal** — all "32 gallons" and "121 L" corrected |
| BACNUNN | **screen/backup** — `SKILL.md:229` already demotes it |
| Zeolite | `emergency-only` — the two labels were compatible, not conflicting |
| Phosphate 5 Sep | **0–0.25** — the evening test supersedes |
| Open question 1 | **answered**, closed |

### Reporting

| | |
|---|---|
| `aqua status` | Unicode sparkline per metric — the agent sees the trend with no file |
| `aqua export --format csv` | one CSV per table, stdlib `csv` |
| `aqua plot ph --tank display` | PNG via `PIL.ImageDraw`: date axis, gridlines, shaded target band |
| `aqua report` | one self-contained HTML — tables plus base64-embedded PNGs |

`ImageFont.load_default()` only, so no font file is required; stdlib SVG fallback if PIL is
ever absent.

### The skill loses its facts

`SKILL.md` keeps When to Use, core rules, the [`04`](04-access-boundary.md) boundary, the
`aqua` contract, decision rules and procedures. **"Never re-ask what is here" becomes "run
`aqua status` first."** Removed: §1 tank tables, §2 dose tables, all of §3, §5 product
table, §6 counts, §7 alert YAML, Open Questions.

`chemistry.md` keeps formulas and mechanisms, loses all three dose-table copies.
`livestock.md` keeps species biology, loses the roster and the wrong volumes.
`inventory.md` collapses to product *reasoning* — why salt is never, the salt×zeolite
hazard. `triage.md` keeps the workflow and calls `aqua dose` instead of hardcoding 3.2 mL.

`DESCRIPTION.md` loses the roster and volumes: it is the index, it cannot be
runtime-generated, so it must not carry facts that go stale. `SOUL.md` loses
`~25-gallon`/`~4-gallon` — `SOUL.md:25` already says facts live in the skill.

### Harness

**`pre_tool_call` gains a modify path.** Allowed `aqua` invocations get `--data-dir <per-run>`
**injected** via `{"action": "modify"}` (`plugins.py:6658-6664`) rather than passed through.
The interceptor is per-run, so parallel eval cases get isolated data directories despite
`AQUA_DATA_DIR` being process-global.

Allow-list guard: reject on any shell metacharacter, then `shlex.split` and require
`argv[0]` is a `python*` and `argv[1]` ends with `scripts/aqua.py`. Everything else —
including `aquadirector` — still blocks, so [`04`](04-access-boundary.md)'s cases stay
valid.

`definition_sha()` gains `evals/fixtures/**`; fixtures change the answer, so they must
invalidate snapshots.

## Options considered

| Decision | Options | Chosen |
|---|---|---|
| Where data lives | skill dir · `assets/` · `workspace/` · `local/` | **`workspace/aquarium/`** — the only one protected on every axis and auto-chowned |
| How the agent reads it | regenerate markdown from data · CLI at answer time · hybrid | **CLI at answer time.** Regenerating markdown reintroduces the sync problem the exercise exists to kill: the agent's writes live on the volume and would be wiped by the next `create-profile.sh` |
| Tool surface | MCP server · CLI in the skill | **CLI.** "Adding the skill is enough"; MCP is a separate process, a config entry and a dependency |
| Spreadsheets | `.xlsx` via openpyxl · hand-rolled OOXML · CSV | **CSV.** Constraint 6 rules out the library; hand-rolling OOXML is ~200 lines to own for formatting nobody asked for |
| Plots | matplotlib · SVG · PNG via Pillow | **PNG via Pillow** — already a core dependency, and renders inline in Element |
| Seeding | none · bundled one-time migration · manual load | **Bundled migration.** Re-entering 21 animals, 17 products and the 5 Sep readings by hand is how data gets entered wrong |
| Repo sync | `dump` back to git · none | **None.** The server is authoritative; the volume backup is the durability story |

## Acceptance criteria

- [x] No number appears in `SKILL.md` or any reference that is also in a data file
- [x] All eight contradictions resolved, each traceable to its resolution above
- [x] `aqua init` populates an empty data dir and refuses a populated one
- [x] `aqua status` reports reading age and flags stale data
- [x] `aqua dose` derives every dose from measured volume; no dose constant in the CLI
- [x] `aqua log` reports the prior reading and delta
- [x] Writes are atomic; a torn NDJSON tail is skipped rather than fatal
- [x] `aqua doctor` exits clean on fixtures and on `initial/`
- [x] `aqua export --format csv` and `aqua report` produce openable artefacts
- [x] `tools/skill_linter.py` still reports zero findings
- [x] Anti-drift test fails if a measurement is reintroduced into the prose
- [x] Interception allows `aqua`, injects `--data-dir`, and still blocks `aquadirector`
- [x] All 16 evals pass after re-recording
- [x] `AGENTS.md` states the deployment's backup obligation

## Verification

**Offline — 136 checks, ~2.5 s, no API key.** Dose maths, volume computation, spectator ion,
swap projection, log→read round trip, atomic write, `init` does not clobber, schema
fails-closed on newer data, staleness reporting, instrument trust, tank-alias resolution and
ambiguity refusal; schema validation of `reference.json` and the migration payload; CSV
shape; a real PNG asserted non-blank; the allow-list against fifteen injection attempts.

The one that stops the drift returning: **fail if the prose states a value attributed to a
tank, an instrument or a date**, plus any dose, volume or count. Targeting *attribution*
rather than units is what lets the skill keep saying "17.86" and "below about 4 dGH" while
refusing "staging sits at 3.5 dGH". Negative-tested both ways — nine real drifted sentences
must fail, eleven real biology statements must pass.

**Live — 16/16, $1.95 recorded.** Every case exercises the CLI in the shape it was designed
for: `dose-display` runs `dose`, `bare-sensor-paste` runs `status` then five `log` calls,
`report-on-request` runs `status` then `report`, `brevity` runs `livestock` alone.
`aqua dose` returns 2.4 mL from 24.2 gal. A cached re-run is 16/16 in **0.4 s for $0.00**.

One case-design bug, the third of its kind: `no-recall-of-stale-numbers` asserted
`runs_aqua: [status]`, and the agent used `readings nitrate --tank display` instead — a more
targeted way to answer the same question. The invariant is that it consulted the data and
gave provenance, not which verb it chose. Added `runs_any_aqua`. Its reply was exactly
right: *"0.0 ppm, measured 2026-09-05 with the Advatec test kit. That's a single reading —
no prior value logged to say whether it's rising, so I can't call it a trend yet."*

**A concurrency limit worth recording.** At `-j 6` the run died with
`HTTP 402: would exceed your available credits given your current in-flight requests`.
The key was fine and single requests succeeded — OpenRouter reserves credit for each
in-flight request's `max_tokens` up front, and six large-context requests reserve more than
a low balance can cover. `-j 2` completed the same work. Read the whole error before
concluding a key is dead.

**Cannot be verified here.** That `workspace/` survives a real `create-profile.sh` run, and
that the data appears in a real `backup.sh` tar. Both are deployment-side and belong to the
`AGENTS.md` contract.

## Found while implementing

**A ninth contradiction.** `SKILL.md` stated the display tank held "≈ 24–26 gal" and dosed
every product on "~25 gal", but its own subtraction — 29.09 gross, minus 2.1 freeboard,
minus 2.5–3.0 displacement — yields **24.0–24.5**. The upper bound was unsupported and the
dosing figure sat above the range it had just computed. `aqua` computes 24.2 gal and doses
2.4 mL. The prose was not merely duplicated; it disagreed with its own arithmetic.

**Two harness bugs the design surfaced**, both recorded in [`04`](04-access-boundary.md)'s
lineage:

1. **`pre_tool_call` hooks are one process-global list**, and Hermes invokes every callback
   in it for every tool call. One interceptor per parallel eval case meant each recorded all
   the others' commands — a green board on which `casual-trigger` reported running `dose`,
   which it never did. Replaced with a single router.
2. **Hermes dispatches tool calls off the thread that called `run_conversation`.** Routing by
   thread sent every call to the fail-safe branch: the agent saw "shell execution is
   unavailable" while the interceptor recorded nothing. `session_id` travels with the hook
   payload (`plugins.py:6640`) and is the correct key. The fail-safe is what made this
   visible — a block with no record is not a silent failure.

## Out of scope

- **Repo↔container sync.** The agent cannot write to the repo, and the server is
  authoritative. `aqua export` is for getting data out, not for round-tripping it back.
- **Rewriting `tairy-agent`.** This spec states the obligations; it does not implement them.
- **The `hermes-matrix` toolset gap** from [`04`](04-access-boundary.md).

## Open questions

1. **The cost increase is real and larger than estimated.** A case that used ~29–40k tokens
   against the prose skill now runs 48–84k: the agent opens the skill, then makes several
   CLI calls, and each result is a tool message carried for the rest of the turn. Roughly
   `$0.10` per case against `$0.06`. Whether the model respects "run `status` once, not per
   turn" is what `status-first` measures, and it remains the assumption most likely to be
   wrong.
2. **The nightly backup cron is not installed by anything.** `docs/ec2-deploy.md:297-311` is
   a copy-paste block and `scripts/install.sh:160` only prints a reminder. Until it is run,
   this data has exactly one copy on one EBS volume — the failure `tairy-agent/specs/15:266`
   names.
3. **CI never proves a `hermes-data` file survives a restore.** The canary is a Postgres
   row; `hermes-data.tar.gz` is only asserted non-empty. A canary file under `workspace/`
   would close it.
4. **`hermes-data` is skipped entirely if the container is down** (`backup.sh:102`), unlike
   the other volumes which are read from the volume directly. An asymmetry worth knowing
   before an incident.
5. **`tairy-agent/docs/storage.md:85-93` is factually stale** about backup coverage and will
   mislead whoever reasons about this next.
