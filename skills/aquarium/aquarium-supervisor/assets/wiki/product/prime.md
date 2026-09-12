---
title: Seachem Prime
slug: prime
category: product
aqua_key: prime
aliases: ["Prime", "dechlorinator", "conditioner", "water conditioner"]
summary: How a dechlorinator works, what it binds, and what it cannot do.
sources:
  - url: https://en.wikipedia.org/wiki/Chloramine
    title: Chloramine
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Sodium_thiosulfate
    title: Sodium thiosulfate
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Seachem Prime

Background on the mechanism. **Every dose comes from `aqua dose prime`** — it computes
against the real tank volume, and the label figure is not the dose for this system.

## The problem it solves

Municipal water is disinfected, and increasingly with **chloramine** rather than free
chlorine. Monochloramine (NH₂Cl) is chlorine bonded to ammonia. It is more stable than
chlorine, which is why utilities prefer it — and it is exactly that stability that matters
here:

- **Chlorine gasses off** if water is left standing or aerated.
- **Chloramine does not.** Standing a bucket overnight is not a treatment for it.

Worse, breaking chloramine apart does not make the problem disappear. It releases the
ammonia that was bonded to the chlorine — so naively dechlorinating chloraminated water
converts a disinfectant problem into an ammonia problem.

## How a conditioner handles it

Two separate chemistries, and conflating them causes most misunderstandings about this
product.

**Reduction.** Chlorine and chloramine are oxidising agents. A reducing agent converts them
to chloride, which is harmless at these concentrations. Sodium thiosulfate is the classic
example and the mechanism most dechlorinators are built on; it is fast, and it is why the
chlorine half of the job is essentially instant.

**Binding the ammonia.** The ammonia freed from chloramine is handled separately, by
converting it to a far less toxic complexed form. Two things follow, and both matter:

- **It is not removal.** The nitrogen is still in the water, in a form the fish and shrimp
  are not harmed by and the filter bacteria can still consume. That is the intent — it
  protects the animals without starving the biological filter.
- **It is temporary.** The complex is not permanent, and if the biofilter has not consumed
  the nitrogen by the time it breaks down, the ammonia returns. A conditioner buys time
  during a cycling problem; it does not fix one.

A consequence worth knowing before it confuses a test: a bound-ammonia complex still shows
on some total-ammonia tests, so a tank can read positive for ammonia while the animals are
genuinely protected. `assets/wiki/method/liquid-reagent-kit.md` covers what the test is
actually measuring.

Most conditioners also bind heavy metals, which is directly relevant here — see
`assets/wiki/species/neocaridina.md` for why copper is the concern in a shrimp tank.

## What it does not do

It is not a pH adjuster, a hardness adjuster, or a substitute for a water change. Run
`aqua` for what this product is recorded as not doing, rather than assuming from the label.

The commonest error is treating it as a general-purpose fix — dosing it at the sight of any
bad reading. It addresses chlorine, chloramine, metals and free ammonia. Nothing else on the
test card responds to it.
