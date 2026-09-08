#!/usr/bin/env bash
# Build a pH trend from the CLI and render it, end to end.
#
# Used by CI so a human can look at the chart rather than trust a green tick,
# and runnable locally for the same reason. The offline tests assert the plotted
# line follows the data; this shows you the line.
#
# The series is the documented story of these tanks: pH climbing toward its
# settling point as the crushed coral equilibrates over several weeks.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-${REPO}/.work/demo}"
DATA="${OUT}/data"

# Prefer the repo venv. Charts are drawn with Pillow, which is a core Hermes
# dependency and therefore present in .venv — and in the deployment container,
# where the venv's python is first on PATH, so this is also what the agent gets.
# A bare system python3 usually has no Pillow and the CLI degrades to SVG. That
# fallback is deliberate and correct, but it is not what we are demonstrating,
# and CI caught exactly that: the first run uploaded an .svg and the .png the
# artifact asked for was silently missing.
if [ -x "${REPO}/.venv/bin/python" ]; then
    PY="${REPO}/.venv/bin/python"
else
    PY="python3"
fi
AQUA="${PY} ${REPO}/skills/aquarium/aquarium-supervisor/scripts/aqua.py"

rm -rf "$OUT"
mkdir -p "$OUT"

aqua() { $AQUA --data-dir "$DATA" "$@"; }

aqua status >/dev/null   # seeds tanks, livestock and inventory from the skill

# Start the reading log empty. The bundled snapshot carries a handful of readings
# from one afternoon, and interleaving those with a synthetic multi-week series
# produces a sawtooth that misrepresents both. This demonstrates the chart, so
# the chart gets a clean series; the real data is what `aqua status` shows.
: > "${DATA}/readings.ndjson"

# Two readings a day apart would be a delta, not a trend. Fourteen over four
# weeks is enough for the shape to mean something.
#
# Dated backwards from today rather than pinned to fixed dates, so the chart
# never renders readings "in the future" and `status` reports a believable age.
VALUES=(6.78 6.80 6.79 6.83 6.85 6.86 6.88 6.91 6.93 6.92 6.97 7.01 7.03 7.05)
COUNT=${#VALUES[@]}
for i in "${!VALUES[@]}"; do
    days_ago=$(( (COUNT - 1 - i) * 2 ))
    # Local time, matching what the CLI stamps on a reading logged "now".
    # Using UTC here put the newest point a day into the future.
    day=$(date -d "${days_ago} days ago" +%Y-%m-%d)
    aqua log ph "${VALUES[$i]}" --tank display --instrument kactoily \
        --at "${day}T09:00" >/dev/null
done

aqua plot ph --tank display --out "${OUT}/ph-trend.png"
aqua report --out "${OUT}/report.html"
aqua export --format csv --out "${OUT}/csv" >/dev/null

# Fail loudly rather than shipping an artifact with a hole in it.
if [ ! -s "${OUT}/ph-trend.png" ]; then
    echo "error: no PNG chart was produced." >&2
    if [ -s "${OUT}/ph-trend.svg" ]; then
        echo "       The CLI fell back to SVG, which means Pillow is missing from" >&2
        echo "       ${PY}. Run ./shrimpy setup, or point this at the venv." >&2
    fi
    exit 1
fi

echo
echo "--- aqua readings ph --tank display ---"
aqua readings ph --tank display --limit 6
