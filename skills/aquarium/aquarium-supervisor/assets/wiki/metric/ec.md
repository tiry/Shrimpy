---
title: EC — electrical conductivity
slug: ec
category: metric
aqua_key: ec
aliases: ["EC", "conductivity", "microsiemens", "uS/cm"]
summary: How well the water carries current - the actual measurement behind TDS.
sources:
  - url: https://en.wikipedia.org/wiki/Electrical_conductivity_meter
    title: Electrical conductivity meter
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Total_dissolved_solids
    title: Total dissolved solids
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# EC — electrical conductivity

What it is and what moves it. Current values are `aqua status`; what to do about a flag is
`references/triage.md`.

## What it is

How readily the water conducts an electric current, in microsiemens per centimetre. Pure
water conducts poorly; dissolved ions carry the current, so conductivity rises with total
dissolved ionic content.

**This is the measurement the pen actually makes.** TDS is calculated from it by a fixed
assumed factor — see `assets/wiki/metric/tds.md` and `references/chemistry.md`. When a
device displays both, it has measured one number and multiplied it.

EC is a **bulk** figure. It says how much ionic material is dissolved and nothing about
which ions those are. Calcium from crushed coral, sodium from a water conditioner, potassium
from fertiliser and nitrate from an overdue water change all raise it, and the reading
cannot tell them apart. Pairing it with GH and KH is what makes it informative — that
comparison is the spectator-ion figure `aqua check` computes, and `references/chemistry.md`
explains what it is and is not good for.

## What raises it

- **Anything dissolved that was not there before** — remineralising salts, fertiliser,
  buffer, conditioner.
- **Evaporation.** Water leaves, ions stay, so the remaining water concentrates. This is why
  topping off with distilled water is maintenance of the *concentration* rather than an
  addition to it.
- **Accumulating waste**, nitrate especially, in a system with no export path.
- **Temperature**, which raises conductivity for the same water. A good meter compensates;
  it is worth knowing the raw quantity is temperature-dependent.

## What lowers it

- **Partial water changes with lower-EC water** — the only reliable route, and the one
  `references/triage.md` names when the figure climbs while hardness stays flat.
- **Uptake**, as plants and animals consume nutrients and minerals.

## What not to do

**Do not treat a rising EC as a hardness problem.** If GH and KH are flat and EC is
climbing, what is accumulating is *not* hardness, and adding minerals makes the number worse
while missing the cause. The answer is a water change, never an additive.

**Do not compare EC across instruments casually.** Cell design and temperature compensation
differ, and `aqua` records which instrument produced each reading for that reason. See
`assets/wiki/method/electrode-pen.md`.
