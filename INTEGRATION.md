# Integrating this repo into a deployment

For whoever wires **Shrimpy** into [`tairy-agent`](../tairy-agent) — or any other
deployment. Nothing in this file changes anything in that repo; it is the list of things
that repo has to be true for the agent defined here to survive contact with a real server.

> **Citations were verified against `tairy-agent` at `e53c3bf`**, which vendors
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

## 3. What is not done yet

Four items, in the order they bite.

### 3.1 The nightly backup cron is not installed by anything

`docs/ec2-deploy.md:295-310` is a copy-paste block for a human. `scripts/install.sh:160`
only *prints* a reminder:

```
3. Set up nightly backups — docs/ec2-deploy.md
```

Until someone runs that block, this data has **one copy on one EBS volume** — precisely the
failure `specs/15:264-268` names:

> a backup on the same disk as the data survives a bad `docker volume rm` but not a dead
> EBS volume

This is the highest-consequence item in this file.

### 3.2 CI proves a Postgres row round-trips, not a file

`.github/workflows/docker-smoke-test.yml` does test backup/restore, and does it carefully —
but the canary it restores and asserts is a **database row**:

```sh
got="$(dc exec -T postgres psql -U "$POSTGRES_USER" -d hindsight -tAc \
  "SELECT v FROM ci_canary" ...)"
[ "$got" = "CI-CANARY-VALUE" ] || { echo "restored data does not match"; exit 1; }
```

For `hermes-data.tar.gz` the only assertion is that the file is non-empty (`[ -s "$d/$f" ]`,
around `:1333-1338`). **No file inside that tarball is ever asserted to survive the round
trip.** A canary written under `workspace/` before the wipe and read back after the restore
closes the gap — and is the only check that would catch a regression in the path this
agent's data actually takes.

### 3.3 `hermes-data` is skipped entirely when the container is down

An asymmetry worth knowing *before* an incident, not during one. `hermes-data` is captured
through the running container:

```sh
dc exec -T hermes tar czf - -C /opt/data . > "${RUN_DIR}/hermes-data.tar.gz"   # backup.sh:106
```

whereas `synapse-media` and `caddy-data` are read from the volume directly
(`backup.sh:127-128`) and are captured either way. **A backup taken while `hermes` is down
silently omits the aquarium data.** `backup.sh` does refuse to exit 0 on an incomplete
backup unless `--allow-partial` is passed, so this surfaces — but only if someone reads the
exit code.

### 3.4 Two scripts destroy it, and one of them is not obvious

- `wipe.sh --yes` removes every volume carrying the compose project label
  (`scripts/wipe.sh:75`), `hermes-data` among them. Unsurprising.
- `restore.sh --yes` is the subtle one: **restoring a backup taken before this data existed
  deletes it just as thoroughly as a wipe.**

---

## 4. Documentation in `tairy-agent` that is already wrong

The volume table at `docs/storage.md:17-25` has three stale cells. `backup.sh` has since
been fixed; the table was not updated:

| Row | Table says | `backup.sh` actually does |
|---|---|---|
| `postgres-data` | ⚠️ `synapse` only | `for db in synapse hindsight` — both (`:80`) |
| `synapse-media` | ❌ | `archive_volume ...` — captured (`:127`) |
| `caddy-data` | ❌ | `archive_volume ...` — captured (`:128`) |

`caddy-logs` and `caddy-config` are correctly marked ❌.

Anyone reasoning about backup coverage from that table reaches the wrong conclusion in both
directions — believing memory is lost when it is safe, and not asking about the one store
that really is conditional (§3.3).

> An earlier version of this note cited `docs/storage.md:85-93` for this. That is now the
> log-retention section and has nothing to do with backup coverage. It is the clearest
> argument for `check-integration-note.sh`.

---

## 5. What this repo does not own

Matrix accounts, display names, avatars on the homeserver, secrets, Hindsight memory,
ingress, the container image, and the deployment's own CI. Unchanged by anything here.
