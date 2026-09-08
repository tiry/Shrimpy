# Triage

Read this before responding to any sick animal, death, or out-of-range reading.

**Order of operations, always:** find and remove the cause first, stabilize
second, dose chemicals last. Most losses in a tank with clean chemistry are
acclimation shock, starvation, or something decomposing out of sight — none of
which are fixed by adding a product.

**Every count, dose and parameter in this file comes from `aqua`, not from here.**
Run `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock` before working through anything below.

---

## 1. Sudden or unexplained mortality

Chemistry reads clean and an animal has died. Work through this in order.

**Step 1 — Look for a body first.** A large dead snail decomposing unseen is the
single most likely cause of a sudden ammonia event, and the snails are all in the
small tank — heavily stocked, no water changes, almost no dilution buffer. That is
where this risk lives. Before anything else:

- `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock --tank <tank>` for the expected counts, then count the animals.
  Every species, not just the one that died.
- Check the floor around the tank. Both snail species climb, and a missing nerite
  is more often on the carpet than dead in the water.
- Check the substrate for inverted nerites that could not right themselves.
- Smell the tank. A dead mystery snail produces a distinct foul odour and is a
  serious ammonia source in a small volume.
- Check inside the filter, under hardscape, and behind the intake.

Record what you find: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove --id <id> --count N` writes
the roster down *and* logs it as an event, so the next death has a history to sit
against. See §4 for what to do with a dead snail.

**Step 2 — Stop feeding for 48 hours.** No food in means no additional nitrogen
load while you diagnose. The livestock will graze; nothing here is at risk from a
two-day fast. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event feeding-change -d "48h fast, investigating a loss"`.

**Step 3 — Lights off for 24 hours.** Reduces stress on the remaining animals and
slows algal and bacterial swings during the diagnostic window.

**Step 4 — Measure, then log.** Ammonia is measurable now, so measure it rather
than reasoning around it. ORP above 400 mV does **not** rule ammonia out.

| Reading | Must be | If not |
|---|---|---|
| Ammonia | 0 | `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`, increase surface agitation, find the cause |
| Nitrite | 0 | same |
| Free chlorine | 0 | dose Prime immediately |
| Copper | 0 | remove the source, run activated carbon, begin serial matched water changes |

Log every one: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ammonia 0 -t staging -i advatec`. A reading taken and
not recorded is a reading you will not have next week.

**Never dose from memory.** `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank <tank>` computes it from the
tank's measured volume. Prime is forgiving, which is why past overdosing did no
harm — that is not a reason to keep guessing.

If all four are clean, the cause is very unlikely to be chemical. Move to Step 5.

**Step 5 — Match the symptom.** See §2.

**Step 6 — Check the sucker.** Belly against the front glass. Hollow or concave
means starvation, which kills quietly over weeks and is easy to miss. Resume
targeted lights-out feeding after the fast. See `livestock.md`.

---

## 2. Symptom → cause

| Symptom | Most likely | Check | Action |
|---|---|---|---|
| Shrimp dead after a molt, split behind the carapace | Failed molt — insufficient calcium | GH; below ~4 dGH is the failure line | Raise GH gradually. Never in one step. |
| Shrimp motionless, on their side, no visible damage | Osmotic shock or a rapid parameter move | Recent changes; `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings tds -t <tank>` | Stop changing things. Stability beats correction. |
| Snail sealed in its shell for days, no movement | Could be normal rest, could be dying | Smell it out of water; a dead snail is unmistakable | If dead, remove immediately — §4 |
| Snail shell chalky, pitted at the spire | Erosion — carbonate dissolving faster than it is laid down | KH and pH | Raise KH. Existing damage never heals. |
| Guppy clamped fins, sitting low, over 12–36 h | Shock, or a bacterial problem | Temperature swing, recent additions | Look before dosing |
| Sucker hollow-bellied | Starvation | Belly against glass | Targeted lights-out feeding |
| Nerite upside down on the substrate | Cannot right itself; will die if left | — | Place it right-side up on a hard surface |
| Anything, plus a foul smell | Something is decomposing | §1 Step 1 | Find the body |
| Everything at once, suddenly | Contamination — aerosol, lotion, cleaner | Copper, chlorine | Carbon, matched water changes |

---

## 3. Out-of-range readings

`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` compares the latest reading of every metric against that tank's
target band and names what is outside it. Use it rather than eyeballing.

**Before acting on any flag, ask whether it is drift or a single point.**
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --tank <tank>` shows the history and says explicitly when
there is not yet a trend. One reading is not a trend.

**pH low.** Check KH first — pH follows carbonate. Thin KH means pH stability is a
live concern, not a theoretical one. The fix is buffer capacity, not pH-down
chemistry. Add crushed coral a tablespoon at a time and wait a week; dissolution is
self-limiting so it cannot overshoot, but it also cannot act fast.

**pH apparently jumping between morning and evening.** Planted tanks climb through
the photoperiod as plants strip CO₂ and fall back overnight. Half a unit is
ordinary. Compare readings only at consistent times of day, and check the
instrument before believing a shift — `aqua` records which instrument produced
each value, and some are not trusted for pH.

**Temperature high.** Surface fans before anything else. Evaporative cooling is
bounded by room wet-bulb, so on a humid day it will not reach the target and that
is not a fault.

**TDS climbing with GH and KH flat.** Something that is not hardness is
accumulating — fertilizer salts, sodium, nitrate. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` reports the
spectator-ion figure. Answer it with a water change, never with an additive.

**Nitrate rising.** Expected in a tank with no export path. Water changes, not
chemistry.

---

## 4. Dead snail protocol

A dead mystery snail is an ammonia emergency in a small volume, not a tidying job.

1. **Remove it immediately**, shell and all.
2. **Test ammonia and nitrite**, and log both.
3. **Dose Prime** at the emergency rate if either is above zero —
   `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime -t <tank> --scenario emergency`.
4. **Increase surface agitation.** Decomposition consumes oxygen.
5. **Water change** with matched water if ammonia is detectable.
6. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove` and `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py event loss`, so the count and the
   date are both recorded.

Do **not** reach for zeolite as a first response, and if you ever do, keep salt
away from the tank entirely until the resin is out and discarded. See
`products.md`.

---

## 5. What not to do

- **Do not dose salt.** Ever, in these tanks. `products.md` explains why, and why
  the combination with zeolite is the one genuinely dangerous pairing on the
  shelf.
- **Do not dose a marine ich treatment.** It kills invertebrates and clashes with
  the conditioner in use.
- **Do not chase a number.** A parameter that is stable and slightly off target is
  healthier than one being actively corrected.
- **Do not treat a proxy as a measurement.** High ORP is not a clean ammonia test.
- **Do not act on one reading.** Ask for the previous one. `aqua` will tell you
  whether one exists.
