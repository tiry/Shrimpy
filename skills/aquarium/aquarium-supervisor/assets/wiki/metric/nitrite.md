---
title: Nitrite
slug: nitrite
category: metric
aqua_key: nitrite
aliases: ["nitrite", "NO2", "nitrites"]
summary: The middle step of the nitrogen cycle. Above zero is an emergency.
sources:
  - url: https://en.wikipedia.org/wiki/Nitrite
    title: Nitrite
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Nitrification
    title: Nitrification
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# Nitrite

**The target is zero, and anything above it is an emergency.** Nothing here is about raising
it. What the tanks read is `aqua status`; what to do about a positive reading is
`references/triage.md`, first and immediately.

## What it is

The intermediate of nitrification: ammonia is oxidised to nitrite, and nitrite to nitrate.
Two different groups of bacteria run the two steps, and **they establish at different
rates** — which is why a new or damaged filter handles ammonia before it handles nitrite,
and why a nitrite spike characteristically *follows* an ammonia spike rather than
accompanying it. `assets/wiki/product/stability.md` covers the organisms involved.

Its toxicity works differently from ammonia's. In fish, nitrite crosses the gills and
interferes with the blood's ability to carry oxygen, so the animal suffocates in fully
oxygenated water. **Invertebrates use haemocyanin rather than haemoglobin**, so the
mechanism differs, but nitrite is not safe for them either and the practical rule is the
same: zero.

A reading above zero means the cycle is incomplete or broken. It is not a metric to manage
at a low level — it is a fault indication.

## What makes it rise

- **An immature biofilter** — a new tank, new media, or a filter restarted after a long
  stop.
- **An ammonia spike working through the cycle.** If ammonia was recently positive, nitrite
  is the next thing to watch.
- **Anything that damages the bacteria**: chlorinated tap water on media, an antibacterial
  treatment, a long power interruption.
- **Zeolite**, which removes ammonium and thereby starves the first-stage colony, without
  binding nitrite at all — so it can produce exactly this.

## How it comes down

- **The second-stage bacteria consume it**, given time and oxygen. This is the real fix and
  it proceeds at its own pace.
- **Water changes**, repeatedly, to hold the concentration down while the colony catches up.
- **A conditioner** temporarily complexes it, as with ammonia, buying a window rather than
  solving it — `assets/wiki/product/prime.md`.
- **Aeration**, which supports the bacteria doing the work.

## What not to do

**Do not stop testing when ammonia reaches zero.** That is the moment nitrite is most likely
to appear, and the tank looks safe on the metric people check.

**Do not add livestock** while it is positive, and do not feed normally — less input means
less to process.
