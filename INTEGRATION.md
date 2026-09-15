# Integrating this repo into a deployment

For whoever wires **Shrimpy** into [`tairy-agent`](../tairy-agent) — or any other
deployment. Nothing in this file changes anything in that repo; it is the list of things
that repo has to be true for the agent defined here to survive contact with a real server.

> **Citations were verified against `tairy-agent` at `9306cf0`**, which vendors
> `hermes-agent` at `29112be` — the same commit this repo pins. Line numbers in another
> repo drift; three of them already had when this note was written, so **re-check before
> acting, and treat a miss as a moved line rather than a fixed problem.**
> `scripts/check-integration-note.sh` re-verifies every one of them when `../tairy-agent`
> is present.

---

## 1. What you get, and what already handles it

Four paths at the root of this repo:

```
SOUL.md  DISPLAYNAME  avatar.png  skills/
```

That is exactly the shape of a `profiles/<name>/` directory, so
`scripts/create-profile.sh` already copies it out with no changes. `tests/test_profile_layout.py`
fails here if that drifts. Everything else in this repo — `harness/`, `evals/`, `tests/`,
`scripts/`, `specs/`, `vendor/` — is tooling a deployment ignores.

**This section needs no work.** The rest of this file does.

---

## 2. The one thing that is genuinely new: live data

The skill ships a CLI, `skills/aquarium/aquarium-supervisor/scripts/aqua.py`, that does not
just read — it **writes**: measurements, livestock, supplies. It writes to

```
${HERMES_HOME}/workspace/aquarium/
```

and that is the **only copy of that data anywhere.** It is not in git and it cannot be: the
agent writes it, and the agent cannot write to a repo. This is the whole reason this file
exists. See [`specs/06`](specs/06-live-data-and-reporting.md).

### What already protects it

Not in `tairy-agent` — in `hermes-agent`, which both repos vendor at `29112be`:

| Protection | Where |
|---|---|
| `workspace` is a profile-owned dir, not replaced on provision | `hermes_cli/profiles.py:62` |
| `workspace` is hard-excluded from profile distribution | `hermes_cli/profile_distribution.py:112`, `:658` |
| `workspace` is created and `chown`ed at container boot | `docker/stage2-hook.sh:250`, `:392` |
| `create-profile.sh`'s `rm -rf` is scoped to `skills/` | `tairy-agent/scripts/create-profile.sh:74` |

That last one is worth reading directly, because it is one edit away from being a disaster:

```sh
dc exec -T hermes sh -c "rm -rf '${home}/skills' && mkdir -p '${home}/skills'"
```

**Widening that to the profile home destroys the data on every provision** — and both
`bootstrap.sh` and `update.sh` call it.

---

## 3. Live-data durability: mostly done, one item left

This section listed four gaps. **Three have since been closed** — the note is kept rather
than deleted because what was fixed, and how, is the useful record.

### 3.1 The nightly backup cron is still not installed by anything — OPEN

`scripts/backup-nightly.sh` now exists, which is the hard part. What is still missing is
anything that *schedules* it. `docs/ec2-deploy.md:490` is a copy-paste block for a human:

```sh
( crontab -l 2>/dev/null
  echo "0 3 * * * /home/ubuntu/tairy-agent/scripts/backup-nightly.sh >> /home/ubuntu/backup.log 2>&1"
) | crontab -
```

and `scripts/install.sh:102` mentions the script only in a comment about the AWS CLI. No
installer writes the crontab.

Until someone runs that block, the aquarium data has **one copy on one EBS volume**. This
is the last remaining item in this section and the highest-consequence one in this file.

### 3.2 CI now proves a file round-trips — CLOSED

The backup/restore smoke test used to assert only that `hermes-data.tar.gz` was non-empty,
so nothing proved a file inside it survived. It now writes a canary into the live-data path
and checks it comes back:

```sh
dc exec -T hermes sh -c 'mkdir -p /opt/data/workspace && echo CI-FILE-CANARY > /opt/data/workspace/ci-canary.txt'
```

`.github/workflows/docker-smoke-test.yml:1384`, asserted at `:1424`. That is exactly the
path this skill's CLI writes to.

