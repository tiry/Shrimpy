"""Build an ephemeral ``HERMES_HOME`` that makes Hermes answer as Shrimpy.

Hermes adopts a persona from a single directory (``hermes_constants.py:114``):

    $HERMES_HOME/SOUL.md      the persona
    $HERMES_HOME/config.yaml  model + behaviour
    $HERMES_HOME/skills/      the skill tree

Everything else in that directory — ``sessions/``, ``logs/``, ``state.db`` — is
runtime state Hermes creates itself. So the harness never copies the repo into a
home; it *links* the two files that are the agent definition and lets Hermes
scribble around them. Editing a ``SKILL.md`` is then live on the next run with no
sync step.

Nothing here writes into the repo. ``.work/`` and temp dirs only.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from . import REPO_ROOT

# Both roles run the same model. Chosen on measurement, not on price alone:
# gemini-3.8-flash passes all 16 evals at about a fifth of Sonnet 5's cost, and
# as a judge it correctly fails every one of five deliberately-bad replies -
# including the fabricated "I ran it, the dashboard shows..." that a judge must
# never let through. gemini-2.5-flash was tried first and rejected: it failed
# three cases on safety-relevant rules and, as a judge, passed a reply that
# should have failed.
#
# The deployment's own model is set separately. If it diverges from this, the
# evals stop measuring what ships - see specs/06.
DEFAULT_MODEL = "google/gemini-3.8-flash"
DEFAULT_JUDGE_MODEL = "google/gemini-3.8-flash"
DEFAULT_PROVIDER = "openrouter"

# The skills index is cached to disk and validated against an mtime/size
# manifest (agent/prompt_builder.py:1519). The manifest is reliable, but a
# harness whose entire job is detecting skill-file changes should not depend on
# cache invalidation being correct — so we delete it every run.
SNAPSHOT = ".skills_prompt_snapshot.json"


# --------------------------------------------------------------------------- #
# .env
# --------------------------------------------------------------------------- #

def load_env(path: Path | None = None) -> dict[str, str]:
    """Load the repo's .env into os.environ without clobbering real env vars.

    Deliberately minimal: KEY=VALUE, ``#`` comments, optional quotes. An actual
    dotenv parser is not worth a dependency for a four-key file.
    """
    path = path or (REPO_ROOT / ".env")
    loaded: dict[str, str] = {}
    if not path.is_file():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if not key or not val:
            continue
        loaded[key] = val
        # A value already exported in the shell wins — that is what makes
        # `SHRIMPY_MODEL=x ./shrimpy ask ...` work.
        os.environ.setdefault(key, val)
    return loaded


def resolve_model(override: str | None = None) -> str:
    return override or os.environ.get("SHRIMPY_MODEL") or DEFAULT_MODEL


def resolve_judge_model(override: str | None = None) -> str:
    return override or os.environ.get("SHRIMPY_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL


def resolve_provider(override: str | None = None) -> str:
    return override or os.environ.get("SHRIMPY_PROVIDER") or DEFAULT_PROVIDER


def require_api_key() -> str:
    """Fail loudly and early rather than mid-run with a provider auth error."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not set.\n"
            "  Put it in .env (see .env.example), or export it.\n"
            "  Offline commands (`./shrimpy test`, `./shrimpy prompt`) need no key."
        )
    return key


# --------------------------------------------------------------------------- #
# home construction
# --------------------------------------------------------------------------- #

def _assert_not_production(home: Path) -> None:
    """Refuse to ever operate on the user's real Hermes install.

    Borrowed from upstream's own test guard (tests/conftest.py:64). A harness bug
    that pointed HERMES_HOME at ~/.hermes would seed SOUL.md, rewrite config.yaml
    and drop a state.db into a live agent.
    """
    real = Path.home() / ".hermes"
    try:
        resolved = home.resolve()
    except OSError:
        return
    if resolved == real or real in resolved.parents:
        raise SystemExit(f"refusing to use a HERMES_HOME inside {real}: {home}")


