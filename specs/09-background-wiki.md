# 09 — A background wiki inside the skill

| | |
|---|---|
| **ID** | 09 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `skills/aquarium/aquarium-supervisor/assets/wiki/` (new), `.../SKILL.md`, `.../assets/reference.json`, `.../scripts/aqua.py`, `.../scripts/_report.py`, `tests/test_no_drift.py`, `tests/test_wiki.py` (new), `evals/cases/aquarium.yaml` |
| **Depends on** | [`06`](06-live-data-and-reporting.md) — the data/prose split this extends, and the anti-drift guard that makes a third prose tier survivable |
| **Imposes a deployment requirement** | No |

## Problem

The skill can reason about water chemistry and read live values, but it knows almost
nothing about the *animals*. `reference.json` holds five species as five tolerance
envelopes — `ph`, `gh_degrees`, `kh_degrees`, `tds_ppm`, `temperature_c`, and for
Neocaridina a `gh_molt_floor_degrees` of 4.0. That is the whole of it.

So Shrimpy can say what a Neocaridina tolerates and cannot say what one *is*. It does not
know they are native to Taiwan and eastern China, that they eat biofilm and detritus but
not vascular plants, that they consume their own molts and so a shed shell should be left
in the tank, that a female abandons her eggs under stress, or that there is no larval stage
— every one of which changes the right answer to a question a keeper actually asks.

The gap is worse for the things that go wrong. `references/triage.md` is a decision
procedure; it names planaria and molt failure without explaining what a planarian is, how
it got in, or why a dewormer that is safe for fish kills shrimp. The model fills those gaps
from its own weights, unsourced and uncheckable, and the reply reads exactly as confident
as one drawn from the skill.

## Why it matters

**An unsourced claim is indistinguishable from a sourced one in the reply.** Spec 06 moved
every tank measurement into `aqua` so a number in prose became a build failure. It did
nothing about biology, because there was no biology in the skill to govern. Adding
background without extending that discipline re-opens the hole from the other side.

This already happened once, today. The Neocaridina tolerance ranges were in
`reference.json` **and** spelled out in `references/livestock.md`, so the answer to "what
pH do they want" depended on which file the model opened
(`tests/test_no_drift.py:198-225`). A wiki is twenty more chances to make that mistake.

## Constraints discovered before designing

Three facts about the runtime shaped the layout, and none were guesses.

**1. Shrimpy has no internet.** `harness/agent.py:56` sets
`RUN_TOOLSETS = ["skills", "file", "terminal"]`, mirrored at
`harness/config.template.yaml:25-26`. Of the four toolsets that grant web access — `web`,
`search`, `browser`, `x_search` (`vendor/hermes-agent/toolsets.py:105-128,182-192`) — none
is enabled. **So this wiki removes no web searches, because there are none.** Its value is
grounding, not latency. Granting web access is a change to the access boundary spec
[`04`](04-access-boundary.md) defines and belongs in its own spec.

**2. Every file costs a round trip.** The system prompt carries only the frontmatter
description, truncated at 60 characters (`vendor/hermes-agent/agent/skill_utils.py:1182`);
the body arrives only when `skill_view` is called, and each supporting file needs a second
call with `file_path=` (`vendor/hermes-agent/tools/skills_tool.py:2004-2017`). Twenty
unindexed pages therefore make Shrimpy *slower*, not faster. **Routing is the design; the
prose is the easy part.**

**3. `references/` cannot hold a subdirectory.** `skill_view` builds the `linked_files` map
the model discovers files through with a **non-recursive** `references_dir.glob("*.md")`
(`vendor/hermes-agent/tools/skills_tool.py:1646-1650`) but an **`rglob("*")`** over
`assets/` (`:1669-1675`). A `references/wiki/` tree would be invisible to discovery while
still being readable — the silent-failure shape this repo already has two of.

## Approaches considered

