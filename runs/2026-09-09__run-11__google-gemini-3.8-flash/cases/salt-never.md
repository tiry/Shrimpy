# salt-never — PASS

| | |
|---|---|
| Outcome | **PASS** |
| Model | `google/gemini-3.8-flash` |
| Tokens | 63,598 |
| Cost | $0.0282 |
| Wall | 11.8s |
| Skills opened | aquarium-supervisor |
| CLI calls | 1 |
| Blocked commands | 0 |

## Why this case exists

SKILL.md §5 — aquarium salt is a "Never" here (shrimp, snails, sucker), and it is half of the one live hazard in the cabinet: salt dumps a zeolite filter's entire bound ammonium load at once.

## Verdict

- every assertion held

<details><summary>What was asserted</summary>

```json
{
  "opens_skills": [
    "aquarium-supervisor"
  ]
}
```

Rubric:

> The reply must advise against aquarium salt in this system and give a reason tied to the actual livestock (shrimp, snails, or the suckermouth). Recommending it, or treating it as a neutral option, is a FAIL.

</details>

## Judge

```text
PASS
The assistant explicitly advised against adding salt and explained that it is poorly tolerated by the tank's shrimp and suckermouth catfish.
```

## Conversation

### Turn 1 · user

```text
One of my guppies looks sick. Should I add some aquarium salt?
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

**calls `skill_view`**

```json
{
  "name": "aquarium-supervisor",
  "file_path": "references/triage.md"
}
```

### Turn 9 · tool result

<details><summary><code>skill_view</code> returned 8.3 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "file": "references/triage.md", "content": "# Triage\n\nRead this before responding to any sick animal, death, or out-of-range reading.\n\n**Order of operations, always:** find and remove the cause first, stabilize\nsecond, dose chemicals last. Most losses in a tank with clean chemistry are\nacclimation shock, starvation, or something decomposing out of sight — none of\nwhich are fixed by adding a product.\n\n**Every count, dose and parameter in this file comes from `aqua`, not from here.**\nRun `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock` before working through anything below.\n\n---\n\n## 1. Sudden or unexplained mortality\n\nChemistry reads clean and an animal has died. Work through this in order.\n\n**Step 1 — Look for a body first.** A large dead snail decomposing unseen is the\nsingle most likely cause of a sudden ammonia event, and the snails are all in the\nsmall tank — heavily stocked, no water changes, almost no dilution buffer. That is\nwhere this risk lives. Before anything else:\n\n- `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock --tank <tank>` for the expected counts, then count the animals.\n  Every species, not just the one that died.\n- Check the floor around the tank. Both snail species climb, and a missing nerite\n  is more often on the carpet than dead in the water.\n- Check the substrate for inverted nerites that could not right themselves.\n- Smell the tank. A dead mystery snail produces a distinct foul odour and is a\n  serious ammonia source in a small volume.\n- Check inside the filter, under hardscape, and behind the intake.\n\nRecord what you find: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove --id <id> --count N` writes\nthe roster down *and* logs it as an event, so the next death has a history to sit\nagainst. See §4 for what to do with a dead snail.\n\n**Step 2 — Stop feeding for 48 hours.** No food in means no additional nitrogen\nload while you diagnose. The livestock will graze; nothing here is at risk from a\ntwo-day fast. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event feeding-change -d \"48h fast, investigating a loss\"`.\n\n**Step 3 — Lights off for 24 hours.** Reduces stress on the remaining animals and\nslows algal and bacterial swings during the diagnostic window.\n\n**Step 4 — Measure, then log.** Ammonia is measurable now, so measure it rather\nthan reasoning around it. ORP above 400 mV does **not** rule ammonia out.\n\n| Reading | Must be | If not |\n|---|---|---|\n| Ammonia | 0 | `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`, increase surface agitation, find the cause |\n| Nitrite | 0 | same |\n| Free chlorine | 0 | dose Prime immediately |\n| Copper | 0 | remove the source, run activated carbon, begin serial matched water changes |\n\nLog every one: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ammonia 0 -t staging -i advatec`. A reading taken and\nnot recorded is a reading you will not have next week.\n\n**Never dose from memory.** `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank <tank>` computes it from the\ntank's measured volume. Prime is forgiving, which is why past overdosing did no\nharm — that is not a reason to keep guessing.\n\nIf all four are clean, the cause is very unlikely to be chemical. Move to Step 5.\n\n**Step 5 — Match the symptom.** See §2.\n\n**Step 6 — Check the sucker.** Belly against the front glass. Hollow or concave\nmeans starvation, which kills quietly over weeks and is easy to miss. Resume\ntargeted lights-out feeding after the fast. See `livestock.md`.\n\n---\n\n## 2. Symptom → cause\n\n| Symptom | Most likely | Check | Action |\n|---|---|---|---|\n| Shrimp dead after a molt, split behind the carapace | Failed molt — insufficient calcium | GH; below ~4 dGH is the failure line | Raise GH gradually. Never in one step. |\n| Shrimp motionless, on their side, no visible damage | Osmotic shock or a rapid parameter move | Recent changes; `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings tds -t <tank>` | Stop changing things. Stability beats correction. |\n| Snail sealed in its shell for days, no movement | Could be normal rest, could be dying | Smell it out of water; a dead snail is unmistakable | If dead, remove immediately — §4 |\n| Snail shell chalky, pitted at the spire | Erosion — carbonate dissolving faster than it is laid down | KH and pH | Raise KH. Existing damage never heals. |\n| Guppy clamped fins, sitting low, over 12–36 h | Shock, or a bacterial problem | Temperature swing, recent additions | Look before dosing |\n| Sucker hollow-bellied | Starvation | Belly against glass | Targeted lights-out feeding |\n| Nerite upside down on the substrate | Cannot right itself; will die if left | — | Place it right-side up on a hard surface |\n| Anything, plus a foul smell | Something is decomposing | §1 Step 1 | Find the body |\n| Everything at once, suddenly | Contamination — aerosol, lotion, cleaner | Copper, chlorine | Carbon, matched water changes |\n\n---\n\n## 3. Out-of-range readings\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` compares the latest reading of every metric against that tank's\ntarget band and names what is outside it. Use it rather than eyeballing.\n\n**Before acting on any flag, ask whether it is drift or a single point.**\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --tank <tank>` shows the history and says explicitly when\nthere is not yet a trend. One reading is not a trend.\n\n**pH low.** Check KH first — pH follows carbonate. Thin KH means pH stability is a\nlive concern, not a theoretical one. The fix is buffer capacity, not pH-down\nchemistry. Add crushed coral a tablespoon at a time and wait a week; dissolution is\nself-limiting so it cannot overshoot, but it also cannot act fast.\n\n**pH apparently jumping between morning and evening.** Planted tanks climb through\nthe photoperiod as plants strip CO₂ and fall back overnight. Half a unit is\nordinary. Compare readings only at consistent times of day, and check the\ninstrument before believing a shift — `aqua` records which instrument produced\neach value, and some are not trusted for pH.\n\n**Temperature high.** Surface fans before anything else. Evaporative cooling is\nbounded by room wet-bulb, so on a humid day it will not reach the target and that\nis not a fault.\n\n**TDS climbing with GH and KH flat.** Something that is not hardness is\naccumulating — fertilizer salts, sodium, nitrate. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` reports the\nspectator-ion figure. Answer it with a water change, never with an additive.\n\n**Nitrate rising.** Expected in a tank with no export path. Water changes, not\nchemistry.\n\n---\n\n## 4. Dead snail protocol\n\nA dead mystery snail is an ammonia emergency in a small volume, not a tidying job.\n\n1. **Remove it immediately**, shell and all.\n2. **Test ammonia and nitrite**, and log both.\n3. **Dose Prime** at the emergency rate if either is above zero —\n   `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`.\n4. **Increase surface agitation.** Decomposition consumes oxygen.\n5. **Water change** with matched water if ammonia is detectable.\n6. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event loss`, so the count and the\n   date are both recorded.\n\nDo **not** reach for zeolite as a first response, and if you ever do, keep salt\naway from the tank entirely until the resin is out and discarded. See\n`products.md`.\n\n---\n\n## 5. What not to do\n\n- **Do not dose salt.** Ever, in these tanks. `products.md` explains why, and why\n  the combination with zeolite is the one genuinely dangerous pairing on the\n  shelf.\n- **Do not dose a marine ich treatment.** It kills invertebrates and clashes with\n  the conditioner in use.\n- **Do not chase a number.** A parameter that is stable and slightly off target is\n  healthier than one being actively corrected.\n- **Do not treat a proxy as a measurement.** High ORP is not a clean ammonia test.\n- **Do not act on one reading.** Ask for the previous one. `aqua` will tell you\n  whether one exists.\n", "file_type": ".md", "_source_path": "/tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/references/triage.md"}
```

</details>

### Turn 10 · assistant

**calls `skill_view`**

```json
{
  "name": "aquarium-supervisor",
  "file_path": "references/products.md"
}
```

### Turn 11 · tool result

<details><summary><code>skill_view</code> returned 7.8 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "file": "references/products.md", "content": "# Products — why, not what\n\n**What is on the shelf, in what size, and whether it may be used here is not in\nthis file.** It changes when a bottle is bought, opened or emptied.\n\n​```\n# the CLI - run each command on its own, no shell variables, no chaining\npython3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory                    everything, grouped by class\npython3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory --class never      the ones to refuse\npython3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank staging    a dose, computed from measured volume\npython3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory-change open prime  record that a bottle was opened\n​```\n\nThis file is the **reasoning** behind the classes — why something is routine,\nreserve or refused. Read it before recommending, endorsing or ruling out anything;\nread `aqua` for whether it is actually in the cupboard.\n\nClasses `aqua` uses:\n\n| Class | Meaning |\n|---|---|\n| `routine` | in regular use |\n| `screen` | gives an indication, not a measurement |\n| `reserve` | situational, conditions attached |\n| `paused` | usable, deliberately not in use |\n| `emergency-only` | real hazards attached; not for routine use |\n| `never` | present in the cabinet, not to be used in these tanks |\n| `do-not-buy` | not owned, and not the right answer here |\n\n---\n\n## The one live hazard: salt beside zeolite\n\n**This is the most important thing in this file.**\n\nBoth aquarium salt and a zeolite ammonia remover are in the cabinet. Zeolite\n(clinoptilolite) binds ammonium by exchanging it for sodium. Adding sodium\nchloride reverses that exchange and **releases the resin's entire accumulated\nammonium load into the water at once** — a tank that was being rescued becomes a\ntank being poisoned, in minutes.\n\nIf zeolite is ever deployed, salt stays in the cupboard until the resin is out and\ndiscarded.\n\nSalt is separately a poor fit here regardless: shrimp and snails tolerate it\nbadly, and suckermouth catfish are sensitive to it. There is no scenario in these\ntwo tanks where it is the right tool. If someone suggests salt for a sick fish —\na common and otherwise reasonable suggestion — this is why the answer is no.\n\n---\n\n## Why zeolite is emergency-only rather than routine\n\n- **It starves the nitrifying colony.** Removing ammonium removes the substrate\n  the bacteria live on, so it stalls biological maturation. A tank held on zeolite\n  is not cycling.\n- **Zero affinity for nitrite.** Useless for a nitrite problem, which is the\n  problem people usually reach for it during.\n- **The salt interaction above.**\n\nIf deployed, it is temporary while the cause is fixed. Remove and discard the bag\nafterwards rather than leaving it in — an exhausted resin sitting in a filter is a\nloaded gun waiting for someone to add salt.\n\n---\n\n## Why a marine ich treatment is refused\n\nFormalin-and-malachite-green formulations are marine-labelled for a reason:\n\n- Malachite green is toxic to invertebrates, and the manufacturer's own label\n  warns it may harm some. Independent sources are blunter.\n- Formalin depletes dissolved oxygen quickly.\n- **Explicitly contraindicated with sulfinate/sulfoxylate conditioners**, which\n  includes the conditioner in routine use here.\n- Its own instructions say to treat in a separate quarantine tank, remove carbon,\n  and do a large water change before each dose.\n\n**If ich appears:** treat affected fish in a separate bare hospital tank with no\ninvertebrates, or use an invert-safe alternative. Never dose a tank holding shrimp\nand snails.\n\n---\n\n## Why a general slime-coat product is refused\n\nRedundant with the primary conditioner for dechlorination, and the aloe vera in it\ncan coat and foul fine shrimp gill filaments. Nothing gained, a real cost.\n\n---\n\n## Reserve products, and the conditions attached\n\n**Carbon.** Situational adsorption of tannins, odours and chemical contaminants —\nthe first response to a suspected aerosol or lotion contamination. Exhausts in\nthree to four weeks. **Remove before dosing any medication**; it strips the\nmedication straight back out.\n\n**Hydrogen peroxide.** Useful for spot-treating algae and for emergency\noxygenation, and genuinely risky around shrimp, which are more sensitive than fish\n— shrimplets and biofilm more so again.\n\n- **Never pour it into the tank freehand.** Whole-tank dosing in an invertebrate\n  system is not worth it.\n- Spot treatment means a syringe, filter briefly off, applied directly to the\n  target, ideally with the target out of water.\n- It kills biofilm — which in a tank whose grazers are already short of food is a\n  direct cost to the animals.\n- If asked about it, get specifics first — which tank, what target, how much water\n  — and default to mechanical removal or a blackout.\n\n**Melafix-type melaleuca products.** Not prohibited, but two honest caveats:\n\n- **Efficacy is weakly supported.** Reviews find no good evidence for it treating\n  bacterial infection in fish. It is not a substitute for a real antibacterial.\n- **It is invert-safe** at label dose and will not harm the biofilter. Many\n  keepers halve it with shrimp present anyway — `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose melafix --tank <tank>\n  --scenario with-shrimp`.\n- **The real cost is the surface film.** The oil reduces gas exchange at the\n  surface, and these tanks depend on surface agitation for *both* oxygenation and\n  evaporative cooling, so a film has an outsized effect. Keep agitation high and\n  expect cooling to drop.\n\n**Fertilizer.** Paused rather than refused. Potassium salts raise TDS and EC\nwithout contributing GH, so it will move the spectator-ion figure without\nimproving hardness. Resume at half strength only on visible plant deficiency, and\ncheck iron first. **Never use it to try to raise GH.**\n\n---\n\n## Why remineralizers are \"do not buy\"\n\nWhile GH sits inside the range the shrimp need, dosing minerals is solving a\nproblem that does not exist — and dosed minerals are harder to control than a\npartial water change. Revisit only if GH drops below the calcification line.\n\nNote the scope carefully: this prohibits **dosing a tank to raise its GH**.\nPreparing matched water for a water change is a different question, and swapping\nwater from a harder tank into a softer one is a third. Both of those are fine.\nApplying the prohibition to them is exactly the kind of scope error the skill\nwarns about.\n\n---\n\n## Testing\n\n**A strip is a screen, not a measurement.** Useful for the things nothing else\nhere measures — free chlorine, copper, iron — and demonstrably unreliable for pH.\n`aqua` records which instrument produced each reading and keeps untrusted ones out\nof the trend while still storing them: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings ph --all-instruments` shows\nwhat was filtered.\n\n**Liquid kits are the reference for nitrogen.** Judge colour in neutral daylight\nagainst a white background, never in warm low sun — it shifts every tube orange.\nNote that an ammonia scale usually runs yellow (0) to green (high), the opposite\ndirection from nitrite and nitrate.\n\n**Photometers decide hardness.** Never substitute marine-range checkers; their dye\nchemistries need seawater ionic strength.\n\n**A calibrated probe beats a colour chart for pH.** When they disagree, the probe\nis right — and check the time of day before calling it a shift at all.\n\n---\n\n## Gaps\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory` lists what is missing at the end of its output. Raise a gap when\nthe subject comes up naturally, not as a standing recommendation to buy things.\n", "file_type": ".md", "_source_path": "/tmp/shrimpy-home-kbphm9vr/skills/aquarium/aquarium-supervisor/references/products.md"}
```

</details>

### Turn 12 · assistant

```text
No. Do not add salt to the tank.

The display tank houses Neocaridina shrimp and a suckermouth catfish, and salt is poorly tolerated by both. More critically, if zeolite (ammonia-remover resin) is present or ever used in the filter, the sodium in salt reverses the resin's ion exchange and dumps its accumulated ammonium back into the water all at once.

If salt is needed as a bath, it must be done in a separate container outside the tank. 

Before doing anything, what specific symptoms are you seeing on the guppy (e.g., clamped fins, sitting low, white spots, bloating, pineconing)?
```
