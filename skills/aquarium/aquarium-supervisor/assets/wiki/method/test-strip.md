---
title: Multi-parameter test strips
slug: test-strip
category: method
aqua_key: null
aliases:
  - "strips"
  - "dip strip"
  - "9-in-1"
summary: Fast, cheap, broad — and the least trustworthy thing in the cabinet.
sources:
  - url: https://en.wikipedia.org/wiki/Colorimetry
    title: Colorimetry
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Multi-parameter test strips

Background on the measuring principle. Which metrics a given strip is trusted for is data —
run `aqua instruments`, which also records the ones it is explicitly **not** trusted for.

## What it actually measures

A strip carries several reagent pads on one plastic stick. Dipped and withdrawn, each pad
develops a colour that is compared against a printed chart. It is colour-comparison
chemistry with all the reagent immobilised in advance.

Everything good about strips follows from that: no measuring, no drop counting, no vials,
several metrics in under a minute. Everything bad follows from it too.

## Why the results are weak

- **The pads are tiny and the scale is coarse.** A small patch of colour read against
  widely spaced swatches cannot resolve much. Strips are a screen, not a measurement.
- **Cross-contamination between pads.** Water runs along the stick, carrying reagent from
  one pad onto its neighbour. This is why the instruction to hold the strip horizontally
  and shake off the excess is not fussiness — it is the difference between reading a pad and
  reading two pads mixed.
- **Timing is per-pad and they differ.** Each pad has its own development window, and they
  do not coincide. Reading the whole strip at one moment means reading some pads early and
  others late, which is unavoidable and is why a strip is approximate by construction.
- **Humidity kills the tube.** The pads are hygroscopic. An open or poorly sealed tube
  degrades every strip inside it, and the degradation is invisible until the results are
  compared with something better.
- **Lighting and the reader**, exactly as for a colour card. See
  `assets/wiki/method/liquid-reagent-kit.md`.

## What strips are genuinely good for

Two things, and they are worth having:

1. **Detecting a substance that should be completely absent.** A strip that indicates any
   free chlorine, or any copper, has told you something actionable even though the number is
   unreliable. Copper matters enormously in a shrimp tank — see
   `assets/wiki/species/neocaridina.md`.
2. **A fast look before a water change**, to decide whether a proper test is warranted.

## What they must not be used for

Anything where the *value* drives a decision. A strip that suggests hardness or pH is near a
limit is a prompt to run the liquid kit, never a result to act on, and a strip result that
contradicts a trusted instrument loses.

`aqua` enforces this: an instrument is recorded as trusted or not trusted per metric, and
untrusted readings are kept out of the trend rather than silently averaged in. Log the strip
result anyway — a clear positive for something that should be zero is worth keeping even
when the magnitude is not.