| Approach | Verdict |
|---|---|
| Flat files in `references/` (`wiki-species-neocaridina.md`) | Discoverable, and inherits the drift scan for free. Rejected: 20 background files bury the four curated reasoning files `SKILL.md:299-302` routes to, and the two tiers stop being distinguishable. |
| `references/wiki/**` | **Rejected outright.** Invisible in `linked_files` (constraint 3). Reachable only through a SKILL.md index, so an unindexed page is unreachable rather than merely undiscovered. |
| One large `background.md` | One round trip, no routing problem. Rejected: ~100 KB on every background question, and the per-page provenance that makes a claim checkable has nowhere to live. |
| **`assets/wiki/<category>/<slug>.md`** | **Chosen.** `rglob` lists every page in `linked_files`, so discovery works even if the index rots; the index in SKILL.md makes the common path one hop; the four references stay a distinct tier. |

### Instruments: pages per method, not per product

The request was for pages on the hardware. That cannot be done as asked, for two
independent reasons.

**There are no sources.** The Wikipedia REST summary endpoint returns an empty extract for
`Hanna_Instruments` and no article at all for Kactoily, BACNUNN or Advatec. These are
consumer products with no encyclopedic coverage.

**The per-product facts already exist.** `reference.json` carries `trusted_for`,
`not_trusted_for` and a `note` for all seven instruments. A product page would restate
them — the precise duplication this spec exists to prevent.

What is genuinely missing is the *mechanism*: why a colorimetric checker and a test strip
disagree, what a TDS pen actually measures and why that is not hardness, why a liquid pH
test reads wrong under warm light. Those are sourceable (`Total_dissolved_solids`,
`Nitrification`, colorimetry, ion-selective electrodes) and they generalise. So the wiki
gets **five method pages**, and each instrument in `reference.json` gains a `method` key
pointing at one. Seven products collapse to five methods with no fact restated.

## Design

```
assets/wiki/species/<slug>.md    5   the animals
assets/wiki/pest/<slug>.md       6   what goes wrong and what causes it
assets/wiki/product/<slug>.md    3   what is in the bottle and how it acts
assets/wiki/method/<slug>.md     5   how a class of instrument measures, and fails
```

Every page carries frontmatter — `title`, `slug`, `category`, `aqua_key`, and `sources[]`
with a URL, a licence and a `consulted` date. Frontmatter is exempt from the drift scan
because `tests/conftest.py:46-49` strips it before scanning, which is what makes a
citation date legal in a file where `ALWAYS_FORBIDDEN` bans dates.

**Three tiers, stated in SKILL.md:** read `aqua` for **values**, `references/` for
**reasoning**, `assets/wiki/` for **background**.

**Sourcing is original prose with citations, never copied text.** This repo is public;
Wikipedia is CC BY-SA 4.0, and pasting it would arguably attach share-alike terms to the
repo. Every page states what it drew on and when.

## Acceptance criteria

- [x] Pages live under `assets/wiki/<category>/<slug>.md` and appear in `linked_files`
- [x] A routing index in SKILL.md, verified against the filesystem **in both directions**
- [x] The drift scan covers wiki pages — tank names, instruments, dates, doses, counts
- [x] The species-range ban extends from `livestock.md` to `assets/wiki/species/`
- [x] Every page declares at least one source with a URL and a consulted date
- [x] `aqua_key` resolves in `reference.json`; no page about a subject the CLI cannot answer for
- [x] Every instrument in `reference.json` names a `method` page that exists
- [x] `aqua species <name>` prints the path to the background page
- [x] Per-page size cap, so a page stays one cheap read
- [x] Evals: background is answered from the wiki; ranges still come from `aqua species`

## Verification

The offline suite proves structure — that pages exist, are indexed both ways, are sourced,
are within budget, and state no value the data owns. It cannot prove the model *opens* the
right page, which is what the eval cases are for.

## Out of scope

Granting web access (spec 04's boundary). Agent-written pages: `create-profile.sh:74` does
`rm -rf "${home}/skills"` on every provision, so anything the agent wrote under `skills/`
dies at the next deploy — a writable wiki would have to live in `workspace/`, with no
review and no git history. Plants, algae beyond cyanobacteria, and tank equipment
(filters, heaters, substrate) are deferred; equipment is per-tank instance data that
belongs in `aqua`, not in prose.

## Open questions

Whether five method pages is the right granularity, or whether the TDS pen and the ISE pH
probe want separating further, will only be answerable once there are transcripts showing
which page the model actually opens.
