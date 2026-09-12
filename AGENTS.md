# AGENTS.md

Working notes for this repository. Read this before changing anything here.

## What this repo is

The source of truth for **Shrimpy**, an aquarium keeper's assistant built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent) — the persona, the skills, and
a harness for running and testing them locally with nothing else attached.

It is *not* a deployment. No Matrix, no Synapse, no Hindsight, no Caddy, no
docker-compose. [`../tairy-agent`](../tairy-agent) deploys what is defined here.

## Layout is a contract

```
SOUL.md  DISPLAYNAME  avatar.png  skills/
```

at the repo root, because that is exactly what `tairy-agent/scripts/create-profile.sh`
copies out of a `profiles/<name>/` directory. This repo can therefore be dropped in as one.
`tests/test_profile_layout.py` fails if it drifts.

Everything else — `harness/`, `evals/`, `tests/`, `scripts/`, `specs/`, `vendor/` — is
tooling the deployment ignores.

## Commands

```bash
./shrimpy setup      # uv, .venv, hermes-agent (once, a few minutes)
./shrimpy test       # offline checks — no API key, no cost, ~1s. Run this constantly.
./shrimpy prompt     # the assembled system prompt; --skills for just the index
./shrimpy ask "..."  # one question; -v shows skills opened, tools, tokens, cost
./shrimpy chat       # interactive REPL as Shrimpy
./shrimpy eval       # behavioural evals — cached; --live to re-record
./shrimpy snapshots  # inspect or clear the eval cache
```

CI (`.github/workflows/ci.yml`) runs `ruff`, the skill's CLI on Python 3.11-3.13
without hermes-agent installed, and `./shrimpy test` on every push. The
behavioural evals run **monthly and on demand**, never on `pull_request` — a
secret must not be exposed to whatever code a PR contains. Run them locally
before changing `SOUL.md` or a skill; snapshots make a re-run free until the
definition actually changes.

**Read the transcript before touching the skill.** Every eval run renders one to
`.work/transcripts/`, and live CI runs publish to the `eval-transcripts` branch. Three
times the case was wrong and the agent was right; the reply is where that shows.

**A live eval failure is not automatically your bug.** The runner exits 1 when
the agent misbehaved and **3** when the provider was unreachable, and CI reports
those differently. Do not "fix" a 402.

**Pick the eval model to match the deployment, not to save money.**
`gemini-2.5-flash` is 7x cheaper than the current default and fails three cases
on safety-relevant rules; as a judge it passes replies that should fail. The
current choice was measured — see the table in `README.md`.

## Specs

Planned and completed work lives in [`specs/`](specs/README.md), numbered in execution
order, same convention as `tairy-agent/specs`. Declarative: problem, reasoning, tradeoffs,
acceptance criteria — no ready-to-paste diffs. Every factual claim carries a `file:line`
citation.

**Write the spec before the code** for anything that changes what the agent is. The
retroactive specs `01`–`05` exist because the reasoning was worth keeping; do not add more
of those.

## Things that will bite you

**Two ways a skill vanishes with no error.** A `description` over 60 characters is truncated
in the index (`SKILL_PROMPT_DESC_LIMIT`). A description containing an unquoted `": "` is
invalid YAML, `platforms` parses as a string, and **the skill is dropped from the index
entirely** — while still parsing, and logging nothing. Both are covered by `./shrimpy test`.
See [`specs/02`](specs/02-offline-skill-checks.md).

**`--safe-mode` and `--ignore-rules` silently drop `SOUL.md`** and substitute a generic
identity (`agent/system_prompt.py:472-487`). Never use them in the harness.

**The skill index is empty without a skills tool in the toolset**
(`agent/system_prompt.py:619`).

**`HERMES_HOME` must be set before `import run_agent`** — that module binds it at import
time (`run_agent.py:127-129`).

