#!/usr/bin/env bash
# Create the local Python environment for the Shrimpy harness.
#
# Installs (in this order, each step skipped when already satisfied):
#   1. uv                              -> ~/.local/bin/uv
#   2. .venv on Python 3.11            -> the version upstream Hermes pins
#   3. hermes-agent, editable, CORE ONLY (no extras: no Playwright, no Postgres)
#   4. pytest + pyyaml                 -> the harness itself
#
# Idempotent. Safe to re-run after `git submodule update`.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
die() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# --- 1. uv ------------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
    if [ -x "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    else
        say "installing uv"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi
command -v uv >/dev/null 2>&1 || die "uv is not on PATH after install; add ~/.local/bin to PATH"
say "uv $(uv --version | awk '{print $2}')"

# --- 2. the submodule -------------------------------------------------------
if [ ! -f vendor/hermes-agent/pyproject.toml ]; then
    say "fetching the hermes-agent submodule"
    git submodule update --init --depth 1 vendor/hermes-agent
fi
HERMES_SHA="$(git -C vendor/hermes-agent rev-parse --short HEAD)"
say "hermes-agent @ ${HERMES_SHA}"

# --- 3. venv ----------------------------------------------------------------
# Upstream requires >=3.11,<3.14 and pins 3.11 in .python-version. uv fetches it
# if the host has no 3.11, which keeps this independent of whatever python3 is.
if [ ! -x .venv/bin/python ]; then
    say "creating .venv (python 3.11)"
    uv venv .venv --python 3.11
fi

# --- 4. dependencies --------------------------------------------------------
# Core only. `[all]` pulls messaging/voice/browser backends this harness never uses.
say "installing hermes-agent (editable, core only)"
VIRTUAL_ENV="$REPO/.venv" uv pip install --quiet -e vendor/hermes-agent

say "installing harness dependencies"
VIRTUAL_ENV="$REPO/.venv" uv pip install --quiet pytest pyyaml

# --- 5. .env ----------------------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
    say "created .env from .env.example — add your OPENROUTER_API_KEY"
fi

say "ready. Try:  ./shrimpy test        (offline, no API key needed)"
say "             ./shrimpy prompt --skills"
say "             ./shrimpy ask 'is 6.6 too low'"
