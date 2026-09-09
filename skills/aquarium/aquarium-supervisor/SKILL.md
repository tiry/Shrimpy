---
name: aquarium-supervisor
description: "Tiry's aquariums: shrimp, guppies, water chemistry, alerts"
version: 2.0.0
author: tairy-agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [aquarium, shrimp, neocaridina, guppies, water-chemistry, aquadirector]
---

# Aquarium Supervisor

Two tanks, one keeper (Tiry). **The facts live in a database, not in this file.**
This file is the rules for reading and acting on them.

## When to Use

Load this for **anything** touching Tiry's aquariums — the tanks, the animals, the
water, the products, or the sensor. Casual phrasing counts: "my shrimp look
weird", "is 6.6 too low", "lost a guppy overnight". A bare paste of sensor output
with no question attached counts. So does a question from someone else in the
household who does not know the setup.

Three things to settle before answering anything specific:

1. **Which tank.** They differ about sixfold in volume; a dose or a stocking
   judgment right for one is badly wrong for the other. `aqua` refuses to guess.
2. **Is the number measured, and when.** You cannot read the sensor yourself.
3. **Is it drifting, or merely not the textbook number.** Only drift justifies
   action.

Do **not** use this for general aquarium questions unconnected to these two
tanks — answer those from ordinary knowledge, without pretending the specifics
here apply.

---

## The `aqua` CLI — run this first

The CLI lives at `${HERMES_SKILL_DIR}/scripts/aqua.py`. **Run each command on its
own, exactly as written below.** Do not set a shell variable for the path, and do
not chain commands with `;` or `&&` — one invocation per terminal call.

```
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status
```

**Start every aquarium conversation with that.** It is one call and it returns the
whole picture: volumes, rosters, the latest reading of every metric with its age
and trend, anything outside target, and the open questions. Do it once per
conversation, not once per turn.

This replaces the "never re-ask what is here" rule. Nothing about these tanks is
in your head or in this file — it is in the data, and it is current. Reciting a
number from memory is the failure this design exists to prevent.

### Reading

```
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status --tank staging
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock --tank display
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock --species neocaridina
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py species neocaridina
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory --class never
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings ph --tank display
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank staging
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py questions
```

### Writing — record what you are told

Tiry telling you a number is the only way a number gets in. **Log it.** An
unlogged reading is one nobody can plot and one you will not have next week.

```
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ph 6.91 --tank display --instrument kactoily
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log gh 75 --tank staging --instrument hi735 --note "after first swap"
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log phosphate 0.25 --tank display --instrument advatec --min 0 --max 0.25
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event water-change --tank staging --detail "15% with display water"
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change add --id display-neocaridina --count 1
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove --id staging-neocaridina --count 1
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory-change open prime
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py question answer --id 4 --text "6 female, 3 male"
```

Use `--min` and `--max` when the reading was a band rather than a point — a colour
chart between two swatches is a band, and flattening it invents precision.

**A species question is not a tank question.** What an animal *tolerates* comes
from `aqua species`; what these tanks *currently read* comes from `aqua status`
and `aqua check`. Do not answer one with the other, and do not answer either from
memory — a plausible wrong range is indistinguishable from a right one to someone
asking because they do not know.

**Record roster changes as they are mentioned.** `livestock-change add --id <id>
--count N` needs nothing else for a group that already exists, and dates the
change so "how long have they been in there" stops being unanswerable.

`--instrument` matters. Some instruments are not trusted for some metrics — the
strip pH pad reads demonstrably low, the liquid kit's pH is unreliable under warm
light — and `aqua` will say so and keep those readings out of the trend while
still recording them.

### Reporting

```
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py export --format csv
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py plot ph --tank display
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py report
```

Tell Tiry the path it prints. Offer a report when a trend question comes up, not
reflexively.

### Rules for using it

- **Never state a number you did not just read from `aqua` or from Tiry in this
  conversation.** If you are unsure whether it is current, run `status` again.
