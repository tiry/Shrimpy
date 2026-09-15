#!/usr/bin/env bash
# Re-verify every citation in INTEGRATION.md against the real tairy-agent checkout.
#
# The note points into another repo. Three of its line numbers had already drifted when it
# was written, and one of them had drifted so far it pointed at an unrelated section --
# which is the kind of error that makes a reader conclude the opposite of the truth.
#
# Skips cleanly when ../tairy-agent is absent, so CI stays green on a runner that has only
# this repo. Run it before trusting the note.
#
#   scripts/check-integration-note.sh [path-to-tairy-agent]

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAIRY="${1:-${ROOT}/../tairy-agent}"
NOTE="${ROOT}/INTEGRATION.md"

if [ ! -d "$TAIRY" ]; then
    echo "skip: no tairy-agent checkout at ${TAIRY}"
    echo "      INTEGRATION.md citations were NOT verified."
    exit 0
fi

VENDOR="${TAIRY}/vendor/hermes-agent"
pass=0 fail=0 moved=0

# claim <file> <line> <pattern-that-must-be-on-or-near-it>
claim() {
    local file="$1" want_line="$2" pattern="$3" label="${4:-}"
    local path="${file/#hermes-agent\//${VENDOR}/}"
    [ "$path" = "$file" ] && path="${TAIRY}/${file}"

    if [ ! -f "$path" ]; then
        printf '  FAIL  %-58s file does not exist\n' "${file}:${want_line}"
        fail=$((fail + 1)); return
    fi

    local got
    got="$(grep -n -- "$pattern" "$path" 2>/dev/null | head -1 | cut -d: -f1)"
    if [ -z "$got" ]; then
        printf '  FAIL  %-58s pattern gone: %s\n' "${file}:${want_line}" "$pattern"
        printf '        %s\n' "${label:-the claim this supports may no longer be true}"
        fail=$((fail + 1)); return
    fi

    # A cited range "295-310" is satisfied by a hit anywhere inside it.
    local lo="${want_line%%-*}" hi="${want_line##*-}"
    if [ "$got" -ge "$lo" ] && [ "$got" -le "$hi" ]; then
        printf '  ok    %-58s\n' "${file}:${want_line}"
        pass=$((pass + 1))
    else
        printf '  MOVED %-58s now at line %s\n' "${file}:${want_line}" "$got"
        printf '        fix INTEGRATION.md: %s -> %s:%s\n' "${file}:${want_line}" "$file" "$got"
        moved=$((moved + 1))
    fi
}

echo "verifying INTEGRATION.md against ${TAIRY}"
echo "  tairy-agent   $(git -C "$TAIRY" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo "  hermes-agent  $(git -C "$VENDOR" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo

# 2 - what already protects the data
claim "hermes-agent/hermes_cli/profiles.py"             62       '"workspace"' \
      "workspace may no longer be a profile-owned dir"
claim "hermes-agent/hermes_cli/profile_distribution.py" 112      '"workspace"' \
      "workspace may no longer be hard-excluded from distribution"
claim "hermes-agent/docker/stage2-hook.sh"              250      'workspace' \
      "workspace may no longer be created/chowned at boot"
claim "scripts/create-profile.sh"                       74       'rm -rf' \
      "CRITICAL: if this rm -rf is no longer scoped to skills/, live data dies on provision"

# 3.1 - the cron nobody schedules
claim "docs/ec2-deploy.md"                              490      'crontab -l'
claim "scripts/install.sh"                              102      'backup-nightly' \
      "install.sh may now actually schedule the cron -- good news, update the note"

# 3.2 / 3.3 - what CI proves and how backup.sh captures hermes-data
claim ".github/workflows/docker-smoke-test.yml"         1384     'ci-canary.txt' \
      "the workspace file canary may have been removed; 3.2 would reopen"
claim ".github/workflows/docker-smoke-test.yml"         1424     'grep -c .workspace/ci-canary'
claim "scripts/backup.sh"                               167      'archive_volume.*hermes-data' \
      "hermes-data may be captured through the container again; 3.3 would reopen"
claim "scripts/backup.sh"                               81       'for db in synapse hindsight'

# 3.4 - what destroys it
claim "scripts/wipe.sh"                                 75       'docker volume ls'

# 4 - the one stale cell
claim "docs/storage.md"                                 20       'only while the container is running' \
      "the stale caveat may have been fixed -- if so, delete section 4"

# 5 - the bundled-skill re-seed chain
claim "docker-compose.yml"                              222      'command:' \
      "the container may no longer start via the gateway; re-check whether the skill sync runs"
claim "hermes-agent/hermes_cli/main.py"                 3512     '^    _sync_bundled_skills_quietly()' \
      "cmd_gateway may no longer re-seed bundled skills - good news, update the note"
claim "hermes-agent/tools/skills_sync.py"               711      'def sync_skills'
claim "hermes-agent/tools/skills_sync.py"               728      'essential_only = ' \
      "CRITICAL: the opt-out marker is what the fix in section 5 depends on"
claim "hermes-agent/agent/skill_utils.py"               443      'ESSENTIAL_SKILLS: frozenset'
claim "scripts/bootstrap.sh"                            672      'dc restart hermes' \
      "if bootstrap no longer restarts hermes after create-profile, the re-seed may not happen"

# 6 - the toolset divergence
claim "hermes-agent/toolsets.py"                        33       '"web_search", "web_extract"' \
      "_HERMES_CORE_TOOLS may no longer grant web access to the Matrix bundle"
claim "hermes-agent/toolsets.py"                        552      '"hermes-matrix"'

echo
printf 'verified %d, moved %d, failed %d\n' "$pass" "$moved" "$fail"
if [ "$fail" -gt 0 ] || [ "$moved" -gt 0 ]; then
    echo
    echo "INTEGRATION.md is out of date. A citation that points at the wrong lines is"
    echo "worse than none: the storage.md one drifted into an unrelated section and"
    echo "would have had a reader conclude the opposite of the truth."
    exit 1
fi
echo "INTEGRATION.md citations are accurate."
