# coral-scope — PASS

| | |
|---|---|
| Outcome | **PASS** |
| Model | `google/gemini-3.8-flash` |
| Tokens | 92,571 |
| Cost | $0.0432 |
| Wall | 24.0s |
| Skills opened | aquarium-supervisor |
| CLI calls | 3 |
| Blocked commands | 0 |

## Why this case exists

SKILL.md — "'Don't add more coral yet' applies to the DISPLAY tank only." The staging tank is far below target on GH and KH and is undersupplied. Over-applying a caution is the failure being tested. A correct reply typically *also* restates the display-tank prohibition, so "do not add" cannot be forbidden outright; the judge reads the intent.

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

> The reply must support adding coral to the STAGING / quarantine tank (target 1-2 tbsp). Refusing on the grounds that coral is already dissolving, or that pH is near target, is a FAIL — that caution belongs to the display tank only. Separately warning that the DISPLAY tank should not get more coral is correct and does not affect the grade.

</details>

## Judge

```text
PASS
The assistant clearly supports adding more crushed coral to the quarantine/staging tank.
```

## Conversation

### Turn 1 · user

```text
Should I add more crushed coral to the 4 gallon quarantine tank?
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
{"success": false, "error": "Skill 'aquarium' not found.", "available_skills": ["aquarium-supervisor", "youtube-content", "grounded-citations"], "hint": "Use skills_list to see all available skills"}
```

### Turn 4 · assistant

**calls `skill_view`**

```json
{
  "name": "aquarium-supervisor"
}
```

### Turn 5 · tool result

