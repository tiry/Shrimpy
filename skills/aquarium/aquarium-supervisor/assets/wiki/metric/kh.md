---
title: KH — carbonate hardness
slug: kh
category: metric
aqua_key: kh
aliases: ["KH", "carbonate hardness", "alkalinity", "buffer", "dKH"]
summary: Buffering capacity - the metric that decides whether pH holds.
sources:
  - url: https://en.wikipedia.org/wiki/Alkalinity
    title: Alkalinity
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Buffer_solution
    title: Buffer solution
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# KH — carbonate hardness

What it is and what moves it. The bands this system targets are `aqua check`; what a
species tolerates is `aqua species`; what to do about a flag is `references/triage.md`.

## What it is

The water's **capacity to neutralise acid** — carbonate and bicarbonate, measured as an
equivalent concentration of calcium carbonate. It is reported either in ppm or in German
degrees, related by 17.86 (`references/chemistry.md`).

KH is not a nutrient and no animal needs a particular KH for its own sake. **What it does
is hold pH still.** Acid enters the water constantly from respiration, decomposition and
nitrification; carbonate consumes it. Thin KH means each of those inputs moves pH further,
and a tank with almost no KH can swing between morning and night far more than its keeper
expects.

This is why "the pH keeps moving" is usually a KH question. See
`assets/wiki/metric/ph.md`.

## What raises it

- **Dissolving carbonate minerals.** Aragonite — crushed coral — is the standard route, and
  it is self-regulating: dissolution slows as pH rises and effectively stops once the water
  is no longer acidic enough to attack it. It is also slow, working over weeks, which is why
  it cannot rescue an animal on a molt clock by itself. `references/chemistry.md` has the
  mechanism and `aqua tanks` tracks what is installed.
- **Bicarbonate salts**, which act immediately rather than over weeks. Fast is not obviously
  better here — see below.
- **Partial changes with harder water**, which move the number now while coral holds it
  afterwards.

## What lowers it

- **Nitrification**, continuously. The biofilter consumes alkalinity converting ammonia to
  nitrate, so a working tank depletes KH on its own and a tank with no replenishment drifts
  down.
- **Dilution with soft or distilled water.** A partial change lowers KH by the same fraction
  of the volume replaced — `references/chemistry.md` has the arithmetic.
- **Acid production** from decomposition and CO₂.

## What not to do

**Do not raise it fast.** A rapid change in dissolved mineral is an osmotic event in its own
right, and for shrimp that is most dangerous mid-moult. Walk it up over days with repeated
partial swaps rather than correcting it in one session. `references/triage.md` is explicit
about this.

**Do not confuse it with GH.** They are separate measurements of different ions and they
move independently — water can be high in one and low in the other. See
`assets/wiki/metric/gh.md`.

**Do not read it from a strip** when the value is driving a decision. Strips screen; the
titration in a liquid kit or a photometric checker decides. See
`assets/wiki/method/liquid-reagent-kit.md`.
