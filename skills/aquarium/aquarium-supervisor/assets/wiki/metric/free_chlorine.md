---
title: Free chlorine
slug: free_chlorine
category: metric
aqua_key: free_chlorine
aliases: ["chlorine", "free chlorine", "Cl2", "chloramine", "tap water"]
summary: Arrives with tap water, kills the biofilter. Target is zero.
sources:
  - url: https://en.wikipedia.org/wiki/Chloramine
    title: Chloramine
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Sodium_thiosulfate
    title: Sodium thiosulfate
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# Free chlorine

**Never added. The target is zero.** This page covers how it arrives and how it is removed.
What the tanks read is `aqua status`; what to do about a positive reading is
`references/triage.md`.

## What it is

A disinfectant residual in municipal water, present specifically to kill microorganisms. It
does that in an aquarium too — which is the whole problem, because the nitrifying colony is
a microorganism population the tank depends on.

Two forms matter and they behave very differently:

- **Free chlorine** is volatile. It gasses off if water stands or is aerated.
- **Chloramine** — chlorine bonded to ammonia — **does not**. It is more stable, which is
  why many utilities prefer it, and why "let the bucket stand overnight" is not a treatment
  for it.

There is a sting in the tail. Breaking chloramine apart releases the ammonia that was bonded
to the chlorine, so dechlorinating chloraminated water converts a disinfectant problem into
an ammonia one. `assets/wiki/product/prime.md` explains how a conditioner handles both
halves, and `assets/wiki/metric/ammonia.md` covers the result.

## How it gets in

- **Tap water**, whether for a water change or a top-off.
- **Rinsing filter media under the tap** — the single most damaging route, because it
  applies the disinfectant directly to the bacterial colony rather than diluting it into the
  tank. Media is rinsed in discarded tank water, never tap.
- **Buckets and equipment** washed with tap water or bleach and not thoroughly rinsed.

## How it comes down

- **A dechlorinator**, which reduces chlorine and chloramine to harmless chloride almost
  instantly. This is the reliable route and it is why the bottle exists.
- **Aeration or standing**, which works for free chlorine and **not** for chloramine.
- **Activated carbon**, partially.

## What not to do

**Do not assume the local supply is chlorine rather than chloramine.** The treatment differs
and the assumption fails silently — the tank looks fine until the biofilter does not.

**Do not add untreated tap water** to a stocked tank, in any quantity, including a top-off.

**Do not dose a conditioner and immediately conclude the ammonia reading is a fault.** If
the supply is chloraminated, that ammonia is expected — see
`assets/wiki/product/prime.md`.