def _link_or_copy(src: Path, dst: Path) -> None:
    """Symlink src -> dst, falling back to a copy where symlinks are unavailable."""
    if dst.is_symlink() or dst.exists():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    try:
        dst.symlink_to(src, target_is_directory=src.is_dir())
    except OSError:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def _soul_is_safe_to_link(soul: Path) -> bool:
    """Would Hermes overwrite this SOUL.md in place?

    ``_ensure_default_soul_md`` (hermes_cli/config.py:916) replaces a SOUL.md it
    considers a legacy comment-only scaffold. Through a symlink that write would
    land in the repo. A real persona never trips it, but the check is three lines
    and the failure mode is losing the file under test.
    """
    try:
        text = soul.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return len(text.strip()) > 200


def render_config(model: str, provider: str) -> str:
    template = (REPO_ROOT / "harness" / "config.template.yaml").read_text(encoding="utf-8")
    return template.replace("${MODEL}", model).replace("${PROVIDER}", provider)


def build_home(
    *,
    ephemeral: bool = False,
    model: str | None = None,
    provider: str | None = None,
) -> Path:
    """Create a HERMES_HOME wired to this repo's persona and return its path.

    ephemeral=True  -> a temp dir, for tests and evals (no cross-run state)
    ephemeral=False -> .work/home, for `chat` and `ask` (sessions survive restarts)
    """
    load_env()
    model = resolve_model(model)
    provider = resolve_provider(provider)

    if ephemeral:
        home = Path(tempfile.mkdtemp(prefix="shrimpy-home-"))
    else:
        home = REPO_ROOT / ".work" / "home"
        home.mkdir(parents=True, exist_ok=True)

    _assert_not_production(home)

    # The agent definition, linked live from the repo.
    soul = REPO_ROOT / "SOUL.md"
    if not soul.is_file():
        raise SystemExit(f"missing {soul} — this repo is the agent definition")
    if _soul_is_safe_to_link(soul):
        _link_or_copy(soul, home / "SOUL.md")
    else:
        shutil.copy2(soul, home / "SOUL.md")

    # skills/ itself is a real directory the harness owns (Hermes chmods it);
    # each category inside is a symlink to the repo, so reference files stay live.
    skills_home = home / "skills"
    if skills_home.is_symlink():
        skills_home.unlink()
    skills_home.mkdir(parents=True, exist_ok=True)
    repo_skills = REPO_ROOT / "skills"
    linked = set()
    if repo_skills.is_dir():
        for category in sorted(p for p in repo_skills.iterdir() if p.is_dir()):
            _link_or_copy(category, skills_home / category.name)
            linked.add(category.name)
    # Drop categories deleted from the repo, matching create-profile.sh's
    # wholesale-replace semantics: removing a skill here removes it from the run.
    for stale in skills_home.iterdir():
        if stale.name not in linked:
            if stale.is_symlink() or stale.is_file():
                stale.unlink()
            else:
                shutil.rmtree(stale)

    (home / "config.yaml").write_text(render_config(model, provider), encoding="utf-8")

    # Force a cold rebuild of the skills index.
    snapshot = home / SNAPSHOT
    if snapshot.exists():
        snapshot.unlink()

    return home


def activate(home: Path) -> None:
    """Point this process at ``home``.

    MUST be called before ``import run_agent``: that module resolves
    ``get_hermes_home()`` and loads .env at import time (run_agent.py:127), so a
    later change to the variable is ignored.
    """
    os.environ["HERMES_HOME"] = str(home)
    # Oneshot mode sets these itself (hermes_cli/oneshot.py:255); the library
    # path does not, and an approval prompt would hang a non-interactive run.
    os.environ["HERMES_YOLO_MODE"] = "1"
    os.environ["HERMES_ACCEPT_HOOKS"] = "1"
    # Keep provider auto-detection from wandering off to a key that happens to
    # be exported in the shell (mirrors evals/readtool/runner.py:87).
    for var in [v for v in os.environ if v.endswith("_API_KEY")]:
        if var != "OPENROUTER_API_KEY":
            os.environ.pop(var, None)
