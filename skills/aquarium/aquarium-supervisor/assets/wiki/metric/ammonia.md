---
title: Ammonia
slug: ammonia
category: metric
aqua_key: ammonia
aliases: ["ammonia", "NH3", "ammonium", "NH4"]
summary: The first product of waste, and acutely toxic. Target is zero.
sources:
  - url: https://en.wikipedia.org/wiki/Ammonia_poisoning
    title: Ammonia poisoning
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
  - url: https://en.wikipedia.org/wiki/Nitrification
    title: Nitrification
    licence: CC BY-SA 4.0
    consulted: 2026-09-13
---

# Ammonia

**The target is zero.** There is no reason to raise this and no safe amount to aim for; the
sections below are about what puts it there and how it comes down. What the tanks read is
`aqua status`; what to do about a positive reading is `references/triage.md`, immediately.

## What it is

The first nitrogen product of everything that breaks down in the tank — waste, uneaten food,
dead plant matter, a dead animal. It exists in two forms in equilibrium:

- **NH₃**, free ammonia, which is highly toxic
- **NH₄⁺**, ammonium, which is far less so

**The balance between them depends on pH and temperature.** Higher pH and warmer water push
it toward the toxic free form. That is the practically important part: the same total
ammonia reading is considerably more dangerous in a warm, alkaline tank than in a cool,
acidic one, and most hobby tests report the *total* without distinguishing them.

A healthy established tank reads zero not because nothing produces ammonia but because the
nitrifying colony consumes it as fast as it appears. A positive reading means production has
outrun that colony — see `assets/wiki/product/stability.md`.

## What makes it rise

- **A dead animal that has not been found.** In a small volume this is the fastest route to
  a dangerous reading, and it is why a missing snail is urgent rather than untidy.
- **Overfeeding**, directly and via the decay of what was not eaten.
- **A damaged biofilter** — media rinsed in tap water, a filter switched off for hours, an
  antibacterial treatment.
- **Adding livestock faster than the colony can grow.**
- **Disturbing substrate** that has accumulated organic matter.

## How it comes down

- **The biofilter consumes it**, converting it to nitrite and then nitrate. This is the only
  permanent route and it cannot be hurried much.
- **A water change** removes it directly and immediately, and dilutes whatever is producing
  it.
- **A conditioner** temporarily complexes it into a form the animals are not harmed by while
  leaving it available to the bacteria. It buys hours, not a solution, and it expires — see
  `assets/wiki/product/prime.md`.
- **Removing the cause**, which is the only step that makes the others stick.

## What not to do

**Do not treat a bound-ammonia reading as an ongoing emergency without rechecking.** A
conditioner's complex still registers on some total-ammonia tests, so the number can stay
positive while the animals are protected — see `assets/wiki/method/liquid-reagent-kit.md`.

**Do not use ORP as a substitute test.** It cannot detect this. See
`assets/wiki/metric/orp.md`.

**Do not reach for zeolite casually.** It binds ammonium but starves the nitrifying colony,
has no effect on nitrite, and dumps its entire load back into the water if salt is added.
`references/chemistry.md` has the detail.