- **Never compute a dose yourself.** `aqua dose` derives it from measured volume
  and shows its basis. Every historic dosing error here came from arithmetic done
  in prose.
- **`status` tells you how stale the data is.** If it says the newest reading is
  weeks old, say so before answering, not after.
- If a command fails or the data looks wrong, run `doctor`.

---

## You cannot see or touch the tanks

You run in the cloud. The Kactoily sensor, the `aquadirector` CLI and the Eheim
feeder are all on Tiry's LAN and unreachable from where you execute. Having a
terminal does not change that — the tool is not installed here and the sensor is
not routable.

The `aqua` CLI above is different: it is part of this skill, it runs where you
run, and it reads a database, not a tank.

So:

- **Never run, or offer to run, an `aquadirector` command.** Ask Tiry to run it
  and paste the output — then log what he pastes.
- **Never claim to have checked anything.**
- Name the exact command you want. `aquadirector sensor status` is a five-second
  favour; "can you check the tank?" is a chore.

Commands to **ask for**, not to run:

```
aquadirector dashboard --output json          # the most useful paste: every field, no transcription
aquadirector sensor status [--watch 30s]      # Kactoily 7-in-1
aquadirector feeder status | feed             # Eheim autofeeder+
aquadirector feeder schedule clear --day tue  # a fasting day
aquadirector alerts check --notify
```

The Kactoily also reports to the **SmartLife** app (Tuya), which has a History
view. A screenshot of it is often the fastest way to answer "is this drifting?",
and Tiry can send one from a phone.

**The tool is reef-oriented.** Its salinity and SG readings carry no information
in freshwater. Ignore them.

### Handling pasted sensor output

This is the main way you see the tanks, so treat a paste as the event it is.

**Which tank a paste belongs to.** The Kactoily probe lives in one tank —
`aqua tanks` says which. A bare paste of sensor output is from that tank unless
Tiry says otherwise. He does sometimes drop the probe into the other tank to
track a swap, and will say so when he does. Do not stall a paste to ask; log it,
and say which tank you logged it against so a correction is one line.

1. **Log it.** Every value, with `--instrument` and `--at` if the paste carries a
   timestamp. Do this before commenting on it.
2. `aqua` gives you the prior value and the delta for each. Name only what moved.
3. Run `check` for the target comparison rather than eyeballing it.
4. **A paste has no timestamp unless Tiry gives one.** If the reading is doing
   real work in your answer, ask when it was taken — planted tanks swing pH
   through the photoperiod, so the hour matters as much as the number.
5. One reading is not a trend. `aqua` will tell you when there isn't one yet.


---

## Decision rules

**Stability beats optimization.** Ask whether a reading is *drifting* or merely
*not the textbook number*. Only drift justifies action. A parameter that is stable
and slightly off target is healthier than one being actively corrected.

**Rules have scope, and the scope is per tank.** A caution that is right for one
tank is not a general law. The clearest example: crushed coral. The display tank
is near its pH target and climbing on its own, so more media there risks
overshooting something the existing coral will reach unaided. The staging tank is
below target on both GH and KH and undersupplied with media — there, adding coral
is correct. Check `aqua status` before applying either.

**Aragonite dissolution is self-limiting.** The rate falls as pH rises and
effectively stalls around 7.2–7.5, so coral is a buffer that stops working once it
is no longer needed. Overshoot is not a realistic failure mode; undersupply is.

**Prefer the cheap check first, and the mechanical fix over the chemical one.**
Move the probe rather than spend a reagent. Remove the uneaten food rather than
dose something. Reach for a bottle last.

**Telemetry is not the tank.** Plenty of questions are answered by looking at the
animal. A sucker's belly against the glass says more about whether it is eating
than any parameter will. Say "go look" when looking is the answer.

**ORP does not tell you whether there is ammonia.** Tiry has been told otherwise.
It is not reliable and must not substitute for an ammonia test:

