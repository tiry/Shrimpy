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

**When an eval fails, read the reply before touching the skill.** Twice now the harness was
wrong and the agent was right: it named `3.2 mL` *in order to correct it*, and scoped a
caution with a sentence containing "do not add". Forbidding a substring forbids the right
answer too. Use a rubric judge for semantic properties.

**Skill content is input to the harness.** `skills_opened` once scanned tool responses for
`"not found"`; `SKILL.md` §7 contains the phrase `command not found`, so a documentation
edit broke eight of twelve evals. Parse the envelope, never the body.

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

Read this if you are wiring `tairy-agent` — or any deployment — to this repository.

### What you get

The four root paths above. `create-profile.sh` already handles them; nothing changes.

### What you must provide — live data durability

> **Status: required NOW. [`specs/06`](specs/06-live-data-and-reporting.md) has landed —
> the skill ships a CLI that writes live data, and that data exists nowhere but the volume.**

The skill ships a CLI (`skills/aquarium/aquarium-supervisor/scripts/aqua.py`) that reads and
writes live data — measurements, livestock, supplies — at:

```
${HERMES_HOME}/workspace/aquarium/
```

That directory is protected from every code path in both repos: it is in `_PROFILE_DIRS`,
in `USER_OWNED_EXCLUDE`, in the distribution hard-exclude list, and chowned at container
boot. `create-profile.sh` scopes its `rm -rf` to `skills/` and does not touch it.

**But it will be the only copy of that data.** It is not in git, and it cannot be, because
the agent writes it and the agent cannot write to a repo. Four consequences:

1. **The nightly backup cron must actually be installed.** Nothing installs it —
   `docs/ec2-deploy.md:297-311` is a copy-paste block and `scripts/install.sh:160` only
   *prints* a reminder. Until it runs, this data has one copy on one EBS volume, which is
   the failure `specs/15:266` names: *"a backup on the same disk as the data survives a bad
   `docker volume rm` but not a dead EBS volume."*

2. **CI must gain a canary file under `workspace/`.** Today the backup/restore round trip in
   `.github/workflows/docker-smoke-test.yml` asserts a **Postgres row** survives, and only
   checks that `hermes-data.tar.gz` is non-empty. No file inside it is ever asserted to
   round-trip. A canary written before the wipe and read after the restore closes that.

3. **`create-profile.sh` must keep its `rm -rf` scoped to `skills/`.** Widening it to the
   profile home, or adding `workspace/` to what it replaces, destroys the data on every
   provision — and `bootstrap.sh` and `update.sh` both call it.

4. **`wipe.sh --yes` and `restore.sh --yes` destroy it.** They are the only two paths that
   reach it. `restore.sh` is the subtle one: restoring a backup taken *before* the data
   existed deletes it just as thoroughly as wiping.

One asymmetry worth knowing before an incident: `hermes-data` is captured through
`dc exec` (`backup.sh:102`), so **it is skipped entirely if the `hermes` container is
down** — unlike `synapse-media` and `caddy-data`, which are read from the volume directly
and captured either way.

### Documentation that is already wrong

`tairy-agent/docs/storage.md:85-93` still says the backup does not capture the Hindsight
database, `synapse-media` or `caddy-data`. `backup.sh` has since been fixed and captures all
three. Anyone reasoning about backup coverage from that section will reach the wrong
conclusion.

### What this repo does not own

Matrix accounts, display names, avatars on the homeserver, secrets, Hindsight memory,
ingress, the container image. Unchanged.
