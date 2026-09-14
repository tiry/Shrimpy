---
title: GH — general hardness
slug: gh
category: metric
aqua_key: gh
aliases: ["GH", "general hardness", "hardness", "dGH", "calcium", "magnesium"]
summary: Dissolved calcium and magnesium - what a shell and a shrimp cuticle are built from.
sources:
  - url: https://en.wikipedia.org/wiki/Hard_water
    title: Hard water
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# GH — general hardness

What it is and what moves it. What a species needs is `aqua species`; what these tanks read
is `aqua status`; what to do about a flag is `references/triage.md`.

## What it is

The concentration of **dissolved divalent cations** — principally calcium and magnesium —
reported as a calcium-carbonate equivalent, in ppm or German degrees (related by 17.86, see
`references/chemistry.md`).

Unlike KH, this one is consumed as a **material**. It is what a snail builds its shell from
and what a shrimp draws on to calcify a new cuticle after each moult. That makes it the
hardness measurement with a direct biological floor: below a certain point the animal
cannot complete a moult, and the failure appears without warning as a split behind the
carapace. `aqua species neocaridina` carries that floor — it is data, not prose, and it is
not repeated here.

Animals that moult and animals that build shells are drawing this down continuously. A tank
with no replenishment path is a tank where GH falls.

## What raises it

- **Dissolving calcium and magnesium minerals** — aragonite and crushed coral supply
  calcium carbonate, raising GH and KH together. Slow and self-limiting;
  `references/chemistry.md` has the mechanism.
- **Remineralising salts** designed for the purpose, which raise GH with a controlled
  calcium-to-magnesium ratio and act immediately.
- **Partial changes with harder water.** In a two-tank system the harder tank is often the
  best source, because it is also temperature-matched and biologically mature.

## What lowers it

- **Uptake by the animals**, permanently, into shells and exoskeletons.
- **Dilution.** Distilled top-off replaces evaporated water without returning minerals, so
  GH falls as a fraction of any water replaced with softer water.
- **Precipitation** at high pH, which takes calcium out of solution.

## What not to do

**Do not raise it in one step.** A rapid rise is as much an osmotic event as a rapid fall,
and walking it up over days is the standard advice for exactly that reason —
`references/triage.md`.

**Do not use a fertiliser to raise it.** Plant fertilisers raise TDS and EC without
supplying usable hardness, and `references/products.md` prohibits this specifically.

**Do not infer it from TDS.** TDS counts every dissolved ion, hardness or not, so two tanks
with the same TDS can differ completely in GH. See `assets/wiki/metric/tds.md`.

**Do not assume GH and KH move together.** Coral raises both, but dilution, uptake and
nitrification act on them differently.
