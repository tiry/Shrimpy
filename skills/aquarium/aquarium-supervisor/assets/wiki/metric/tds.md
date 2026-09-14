---
title: TDS — total dissolved solids
slug: tds
category: metric
aqua_key: tds
aliases: ["TDS", "dissolved solids", "ppm"]
summary: A conversion of EC, not an independent measurement.
sources:
  - url: https://en.wikipedia.org/wiki/Total_dissolved_solids
    title: Total dissolved solids
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# TDS — total dissolved solids

What it is and what moves it. Current values are `aqua status`; what a species tolerates is
`aqua species`; what to do about a flag is `references/triage.md`.

## What it is, and the one thing to know about it

The combined content of everything dissolved in the water, reported in ppm.

**A hobby TDS pen does not measure it.** It measures conductivity and multiplies by an
assumed factor — commonly 0.5, referenced to sodium chloride. So the TDS figure and the EC
figure from the same device are **one measurement shown twice**, and treating them as two
pieces of evidence double-counts. `references/chemistry.md` states the factor and warns
against presenting it as physics.

That has a real consequence. The conversion is calibrated for a salt solution, and aquarium
water is largely calcium and bicarbonate, which the NaCl factor under-reads. So the number
is a consistent, comparable index of how much is dissolved — genuinely useful for spotting
change — and a poor estimate of actual dissolved mass.

**Use it for trend, not for truth.** A TDS that has climbed since last month is information.
A TDS of a particular value is barely a chemical statement at all.

Everything about what raises and lowers it is the same as for conductivity, because it *is*
conductivity: see `assets/wiki/metric/ec.md`.

## What not to do

**Do not infer hardness from it.** TDS counts every ion, hardness or not. Two tanks with
identical TDS can have completely different GH and KH — see `assets/wiki/metric/gh.md`. The
comparison that carries information is TDS against GH plus KH, which `aqua check` computes
as the spectator-ion figure.

**Do not match two tanks on TDS alone** before moving animals between them. Equal TDS with
unequal hardness still means an osmotic step, and hardness is the part that matters for a
moult.

**Do not chase a target value with additives.** Raising TDS is trivial and almost never the
goal; what matters is what the dissolved material *is*.
