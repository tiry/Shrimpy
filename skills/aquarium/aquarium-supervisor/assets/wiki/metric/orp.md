---
title: ORP — oxidation-reduction potential
slug: orp
category: metric
aqua_key: orp
aliases: ["ORP", "redox", "redox potential", "mV"]
summary: A bulk oxidising signal - and NOT an ammonia test.
sources:
  - url: https://en.wikipedia.org/wiki/Reduction_potential
    title: Redox potential
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# ORP — oxidation-reduction potential

What it is and what moves it. Current values are `aqua status`; what to do about a flag is
`references/triage.md`.

## The thing to get right first

**ORP does not tell you whether there is ammonia in the tank.** This is the most
consequential misconception attached to any metric here.

`SKILL.md` owns that rule and sets out why the electrode cannot serve as an ammonia test —
read it there rather than here, because a second copy of a safety rule is a copy that can
drift out of agreement with the first. The short version is that the reading is dominated by
something other than ammonia, and the instrument is not calibrated for it.

Ammonia is directly measurable. Measure it — see `assets/wiki/metric/ammonia.md`.

## What it is

The tendency of the water's chemistry to gain or lose electrons, in millivolts. A higher
value means more oxidising conditions. It is a genuine physical quantity and a real
electrode reading; the problem is only what people infer from it.

What it is honestly good for is **gross organic load**: a sustained fall suggests something
substantial is decomposing and consuming oxidising capacity — a dead animal that has not
been found, a large uneaten feed, a failing filter. `SKILL.md` states how that differs from
what the biofilter is doing.

Treat it as a **trend on one tank with one probe**. Absolute values are not comparable
between instruments or between setups.

## What raises it

- **Dissolved oxygen** — surface agitation, an open lid, fans, cooler water.
- **Removing organic load**: a water change, siphoning detritus, finding the dead animal.
- **Oxidisers** such as hydrogen peroxide or ozone. `references/chemistry.md` covers why
  peroxide is indiscriminate and shrimp are among the sensitive parties.

## What lowers it

- **Decomposition** of anything organic — the signal worth acting on.
- **Falling oxygen**: a surface film, warm water, a stopped filter, heavy stocking. A
  surface film from an oil-based remedy is a documented case; see
  `assets/wiki/product/melafix.md`.
- **A dirty or ageing electrode**, which is an instrument fault rather than a water change.
  See `assets/wiki/method/electrode-pen.md`.

## What not to do

Do not act on an absolute number, do not compare it against someone else's tank, and do not
let a reassuringly high reading substitute for an ammonia or nitrite test.