<details><summary><code>skill_view</code> returned 22.3 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "description": "Tiry's aquariums: shrimp, guppies, water chemistry, alerts", "tags": ["aquarium", "shrimp", "neocaridina", "guppies", "water-chemistry", "aquadirector"], "related_skills": [], "content": "---\nname: aquarium-supervisor\ndescription: \"Tiry's aquariums: shrimp, guppies, water chemistry, alerts\"\nversion: 2.0.0\nauthor: tairy-agent\nlicense: MIT\nplatforms: [linux, macos, windows]\nmetadata:\n  hermes:\n    tags: [aquarium, shrimp, neocaridina, guppies, water-chemistry, aquadirector]\n---\n\n# Aquarium Supervisor\n\nTwo tanks, one keeper (Tiry). **The facts live in a database, not in this file.**\nThis file is the rules for reading and acting on them.\n\n## When to Use\n\nLoad this for **anything** touching Tiry's aquariums — the tanks, the animals, the\nwater, the products, or the sensor. Casual phrasing counts: \"my shrimp look\nweird\", \"is 6.6 too low\", \"lost a guppy overnight\". A bare paste of sensor output\nwith no question attached counts. So does a question from someone else in the\nhousehold who does not know the setup.\n\nThree things to settle before answering anything specific:\n\n1. **Which tank.** They differ about sixfold in volume; a dose or a stocking\n   judgment right for one is badly wrong for the other. `aqua` refuses to guess.\n2. **Is the number measured, and when.** You cannot read the sensor yourself.\n3. **Is it drifting, or merely not the textbook number.** Only drift justifies\n   action.\n\nDo **not** use this for general aquarium questions unconnected to these two\ntanks — answer those from ordinary knowledge, without pretending the specifics\nhere apply.\n\n---\n\n## The `aqua` CLI — run this first\n\nThe CLI lives at `/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py`. **Run each command on its\nown, exactly as written below.** Do not set a shell variable for the path, and do\nnot chain commands with `;` or `&&` — one invocation per terminal call.\n\n​```\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py status\n​```\n\n**Start every aquarium conversation with that.** It is one call and it returns the\nwhole picture: volumes, rosters, the latest reading of every metric with its age\nand trend, anything outside target, and the open questions. Do it once per\nconversation, not once per turn.\n\nThis replaces the \"never re-ask what is here\" rule. Nothing about these tanks is\nin your head or in this file — it is in the data, and it is current. Reciting a\nnumber from memory is the failure this design exists to prevent.\n\n### Reading\n\n​```\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py status --tank staging\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py tanks\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock --tank display\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock --species neocaridina\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py species neocaridina\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory --class never\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py readings ph --tank display\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py dose prime --tank staging\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py check\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py questions\n​```\n\n### Writing — record what you are told\n\nTiry telling you a number is the only way a number gets in. **Log it.** An\nunlogged reading is one nobody can plot and one you will not have next week.\n\n​```\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py log ph 6.91 --tank display --instrument kactoily\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py log gh 75 --tank staging --instrument hi735 --note \"after first swap\"\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py log phosphate 0.25 --tank display --instrument advatec --min 0 --max 0.25\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py event water-change --tank staging --detail \"15% with display water\"\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock-change add --id display-neocaridina --count 1\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py livestock-change remove --id staging-neocaridina --count 1\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py inventory-change open prime\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py question answer --id 4 --text \"6 female, 3 male\"\n​```\n\nUse `--min` and `--max` when the reading was a band rather than a point — a colour\nchart between two swatches is a band, and flattening it invents precision.\n\n**A species question is not a tank question.** What an animal *tolerates* comes\nfrom `aqua species`; what these tanks *currently read* comes from `aqua status`\nand `aqua check`. Do not answer one with the other, and do not answer either from\nmemory — a plausible wrong range is indistinguishable from a right one to someone\nasking because they do not know.\n\n**Record roster changes as they are mentioned.** `livestock-change add --id <id>\n--count N` needs nothing else for a group that already exists, and dates the\nchange so \"how long have they been in there\" stops being unanswerable.\n\n`--instrument` matters. Some instruments are not trusted for some metrics — the\nstrip pH pad reads demonstrably low, the liquid kit's pH is unreliable under warm\nlight — and `aqua` will say so and keep those readings out of the trend while\nstill recording them.\n\n### Reporting\n\n​```\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py export --format csv\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py plot ph --tank display\npython3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py report\n​```\n\nTell Tiry the path it prints. Offer a report when a trend question comes up, not\nreflexively.\n\n### Rules for using it\n\n- **Never state a number you did not just read from `aqua` or from Tiry in this\n  conversation.** If you are unsure whether it is current, run `status` again.\n- **Never compute a dose yourself.** `aqua dose` derives it from measured volume\n  and shows its basis. Every historic dosing error here came from arithmetic done\n  in prose.\n- **`status` tells you how stale the data is.** If it says the newest reading is\n  weeks old, say so before answering, not after.\n- If a command fails or the data looks wrong, run `doctor`.\n\n---\n\n## You cannot see or touch the tanks\n\nYou run in the cloud. The Kactoily sensor, the `aquadirector` CLI and the Eheim\nfeeder are all on Tiry's LAN and unreachable from where you execute. Having a\nterminal does not change that — the tool is not installed here and the sensor is\nnot routable.\n\nThe `aqua` CLI above is different: it is part of this skill, it runs where you\nrun, and it reads a database, not a tank.\n\nSo:\n\n- **Never run, or offer to run, an `aquadirector` command.** Ask Tiry to run it\n  and paste the output — then log what he pastes.\n- **Never claim to have checked anything.**\n- Name the exact command you want. `aquadirector sensor status` is a five-second\n  favour; \"can you check the tank?\" is a chore.\n\nCommands to **ask for**, not to run:\n\n​```\naquadirector dashboard --output json          # the most useful paste: every field, no transcription\naquadirector sensor status [--watch 30s]      # Kactoily 7-in-1\naquadirector feeder status | feed             # Eheim autofeeder+\naquadirector feeder schedule clear --day tue  # a fasting day\naquadirector alerts check --notify\n​```\n\nThe Kactoily also reports to the **SmartLife** app (Tuya), which has a History\nview. A screenshot of it is often the fastest way to answer \"is this drifting?\",\nand Tiry can send one from a phone.\n\n**The tool is reef-oriented.** Its salinity and SG readings carry no information\nin freshwater. Ignore them.\n\n### Handling pasted sensor output\n\nThis is the main way you see the tanks, so treat a paste as the event it is.\n\n**Which tank a paste belongs to.** The Kactoily probe lives in one tank —\n`aqua tanks` says which. A bare paste of sensor output is from that tank unless\nTiry says otherwise. He does sometimes drop the probe into the other tank to\ntrack a swap, and will say so when he does. Do not stall a paste to ask; log it,\nand say which tank you logged it against so a correction is one line.\n\n1. **Log it.** Every value, with `--instrument` and `--at` if the paste carries a\n   timestamp. Do this before commenting on it.\n2. `aqua` gives you the prior value and the delta for each. Name only what moved.\n3. Run `check` for the target comparison rather than eyeballing it.\n4. **A paste has no timestamp unless Tiry gives one.** If the reading is doing\n   real work in your answer, ask when it was taken — planted tanks swing pH\n   through the photoperiod, so the hour matters as much as the number.\n5. One reading is not a trend. `aqua` will tell you when there isn't one yet.\n\n\n---\n\n## Decision rules\n\n**Stability beats optimization.** Ask whether a reading is *drifting* or merely\n*not the textbook number*. Only drift justifies action. A parameter that is stable\nand slightly off target is healthier than one being actively corrected.\n\n**Rules have scope, and the scope is per tank.** A caution that is right for one\ntank is not a general law. The clearest example: crushed coral. The display tank\nis near its pH target and climbing on its own, so more media there risks\novershooting something the existing coral will reach unaided. The staging tank is\nbelow target on both GH and KH and undersupplied with media — there, adding coral\nis correct. Check `aqua status` before applying either.\n\n**Aragonite dissolution is self-limiting.** The rate falls as pH rises and\neffectively stalls around 7.2–7.5, so coral is a buffer that stops working once it\nis no longer needed. Overshoot is not a realistic failure mode; undersupply is.\n\n**Prefer the cheap check first, and the mechanical fix over the chemical one.**\nMove the probe rather than spend a reagent. Remove the uneaten food rather than\ndose something. Reach for a bottle last.\n\n**Telemetry is not the tank.** Plenty of questions are answered by looking at the\nanimal. A sucker's belly against the glass says more about whether it is eating\nthan any parameter will. Say \"go look\" when looking is the answer.\n\n**ORP does not tell you whether there is ammonia.** Tiry has been told otherwise.\nIt is not reliable and must not substitute for an ammonia test:\n\n- ORP measures net redox potential, which in an aerated tank is dominated by\n  dissolved oxygen. An open lid, surface fans and heavy agitation pin it high more\n  or less regardless of what else is dissolved.\n- Ammonia at spike concentrations is a trace reductant, easily swamped in a mixed\n  electrode potential.\n- The probe is uncalibrated for ORP, and ORP electrodes drift over months.\n- A tank can carry 1 ppm ammonia at 440 mV.\n\nHigh ORP is genuinely reassuring about *gross organic load* — nothing large is\nrotting — which is a different question from whether the biofilter is keeping up.\nAmmonia is measurable now; measure it.\n\n**Never invent a number, and never round one into a decision.** `aqua` reports\nbands as bands (`0.00-0.25`) and marks estimated volumes as estimated. Carry that\nthrough instead of flattening it.\n\n---\n\n## Water changes\n\nThe regime differs per tank now — **check `aqua tanks`**, which is the only current\nrecord. Partial changes have begun on one of them; the other is still top-off only.\n\nTop-off with 0 TDS water is correct and should continue: it replaces evaporated\nwater without adding minerals. But it is not maintenance. **Evaporation removes\nnothing.** Nitrate, phosphate, dissolved organics, potassium and sodium have no\nexport path except plant uptake.\n\n- **Start weekly changes as habit rather than rescue**, sized to the tank. The\n  staging tank's stocking makes this more urgent than the display's.\n- **Matched water, not pure.** A pure-distilled change drops GH and KH by the same\n  fraction as the volume replaced, in one step — the rapid osmotic move that\n  triggers emergency molts. Match within about 1 °C and 20 ppm TDS.\n- **Display-tank water is the best source for the staging tank**: harder,\n  temperature-matched, biologically clean, free, and it converges the two tanks,\n  which is needed before any transfer regardless.\n- **A rapid GH *rise* is its own osmotic event.** Walk it up over days.\n- Tap water is unmeasured. If it tests close to the display tank on the Hanna\n  checkers, dechlorinated tap is simplest. Otherwise remineralize distilled.\n\nRaise this once when relevant, then treat it as a known choice.\n\n---\n\n## Routine\n\n### Feeding\n- **Guppies:** once daily, a pinch, gone in 30–60 s. Verify against consumption,\n  not the schedule.\n- **Sucker and display shrimp:** every 2–3 days at lights-out, half a sinking\n  spirulina or herbivore wafer. Siphon the remainder after 2–3 hours.\n- **Staging tank:** mystery snails take sinking vegetable pellets, blanched\n  zucchini or spinach. Nerites need biofilm and refuse prepared food — the tank is\n  planted, so there is grazing surface, but a young setup carries thin biofilm.\n  Judge by animal condition. **Uneaten food matters far more here** — four gallons\n  has almost no buffer. Remove it.\n- **One fast day per week.** Tiry clears it on the feeder.\n\n### Maintenance\n- Rinse the mechanical sponge in **discarded tank water only**, never tap.\n- Replace 50% of the crushed coral every 6–9 months. `aqua tanks` carries the\n  install dates and computes when.\n- Test GH and KH monthly on the Hanna checkers, in **both** tanks, same session —\n  and log both.\n\n### Acclimation (staging → display)\n1. Confirm both tanks read close on GH, KH and pH — `aqua check` and\n   `aqua readings gh` for each. That match is the whole point of the staging tank.\n2. Float 15–20 min for temperature.\n3. Drip or ladle ¼ cup receiving-tank water every 5–10 min over 45–60 min until\n   the holding volume triples.\n4. Net or hand-transfer. **Discard all transit water.**\n5. Place nerites right-side up on rock, wood or glass.\n6. **Before moving any snail into the display tank, seal its lid gaps and confirm\n   at least an inch of headspace.** Those requirements travel with the snails.\n7. `aqua livestock-change move` afterwards, so the rosters stay true.\n\n---\n\n## When something is wrong\n\n`references/triage.md` first for any sick, dying or dead animal or out-of-range\nreading. `references/chemistry.md` for the mechanisms behind the numbers.\n`references/livestock.md` for anything species-specific.\n`references/products.md` for why a product is or is not usable here.\n\nRead them for *reasoning*. Read `aqua` for *values*.\n\n---\n\n## Background — `assets/wiki/`\n\nThree tiers, and they do not overlap:\n\n| Read | For | Example |\n|---|---|---|\n| `aqua` | **values** | what this tank reads, what this species tolerates |\n| `references/` | **reasoning** | why a number matters, what to do about it |\n| `assets/wiki/` | **background** | what the animal *is*, how a product works, how an instrument fails |\n\nOpen a wiki page with `skill_view(file_path=\"assets/wiki/<category>/<slug>.md\")`. The pages\nstate no measurement and no tolerance range — those are `aqua`'s. Each cites its sources.\n\n**Read the page when being wrong is expensive**, not for every background question. The\nrule above still holds — ordinary husbandry you are confident about is answered from\nordinary knowledge, and a lookup for its own sake is a wasted round trip. Open the page\nwhen the answer turns on something specific to *these* animals and products:\n\n- a treatment that conflicts with the rest of the stocking (the planaria/snail case)\n- what a product actually does here, as opposed to what the label claims\n- why two instruments disagree\n- a pest or disease that has to be told apart from a similar one\n\nIn those, a plausible recollection and a sourced fact read identically in a reply, and only\none of them is checkable.\n\n**Do not read a wiki page to answer a question about a number.** `aqua` is faster and it is\nthe only copy that is current.\n\n<!-- WIKI-INDEX START -->\n\n| Subject | Page |\n|---|---|\n| **The animals** | |\n| Neocaridina davidi, cherry shrimp, Neocaridina, shrimp | `assets/wiki/species/neocaridina.md` |\n| Otocinclus, oto, otos, otocinclus, dwarf suckermouth | `assets/wiki/species/otocinclus.md` |\n| Poecilia reticulata, guppy, guppies, fancy guppy, millionfish | `assets/wiki/species/guppy.md` |\n| Pomacea diffusa, mystery snail, apple snail, spike-topped apple snail, snail | `assets/wiki/species/mystery_snail.md` |\n| Vittina waigiensis, nerite, red racer nerite, nerite snail, snail | `assets/wiki/species/nerite.md` |\n| **Pests, disease and algae** | |\n| Cyanobacteria, cyanobacteria, blue-green algae, BGA, slime algae | `assets/wiki/pest/cyanobacteria.md` |\n| Hydra, hydra, polyp, stinging polyp | `assets/wiki/pest/hydra.md` |\n| Ichthyophthirius multifiliis, ich, ick, white spot, white spot disease | `assets/wiki/pest/ich.md` |\n| Planaria, planaria, flatworm, flatworms | `assets/wiki/pest/planaria.md` |\n| Scutariella japonica, scutariella, white worms on shrimp, nose worms, rostrum worms | `assets/wiki/pest/scutariella.md` |\n| **What a number means** | |\n| Ammonia, ammonia, NH3, ammonium, NH4 | `assets/wiki/metric/ammonia.md` |\n| Copper, copper, Cu, heavy metal | `assets/wiki/metric/copper.md` |\n| EC — electrical conductivity, EC, conductivity, microsiemens, uS/cm | `assets/wiki/metric/ec.md` |\n| Free chlorine, chlorine, free chlorine, Cl2, chloramine, tap water | `assets/wiki/metric/free_chlorine.md` |\n| GH — general hardness, GH, general hardness, hardness, dGH, calcium, magnesium | `assets/wiki/metric/gh.md` |\n| Iron, iron, Fe, micronutrient | `assets/wiki/metric/iron.md` |\n| KH — carbonate hardness, KH, carbonate hardness, alkalinity, buffer, dKH | `assets/wiki/metric/kh.md` |\n| Nitrate, nitrate, NO3, nitrates | `assets/wiki/metric/nitrate.md` |\n| Nitrite, nitrite, NO2, nitrites | `assets/wiki/metric/nitrite.md` |\n| ORP — oxidation-reduction potential, ORP, redox, redox potential, mV | `assets/wiki/metric/orp.md` |\n| Phosphate, phosphate, PO4, phosphates | `assets/wiki/metric/phosphate.md` |\n| TDS — total dissolved solids, TDS, dissolved solids, ppm | `assets/wiki/metric/tds.md` |\n| Temperature, temperature, temp, heat, cooling, degrees | `assets/wiki/metric/temperature.md` |\n| pH, pH, acidity, alkaline, acidic | `assets/wiki/metric/ph.md` |\n| **What is in the bottle** | |\n| API Melafix, Melafix, tea tree, melaleuca, bacterial remedy | `assets/wiki/product/melafix.md` |\n| Seachem Prime, Prime, dechlorinator, conditioner, water conditioner | `assets/wiki/product/prime.md` |\n| Seachem Stability, Stability, bacteria starter, cycling bacteria, bottled bacteria | `assets/wiki/product/stability.md` |\n| **How an instrument measures** | |\n| Colorimetric checkers, checker, colorimeter, Hanna checker | `assets/wiki/method/colorimetric-checker.md` |\n| Electrode pens and multiparameter probes, probe, pen, pH meter, TDS meter, ORP | `assets/wiki/method/electrode-pen.md` |\n| Liquid reagent test kits, liquid kit, drop test, titration | `assets/wiki/method/liquid-reagent-kit.md` |\n| Multi-parameter test strips, strips, dip strip, 9-in-1 | `assets/wiki/method/test-strip.md` |\n| Observed and reported values, observed, reported, from memory | `assets/wiki/method/observation.md` |\n\n<!-- WIKI-INDEX END -->\n", "path": "aquarium/aquarium-supervisor/SKILL.md", "skill_dir": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor", "org_provenance": null, "linked_files": {"references": ["references/triage.md", "references/livestock.md", "references/chemistry.md", "references/products.md"], "assets": ["assets/reference.json", "assets/initial/tanks.json", "assets/initial/events.ndjson", "assets/initial/questions.json", "assets/initial/inventory.json", "assets/initial/livestock.json", "assets/initial/readings.ndjson", "assets/wiki/pest/ich.md", "assets/wiki/pest/cyanobacteria.md", "assets/wiki/pest/scutariella.md", "assets/wiki/pest/hydra.md", "assets/wiki/pest/planaria.md", "assets/wiki/species/guppy.md", "assets/wiki/species/otocinclus.md", "assets/wiki/species/mystery_snail.md", "assets/wiki/species/neocaridina.md", "assets/wiki/species/nerite.md", "assets/wiki/metric/iron.md", "assets/wiki/metric/orp.md", "assets/wiki/metric/free_chlorine.md", "assets/wiki/metric/ph.md", "assets/wiki/metric/ec.md", "assets/wiki/metric/nitrate.md", "assets/wiki/metric/ammonia.md", "assets/wiki/metric/kh.md", "assets/wiki/metric/nitrite.md", "assets/wiki/metric/temperature.md", "assets/wiki/metric/tds.md", "assets/wiki/metric/phosphate.md", "assets/wiki/metric/copper.md", "assets/wiki/metric/gh.md", "assets/wiki/product/melafix.md", "assets/wiki/product/stability.md", "assets/wiki/product/prime.md", "assets/wiki/method/liquid-reagent-kit.md", "assets/wiki/method/observation.md", "assets/wiki/method/test-strip.md", "assets/wiki/method/colorimetric-checker.md", "assets/wiki/method/electrode-pen.md"], "scripts": ["scripts/_report.py", "scripts/_calc.py", "scripts/aqua.py", "scripts/_store.py"]}, "usage_hint": "To view linked files, call skill_view(name, file_path) where file_path is e.g. 'references/api.md' or 'assets/config.yaml'", "required_environment_variables": [], "required_commands": [], "missing_required_environment_variables": [], "missing_credential_files": [], "missing_required_commands": [], "setup_needed": false, "setup_skipped": false, "readiness_status": "available", "_source_path": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/SKILL.md", "metadata": {"hermes": {"tags": ["aquarium", "shrimp", "neocaridina", "guppies", "water-chemistry", "aquadirector"]}}}
```

</details>

### Turn 6 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py status"
}
```

