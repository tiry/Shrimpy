---
title: Temperature
slug: temperature
category: metric
aqua_key: temperature
aliases: ["temperature", "temp", "heat", "cooling", "degrees"]
summary: Sets the pace of everything, and how much oxygen the water can hold.
sources:
  - url: https://en.wikipedia.org/wiki/Oxygen_saturation
    title: Oxygen saturation
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Evaporative_cooler
    title: Evaporative cooler
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# Temperature

What it is and what moves it. What a species tolerates is `aqua species`; what the tanks
read is `aqua status`; what to do about a flag is `references/triage.md`.

## What it does

More than set comfort. Three effects run through everything else on the list:

- **Metabolic rate.** Warmer water means faster metabolism, faster growth, a shorter moult
  cycle, more feeding and more waste. Warmer is not simply better: for shrimp it shortens
  lifespan and, at the upper end, reduces reproductive success.
- **Dissolved oxygen.** Warm water holds **less** oxygen, while the animals in it demand
  more. Those two curves move in opposite directions, which is why heat stress and
  suffocation arrive together on a hot day.
- **Biological and chemical rates.** The nitrifying colony, decomposition and dissolution
  all speed up with temperature.

**Stability matters more than the exact figure**, as with every metric here. A steady value
slightly off target is healthier than a correct one that swings.

## What raises it

- Room temperature, which is the dominant term in an unheated tank.
- A heater, lighting close to the surface, and pump motors.
- A closed lid, which traps heat and stops evaporative loss.

## What lowers it

- **Surface agitation and evaporation**, the primary lever here — fans across the surface,
  an open top, raised lighting. Evaporative cooling is **bounded by the room's wet-bulb
  temperature**, so on a humid day it cannot reach the target and that is a limit, not a
  fault. `references/triage.md` says this directly.
- Turning the heater down or off; reducing lighting.
- Cooler top-off water, gradually.

## What not to do

**Do not drop it quickly.** A rapid fall is a shock, and ice or cold water poured in is a
worse problem than the heat was.

**Do not forget that cooling by evaporation concentrates everything left behind.** Fast
evaporation raises EC and TDS and drops the water line; top-off with distilled water is what
keeps the concentration steady. See `assets/wiki/metric/ec.md`.

**Do not read temperature from an instrument not trusted for it** — `aqua instruments`
records which are.
