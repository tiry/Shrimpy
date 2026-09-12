---
title: Seachem Stability
slug: stability
category: product
aqua_key: stability
aliases: ["Stability", "bacteria starter", "cycling bacteria", "bottled bacteria"]
summary: What bottled nitrifying bacteria do, and when they are pointless.
sources:
  - url: https://en.wikipedia.org/wiki/Nitrification
    title: Nitrification
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Nitrifying_bacteria
    title: Nitrifying bacteria
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Nitrospira
    title: Nitrospira
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Seachem Stability

Background on the mechanism. **Every dose comes from `aqua dose stability`.**

## What the filter actually is

The "biological filter" is a population of chemolithotrophic bacteria living on every
surface in the tank — media, substrate, glass, hardscape. They get their energy from
oxidising inorganic nitrogen, and they are what makes a closed aquarium possible at all.

Nitrification is the biological oxidation of ammonia to nitrate, via nitrite:

**ammonia → nitrite → nitrate**

Different organisms run each step. Ammonia oxidisers such as *Nitrosomonas* handle the
first; the second is run by nitrite oxidisers, and in freshwater aquaria the dominant genus
is *Nitrospira* rather than the *Nitrobacter* that older aquarium literature names. Some
*Nitrospira* are now known to perform complete ammonia oxidation — comammox — carrying
ammonia all the way to nitrate in a single organism.

The reason this matters practically: **the two steps establish at different rates.** A new
filter typically handles ammonia before it handles nitrite, which is why a nitrite spike
follows an ammonia spike during cycling rather than accompanying it. Nitrite above zero is
an emergency in its own right — `references/triage.md`.

## What the bottle contains, and what it can do

A bottled starter is a dormant or slow-metabolising preparation of these organisms. It
seeds surfaces that are not yet colonised, shortening the wait rather than eliminating it.
It is genuinely useful in four situations:

- Starting a new tank or a new filter
- After media has been replaced or heavily rinsed
- After adding livestock faster than the existing colony can keep up with
- After anything antibacterial has been in the water — see
  `assets/wiki/pest/cyanobacteria.md`, where an antibiotic is one of the options

## When it is pointless

**When the tank is already cycled.** A colony that is converting ammonia and nitrite to
nitrate is self-sustaining and sized to its food supply. Adding more bacteria does not
enlarge it, because the limit is available ammonia and surface area, not the number of
organisms introduced. Run `aqua` before dosing; the check is whether ammonia and nitrite are
absent while nitrate is present.

Dosing a healthy tank is not harmful, only wasteful — but the habit obscures a real problem
by treating the symptom of a reading with a product that does not act on it.

## Why the colony is fragile in specific ways

These bacteria are slow-growing, aerobic, and attached to surfaces rather than free in the
water. So:

- **Rinsing media in chlorinated tap water kills them.** See
  `assets/wiki/product/prime.md`.
- **Losing flow starves them of oxygen**, and a filter switched off for hours is a damaged
  filter, not a paused one.
- **They cannot be replaced quickly.** Recovery takes the time it takes; there is no dose
  that shortens it much.

That last point is the argument for caution with any antibacterial treatment in a tank whose
animals depend on the filter.
