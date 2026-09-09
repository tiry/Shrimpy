# log-a-reading — PASS

| | |
|---|---|
| Outcome | **PASS** |
| Model | `google/gemini-3.8-flash` |
| Tokens | 45,033 |
| Cost | $0.0243 |
| Wall | 10.3s |
| Skills opened | aquarium-supervisor |
| CLI calls | 2 |
| Blocked commands | 0 |

## Why this case exists

SKILL.md: "Tiry telling you a number is the only way a number gets in. Log it." An unlogged reading cannot be plotted and is gone next week. This is the write half of the design and the easiest half to silently skip.

## Verdict

- every assertion held

<details><summary>What was asserted</summary>

```json
{
  "opens_skills": [
    "aquarium-supervisor"
  ],
  "runs_aqua": [
    "log"
  ]
}
```

Rubric:

> The reply must confirm the reading was recorded, and should relate it to the previous value (6.86) rather than treating it as an isolated fact. Merely commenting on the number without logging it is a FAIL.

</details>

## Judge

```text
PASS
The assistant explicitly logged the new reading and compared it directly to the previous value of 6.86.
```

## Conversation

### Turn 1 · user

```text
Just tested the display tank - pH is 6.94 on the probe.
```

### Turn 2 · assistant

**calls `skill_view`**

```json
{
  "name": "aquarium"
}
```

### Turn 3 · tool result

`skill_view`

```text
{"success": false, "error": "Skill 'aquarium' not found.", "available_skills": ["aquarium-supervisor"], "hint": "Use skills_list to see all available skills"}
```

### Turn 4 · assistant

**calls `skill_view`**

```json
{
  "name": "aquarium-supervisor"
}
```

### Turn 5 · tool result

