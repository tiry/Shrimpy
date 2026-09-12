---
title: Liquid reagent test kits
slug: liquid-reagent-kit
category: method
aqua_key: null
aliases:
  - "liquid kit"
  - "drop test"
  - "titration"
summary: Drop-count and colour-card chemistry — the workhorse, and its blind spots.
sources:
  - url: https://en.wikipedia.org/wiki/Titration
    title: Titration
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Colorimetry
    title: Colorimetry
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Liquid reagent test kits

Background on the measuring principle. Which kit is trusted for which metric is data —
run `aqua instruments`. What it last read is `aqua readings`.

## Two different tests in one box

A freshwater liquid kit bundles two methods that fail in different ways, and treating them
as one thing is a common mistake.

**Colour comparison** covers ammonia, nitrite, nitrate and phosphate. A reagent develops a
colour, and the reader matches it against a printed card. The output is a judgement, not a
measurement, and it is quantised to whatever steps the card prints.

**Drop-count titration** covers hardness and alkalinity. Reagent is added one drop at a
time until the sample changes colour; the count of drops is the result. This is a genuine
titration — a standard solution reacting with the analyte until an endpoint — and it is
considerably more trustworthy than colour matching, because the endpoint is a change of
state rather than a shade.

**So a kit's hardness result and its ammonia result do not deserve equal confidence**, even
though they come from the same box on the same afternoon.

## How colour comparison goes wrong

- **Lighting.** The card assumes neutral light. Warm indoor light shifts a reading toward
  the warm end of the scale, and a marginal result can be read as clear or as a problem
  depending on the bulb overhead. Compare in daylight, against white.
- **The reader.** Colour matching varies between people, and colour vision deficiency makes
  some of these scales unusable.
- **The gap between steps.** A card printing widely spaced values cannot express anything
  in between, and the eye rounds toward the nearer swatch — which is why a low but non-zero
  ammonia result and a true zero can look identical.
- **Timing and shaking.** Reagents specify both. The nitrate test in particular depends on
  vigorous agitation of one bottle, and under-shaken reagent reads low — the direction that
  reassures rather than warns.
- **Age.** Reagents degrade. An old kit drifts quietly.

## How drop-count titration goes wrong

- **Drop size.** The result is a count, so it assumes every drop is the same volume. Holding
  the bottle at an angle, or squeezing rather than letting drops fall, changes the answer.
- **Overshooting the endpoint.** The change is sudden. A drop added past it is a whole unit
  of error.
- **Sample volume.** The count only means anything against the specified volume, measured to
  the line rather than near it.

## Why it stays the primary method

Despite all of that, a liquid kit is the reference the others are checked against. It tests
the things that matter most for a shrimp tank and cannot be read any other cheap way, and
its titration results are solid. A strip is a screen; a probe is a continuous signal; the
liquid kit is the arbiter when they disagree.

Log every result with `aqua` — including the ones that look wrong. A single reading is not a
trend, and the kit's value shows up across repeats rather than in any one vial.
