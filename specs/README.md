# Specs

Scoped, executable work items for this repository. **The number is the execution order** —
work `01` through `08`.

The convention is borrowed from [`tairy-agent/specs`](../../tairy-agent/specs/README.md),
which consumes this repo. Same numbering, same section layout, same rule about citations.

## What these are (and aren't)

These are **declarative specs**: problem, reasoning, tradeoffs between candidate
approaches, and acceptance criteria. They deliberately do *not* contain ready-to-paste
diffs. Two reasons:

1. Several decisions here can only be settled by running the agent — whether a rule is
   *followed* is not answerable by reading code, and three of the first ten eval cases
   failed on correct answers. A spec that bakes in an assertion reads as more settled than
   it is.
2. Upstream moves. This repo pins `vendor/hermes-agent` at `29112be`, but the deployment
   will bump it. A spec written around *intent* survives that; one written around an exact
   line number does not.

Every factual claim carries a `file:line` citation, verified when written. Line numbers
drift — if one doesn't match, trust the quoted text.

## Index

`01` establishes the repo and the harness. `02`–`05` are each a distinct testing capability
built on it, in the order they were needed. `06` is the first spec that changes what the
agent *is* rather than how it is tested. `07` puts the whole lot on CI, and `08` makes a
live run readable rather than merely green.

A ✅ marks a spec that has been implemented.

| # | Spec | What | Severity |
|---|---|---|---|
| [01](01-standalone-agent-repo.md) ✅ | Standalone agent repo | Shrimpy's definition lives inside a deployment repo, and cannot be run or changed without the whole stack | High |
| [02](02-offline-skill-checks.md) ✅ | Offline skill checks | Two documented ways a skill vanishes from the agent's world with no error anywhere | High |
| [03](03-behavioural-evals.md) ✅ | Behavioural evals | Assembling the prompt correctly proves nothing about whether the rules are followed | Medium |
| [04](04-access-boundary.md) ✅ | Access boundary | The agent runs in the cloud; the aquarium is on a LAN. It has a real terminal and a skill full of commands it cannot run | High |
| [05](05-eval-snapshots.md) ✅ | Eval snapshots | A full eval pass costs ~$1 and draws a fresh sample, so a regression and model variance are indistinguishable | Medium |
| [06](06-live-data-and-reporting.md) ✅ | Live data and reporting | ~150 facts are restated across the skill and eight have already contradicted each other; nothing can be updated | High |
| [07](07-ci-and-lint.md) ✅ | CI and a lint baseline | Nothing runs on push, there is no lint config at all, and no schedule catches the model moving under a stable alias | Medium |
| [08](08-eval-transcripts.md) | Eval transcripts | A live run says pass or fail and cannot show what the agent said — three times the case was wrong and only the reply revealed it | Medium |

## Dependencies

```
01 ──┬── 02            (offline checks need the ephemeral home and prompt assembly)
     ├── 03 ── 05      (snapshots cache eval results, so evals must exist first)
     └── 04            (interception needs the harness's agent construction)
02,03,04,05 ── 06      (06 rewrites the skill; every existing check is its safety net)
02,03,06 ────── 07     (CI runs what they built; the live job needs the evals to exist)
03,05,07 ────── 08     (transcripts render eval results, cache them, and publish from CI)
```

Two sequencing notes that matter more than the rest:

- **[`06`](06-live-data-and-reporting.md) is the reason `02`–`05` were worth building.** It
  deletes most of the skill's prose and replaces it with a CLI. Doing that against a repo
  with no offline checks and no behavioural evals would be a rewrite with no way to tell
  whether the persona survived. Two of the existing evals — `dose-display` and
  `coral-scope` — already test behaviour the skill contradicts elsewhere in its own text,
  which is both the argument for `06` and the demonstration that the evals catch it.

## Conventions

| Section | Contents |
|---|---|
| Header | ID, severity, status, affected files, dependencies |
| Problem | What's wrong, with `file:line` evidence |
| Why it matters | The failure mode at stake |
| Constraints | What bounds the solution |
| Proposed change | Declarative |
| Options considered | Only where a genuine decision exists |
| Acceptance criteria | Verifiable checklist |
| Verification | What the offline suite proves vs. what only a live run can |
| Out of scope | Explicit boundaries |
| Open questions | What could not be settled by analysis |

## Relationship to `tairy-agent`

This repo is the source of truth for Shrimpy's persona and skills; `tairy-agent` deploys
them. The layout at the repo root (`SOUL.md`, `DISPLAYNAME`, `avatar.png`, `skills/`) is
exactly what `tairy-agent/scripts/create-profile.sh` copies out of a `profiles/<name>/`
directory, so this repo can be dropped in as one.
`tests/test_profile_layout.py` fails if that drifts.

[`06`](06-live-data-and-reporting.md) is the first spec that imposes a **requirement on the
deployment**: the agent gains live data that exists nowhere but the `hermes-data` volume, so
the backup story has to change. That contract is stated in
[`../AGENTS.md`](../AGENTS.md#consuming-this-repo) rather than only here, because the
deployment reads that file and will not read this directory.