<details><summary><code>skill_view</code> returned 15.6 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "description": "Tiry's aquariums: shrimp, guppies, water chemistry, alerts", "tags": ["aquarium", "shrimp", "neocaridina", "guppies", "water-chemistry", "aquadirector"], "related_skills": [], "content": "---\nname: aquarium-supervisor\ndescription: \"Tiry's aquariums: shrimp, guppies, water chemistry, alerts\"\nversion: 2.0.0\nauthor: tairy-agent\nlicense: MIT\nplatforms: [linux, macos, windows]\nmetadata:\n  hermes:\n    tags: [aquarium, shrimp, neocaridina, guppies, water-chemistry, aquadirector]\n---\n\n# Aquarium Supervisor\n\nTwo tanks, one keeper (Tiry). **The facts live in a database, not in this file.**\nThis file is the rules for reading and acting on them.\n\n## When to Use\n\nLoad this for **anything** touching Tiry's aquariums — the tanks, the animals, the\nwater, the products, or the sensor. Casual phrasing counts: \"my shrimp look\nweird\", \"is 6.6 too low\", \"lost a guppy overnight\". A bare paste of sensor output\nwith no question attached counts. So does a question from someone else in the\nhousehold who does not know the setup.\n\nThree things to settle before answering anything specific:\n\n1. **Which tank.** They differ about sixfold in volume; a dose or a stocking\n   judgment right for one is badly wrong for the other. `aqua` refuses to guess.\n2. **Is the number measured, and when.** You cannot read the sensor yourself.\n3. **Is it drifting, or merely not the textbook number.** Only drift justifies\n   action.\n\nDo **not** use this for general aquarium questions unconnected to these two\ntanks — answer those from ordinary knowledge, without pretending the specifics\nhere apply.\n\n---\n\n## The `aqua` CLI — run this first\n\nThe CLI lives at `/tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py`. **Run each command on its\nown, exactly as written below.** Do not set a shell variable for the path, and do\nnot chain commands with `;` or `&&` — one invocation per terminal call.\n\n​```\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py status\n​```\n\n**Start every aquarium conversation with that.** It is one call and it returns the\nwhole picture: volumes, rosters, the latest reading of every metric with its age\nand trend, anything outside target, and the open questions. Do it once per\nconversation, not once per turn.\n\nThis replaces the \"never re-ask what is here\" rule. Nothing about these tanks is\nin your head or in this file — it is in the data, and it is current. Reciting a\nnumber from memory is the failure this design exists to prevent.\n\n### Reading\n\n​```\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py status --tank staging\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py tanks\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock --tank display\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory --class never\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py readings ph --tank display\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py dose prime --tank staging\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py check\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py questions\n​```\n\n### Writing — record what you are told\n\nTiry telling you a number is the only way a number gets in. **Log it.** An\nunlogged reading is one nobody can plot and one you will not have next week.\n\n​```\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py log ph 6.91 --tank display --instrument kactoily\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py log gh 75 --tank staging --instrument hi735 --note \"after first swap\"\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py log phosphate 0.25 --tank display --instrument advatec --min 0 --max 0.25\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py event water-change --tank staging --detail \"15% with display water\"\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock-change remove --id staging-neocaridina --count 1\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory-change open prime\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py question answer --id 4 --text \"6 female, 3 male\"\n​```\n\nUse `--min` and `--max` when the reading was a band rather than a point — a colour\nchart between two swatches is a band, and flattening it invents precision.\n\n`--instrument` matters. Some instruments are not trusted for some metrics — the\nstrip pH pad reads demonstrably low, the liquid kit's pH is unreliable under warm\nlight — and `aqua` will say so and keep those readings out of the trend while\nstill recording them.\n\n### Reporting\n\n​```\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py export --format csv\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py plot ph --tank display\npython3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py report\n​```\n\nTell Tiry the path it prints. Offer a report when a trend question comes up, not\nreflexively.\n\n### Rules for using it\n\n- **Never state a number you did not just read from `aqua` or from Tiry in this\n  conversation.** If you are unsure whether it is current, run `status` again.\n- **Never compute a dose yourself.** `aqua dose` derives it from measured volume\n  and shows its basis. Every historic dosing error here came from arithmetic done\n  in prose.\n- **`status` tells you how stale the data is.** If it says the newest reading is\n  weeks old, say so before answering, not after.\n- If a command fails or the data looks wrong, run `doctor`.\n\n---\n\n## You cannot see or touch the tanks\n\nYou run in the cloud. The Kactoily sensor, the `aquadirector` CLI and the Eheim\nfeeder are all on Tiry's LAN and unreachable from where you execute. Having a\nterminal does not change that — the tool is not installed here and the sensor is\nnot routable.\n\nThe `aqua` CLI above is different: it is part of this skill, it runs where you\nrun, and it reads a database, not a tank.\n\nSo:\n\n- **Never run, or offer to run, an `aquadirector` command.** Ask Tiry to run it\n  and paste the output — then log what he pastes.\n- **Never claim to have checked anything.**\n- Name the exact command you want. `aquadirector sensor status` is a five-second\n  favour; \"can you check the tank?\" is a chore.\n\nCommands to **ask for**, not to run:\n\n​```\naquadirector dashboard --output json          # the most useful paste: every field, no transcription\naquadirector sensor status [--watch 30s]      # Kactoily 7-in-1\naquadirector feeder status | feed             # Eheim autofeeder+\naquadirector feeder schedule clear --day tue  # a fasting day\naquadirector alerts check --notify\n​```\n\nThe Kactoily also reports to the **SmartLife** app (Tuya), which has a History\nview. A screenshot of it is often the fastest way to answer \"is this drifting?\",\nand Tiry can send one from a phone.\n\n**The tool is reef-oriented.** Its salinity and SG readings carry no information\nin freshwater. Ignore them.\n\n### Handling pasted sensor output\n\nThis is the main way you see the tanks, so treat a paste as the event it is.\n\n**Which tank a paste belongs to.** The Kactoily probe lives in one tank —\n`aqua tanks` says which. A bare paste of sensor output is from that tank unless\nTiry says otherwise. He does sometimes drop the probe into the other tank to\ntrack a swap, and will say so when he does. Do not stall a paste to ask; log it,\nand say which tank you logged it against so a correction is one line.\n\n1. **Log it.** Every value, with `--instrument` and `--at` if the paste carries a\n   timestamp. Do this before commenting on it.\n2. `aqua` gives you the prior value and the delta for each. Name only what moved.\n3. Run `check` for the target comparison rather than eyeballing it.\n4. **A paste has no timestamp unless Tiry gives one.** If the reading is doing\n   real work in your answer, ask when it was taken — planted tanks swing pH\n   through the photoperiod, so the hour matters as much as the number.\n5. One reading is not a trend. `aqua` will tell you when there isn't one yet.\n\n\n---\n\n## Decision rules\n\n**Stability beats optimization.** Ask whether a reading is *drifting* or merely\n*not the textbook number*. Only drift justifies action. A parameter that is stable\nand slightly off target is healthier than one being actively corrected.\n\n**Rules have scope, and the scope is per tank.** A caution that is right for one\ntank is not a general law. The clearest example: crushed coral. The display tank\nis near its pH target and climbing on its own, so more media there risks\novershooting something the existing coral will reach unaided. The staging tank is\nbelow target on both GH and KH and undersupplied with media — there, adding coral\nis correct. Check `aqua status` before applying either.\n\n**Aragonite dissolution is self-limiting.** The rate falls as pH rises and\neffectively stalls around 7.2–7.5, so coral is a buffer that stops working once it\nis no longer needed. Overshoot is not a realistic failure mode; undersupply is.\n\n**Prefer the cheap check first, and the mechanical fix over the chemical one.**\nMove the probe rather than spend a reagent. Remove the uneaten food rather than\ndose something. Reach for a bottle last.\n\n**Telemetry is not the tank.** Plenty of questions are answered by looking at the\nanimal. A sucker's belly against the glass says more about whether it is eating\nthan any parameter will. Say \"go look\" when looking is the answer.\n\n**ORP does not tell you whether there is ammonia.** Tiry has been told otherwise.\nIt is not reliable and must not substitute for an ammonia test:\n\n- ORP measures net redox potential, which in an aerated tank is dominated by\n  dissolved oxygen. An open lid, surface fans and heavy agitation pin it high more\n  or less regardless of what else is dissolved.\n- Ammonia at spike concentrations is a trace reductant, easily swamped in a mixed\n  electrode potential.\n- The probe is uncalibrated for ORP, and ORP electrodes drift over months.\n- A tank can carry 1 ppm ammonia at 440 mV.\n\nHigh ORP is genuinely reassuring about *gross organic load* — nothing large is\nrotting — which is a different question from whether the biofilter is keeping up.\nAmmonia is measurable now; measure it.\n\n**Never invent a number, and never round one into a decision.** `aqua` reports\nbands as bands (`0.00-0.25`) and marks estimated volumes as estimated. Carry that\nthrough instead of flattening it.\n\n---\n\n## Water changes\n\nThe current regime is distilled top-off only, no water changes, in either tank —\ncheck `aqua tanks` for what is actually recorded.\n\nTop-off with 0 TDS water is correct and should continue: it replaces evaporated\nwater without adding minerals. But it is not maintenance. **Evaporation removes\nnothing.** Nitrate, phosphate, dissolved organics, potassium and sodium have no\nexport path except plant uptake.\n\n- **Start weekly changes as habit rather than rescue**, sized to the tank. The\n  staging tank's stocking makes this more urgent than the display's.\n- **Matched water, not pure.** A pure-distilled change drops GH and KH by the same\n  fraction as the volume replaced, in one step — the rapid osmotic move that\n  triggers emergency molts. Match within about 1 °C and 20 ppm TDS.\n- **Display-tank water is the best source for the staging tank**: harder,\n  temperature-matched, biologically clean, free, and it converges the two tanks,\n  which is needed before any transfer regardless.\n- **A rapid GH *rise* is its own osmotic event.** Walk it up over days.\n- Tap water is unmeasured. If it tests close to the display tank on the Hanna\n  checkers, dechlorinated tap is simplest. Otherwise remineralize distilled.\n\nRaise this once when relevant, then treat it as a known choice.\n\n---\n\n## Routine\n\n### Feeding\n- **Guppies:** once daily, a pinch, gone in 30–60 s. Verify against consumption,\n  not the schedule.\n- **Sucker and display shrimp:** every 2–3 days at lights-out, half a sinking\n  spirulina or herbivore wafer. Siphon the remainder after 2–3 hours.\n- **Staging tank:** mystery snails take sinking vegetable pellets, blanched\n  zucchini or spinach. Nerites need biofilm and refuse prepared food — the tank is\n  planted, so there is grazing surface, but a young setup carries thin biofilm.\n  Judge by animal condition. **Uneaten food matters far more here** — four gallons\n  has almost no buffer. Remove it.\n- **One fast day per week.** Tiry clears it on the feeder.\n\n### Maintenance\n- Rinse the mechanical sponge in **discarded tank water only**, never tap.\n- Replace 50% of the crushed coral every 6–9 months. `aqua tanks` carries the\n  install dates and computes when.\n- Test GH and KH monthly on the Hanna checkers, in **both** tanks, same session —\n  and log both.\n\n### Acclimation (staging → display)\n1. Confirm both tanks read close on GH, KH and pH — `aqua check` and\n   `aqua readings gh` for each. That match is the whole point of the staging tank.\n2. Float 15–20 min for temperature.\n3. Drip or ladle ¼ cup receiving-tank water every 5–10 min over 45–60 min until\n   the holding volume triples.\n4. Net or hand-transfer. **Discard all transit water.**\n5. Place nerites right-side up on rock, wood or glass.\n6. **Before moving any snail into the display tank, seal its lid gaps and confirm\n   at least an inch of headspace.** Those requirements travel with the snails.\n7. `aqua livestock-change move` afterwards, so the rosters stay true.\n\n---\n\n## When something is wrong\n\n`references/triage.md` first for any sick, dying or dead animal or out-of-range\nreading. `references/chemistry.md` for the mechanisms behind the numbers.\n`references/livestock.md` for anything species-specific.\n`references/products.md` for why a product is or is not usable here.\n\nRead them for *reasoning*. Read `aqua` for *values*.\n", "path": "aquarium/aquarium-supervisor/SKILL.md", "skill_dir": "/tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor", "org_provenance": null, "linked_files": {"references": ["references/triage.md", "references/livestock.md", "references/chemistry.md", "references/products.md"], "assets": ["assets/reference.json", "assets/initial/readings.ndjson", "assets/initial/livestock.json", "assets/initial/inventory.json", "assets/initial/events.ndjson", "assets/initial/questions.json", "assets/initial/tanks.json"], "scripts": ["scripts/_store.py", "scripts/aqua.py", "scripts/_calc.py", "scripts/_report.py"]}, "usage_hint": "To view linked files, call skill_view(name, file_path) where file_path is e.g. 'references/api.md' or 'assets/config.yaml'", "required_environment_variables": [], "required_commands": [], "missing_required_environment_variables": [], "missing_credential_files": [], "missing_required_commands": [], "setup_needed": false, "setup_skipped": false, "readiness_status": "available", "_source_path": "/tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/SKILL.md", "metadata": {"hermes": {"tags": ["aquarium", "shrimp", "neocaridina", "guppies", "water-chemistry", "aquadirector"]}}}
```

</details>

### Turn 6 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py status"
}
```

