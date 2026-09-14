---
title: pH
slug: ph
category: metric
aqua_key: ph
aliases: ["pH", "acidity", "alkaline", "acidic"]
summary: Acidity on a log scale - a symptom of buffering, not a dial.
sources:
  - url: https://en.wikipedia.org/wiki/PH
    title: pH
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Buffer_solution
    title: Buffer solution
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# pH

What it is and what moves it. What the tanks currently read is `aqua status`; what to do
about a flagged value is `references/triage.md`.

## What it is

A **logarithmic** scale of hydrogen-ion activity. Each whole unit is a tenfold change in
acidity, so a shift from 7.0 to 6.0 is ten times more acidic, and 7.0 to 5.0 is a hundred
times. This is the single most misread property of the number: a swing that looks small
written down is not small chemically, and averaging pH values is meaningless arithmetic.

pH is best understood as a **readout of the water's buffering**, not as an independent
property. In a freshwater aquarium what holds it steady is carbonate and bicarbonate —
see `assets/wiki/metric/kh.md`. Ask what the buffer is doing before asking what the pH is
doing.

## What raises it

- **Dissolving carbonate.** Aragonite (crushed coral) raises KH, and pH follows. The
  mechanism, including why it cannot overshoot, is in `references/chemistry.md`.
- **Photosynthesis.** Plants strip CO₂ during the photoperiod, which removes carbonic acid
  and lifts pH through the day.
- **Surface agitation**, when the water is CO₂-rich relative to air — outgassing CO₂ raises
  pH.

## What lowers it

- **Respiration and decomposition.** Animals, bacteria and decaying matter produce CO₂,
  which forms carbonic acid. This runs continuously and is why pH falls overnight.
- **Nitrification.** Converting ammonia to nitrate consumes alkalinity, so an active
  biofilter pushes pH down over time and eats the buffer doing it.
- **Dilution with soft water.** Distilled top-off and pure-water changes remove buffer along
  with everything else, which lowers the tank's ability to hold pH rather than lowering pH
  directly.
- **Tannins** from wood and leaf litter.

## What not to do

**Do not chase pH with pH-adjusting chemicals.** They move the number without touching the
buffer, so it drifts straight back, and the round trip is a swing the animals pay for.
Stability beats the textbook figure — an animal is far better off at a steady value slightly
off target than at a correct one that is being pushed around.

**A morning and an evening reading are not comparable.** The daily cycle above is not
drift, and `references/triage.md` gives the rule for how far apart the two ends of a day can
legitimately sit before it counts as one.

**Check the instrument before believing a shift.** A pH electrode drifts as it ages and is
least reliable in soft, low-ionic-strength water — see
`assets/wiki/method/electrode-pen.md`. Which instruments are trusted for pH is recorded in
`aqua instruments`.