### Turn 7 · tool result

<details><summary><code>terminal</code> returned 10.3 KB</summary>

```text
{"output": "!! newest reading is 25 days ago\n\n== Display tank (display)\n   24.2 gal water (computed) · 9x Neocaridina shrimp, 9x Fancy guppy, 1x Suckermouth catfish\n   pH           6.86  (smartlife, 25 days ago)\n   Temperature  24.5 C  (smartlife, 25 days ago)\n   TDS          255 ppm  (smartlife, 25 days ago)\n   EC           510 uS/cm  (smartlife, 25 days ago)\n   ORP          440 mV  (smartlife, 25 days ago)\n   GH           161 ppm  (hi735, 26 days ago)\n   KH           46 ppm  (hi775, 26 days ago)\n   Ammonia      0.00 ppm  (advatec, 25 days ago)\n   Nitrite      0.00 ppm  (advatec, 25 days ago)\n   Nitrate      0.0 ppm  (advatec, 25 days ago)\n   Phosphate    0.00-0.25 ppm  (advatec, 25 days ago)\n   Free Cl2     0.00 ppm  (bacnunn, 25 days ago)\n   Copper       0.00 ppm  (bacnunn, 25 days ago)\n   Iron         0.00 ppm  (bacnunn, 25 days ago)\n   prior bands (pre-log, no timestamps): pH 6.77-6.87, Temperature 23.8-24.3, TDS 247-254, EC 494-509, ORP 377-440\n\n== Staging / quarantine tank (staging)\n   4.0 gal water (computed) · 3x Albino mystery snail, 3x Red Racer nerite, 9x Neocaridina shrimp\n   GH           62 ppm  (hi735, 26 days ago)\n   KH           22 ppm  (hi775, 26 days ago)\n   Ammonia      0.00 ppm  (advatec, 25 days ago)\n   Nitrite      0.00 ppm  (advatec, 25 days ago)\n   Nitrate      0.0 ppm  (advatec, 25 days ago)\n   Phosphate    0.25 ppm  (advatec, 25 days ago)\n   Free Cl2     0.00 ppm  (bacnunn, 25 days ago)\n   Copper       0.00 ppm  (bacnunn, 25 days ago)\n   Iron         0.00 ppm  (bacnunn, 25 days ago)\n   !! GH 62.0 is below target 105 — also needs to converge on the display tank before any transfer\n   !! KH 22.0 is below target 35\n\nOpen questions (7):\n   2. Tap water GH, KH and TDS - untested, so change-water preparation cannot be specified.\n   3. Substrate depth in the display tank, to firm up the ~25 gal estimate.\n   4. Guppy sex ratio - if mixed, expect fry and a compounding bioload.\n   5. Is the suckermouth an Otocinclus or a juvenile pleco? A common pleco would outgrow the tank.\n   6. Is the Eheim autofeeder in use, and on what schedule?\n   7. How long have the staging animals been in quarantine, and what is the plan for moving them out?\n   8. Plant species in the staging tank and how established they are - it determines how much grazing surface the nerites and shrimp actually have.", "exit_code": 0, "error": null}

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

**A rubric must not re-judge what a deterministic assertion already proves.** The judge is
shown the reply and nothing else — it cannot see tool calls. A rubric asking for a value
"obtained from the CLI rather than asserted" made the judge guess, and it vetoed a
`runs_aqua` check that had already passed on the transcript. Provenance belongs to
`runs_aqua`/`opens_skills`/`opens_wiki`; the rubric judges the text.
`tests/test_harness.py` fails on the phrasings that ask otherwise.

**The wiki is for when being wrong is expensive, not for every background question.**
`SKILL.md:34-36` tells the agent to answer general husbandry from ordinary knowledge, so an
`opens_wiki` assertion on "should I remove shed molts" failed a correct reply for obeying
the older rule. Scope a lookup requirement to what is specific to these animals and
products — the planaria/snail treatment conflict is the paradigm case.

**A wiki page must not restate a rule SKILL.md or a reference already owns.** `metric/orp.md`
was written with all four of `SKILL.md`'s reasons that ORP is not an ammonia test, copied
almost verbatim — and the eval meant to catch it *passed*, because the agent answered
correctly from `SKILL.md` without opening the page. Duplication in prose survives review
because every sentence looks fine; `tests/test_wiki.py` measures it as shared nine-word
runs instead. A page may restate a conclusion, never the argument.

**When an eval fails, read the reply before touching the skill.** **Eight times** now the
harness was wrong and the agent was right — it named `3.2 mL` *in order to correct it*,
scoped a caution with a sentence containing "do not add", chose a more targeted CLI verb
than the one asserted, said "don't dose chemical pH adjusters" against a case that banned
the phrase, gave a correct range that a rubric called unsourced because the judge cannot see
a tool call, answered a husbandry question from ordinary knowledge exactly as SKILL.md instructs, and
gave a fuller answer on ORP than the rubric demanded without needing the page an
`opens_wiki` assertion insisted on. A substring test cannot tell "recommends X" from "warns against X".
`tests/test_harness.py` now refuses a `not_matches` with no rubric behind it; every run
renders a transcript, so read it first.

**Skill content is input to the harness.** `skills_opened` once scanned tool responses for
`"not found"`; `SKILL.md` §7 contains the phrase `command not found`, so a documentation
edit broke eight of twelve evals. Parse the envelope, never the body.

**The eval case format is bespoke, and validated because of it.** `evals/schema.py` says
why promptfoo was not adopted and checks every case before a model is called — every
assertion is read with `expect.get(...)`, so a misspelled key was silently ignored and the
case passed having asserted nothing. `evals/cases/schema.json` is generated from the same
definitions for editor autocomplete; a test fails if they drift.

**Wiping `$HERMES_HOME/skills/` does not give you a skills-only profile.** `hermes gateway`
calls `_sync_bundled_skills_quietly()` on every start, which re-seeds all 58 bundled skills —
and `tairy-agent/scripts/bootstrap.sh` restarts hermes immediately after `create-profile.sh`
wipes the directory. Only the `.no-bundled-skills` marker survives a restart. See
[`specs/11`](specs/11-vendored-skills.md) and [`INTEGRATION.md`](INTEGRATION.md).

**A vendored skill can advertise a capability the container cannot deliver.** `productivity/pdf`
was rejected because `pymupdf` and `pdfplumber` are in neither hermes's `[all]` extra nor
`tools/lazy_deps.py`, and the skill declares no `required_commands` — so `skill_view` would
report it available and every script would die on import. `tests/test_vendored_skills.py`
checks imports against what the image can actually satisfy, and byte-matches each copy against
the pinned submodule so it cannot drift into an unmaintained fork.

**Hook and middleware dispatch is fail-open.** An exception in a `pre_tool_call` hook is
swallowed into a debug log. Anything registered there must 

[...truncated AGENTS.md: 10,216 chars total]
```