### Turn 7 · tool result

<details><summary><code>terminal</code> returned 10.3 KB</summary>

```text
{"output": "== Display tank (display)\n   24.2 gal water (computed) · 9x Neocaridina shrimp, 9x Fancy guppy, 1x Suckermouth catfish\n   pH           6.86  (smartlife, 3 days ago)\n   Temperature  24.5 C  (smartlife, 3 days ago)\n   TDS          255 ppm  (smartlife, 3 days ago)\n   EC           510 uS/cm  (smartlife, 3 days ago)\n   ORP          440 mV  (smartlife, 3 days ago)\n   GH           161 ppm  (hi735, 4 days ago)\n   KH           46 ppm  (hi775, 4 days ago)\n   Ammonia      0.00 ppm  (advatec, 3 days ago)\n   Nitrite      0.00 ppm  (advatec, 3 days ago)\n   Nitrate      0.0 ppm  (advatec, 3 days ago)\n   Phosphate    0.00-0.25 ppm  (advatec, 3 days ago)\n   Free Cl2     0.00 ppm  (bacnunn, 3 days ago)\n   Copper       0.00 ppm  (bacnunn, 3 days ago)\n   Iron         0.00 ppm  (bacnunn, 3 days ago)\n   prior bands (pre-log, no timestamps): pH 6.77-6.87, Temperature 23.8-24.3, TDS 247-254, EC 494-509, ORP 377-440\n\n== Staging / quarantine tank (staging)\n   4.0 gal water (computed) · 3x Albino mystery snail, 3x Red Racer nerite, 9x Neocaridina shrimp\n   GH           62 ppm  (hi735, 4 days ago)\n   KH           22 ppm  (hi775, 4 days ago)\n   Ammonia      0.00 ppm  (advatec, 3 days ago)\n   Nitrite      0.00 ppm  (advatec, 3 days ago)\n   Nitrate      0.0 ppm  (advatec, 3 days ago)\n   Phosphate    0.25 ppm  (advatec, 3 days ago)\n   Free Cl2     0.00 ppm  (bacnunn, 3 days ago)\n   Copper       0.00 ppm  (bacnunn, 3 days ago)\n   Iron         0.00 ppm  (bacnunn, 3 days ago)\n   !! GH 62.0 is below target 105 — also needs to converge on the display tank before any transfer\n   !! KH 22.0 is below target 35\n\nOpen questions (7):\n   2. Tap water GH, KH and TDS - untested, so change-water preparation cannot be specified.\n   3. Substrate depth in the display tank, to firm up the ~25 gal estimate.\n   4. Guppy sex ratio - if mixed, expect fry and a compounding bioload.\n   5. Is the suckermouth an Otocinclus or a juvenile pleco? A common pleco would outgrow the tank.\n   6. Is the Eheim autofeeder in use, and on what schedule?\n   7. How long have the staging animals been in quarantine, and what is the plan for moving them out?\n   8. Plant species in the staging tank and how established they are - it determines how much grazing surface the nerites and shrimp actually have.", "exit_code": 0, "error": null}

[Subdirectory context discovered: work/Shrimpy/Shrimpy/AGENTS.md]
# AGENTS.md

Working notes for this repository. Read this before changing anything here.

## What this repo is

The source of truth for **Shrimpy**, an aquarium keeper's assistant built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent) — the persona, the skills, and
a harness for running and testing them locally with nothing else attached.

It is *not* a deployment. No Matrix, no Synapse, no Hindsight, no Caddy, no
docker-compose. [`../tairy-agent`](../tairy-agent) deploys what is defined here.

## Layout is a contract

​```
SOUL.md  DISPLAYNAME  avatar.png  skills/
​```

at the repo root, because that is exactly what `tairy-agent/scripts/create-profile.sh`
copies out of a `profiles/<name>/` directory. This repo can therefore be dropped in as one.
`tests/test_profile_layout.py` fails if it drifts.

Everything else — `harness/`, `evals/`, `tests/`, `scripts/`, `specs/`, `vendor/` — is
tooling the deployment ignores.

## Commands

​```bash
./shrimpy setup      # uv, .venv, hermes-agent (once, a few minutes)
./shrimpy test       # offline checks — no API key, no cost, ~1s. Run this constantly.
./shrimpy prompt     # the assembled system prompt; --skills for just the index
./shrimpy ask "..."  # one question; -v shows skills opened, tools, tokens, cost
./shrimpy chat       # interactive REPL as Shrimpy
./shrimpy eval       # behavioural evals — cached; --live to re-record
./shrimpy snapshots  # inspect or clear the eval cache
​```

CI (`.github/workflows/ci.yml`) runs `ruff`, the skill's CLI on Python 3.11-3.13
without hermes-agent installed, and `./shrimpy test` on every push. The
behavioural evals run **monthly and on demand**, never on `pull_request` — a
secret must not be exposed to whatever code a PR contains. Run them locally
before changing `SOUL.md` or a skill; snapshots make a re-run free until the
definition actually changes.

**Read the transcript before touching the skill.** Every eval run renders one to
`.work/transcripts/`, and live CI runs publish to the `eval-transcripts` branch. Three
times the case was wrong and the agent was right; the reply is where that shows.

**A live eval failure is not automatically your bug.** The runner exits 1 when
the agent misbehaved and **3** when the provider was unreachable, and CI reports
those differently. Do not "fix" a 402.

**Pick the eval model to match the deployment, not to save money.**
`gemini-2.5-flash` is 7x cheaper than the current default and fails three cases
on safety-relevant rules; as a judge it passes replies that should fail. The
current choice was measured — see the table in `README.md`.

## Specs

Planned and completed work lives in [`specs/`](specs/README.md), numbered in execution
order, same convention as `tairy-agent/specs`. Declarative: problem, reasoning, tradeoffs,
acceptance criteria — no ready-to-paste diffs. Every factual claim carries a `file:line`
citation.

**Write the spec before the code** for anything that changes what the agent is. The
retroactive specs `01`–`05` exist because the reasoning was worth keeping; do not add more
of those.

## Things that will bite you

**Two ways a skill vanishes with no error.** A `description` over 60 characters is truncated
in the index (`SKILL_PROMPT_DESC_LIMIT`). A description containing an unquoted `": "` is
invalid YAML, `platforms` parses as a string, and **the skill is dropped from the index
entirely** — while still parsing, and logging nothing. Both are covered by `./shrimpy test`.
See [`specs/02`](specs/02-offline-skill-checks.md).

**`--safe-mode` and `--ignore-rules` silently drop `SOUL.md`** and substitute a generic
identity (`agent/system_prompt.py:472-487`). Never use them in the harness.

**The skill index is empty without a skills tool in the toolset**
(`agent/system_prompt.py:619`).

**`HERMES_HOME` must be set before `import run_agent`** — that module binds it at import
time (`run_agent.py:127-129`).

**When an eval fails, read the reply before touching the skill.** Twice now the harness was
wrong and the agent was right: it named `3.2 mL` *in order to correct it*, and scoped a
caution with a sentence containing "do not add". Forbidding a substring forbids the right
answer too. Use a rubric judge for semantic properties.

**Skill content is input to the harness.** `skills_opened` once scanned tool responses for
`"not found"`; `SKILL.md` §7 contains the phrase `command not found`, so a documentation
edit broke eight of twelve evals. Parse the envelope, never the body.

**Hook and middleware dispatch is fail-open.** An exception in a `pre_tool_call` hook is
swallowed into a debug log. Anything registered there must record, never raise.

**`pre_tool_call` hooks are one process-global list**, and Hermes invokes every callback in
it for every tool call. Registering one per parallel eval case made each record all the
others' commands. `harness/interception.py` installs a single router instead.

**Hermes dispatches tool calls off the thread that called `run_conversation`.** Scope
anything per-run by `session_id`, which travels with the hook payload
(`hermes_cli/plugins.py:6640`), never by thread.

**`./shrimpy eval -j 6` can 402 on a healthy key.** OpenRouter reserves credit for each
in-flight request's `max_tokens`, so several large-context requests in parallel can exceed a
low balance while any one of them succeeds. The error says so — *"given your current
in-flight requests"*. Drop to `-j 2` before concluding the key is dead.

**The skill's facts are in a database, not in the prose.** `tests/test_no_drift.py` fails if
a value attributed to a tank, an instrument or a date reappears in `SKILL.md` or a
reference. That guard is what stops the eight documented contradictions coming back — do not
weaken it to land a sentence.

## Consuming this repo

Read this if you are wiring `tairy-agent` — or any deployment — to this repository.

### What you get

The four root paths above. `create-profile.sh` already handles them; nothing changes.

### What you must provide — live data durability

> **Status: required NOW. [`specs/06`](specs/06-live-data-and-reporting.md) has landed —
> the skill ships a CLI that writes live data, and that data exists nowhere but the volume.**

The skill ships a CLI (`skills/aquarium/aquarium-supervisor/scripts/aqua.py`) that reads and
writes live data — measurements, livestock, supplies — at:

​```
${HERMES_HOME}/workspace/aquarium/
​```

That directory is protected from every code path in both repos: it is in `_PROFILE_DIRS`,
in `USER_OWNED_EXCLUDE`, in the distribution hard-exclude list, and chowned at container
boot. `create-profile.sh` scopes its `rm -rf` to `skills/` and does not touch it.

**But it will be the only copy of that data.** It is not in git, and it cannot be, because
the agent writes it and the agent cannot write to a repo. Four consequences:

1. **The nightly backup cron must actually be installed.** Nothing installs it —
   `docs/ec2-deploy.md:297-311` is a copy-paste block and `scripts/install.sh:160` only
   *prints* a reminder. Until it runs, this data has one copy on one EBS volume, which is
   the failure `specs/15:266` names: *"a backup on the same disk as the data survives a bad
   `docker volume rm` but not a dead EBS volume."*

2. **CI must gain a canary file under `workspace/`.** Today the backup/restore round trip in
   `.github/workflows/docker-smoke-test.yml` asserts a **Postgres row** survives, and only
   checks that `hermes-data.tar.gz` is non-empty. No file inside it is ever asserted to
   round-trip. A canary written before the wipe and read after the restore closes that.

3. **`create-profile.sh` must keep its `rm -rf` scoped to `skills/`.** Widening it to the
   profile home, or adding `workspace/` to what it replaces, destroys the data on every
   provision — and `bootstrap.sh` and `update.sh` both call it.

4. **`wipe.sh --yes` and `restore.sh --yes` destroy it.** They are the only two paths that
   reach it. `restore.sh` is the subtle one: restoring a b

[...truncated AGENTS.md: 8,847 chars total]
```

</details>

### Turn 8 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/scripts/aqua.py log ph 6.94 --tank display --instrument kactoily"
}
```

### Turn 9 · tool result

`terminal`

```text
{"output": "logged pH 6.94 for display at 2026-09-09T03:40 (kactoily)\n  prior 6.86 (2026-09-05T16:43), Δ+0.08 over 3 days\n  inside target 6.8-7.4", "exit_code": 0, "error": null}
```

### Turn 10 · assistant

```text
Logged 6.94 for the display tank (Kactoily).

Up +0.08 from 6.86 three days ago, sitting comfortably inside the 6.8–7.4 target. Aragonite dissolution in the crushed coral slows as it approaches 7.2–7.5, so this upward creep is expected and self-limiting. No action needed.
```
