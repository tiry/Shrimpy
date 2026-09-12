---
title: Colorimetric checkers
slug: colorimetric-checker
category: method
aqua_key: null
aliases:
  - "checker"
  - "colorimeter"
  - "Hanna checker"
summary: Reagent plus photometer — the most accurate hobby option, and its limits.
sources:
  - url: https://en.wikipedia.org/wiki/Colorimetry
    title: Colorimetry
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Titration
    title: Titration
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Colorimetric checkers

Background on the measuring principle. Which device is trusted for which metric is data —
run `aqua instruments`.

## What it actually measures

A handheld checker replaces the human eye in a reagent test. A measured sample gets a
measured reagent; the reagent develops a colour whose intensity tracks the analyte; a
fixed-wavelength LED shines through the vial and a photodetector measures how much light
is absorbed. The device reports a number derived from that absorbance.

The gain over a colour card is real and worth stating plainly: **the comparison step stops
being a judgement.** Two people reading the same vial against a printed chart routinely
disagree, and the same person disagrees with themselves under different lighting. A
photodetector does not.

That is also the whole of the advantage. The chemistry is the same reagent chemistry as the
liquid kit, so it inherits the same failure modes — see
`assets/wiki/method/liquid-reagent-kit.md`.

## How these go wrong

- **Expired or heat-damaged reagent.** The colour still develops; it develops to the wrong
  intensity. This is silent, and it is the most common cause of a checker that is confidently
  wrong.
- **Timing.** The reaction is read at a specified point in its development. Reading early or
  late is reading a different reaction.
- **A scratched, smeared or wet vial.** The instrument measures light transmission, so
  anything on the glass is indistinguishable from something in the water.
- **Out-of-range samples.** Every checker has a working range. Past its top the response
  flattens and a very high value reads as a merely high one, which is the dangerous
  direction of error.
- **Zeroing against the wrong blank.** The instrument is calibrated against an untreated
  sample of the same water. Zeroing against something else builds the error into every
  subsequent reading.

## Reading the result honestly

A checker reports more decimal places than the method justifies. Precision is not accuracy:
repeatability comes from the photometer, but correctness depends on reagent condition,
timing and technique, none of which the display knows about. A number that disagrees
sharply with a trend deserves a second run with fresh reagent before it is believed.

`aqua` records every reading with its instrument, so a checker's history is separable from
everything else's. Log the result — including a suspicious one — and let the trend decide.