</details>

### Turn 8 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py tanks"
}
```

### Turn 9 · tool result

<details><summary><code>terminal</code> returned 2.5 KB</summary>

```text
{"output": "== Display tank (display)\n   dimensions   32.0 x 15.0 x 14.0 in\n   gross        29.1 gal\n   water        24.2 gal (computed) — gross minus 2.1 freeboard and 2.75 displacement\n                Substrate depth is unrecorded, so displacement is an estimate. To settle it: during a water change, refill from a marked jug and count. Once.\n   substrate    Inert sand/gravel, planted. No buffering aquasoil.\n   filtration   Multi-stage mechanical sponge\n   media        2-3 tbsp CaribSea Florida Crushed Coral (aragonite, 2.0-5.5 mm), installed 2026-08-29 (33 days ago)\n   cooling      Open-top lid, 12V fans at 45 degrees across the surface, lighting raised 2-3 in, heater off or low. Evaporative cooling gives about 2.0-3.5 C below ambient, bounded by room wet-bulb.\n   regime       Distilled top-off only. No water changes.\n   sensor       the Kactoily probe lives in this tank\n   note         The sensor lives in this tank, so it is the only one with continuous data.\n\n== Staging / quarantine tank (staging)\n   dimensions   17.0 x 6.6 x 9.5 in\n   gross        4.6 gal\n   water        4.0 gal (computed) — gross minus 0.5 freeboard and 0.1 displacement\n                Bare bottom, planted, minimal displacement.\n   substrate    Bare-bottom glass, planted.\n   filtration   Independent power filter\n   media        less than 1 tbsp CaribSea Florida Crushed Coral (aragonite, 2.0-5.5 mm), installed 2026-09-03 (28 days ago)\n                Undersupplied. Tiry describes it as 'only a little', and the 5 Sep hardness results are consistent with that.\n   regime       Distilled top-off only. No water changes.\n   note         No continuous sensor. Test this tank separately with the Hanna checkers, or drop the probe in and allow 2-4 minutes to settle.\n   note         Overstocked for its volume: six snails and nine shrimp in four gallons, on a filter that is weeks old, with no water changes. Four gallons gives almost no dilution buffer.\n   note         Escape-proofing and at least an inch of headspace are live requirements here, not in the display tank. Both snail species climb.\n   note         Its whole function is holding animals at display-tank parameters so a transfer causes no osmotic shock. Clean ammonia says the tank is safe; it says nothing about whether it matches.\n   note         The Kactoily probe normally lives in the display tank. It can be dropped in here to track a swap - allow 2-4 minutes to settle - but if it has been moved, say so when pasting a reading, or it will be logged against the wrong tank.", "exit_code": 0, "error": null}
```

</details>

### Turn 10 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py check"
}
```

