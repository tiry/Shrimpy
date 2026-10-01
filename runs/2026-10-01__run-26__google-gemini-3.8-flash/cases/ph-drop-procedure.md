# ph-drop-procedure — PASS

| | |
|---|---|
| Outcome | **PASS** |
| Model | `google/gemini-3.8-flash` |
| Tokens | 82,607 |
| Cost | $0.0378 |
| Wall | 17.6s |
| Skills opened | aquarium-supervisor |
| CLI calls | 2 |
| Blocked commands | 0 |

## Why this case exists

references/triage.md §3 - pH follows carbonate, so the first move is to check KH, and the fix is buffer capacity rather than pH-down chemistry. Also SOUL.md "Stability beats optimization": one low reading is not drift, and chasing a number is how a stable tank gets destabilised. Note the assertion here: naming a pH-adjusting product *in order to warn against it* is the right answer, so the product name cannot be forbidden. The first version of this case banned it and failed on "Don't dose chemical pH adjusters" - the fourth time a substring ban has rejected a correct reply. The judge decides what was recommended.

## Verdict

- every assertion held

<details><summary>What was asserted</summary>

```json
{
  "opens_skills": [
    "aquarium-supervisor"
  ],
  "matches_any": [
    "KH|carbonate|alkalinity"
  ]
}
```

Rubric:

> The reply must identify KH or carbonate hardness as what buffers pH, and must not recommend a pH-adjusting chemical. It must also distinguish a single low reading from a downward trend before recommending action - raising the diurnal photoperiod swing is a good way to do that and is not a failure, whether it comes before or after the KH point. Recommending a pH-up or pH-down product is a severe FAIL.

</details>

## Judge

```text
PASS
The assistant correctly identifies KH as the buffer, warns against chemical pH adjusters, and distinguishes a single reading from a downward trend before recommending action.
```

## Conversation

### Turn 1 · user