### 3.3 `hermes-data` is no longer captured through the container — CLOSED

It used to be tarred via `dc exec`, making it the one store that vanished from a backup
taken while its service was down. It is now read from the volume like everything else —
`scripts/backup.sh:167`, with the reasoning recorded in the comment above it.

### 3.4 Two scripts still destroy it, and one is not obvious — UNCHANGED

- `wipe.sh --yes` removes every volume carrying the compose project label
  (`scripts/wipe.sh:75`), `hermes-data` among them. Unsurprising.
- `restore.sh --yes` is the subtle one: **restoring a backup taken before this data existed
  deletes it just as thoroughly as a wipe.**

---

## 4. One stale cell left in `docs/storage.md`

The volume table has been rewritten and is now correct about coverage — every store reads
✅, including the Hindsight database, `synapse-media` and `caddy-data` that this note
previously flagged.

One cell has gone stale in the opposite direction. `docs/storage.md:20` still qualifies
`hermes-data` with:

> ✅ whole-volume tar, **but only while the container is running**

That was true and is no longer: `scripts/backup.sh:167` reads it from the volume, and the
comment directly above says so in as many words. The caveat now warns about a risk that has
been engineered away, which will cost someone an unnecessary decision during an incident.

---

## 5. The profile is not skills-only, and wiping the directory does not make it so

`create-profile.sh:74` wipes `${home}/skills` and copies the profile's skills in. That is
undone almost immediately, and the chain is worth reading in full because each link looks
harmless:

| | |
|---|---|
| `docker-compose.yml:222` | the container's command is `["gateway", "run"]` |
| `hermes-agent/hermes_cli/main.py:3511` | `cmd_gateway` calls `_sync_bundled_skills_quietly()` |
| `hermes-agent/tools/skills_sync.py:711` | `sync_skills()` copies **all 58 bundled skills** into `$HERMES_HOME/skills/` |
| `scripts/bootstrap.sh:672` | **restarts hermes right after `create-profile.sh`**, so the sync runs again |

So the agent is carrying Apple Notes, p5.js, four coding-agent delegators, GitHub, email and
X posting. Most are inert for want of credentials, and the cost is mainly ~1,175 tokens of
skill index on every API call — but `autonomous-ai-agents/hermes-agent` can "configure,
theme, extend, and orchestrate Hermes Agent", and it **cannot be disabled**
(`hermes-agent/agent/skill_utils.py:443`).

**Check it before deciding it does not matter:**

```sh
docker compose exec hermes ls ~/.hermes/skills/
```

One directory means the profile is clean. Twelve means the sync has run.

### The fix

One marker file, which is the only mechanism that survives a gateway restart
(`hermes-agent/tools/skills_sync.py:728,746-751`):

```sh
docker compose exec hermes touch /opt/data/.no-bundled-skills
```

Better, in `create-profile.sh` beside the `rm -rf`, so it is reapplied on every provision.
With it, `sync_skills()` seeds only `ESSENTIAL_SKILLS` — `hermes-agent` and nothing else —
leaving this repo's three skills plus that one.

`skills.disabled` in `config.yaml` is the weaker alternative: it hides skills from the index
but leaves the files, and the list must be re-audited on every hermes-agent upgrade.

## 6. The harness tests a narrower agent than you deploy

Recorded because it changes how much an eval proves, not because this repo can fix it.

| | Toolsets |
|---|---|
| Deployed (Matrix) | `hermes-matrix` → `_HERMES_CORE_TOOLS`: `web_search`, `web_extract`, `terminal`, `process`, and the full `browser_*` set (`hermes-agent/toolsets.py:32`, `:552`) |
| This repo's harness | `["skills", "file", "terminal"]` (`harness/agent.py:56`) |

**No eval exercises the web or browser tools the real agent has.** Every behavioural result
in this repo describes an agent that cannot reach the internet; the deployed one can. The
access boundary in [`specs/04`](specs/04-access-boundary.md) constrains what the agent
should reach on the LAN, and says nothing about this.

## 7. What this repo does not own

Matrix accounts, display names, avatars on the homeserver, secrets, Hindsight memory,
ingress, the container image, and the deployment's own CI. Unchanged by anything here.