### Turn 11 · tool result

`terminal`

```text
{"output": "== display\n   all logged metrics inside target\n   spectator ions 48.0 ppm — normal\n\n== staging\n   !! GH 62.0 below 105 (logged 26 days ago)\n      also needs to converge on the display tank before any transfer\n      background: assets/wiki/metric/gh.md\n   !! KH 22.0 below 35 (logged 26 days ago)\n      background: assets/wiki/metric/kh.md", "exit_code": 0, "error": null}
```

### Turn 12 · assistant

**calls `read_file`**

```json
{
  "limit": 100,
  "offset": 1,
  "path": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/references/chemistry.md"
}
```

### Turn 13 · tool result

<details><summary><code>read_file</code> returned 4.5 KB</summary>

```text
{"content": "1|# Chemistry — mechanisms, not values\n2|\n3|Every number in this file is a **relationship**, not a measurement. Tank values,\n4|volumes, doses and hardness figures come from `aqua`:\n5|\n6|​```\n7|# the CLI - run each command on its own, no shell variables, no chaining\n8|python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose <product> --tank <tank> · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check\n9|​```\n10|\n11|The CLI computes every conversion below. Reproduce the arithmetic by hand only to\n12|explain it, never to answer with it.\n13|\n14|---\n15|\n16|## 1. Unit conversions\n17|\n18|**Hardness.** German degrees and ppm as CaCO₃ relate by 17.86:\n19|\n20|​```\n21|d-units = ppm / 17.86        ppm = d-units × 17.86\n22|​```\n23|\n24|**Volume.** `gallons = L × W × H (inches) / 231`, then subtract freeboard and\n25|displacement. This is the calculation that matters most, because getting it wrong\n26|scales every dose in the system. A tank's nominal name is not its water volume,\n27|and using one for the other is how a routine dose becomes a 30% overdose.\n28|\n29|`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` shows the full chain — gross, freeboard, displacement, water — and\n30|marks whether the result is measured or estimated. To convert an estimate into a\n31|measurement: during a water change, refill from a marked jug and count. Once.\n32|\n33|**Ammonia on a Hanna HI700**, if one is ever acquired. It reads ammonia-nitrogen:\n34|\n35|​```\n36|Total ammonia (mg/L) = HI700 reading × 1.214\n37|​```\n38|\n39|(Molar mass ratio 17.03 / 14.01.)\n40|\n41|**EC and TDS.** The probe reports TDS ≈ 0.5 × EC. That is a *meter setting*, an\n42|NaCl-referenced factor, not a chemical relationship. Do not present it as physics.\n43|\n44|---\n45|\n46|## 2. The spectator-ion heuristic — and its limits\n47|\n48|​```\n49|ΔTDS_spectator = TDS_measured − (GH_ppm + KH_ppm)\n50|​```\n51|\n52|`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` computes it from the latest readings and classifies the result.\n53|\n54|**It is a trend line, not a concentration.** Three reasons it is not a real\n55|quantity:\n56|\n57|1. GH and KH are reported as *ppm CaCO₃ equivalents* — a standardized proxy, not\n58|   the dissolved mass of the ions present. Subtracting them from a mass-like TDS\n59|   figure mixes units.\n60|2. The calcium counted in GH is largely the same ion paired with the bicarbonate\n61|   counted in KH. Subtracting both double-counts.\n62|3. Conductivity-derived TDS uses an NaCl factor that under-reads Ca²⁺ and HCO₃⁻.\n63|\n64|What it *is* good for: if GH and KH hold steady and this figure climbs, something\n65|that is not hardness is accumulating — fertilizer salts, sodium, nitrate. Answer\n66|that with a water change, never with a chemical additive.\n67|\n68|**It inherits the staleness of its inputs.** GH and KH move slowly but they do\n69|move, and a spectator figure computed against a months-old hardness reading is\n70|progressively more wrong. `aqua` reports the age of every reading; if the figure\n71|is driving a conclusion, say how old its inputs are.\n72|\n73|---\n74|\n75|## 3. Dilution and partial changes\n76|\n77|​```\n78|TDS_final = TDS_initial × (1 − V_replaced / V_total)\n79|​```\n80|\n81|The same fraction applies to GH and KH. That is the whole argument for matched\n82|change water: a pure-distilled change does not just dilute nitrate, it drops\n83|hardness by the same proportion, in one step. For an animal that needs dissolved\n84|calcium to build a new shell, that step is the event.\n85|\n86|**A rapid hardness *rise* is also an osmotic event.** Converging two tanks means\n87|walking the softer one up over days with repeated partial swaps, not fixing it in\n88|one session. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings gh --tank <tank>` shows whether it is moving.\n89|\n90|---\n91|\n92|## 4. Buffering with aragonite\n93|\n94|Crushed coral is calcium carbonate. It dissolves when the water is acidic enough\n95|to dissolve it and stops when it is not — the rate falls as pH rises and\n96|effectively stalls around 7.2–7.5.\n97|\n98|Two consequences worth stating plainly:\n99|\n100|- **Overshoot is not a realistic failure mode.** It is a buffer that switches\n101|", "total_lines": 160, "file_size": 7016, "truncated": true, "hint": "Use offset=101 to continue reading (showing 1-100 of 160 lines)", "is_binary": false, "is_image": false}
```

</details>

### Turn 14 · assistant

**calls `read_file`**

```json
{
  "limit": 60,
  "path": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/references/chemistry.md",
  "offset": 100
}
```

### Turn 15 · tool result

<details><summary><code>read_file</code> returned 3.5 KB</summary>

```text
{"content": "100|- **Overshoot is not a realistic failure mode.** It is a buffer that switches\n101|  itself off. Undersupply is the failure mode that actually happens.\n102|- **It is slow.** Weeks, not days. It cannot beat a molt clock on its own, which\n103|  is why a hardness problem with animals at risk needs partial swaps *and* coral:\n104|  swaps move the number now, coral holds it afterwards.\n105|\n106|Placement matters more than amount past a point — media in a dead corner of a\n107|filter does very little. Rinse before adding.\n108|\n109|`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` carries install dates and computes when a replacement is due.\n110|\n111|---\n112|\n113|## 5. Product mechanisms\n114|\n115|Which products are on the shelf, in what quantity, and whether they may be used\n116|here: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory`. Why: `products.md`. Doses: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose`.\n117|\n118|**Conditioners (Prime).** Neutralize chlorine and chloramine, bind heavy metals,\n119|and temporarily complex ammonia and nitrite for roughly 24–48 hours. They do not\n120|move pH or GH, and they do not remove nitrogen — they buy time while the cause is\n121|found. Re-dose within that window if the cause persists.\n122|\n123|**Bacterial supplements (Stability).** Nitrifying and facultative bacteria. Useful\n124|after adding livestock, replacing or heavily rinsing media, cycling, or\n125|antibacterial exposure. Pointless when ammonia and nitrite read zero and nitrate\n126|is present — that combination means the colony is already self-sustaining.\n127|\n128|**Zeolite (clinoptilolite).** Binds ammonium by ion exchange, swapping it for\n129|sodium. Three properties that matter: it has **zero affinity for nitrite**, it\n130|**starves the nitrifying colony** of its substrate and so stalls biological\n131|maturation, and adding sodium chloride **reverses the exchange and dumps the\n132|resin's entire accumulated ammonium load into the water at once**. Emergency use\n133|only, and never alongside salt.\n134|\n135|**Oxidizers (hydrogen peroxide).** Effective against algae, and indiscriminate.\n136|Shrimp — especially shrimplets — and biofilm are more sensitive than fish. Spot\n137|treatment only: syringe, filter briefly off, applied directly to the target.\n138|\n139|**Carbon.** Adsorbs tannins, odours and many organics. Exhausts in weeks, not\n140|months, and **strips medication out of the water**, so it comes out before any\n141|treatment goes in.\n142|\n143|---\n144|\n145|## 6. Instruments\n146|\n147|`aqua` records which instrument produced every reading and knows which ones are\n148|trustworthy for which metric. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --all-instruments` shows\n149|the ones it normally filters out.\n150|\n151|The general principle: **a colour chart read under warm light is not a\n152|measurement**, and a test strip is a screen. Judge colour in neutral daylight\n153|against a white background. Photometers and a calibrated probe decide; strips\n154|suggest.\n155|\n156|Never substitute marine-range checkers for freshwater ones. Their dye chemistries\n157|need seawater ionic strength and will read nonsense here.\n158|\n159|Distilled water reading pH 5.5–5.8 in the jug is normal atmospheric CO₂ and will\n160|", "total_lines": 160, "file_size": 7016, "truncated": true, "hint": "Use offset=160 to continue reading (showing 100-159 of 160 lines)", "is_binary": false, "is_image": false}
```

</details>

### Turn 16 · assistant

```text
Yes. 

The staging tank currently has less than a tablespoon of crushed coral, installed 28 days ago. Its last logged hardness readings (from 26 days ago) were GH 62 ppm (target ≥ 105) and KH 22 ppm (target ≥ 35) — both well below where your mystery snails, nerites, and Neocaridina need them to prevent shell erosion and molting failure, and far below the display tank (GH 161, KH 46).

Adding more crushed coral is safe and appropriate here:
- **Aragonite is self-limiting:** It dissolves under acidic conditions and naturally stalls around pH 7.2–7.5. Overshoot is not a realistic failure mode; undersupply is what happened here.
- **Rinse first:** Rinse the media in clean water to wash off fine dust, and place it in an area of active flow inside or directly around the power filter rather than a dead corner.
- **Pair with water swaps:** Coral dissolves over weeks. Because the snail shell and shrimp molt clocks are running now, bring the staging tank's hardness up by doing small, matched partial water swaps using water from the display tank, letting the additional coral sustain the buffer once reached.
```
