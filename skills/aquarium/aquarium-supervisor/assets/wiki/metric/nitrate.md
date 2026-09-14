---
title: Nitrate
slug: nitrate
category: metric
aqua_key: nitrate
aliases: ["nitrate", "NO3", "nitrates"]
summary: The cycle's end product - far less toxic, and it accumulates.
sources:
  - url: https://en.wikipedia.org/wiki/Nitrate
    title: Nitrate
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Nitrification
    title: Nitrification
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# Nitrate

The end of the nitrogen cycle, and the one nitrogen metric that is normally present rather
than zero. What the tanks read is `aqua status`; what to do about a flag is
`references/triage.md`.

## What it is

What ammonia becomes after two bacterial oxidations. It is **far less toxic than either
precursor** — orders of magnitude — which is what makes a closed aquarium viable at all: the
dangerous nitrogen is converted into something tolerable that can be removed at leisure.

Its presence is a **good sign in context**. Ammonia and nitrite at zero *with* nitrate
present is the signature of a working, self-sustaining biofilter. Nitrate at zero in a
stocked tank is more suspicious than reassuring — either nothing is being processed, or
plants are consuming it as fast as it appears.

The catch is that nothing consumes it further in a normal freshwater tank. **It
accumulates**, and the only routes out are uptake and export.

## What makes it rise

- **Ordinary function.** Every animal, every feed, every decomposition adds nitrogen, and
  this is where nitrogen ends up. A tank with no export path has nitrate climbing as a
  matter of arithmetic.
- **Increased stocking or feeding.**
- **Evaporation with top-off**, which concentrates what is already dissolved rather than
  adding more.

## How it comes down

- **Water changes.** This is the answer, and `references/triage.md` says so without
  qualification: water changes, not chemistry. **Evaporation removes nothing** — only
  replacing water exports nitrate.
- **Plant uptake**, which is real but rarely sufficient alone in a stocked tank.
- **Reducing input**: less feeding, fewer animals.

## What not to do

**Do not use a chemical nitrate remover in place of a water change.** The change also
exports phosphate, dissolved organics, sodium and potassium — everything else with no
export path. A product that removes only nitrate leaves the rest accumulating and hides the
signal that would have prompted the change.

**Do not read a rising nitrate as an emergency.** It is a maintenance signal. Sudden
interventions to correct it cause more harm than the number does — and a large change on a
tank that has drifted far is itself an osmotic event. See `assets/wiki/metric/tds.md`.

**Do not confuse it with the spectator-ion figure.** If TDS is climbing while GH and KH
stay flat, nitrate is one candidate among several; `aqua check` computes the comparison and
`references/chemistry.md` explains its limits.
