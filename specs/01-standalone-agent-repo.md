# 01 — Standalone agent repo and harness

| | |
|---|---|
| **ID** | 01 |
| **Severity** | High |
| **Status** | **Done** |
| **Affected files** | `SOUL.md`, `DISPLAYNAME`, `avatar.png`, `skills/`, `shrimpy`, `harness/`, `scripts/setup.sh`, `vendor/hermes-agent` (submodule), `.env.example`, `.gitignore` |
| **Depends on** | — |

## Problem

Shrimpy's persona and skills lived inside `tairy-agent/profiles/shrimpy/`, a
Hermes/Synapse deployment repo. Changing a decision rule and seeing the effect required the
whole stack: Synapse, PostgreSQL, Hindsight, Caddy, a Matrix account, a provisioning script
and a container restart (`tairy-agent/scripts/create-profile.sh`,
`tairy-agent/docker-compose.yml`). None of that has anything to do with the persona.

There was also no way to test the agent at all. Upstream's documented method for verifying
a skill is, verbatim (`vendor/hermes-agent/website/docs/developer-guide/creating-skills.md:323`):

> Run the skill and verify the agent follows the instructions correctly:
> `hermes chat --toolsets skills -q "Use the X skill to do Y"`

## Why it matters

The persona is the thing under development. Anything that makes editing it expensive makes
it worse, because the loop that improves a `SOUL.md` is *read the reply, adjust one
sentence, read the reply again*. At a container rebuild per iteration that loop does not
run.

## What upstream actually provides

Verified against the pinned submodule (`vendor/hermes-agent`, `29112be`) rather than the
docs.

**A persona is one directory.** `hermes_constants.py:114-139` — `get_hermes_home()`
resolves `HERMES_HOME`, and everything else follows from it: `SOUL.md`
(`agent/prompt_builder.py:2214`), `config.yaml` (`hermes_cli/config.py:770`), `skills/`
(`hermes_constants.py:1667`). `ensure_hermes_home()` (`hermes_cli/config.py:943-987`)
creates the rest of the tree itself, so the minimum viable home is an empty directory.

**Profiles are not needed.** `hermes -p <name>` is sugar for setting `HERMES_HOME`
(`hermes_cli/main.py:698-719`), and there is no registry — `list_profile_names()`
(`hermes_cli/profiles.py:434-450`) is a directory scan.

**There is no test harness.** `tests/` is 3,594 files but is excluded from the package
(`pyproject.toml:585`), and `setup.py:34-44` hard-blocks wheel and sdist builds, so no
fixture is importable. `evals/` is four bespoke harnesses with no shared code and no
`__init__.py` anywhere. There is no fake LLM provider, no VCR/replay, and neither is a dev
dependency (`pyproject.toml:199`).

## Constraints

1. **Layout must stay drop-in for the deployment.** `create-profile.sh` copies `SOUL.md`,
   `skills/*`, `DISPLAYNAME` and `avatar.png` out of a profile directory. If this repo is
   to be consumed as one, those must sit at the root.
2. **No runtime state in the definition.** `create-profile.sh:74` does
   `rm -rf "${home}/skills"` on every provision, and the deployment generates its own
   `config.yaml` and `.env` on the volume. Committing either would be overwritten at best
   and leak a key at worst.
3. **`HERMES_HOME` must be set before `import run_agent`.** That module resolves the home
   and loads `.env` at import time (`run_agent.py:127-129`), so a later assignment is
   ignored.
4. **`--safe-mode` and `--ignore-rules` silently drop `SOUL.md`.** Both set
   `skip_context_files`, and `agent/system_prompt.py:472-487` then substitutes
   `DEFAULT_AGENT_IDENTITY`. The agent still answers, competently, as nobody in particular.
5. **The skill index requires a skills tool in the toolset.** `agent/system_prompt.py:619`
   gates the entire `<available_skills>` block on `skills_list`/`skill_view`/`skill_manage`
   being present.

## Proposed change

### The repo is the profile

```
SOUL.md  DISPLAYNAME  avatar.png  skills/aquarium/...
```

at the root, so `tairy-agent` can consume the directory unchanged.

### The harness builds a throwaway `HERMES_HOME`

`harness/home.py` creates a home whose `SOUL.md` and skill categories are **symlinks into
the repo**, so editing a `SKILL.md` is live on the next run with no sync step. `skills/`
itself is a real directory the harness owns, because Hermes chmods it. Runtime state lands
in `.work/` or a temp directory, both gitignored.

A guard borrowed from upstream's own test suite (`tests/conftest.py:64`) refuses to operate
on `~/.hermes`.

### Runs go through the Python API, not `hermes -z`

`-z` prints only the final response text (`hermes_cli/_parser.py:153-165`). That makes the
single most important question about a skill-driven persona — *did it open the aquarium
skill?* — unanswerable from its output. It also opens a `state.db`, fires an auto-title LLM
call, and exits via `os._exit()` (`hermes_cli/main.py:117-132`).

`harness/agent.py` constructs `AIAgent` directly with `session_db=None`, `skip_memory=True`
and `skip_background_review=True`, and recovers structured results from the message list.

### One entrypoint

`./shrimpy` — `setup`, `test`, `prompt`, `ask`, `chat`, `eval`, `snapshots`. It re-execs
into `.venv` so nothing depends on an activated shell.

## Options considered

| Option | Why not |
|---|---|
| Docker, single container | Requires an image build per iteration and makes the Python API awkward to reach. The whole point is a sub-second loop. |
| Point at `../tairy-agent/vendor/hermes-agent` | Zero duplication, but the repo stops being self-contained and pins nothing. |
| Local venv + pinned submodule | **Chosen.** Same SHA the deployment runs, so local behaviour matches. |

## Acceptance criteria

- [x] `SOUL.md`, `DISPLAYNAME`, `avatar.png`, `skills/` at the repo root, byte-identical to
      the `tairy-agent` originals at import time
- [x] `vendor/hermes-agent` pinned to `29112be` — the SHA the deployment runs
- [x] `./shrimpy setup` installs `uv`, a 3.11 venv and hermes-agent core-only, idempotently
- [x] `./shrimpy ask` returns an answer with the persona applied
- [x] `./shrimpy chat` drops into the real Hermes REPL as Shrimpy
- [x] No `config.yaml`, `.env`, `state.db` or snapshot file is tracked in git
- [x] `tests/test_profile_layout.py` fails if the deployment-compatible layout drifts

## Verification

**Offline.** `tests/test_profile_layout.py` asserts the four root paths exist, `DISPLAYNAME`
is one line, `avatar.png` is under the 2 MB Matrix cap enforced by
`set-matrix-identity.sh`, the skills tree is two levels deep, and no runtime state is
tracked (checked against `git ls-files`, so a local gitignored `.env` is fine).

**Live.** `./shrimpy ask "Which tank has the snails in it?"` returned the correct tank in
one line, in Shrimpy's register — confirming `SOUL.md` was loaded rather than
`DEFAULT_AGENT_IDENTITY`.

## Out of scope

Matrix, Synapse, Caddy, Hindsight, docker-compose, secrets provisioning, avatar and
display-name publishing, multi-profile multiplexing. All remain the deployment's concern.

## Open questions

- **Sync direction.** `tairy-agent` still holds its own copy of these files. Making it
  consume this repo — as a submodule or via a sync script — is the next structural step and
  is not covered here.