**A rubric must not re-judge what a deterministic assertion already proves.** The judge is
shown the reply and nothing else — it cannot see tool calls. A rubric asking for a value
"obtained from the CLI rather than asserted" made the judge guess, and it vetoed a
`runs_aqua` check that had already passed on the transcript. Provenance belongs to
`runs_aqua`/`opens_skills`/`opens_wiki`; the rubric judges the text.
`tests/test_harness.py` fails on the phrasings that ask otherwise.

**The wiki is for when being wrong is expensive, not for every background question.**
`SKILL.md:34-36` tells the agent to answer general husbandry from ordinary knowledge, so an
`opens_wiki` assertion on "should I remove shed molts" failed a correct reply for obeying
the older rule. Scope a lookup requirement to what is specific to these animals and
products — the planaria/snail treatment conflict is the paradigm case.

**When an eval fails, read the reply before touching the skill.** **Seven times** now the
harness was wrong and the agent was right — it named `3.2 mL` *in order to correct it*,
scoped a caution with a sentence containing "do not add", chose a more targeted CLI verb
than the one asserted, said "don't dose chemical pH adjusters" against a case that banned
the phrase, gave a correct range that a rubric called unsourced because the judge cannot see
a tool call, and answered a husbandry question from ordinary knowledge exactly as SKILL.md
instructs. A substring test cannot tell "recommends X" from "warns against X".
`tests/test_harness.py` now refuses a `not_matches` with no rubric behind it; every run
renders a transcript, so read it first.

**Skill content is input to the harness.** `skills_opened` once scanned tool responses for
`"not found"`; `SKILL.md` §7 contains the phrase `command not found`, so a documentation
edit broke eight of twelve evals. Parse the envelope, never the body.

**The eval case format is bespoke, and validated because of it.** `evals/schema.py` says
why promptfoo was not adopted and checks every case before a model is called — every
assertion is read with `expect.get(...)`, so a misspelled key was silently ignored and the
case passed having asserted nothing. `evals/cases/schema.json` is generated from the same
definitions for editor autocomplete; a test fails if they drift.

**Hook and middleware dispatch is fail-open.** An exception in a `pre_tool_call` hook is
swallowed into a debug log. Anything registered there must record, never raise.

**`pre_tool_call` hooks are one process-global list**, and Hermes invokes every callback in
it for every tool call. Registering one per parallel eval case made each record all the
others' commands. `harness/interception.py` installs a single router instead.

**Hermes dispatches tool calls off the thread that called `run_conversation`.** Scope
anything per-run by `session_id`, which travels with the hook payload
(`hermes_cli/plugins.py:6640`), never by thread.

**`./shrimpy eval -j 6` can 402 on a healthy key.** OpenRouter reserves credit for each
in-flight request's `max_tokens`, so several large-context requests in parallel can exceed a
low balance while any one of them succeeds. The error says so — *"given your current
in-flight requests"*. Drop to `-j 2` before concluding the key is dead.

**The skill's facts are in a database, not in the prose.** `tests/test_no_drift.py` fails if
a value attributed to a tank, an instrument or a date reappears in `SKILL.md` or a
reference. That guard is what stops the eight documented contradictions coming back — do not
weaken it to land a sentence.

## Consuming this repo

Wiring this into `tairy-agent` — or any deployment — is documented in one place:
**[`INTEGRATION.md`](INTEGRATION.md)**.

The short version: the four root paths drop in unchanged, and `create-profile.sh` already
handles them. What is *not* handled is that the skill's CLI writes live data to
`${HERMES_HOME}/workspace/aquarium/`, and **that volume is the only copy** — it is not in
git and cannot be. The nightly backup cron that would protect it is not installed by
anything, and the backup/restore round trip in CI asserts a Postgres row rather than a file.

That detail is deliberately *not* repeated here. It cites line numbers in another repo,
three of which had already drifted when the note was written — one into an entirely
unrelated section. `scripts/check-integration-note.sh` re-verifies all eleven citations
when `../tairy-agent` is present and skips cleanly when it is not.