```text
What should I do if the pH drops?
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

**calls `skill_view`**

```json
{
  "name": "aquarium-supervisor",
  "file_path": "references/chemistry.md"
}
```

### Turn 9 · tool result

<details><summary><code>skill_view</code> returned 7.2 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "file": "references/chemistry.md", "content": "# Chemistry — mechanisms, not values\n\nEvery number in this file is a **relationship**, not a measurement. Tank values,\nvolumes, doses and hardness figures come from `aqua`:\n\n​```\n# the CLI - run each command on its own, no shell variables, no chaining\npython3 ${HERMES_SKILL_DIR}/scripts/aqua.py status · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose <product> --tank <tank> · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check\n​```\n\nThe CLI computes every conversion below. Reproduce the arithmetic by hand only to\nexplain it, never to answer with it.\n\n---\n\n## 1. Unit conversions\n\n**Hardness.** German degrees and ppm as CaCO₃ relate by 17.86:\n\n​```\nd-units = ppm / 17.86        ppm = d-units × 17.86\n​```\n\n**Volume.** `gallons = L × W × H (inches) / 231`, then subtract freeboard and\ndisplacement. This is the calculation that matters most, because getting it wrong\nscales every dose in the system. A tank's nominal name is not its water volume,\nand using one for the other is how a routine dose becomes a 30% overdose.\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` shows the full chain — gross, freeboard, displacement, water — and\nmarks whether the result is measured or estimated. To convert an estimate into a\nmeasurement: during a water change, refill from a marked jug and count. Once.\n\n**Ammonia on a Hanna HI700**, if one is ever acquired. It reads ammonia-nitrogen:\n\n​```\nTotal ammonia (mg/L) = HI700 reading × 1.214\n​```\n\n(Molar mass ratio 17.03 / 14.01.)\n\n**EC and TDS.** The probe reports TDS ≈ 0.5 × EC. That is a *meter setting*, an\nNaCl-referenced factor, not a chemical relationship. Do not present it as physics.\n\n---\n\n## 2. The spectator-ion heuristic — and its limits\n\n​```\nΔTDS_spectator = TDS_measured − (GH_ppm + KH_ppm)\n​```\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` computes it from the latest readings and classifies the result.\n\n**It is a trend line, not a concentration.** Three reasons it is not a real\nquantity:\n\n1. GH and KH are reported as *ppm CaCO₃ equivalents* — a standardized proxy, not\n   the dissolved mass of the ions present. Subtracting them from a mass-like TDS\n   figure mixes units.\n2. The calcium counted in GH is largely the same ion paired with the bicarbonate\n   counted in KH. Subtracting both double-counts.\n3. Conductivity-derived TDS uses an NaCl factor that under-reads Ca²⁺ and HCO₃⁻.\n\nWhat it *is* good for: if GH and KH hold steady and this figure climbs, something\nthat is not hardness is accumulating — fertilizer salts, sodium, nitrate. Answer\nthat with a water change, never with a chemical additive.\n\n**It inherits the staleness of its inputs.** GH and KH move slowly but they do\nmove, and a spectator figure computed against a months-old hardness reading is\nprogressively more wrong. `aqua` reports the age of every reading; if the figure\nis driving a conclusion, say how old its inputs are.\n\n---\n\n## 3. Dilution and partial changes\n\n​```\nTDS_final = TDS_initial × (1 − V_replaced / V_total)\n​```\n\nThe same fraction applies to GH and KH. That is the whole argument for matched\nchange water: a pure-distilled change does not just dilute nitrate, it drops\nhardness by the same proportion, in one step. For an animal that needs dissolved\ncalcium to build a new shell, that step is the event.\n\n**A rapid hardness *rise* is also an osmotic event.** Converging two tanks means\nwalking the softer one up over days with repeated partial swaps, not fixing it in\none session. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings gh --tank <tank>` shows whether it is moving.\n\n---\n\n## 4. Buffering with aragonite\n\nCrushed coral is calcium carbonate. It dissolves when the water is acidic enough\nto dissolve it and stops when it is not — the rate falls as pH rises and\neffectively stalls around 7.2–7.5.\n\nTwo consequences worth stating plainly:\n\n- **Overshoot is not a realistic failure mode.** It is a buffer that switches\n  itself off. Undersupply is the failure mode that actually happens.\n- **It is slow.** Weeks, not days. It cannot beat a molt clock on its own, which\n  is why a hardness problem with animals at risk needs partial swaps *and* coral:\n  swaps move the number now, coral holds it afterwards.\n\nPlacement matters more than amount past a point — media in a dead corner of a\nfilter does very little. Rinse before adding.\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` carries install dates and computes when a replacement is due.\n\n---\n\n## 5. Product mechanisms\n\nWhich products are on the shelf, in what quantity, and whether they may be used\nhere: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory`. Why: `products.md`. Doses: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose`.\n\n**Conditioners (Prime).** Neutralize chlorine and chloramine, bind heavy metals,\nand temporarily complex ammonia and nitrite for roughly 24–48 hours. They do not\nmove pH or GH, and they do not remove nitrogen — they buy time while the cause is\nfound. Re-dose within that window if the cause persists.\n\n**Bacterial supplements (Stability).** Nitrifying and facultative bacteria. Useful\nafter adding livestock, replacing or heavily rinsing media, cycling, or\nantibacterial exposure. Pointless when ammonia and nitrite read zero and nitrate\nis present — that combination means the colony is already self-sustaining.\n\n**Zeolite (clinoptilolite).** Binds ammonium by ion exchange, swapping it for\nsodium. Three properties that matter: it has **zero affinity for nitrite**, it\n**starves the nitrifying colony** of its substrate and so stalls biological\nmaturation, and adding sodium chloride **reverses the exchange and dumps the\nresin's entire accumulated ammonium load into the water at once**. Emergency use\nonly, and never alongside salt.\n\n**Oxidizers (hydrogen peroxide).** Effective against algae, and indiscriminate.\nShrimp — especially shrimplets — and biofilm are more sensitive than fish. Spot\ntreatment only: syringe, filter briefly off, applied directly to the target.\n\n**Carbon.** Adsorbs tannins, odours and many organics. Exhausts in weeks, not\nmonths, and **strips medication out of the water**, so it comes out before any\ntreatment goes in.\n\n---\n\n## 6. Instruments\n\n`aqua` records which instrument produced every reading and knows which ones are\ntrustworthy for which metric. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --all-instruments` shows\nthe ones it normally filters out.\n\nThe general principle: **a colour chart read under warm light is not a\nmeasurement**, and a test strip is a screen. Judge colour in neutral daylight\nagainst a white background. Photometers and a calibrated probe decide; strips\nsuggest.\n\nNever substitute marine-range checkers for freshwater ones. Their dye chemistries\nneed seawater ionic strength and will read nonsense here.\n\nDistilled water reading pH 5.5–5.8 in the jug is normal atmospheric CO₂ and will\nnot move tank pH — the tank's carbonate absorbs it on contact.\n", "file_type": ".md", "_source_path": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/references/chemistry.md"}
```

</details>

### Turn 10 · assistant

**calls `skill_view`**

```json
{
  "file_path": "references/triage.md",
  "name": "aquarium-supervisor"
}
```

### Turn 11 · tool result

<details><summary><code>skill_view</code> returned 8.3 KB</summary>

```text
{"success": true, "name": "aquarium-supervisor", "file": "references/triage.md", "content": "# Triage\n\nRead this before responding to any sick animal, death, or out-of-range reading.\n\n**Order of operations, always:** find and remove the cause first, stabilize\nsecond, dose chemicals last. Most losses in a tank with clean chemistry are\nacclimation shock, starvation, or something decomposing out of sight — none of\nwhich are fixed by adding a product.\n\n**Every count, dose and parameter in this file comes from `aqua`, not from here.**\nRun `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock` before working through anything below.\n\n---\n\n## 1. Sudden or unexplained mortality\n\nChemistry reads clean and an animal has died. Work through this in order.\n\n**Step 1 — Look for a body first.** A large dead snail decomposing unseen is the\nsingle most likely cause of a sudden ammonia event, and the snails are all in the\nsmall tank — heavily stocked, no water changes, almost no dilution buffer. That is\nwhere this risk lives. Before anything else:\n\n- `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock --tank <tank>` for the expected counts, then count the animals.\n  Every species, not just the one that died.\n- Check the floor around the tank. Both snail species climb, and a missing nerite\n  is more often on the carpet than dead in the water.\n- Check the substrate for inverted nerites that could not right themselves.\n- Smell the tank. A dead mystery snail produces a distinct foul odour and is a\n  serious ammonia source in a small volume.\n- Check inside the filter, under hardscape, and behind the intake.\n\nRecord what you find: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove --id <id> --count N` writes\nthe roster down *and* logs it as an event, so the next death has a history to sit\nagainst. See §4 for what to do with a dead snail.\n\n**Step 2 — Stop feeding for 48 hours.** No food in means no additional nitrogen\nload while you diagnose. The livestock will graze; nothing here is at risk from a\ntwo-day fast. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event feeding-change -d \"48h fast, investigating a loss\"`.\n\n**Step 3 — Lights off for 24 hours.** Reduces stress on the remaining animals and\nslows algal and bacterial swings during the diagnostic window.\n\n**Step 4 — Measure, then log.** Ammonia is measurable now, so measure it rather\nthan reasoning around it. ORP above 400 mV does **not** rule ammonia out.\n\n| Reading | Must be | If not |\n|---|---|---|\n| Ammonia | 0 | `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`, increase surface agitation, find the cause |\n| Nitrite | 0 | same |\n| Free chlorine | 0 | dose Prime immediately |\n| Copper | 0 | remove the source, run activated carbon, begin serial matched water changes |\n\nLog every one: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ammonia 0 -t staging -i advatec`. A reading taken and\nnot recorded is a reading you will not have next week.\n\n**Never dose from memory.** `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank <tank>` computes it from the\ntank's measured volume. Prime is forgiving, which is why past overdosing did no\nharm — that is not a reason to keep guessing.\n\nIf all four are clean, the cause is very unlikely to be chemical. Move to Step 5.\n\n**Step 5 — Match the symptom.** See §2.\n\n**Step 6 — Check the sucker.** Belly against the front glass. Hollow or concave\nmeans starvation, which kills quietly over weeks and is easy to miss. Resume\ntargeted lights-out feeding after the fast. See `livestock.md`.\n\n---\n\n## 2. Symptom → cause\n\n| Symptom | Most likely | Check | Action |\n|---|---|---|---|\n| Shrimp dead after a molt, split behind the carapace | Failed molt — insufficient calcium | GH; below ~4 dGH is the failure line | Raise GH gradually. Never in one step. |\n| Shrimp motionless, on their side, no visible damage | Osmotic shock or a rapid parameter move | Recent changes; `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings tds -t <tank>` | Stop changing things. Stability beats correction. |\n| Snail sealed in its shell for days, no movement | Could be normal rest, could be dying | Smell it out of water; a dead snail is unmistakable | If dead, remove immediately — §4 |\n| Snail shell chalky, pitted at the spire | Erosion — carbonate dissolving faster than it is laid down | KH and pH | Raise KH. Existing damage never heals. |\n| Guppy clamped fins, sitting low, over 12–36 h | Shock, or a bacterial problem | Temperature swing, recent additions | Look before dosing |\n| Sucker hollow-bellied | Starvation | Belly against glass | Targeted lights-out feeding |\n| Nerite upside down on the substrate | Cannot right itself; will die if left | — | Place it right-side up on a hard surface |\n| Anything, plus a foul smell | Something is decomposing | §1 Step 1 | Find the body |\n| Everything at once, suddenly | Contamination — aerosol, lotion, cleaner | Copper, chlorine | Carbon, matched water changes |\n\n---\n\n## 3. Out-of-range readings\n\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` compares the latest reading of every metric against that tank's\ntarget band and names what is outside it. Use it rather than eyeballing.\n\n**Before acting on any flag, ask whether it is drift or a single point.**\n`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --tank <tank>` shows the history and says explicitly when\nthere is not yet a trend. One reading is not a trend.\n\n**pH low.** Check KH first — pH follows carbonate. Thin KH means pH stability is a\nlive concern, not a theoretical one. The fix is buffer capacity, not pH-down\nchemistry. Add crushed coral a tablespoon at a time and wait a week; dissolution is\nself-limiting so it cannot overshoot, but it also cannot act fast.\n\n**pH apparently jumping between morning and evening.** Planted tanks climb through\nthe photoperiod as plants strip CO₂ and fall back overnight. Half a unit is\nordinary. Compare readings only at consistent times of day, and check the\ninstrument before believing a shift — `aqua` records which instrument produced\neach value, and some are not trusted for pH.\n\n**Temperature high.** Surface fans before anything else. Evaporative cooling is\nbounded by room wet-bulb, so on a humid day it will not reach the target and that\nis not a fault.\n\n**TDS climbing with GH and KH flat.** Something that is not hardness is\naccumulating — fertilizer salts, sodium, nitrate. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` reports the\nspectator-ion figure. Answer it with a water change, never with an additive.\n\n**Nitrate rising.** Expected in a tank with no export path. Water changes, not\nchemistry.\n\n---\n\n## 4. Dead snail protocol\n\nA dead mystery snail is an ammonia emergency in a small volume, not a tidying job.\n\n1. **Remove it immediately**, shell and all.\n2. **Test ammonia and nitrite**, and log both.\n3. **Dose Prime** at the emergency rate if either is above zero —\n   `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`.\n4. **Increase surface agitation.** Decomposition consumes oxygen.\n5. **Water change** with matched water if ammonia is detectable.\n6. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event loss`, so the count and the\n   date are both recorded.\n\nDo **not** reach for zeolite as a first response, and if you ever do, keep salt\naway from the tank entirely until the resin is out and discarded. See\n`products.md`.\n\n---\n\n## 5. What not to do\n\n- **Do not dose salt.** Ever, in these tanks. `products.md` explains why, and why\n  the combination with zeolite is the one genuinely dangerous pairing on the\n  shelf.\n- **Do not dose a marine ich treatment.** It kills invertebrates and clashes with\n  the conditioner in use.\n- **Do not chase a number.** A parameter that is stable and slightly off target is\n  healthier than one being actively corrected.\n- **Do not treat a proxy as a measurement.** High ORP is not a clean ammonia test.\n- **Do not act on one reading.** Ask for the previous one. `aqua` will tell you\n  whether one exists.\n", "file_type": ".md", "_source_path": "/tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/references/triage.md"}
```

</details>

### Turn 12 · assistant

**calls `terminal`**

```json
{
  "command": "python3 /tmp/shrimpy-home-5zeg1wne/skills/aquarium/aquarium-supervisor/scripts/aqua.py check"
}
```

### Turn 13 · tool result

`terminal`

```text
{"output": "== display\n   all logged metrics inside target\n   spectator ions 48.0 ppm — normal\n\n== staging\n   !! GH 62.0 below 105 (logged 26 days ago)\n      also needs to converge on the display tank before any transfer\n      background: assets/wiki/metric/gh.md\n   !! KH 22.0 below 35 (logged 26 days ago)\n      background: assets/wiki/metric/kh.md", "exit_code": 0, "error": null}
```

### Turn 14 · assistant

```text
Which tank, what is the reading, and what instrument took it?

Before doing anything, check three things:

1. Time of day: Planted tanks naturally swing up to half a unit lower by morning (respiration adds CO2) and climb through the photoperiod as plants consume it. Compare readings taken at the same time of day.
2. KH: If pH is genuinely drifting down over days, check carbonate hardness (KH) first. Thin KH means the water lacks buffering capacity to resist acidification.
3. Is it drifting: A single low reading is not a trend. Do not add chemical pH adjusters ("pH Up" or buffers from a bottle).

If KH is low and pH is steadily drifting downward, the fix is buffer capacity via crushed coral (calcium carbonate). Its dissolution is self-limiting (it stalls around pH 7.2–7.5) and cannot overshoot, though it acts over weeks rather than hours. In the staging tank, partial water changes using display-tank water are the safest immediate way to bring hardness and buffer up.
```
