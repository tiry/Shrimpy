---
title: Observed and reported values
slug: observation
category: method
aqua_key: null
aliases:
  - "observed"
  - "reported"
  - "from memory"
summary: What a number with no instrument behind it is worth.
sources:
  - url: https://en.wikipedia.org/wiki/Anecdotal_evidence
    title: Anecdotal evidence
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Observed and reported values

Background on a pseudo-instrument. `aqua` records "observed" as an instrument in its own
right so that a value with no device behind it is never mistaken for one that has a device
behind it. Run `aqua instruments` to see how it is treated.

## Why it is recorded as an instrument at all

The alternative is worse. A number mentioned in conversation and written down without
provenance becomes indistinguishable from a calibrated reading the moment it enters the
history. Recording the source as `observed` keeps the distinction permanently, so a trend
can exclude it and a reader can weigh it.

**An observation is not worthless.** Some of the most important information about a tank is
only ever observational: that the shrimp were all on the glass this morning, that a snail
has not moved since yesterday, that the water smelled different after a change. None of
that has units and all of it is evidence.

## What it is good for

- **Things no instrument measures.** Behaviour, colour, activity, clarity, smell, whether
  anyone is eating. A shrimp colony's behaviour is a fast and sensitive indicator, and it is
  available continuously, which no test kit is.
- **A timestamp on an event.** When something was added, changed, moved or noticed.
- **Corroboration.** An observation that agrees with an instrument raises confidence in both.

## Where it misleads

- **Recall drifts.** A value remembered from earlier in the week is reconstructed, not
  recalled, and it reconstructs toward what was expected.
- **Rounding toward the target.** A remembered number lands on a round figure near where it
  was supposed to be.
- **A missing timestamp.** An observation with no time attached cannot be placed in a trend,
  and a reading whose age is unknown is treated as unknown rather than as current — see
  `references/triage.md`.
- **Second-hand numbers.** A value someone read off a display and repeated has lost the
  instrument, the units and the settling time along the way.

## The rule this supports

A value from a real instrument is logged against that instrument. A value from memory,
conversation or a photograph is logged as observed, with whatever timestamp is actually
known. `aqua` keeps observed values out of trend calculations, so recording one honestly
costs nothing and pretending it was measured costs the trend.

If the source of a number is genuinely unclear, that is itself worth asking about before it
is written down. A logged number carries authority it may not deserve.
