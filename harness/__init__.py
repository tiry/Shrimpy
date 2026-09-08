"""Shrimpy test harness.

Runs the real Hermes agent against this repo's persona, with nothing else:
no Matrix, no Synapse, no Hindsight, no Caddy, no docker-compose.

The whole trick is that Hermes needs exactly one thing to adopt a persona —
``HERMES_HOME`` pointing at a directory holding ``SOUL.md``, ``config.yaml`` and
``skills/``. Everything in this package is scaffolding around that fact.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

__all__ = ["REPO_ROOT"]
