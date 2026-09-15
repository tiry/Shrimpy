# 11 — Two vendored skills, and the bundled-skill leak

| | |
|---|---|
| **ID** | 11 |
| **Severity** | Medium |
| **Status** | **Done** |
| **Affected files** | `skills/research/` (new), `skills/media/` (new), `tests/test_vendored_skills.py` (new), `INTEGRATION.md`, `scripts/check-integration-note.sh`, `AGENTS.md` |
| **Depends on** | [`01`](01-standalone-agent-repo.md) — the profile layout that makes a vendored skill deployable at all |
| **Imposes a deployment requirement** | **Yes** — see [`INTEGRATION.md`](../INTEGRATION.md) |

## Problem

Two separate things, found together.

**1. Shrimpy is not running with only the aquarium skill.** The belief that it is
is wrong, and the mechanism is a five-step chain:

| | |
|---|---|
| `tairy-agent/docker-compose.yml:222` | the container's command is `["gateway", "run"]` |
| `hermes_cli/main.py:3511-3512` | `cmd_gateway` calls `_sync_bundled_skills_quietly()` |
| `tools/skills_sync.py:711` | `sync_skills()` copies all 58 bundled skills into `$HERMES_HOME/skills/` |
| `tairy-agent/scripts/create-profile.sh:74` | wipes `$HERMES_HOME/skills/` and copies the profile's skills |
| `tairy-agent/scripts/bootstrap.sh:672` | **restarts hermes immediately afterwards**, re-seeding all 58 |

The wipe is undone two lines later. Nothing in the deployment writes
`.no-bundled-skills`, the one marker that survives a restart
(`tools/skills_sync.py:728,746-751`).

So the agent carries ~1,175 tokens of skill index it has no use for, on every API
call, and a surface that includes posting to X, email, GitHub and four
coding-agent delegators. All are credential-gated and therefore mostly inert —
but `autonomous-ai-agents/hermes-agent`, which **cannot** be disabled
(`agent/skill_utils.py:443`), can "configure, theme, extend, and orchestrate
Hermes Agent" on a family server.

**2. Of the 58, almost none fit, but two genuinely do.** An aquarium assistant on
Matrix has no use for Apple Notes, p5.js sketches or test-driven development.
Two are a real fit, and the skill this repo already has argues for both:
`research/grounded-citations` is the same epistemics the wiki was built on, and
`media/youtube-content` matches where aquarium advice actually lives.

## Why a third candidate was rejected

`productivity/pdf` looked obviously useful — Tiry sends a datasheet or a water
report — and it is **broken in this deployment**:

- `pymupdf`, `pdfplumber`, `pypdf`, `reportlab` are not in hermes's `[all]` extra
  (`pyproject.toml:350-360`)
- They are not in `tools/lazy_deps.py` either — only `skill.google_workspace` and
  `skill.youtube` have lazy-install entries (`lazy_deps.py:261,272`)
- The skill declares no `required_commands`, so `skill_view` reports
  `readiness_status: available`

The model would be told it can read PDFs, offer to, and every script would die on
import. That is the silent-failure class this repo exists around — the same shape
as a skill vanishing from the index for a 61-character description.

**The rejection is the more valuable half of this spec**, because it generalises:
a vendored skill must not advertise a capability the container cannot deliver,
and nothing in hermes checks that.

## Design

**Vendor, rather than `hermes skills install`.** Installing at deploy time needs
network at provision and leaves the running set undescribed by this repo. A
vendored copy makes the profile self-describing and reproducible —
`create-profile.sh` already copies `skills/` wholesale — at the cost of drift from
upstream, which is what the second guard below is for.

Both skills get a **freshly written category `DESCRIPTION.md`**. Upstream's
describe siblings that are not being taken (`media` covers gif-search and songsee;
`research` covers arxiv, llm-wiki and competitor-news-monitor), and
`tests/test_frontmatter.py:92` requires one per category — rendered untruncated
into the prompt, so an inherited description would advertise skills that are not
there.

**Two guards**, both generalising the `pdf` finding:

| Guard | Catches |
|---|---|
| unsatisfiable imports | a vendored skill whose third-party imports are in neither stdlib, `[all]`, nor `lazy_deps` — i.e. `pdf` |
| upstream drift | the submodule moving off `29112be` and changing a vendored tree, forcing a deliberate re-vendor |

## Acceptance criteria

- [x] `grounded-citations` and `youtube-content` vendored, each with a scoped category `DESCRIPTION.md`
- [x] Every vendored script's third-party imports are satisfiable in the deployment image
- [x] Vendored trees byte-match upstream at the pinned submodule commit
- [x] The system prompt indexes three skills across three categories, under the size limit
- [x] `INTEGRATION.md` documents the re-seed chain, the `.no-bundled-skills` fix and the toolset divergence
- [x] `scripts/check-integration-note.sh` verifies the new citations

## Out of scope

**Changing `tairy-agent`.** The `.no-bundled-skills` marker is a one-line
deployment change and is documented rather than applied.

**Closing the toolset divergence.** The deployed agent gets `hermes-matrix` =
`_HERMES_CORE_TOOLS` — web, browser, terminal (`toolsets.py:32-33,552-556`) —
while the harness runs `["skills","file","terminal"]` (`harness/agent.py:56`). So
**no eval exercises the web or browser tools the real agent has.** That is a
larger problem than this spec and is recorded, not fixed.

## Open questions

Whether `youtube-content` earns its place. `grounded-citations` has an obvious fit;
the YouTube case is plausible rather than demonstrated, and the transcripts will
show whether it is ever opened.
