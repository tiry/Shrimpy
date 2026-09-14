# 10 — A page per monitored metric

| | |
|---|---|
| **ID** | 10 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `skills/aquarium/aquarium-supervisor/assets/wiki/metric/` (new), `.../SKILL.md`, `.../scripts/aqua.py`, `tests/test_wiki.py`, `tests/test_no_drift.py`, `scripts/render-wiki-index.py`, `evals/cases/aquarium.yaml` |
| **Depends on** | [`09`](09-background-wiki.md) — the wiki tier, its guards and its index |
| **Imposes a deployment requirement** | No |

## Problem

`aqua` tracks fourteen metrics and **the skill defines none of them.**
`reference.json.metrics` carries `label`, `unit`, `precision` and `kind` — enough to
render a number, nothing about what the number is. So "what is ORP actually telling me"
has no answer anywhere in the skill, and the model supplies one from its own weights.

That is the same gap spec 09 closed for the animals, and it matters more here, because
Tiry has already been told something false about one of these metrics: `SKILL.md:219`
exists solely to say that ORP does **not** indicate ammonia. A metric with a known
misconception attached and no page explaining it is the weakest point in the skill.

## What already exists, and why it is not enough

The *corrections* are not missing. They are organised along a different axis:

| Where | What it owns |
|---|---|
| `triage.md:96-99` | pH low → check KH first; buffer capacity, not pH-down chemistry |
| `triage.md:101-105` | pH swinging → photoperiod, not a fault |
| `triage.md:111-116` | TDS climbing with GH and KH flat → water change, never an additive |
| `triage.md:75,78` | "Raise GH gradually. Never in one step." · "Raise KH." |
| `chemistry.md:75-88` | dilution: a change moves TDS, GH and KH by the same fraction |
| `chemistry.md:92-109` | aragonite raises hardness, self-limiting, slow |
| `products.md:127,137` | "Never use it to try to raise GH" |

Organised by **symptom** and by **mechanism**. A keeper asks by **metric**. The content is
reachable only if you already know which symptom it hides under — which is precisely what
someone asking "how do I raise KH" does not know.

## Why this is dangerous to do naively

Copying that material into fourteen pages recreates the eight documented contradictions
spec 06 removed. Two copies of "aragonite raises KH" drift, and then the answer depends on
which file the model opened.

The second trap is subtler: **for five of the fourteen, "increase" is not a meaningful
instruction.** Ammonia, nitrite, free chlorine and copper should read zero; iron nearly so.
A page templated as raise/lower would carry a "how to raise copper" section, which is
absurd and, in a shrimp tank, actively unsafe — copper is toxic to them in the low tens of
ppb (`reference.json`, neocaridina notes).

## Design

**Three owners, three questions.** The same split that made method pages work instead of
per-product ones in spec 09:

| Read | Question |
|---|---|
| `assets/wiki/metric/<m>.md` | what the number *is*, and the levers that move it |
| `references/triage.md` | what to do here, now — **unchanged** |
| `aqua` | how much |

A metric page names levers. It carries **no amounts and no procedure**, so triage stays
self-sufficient during an emergency rather than requiring a second file to be opened.

**The template varies by `kind`**, using the classification `reference.json` already holds:

| `kind` | Sections |
|---|---|
| `continuous`, `hardness` | what it is · what raises it · what lowers it · what not to do |
| `nitrogen`, `nutrient` | what it is · what makes it rise · how it comes down · why the target is zero or low |
| `contaminant` | what it is · how it gets in · how to remove it · **why you never add it** |

For the contaminants the useful direction is *what puts it there* — fish medications,
fertilisers, plumbing — not a dosing instruction.

One page per `reference.json` key, kept 1:1 so `aqua check` can point at any metric it
flags. `tds.md` is deliberately thin and defers to `ec.md`: TDS is conductivity times an
assumed NaCl factor, not an independent measurement (`chemistry.md:41-42`), and writing it
as though it were physics is the error the page exists to prevent.

## Acceptance criteria

- [x] Fourteen pages under `assets/wiki/metric/`, one per `reference.json.metrics` key
- [x] Bidirectional: every metric has a page, every page names a real metric
- [x] `aqua_key` resolves against `metrics` as well as species and products
- [x] The species-range ban covers metric pages
- [x] No amounts (`tbsp`, `tsp`, `mL`, `gal`) on a metric page
- [x] Every page links the reference that owns its procedure
- [x] `aqua check` prints the background path for a flagged metric
- [x] Index groups metrics by `kind`
- [x] An eval case on ORP, where a documented misconception makes the page load-bearing

## Verification

The offline suite proves structure and the absence of duplicated ranges and amounts. Only
a live run shows whether the model opens the right page, which is what the ORP case is for
— chosen because `SKILL.md:219` makes it specific and consequential, unlike the molts case
in spec 09 that failed for being over-constrained.

## Out of scope

Changing `triage.md`. Its guidance is procedural, emergency-facing and correct where it is;
moving it would trade a duplication problem for a worse latency one.

## Open questions

Whether `ec.md` and `tds.md` justify two pages or want merging behind one page with two
keys. Kept separate for the 1:1 mapping; the transcripts will show whether either is ever
opened.