- ORP measures net redox potential, which in an aerated tank is dominated by
  dissolved oxygen. An open lid, surface fans and heavy agitation pin it high more
  or less regardless of what else is dissolved.
- Ammonia at spike concentrations is a trace reductant, easily swamped in a mixed
  electrode potential.
- The probe is uncalibrated for ORP, and ORP electrodes drift over months.
- A tank can carry 1 ppm ammonia at 440 mV.

High ORP is genuinely reassuring about *gross organic load* — nothing large is
rotting — which is a different question from whether the biofilter is keeping up.
Ammonia is measurable now; measure it.

**Never invent a number, and never round one into a decision.** `aqua` reports
bands as bands (`0.00-0.25`) and marks estimated volumes as estimated. Carry that
through instead of flattening it.

---

## Water changes

The current regime is distilled top-off only, no water changes, in either tank —
check `aqua tanks` for what is actually recorded.

Top-off with 0 TDS water is correct and should continue: it replaces evaporated
water without adding minerals. But it is not maintenance. **Evaporation removes
nothing.** Nitrate, phosphate, dissolved organics, potassium and sodium have no
export path except plant uptake.

- **Start weekly changes as habit rather than rescue**, sized to the tank. The
  staging tank's stocking makes this more urgent than the display's.
- **Matched water, not pure.** A pure-distilled change drops GH and KH by the same
  fraction as the volume replaced, in one step — the rapid osmotic move that
  triggers emergency molts. Match within about 1 °C and 20 ppm TDS.
- **Display-tank water is the best source for the staging tank**: harder,
  temperature-matched, biologically clean, free, and it converges the two tanks,
  which is needed before any transfer regardless.
- **A rapid GH *rise* is its own osmotic event.** Walk it up over days.
- Tap water is unmeasured. If it tests close to the display tank on the Hanna
  checkers, dechlorinated tap is simplest. Otherwise remineralize distilled.

Raise this once when relevant, then treat it as a known choice.

---

## Routine

### Feeding
- **Guppies:** once daily, a pinch, gone in 30–60 s. Verify against consumption,
  not the schedule.
- **Sucker and display shrimp:** every 2–3 days at lights-out, half a sinking
  spirulina or herbivore wafer. Siphon the remainder after 2–3 hours.
- **Staging tank:** mystery snails take sinking vegetable pellets, blanched
  zucchini or spinach. Nerites need biofilm and refuse prepared food — the tank is
  planted, so there is grazing surface, but a young setup carries thin biofilm.
  Judge by animal condition. **Uneaten food matters far more here** — four gallons
  has almost no buffer. Remove it.
- **One fast day per week.** Tiry clears it on the feeder.

### Maintenance
- Rinse the mechanical sponge in **discarded tank water only**, never tap.
- Replace 50% of the crushed coral every 6–9 months. `aqua tanks` carries the
  install dates and computes when.
- Test GH and KH monthly on the Hanna checkers, in **both** tanks, same session —
  and log both.

### Acclimation (staging → display)
1. Confirm both tanks read close on GH, KH and pH — `aqua check` and
   `aqua readings gh` for each. That match is the whole point of the staging tank.
2. Float 15–20 min for temperature.
3. Drip or ladle ¼ cup receiving-tank water every 5–10 min over 45–60 min until
   the holding volume triples.
4. Net or hand-transfer. **Discard all transit water.**
5. Place nerites right-side up on rock, wood or glass.
6. **Before moving any snail into the display tank, seal its lid gaps and confirm
   at least an inch of headspace.** Those requirements travel with the snails.
7. `aqua livestock-change move` afterwards, so the rosters stay true.

---

## When something is wrong

`references/triage.md` first for any sick, dying or dead animal or out-of-range
reading. `references/chemistry.md` for the mechanisms behind the numbers.
`references/livestock.md` for anything species-specific.
`references/products.md` for why a product is or is not usable here.

Read them for *reasoning*. Read `aqua` for *values*.
