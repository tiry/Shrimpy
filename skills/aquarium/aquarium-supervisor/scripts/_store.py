"""Storage for the aquarium CLI: paths, atomic IO, seeding, schema migration.

Three tiers, and the distinction is the whole design (see specs/06):

  reference   <skill>/assets/reference.json    ships with the skill, replaced on
                                               every provision, in git
  initial     <skill>/assets/initial/*.json    a one-time migration payload
  instance    $HERMES_HOME/workspace/aquarium/ the live data, on the volume only

The instance directory is deliberate. ``create-profile.sh`` does
``rm -rf "${home}/skills"`` on every provision, so anything under the skill is
destroyed; ``workspace/`` is in ``_PROFILE_DIRS``, in ``USER_OWNED_EXCLUDE`` and in
the distribution hard-exclude list, and no code path in either repo deletes inside
it.

Writes are atomic (temp file + ``os.replace`` in the same directory) because the
deployment's backup tars ``/opt/data`` live, without quiescing. A half-written JSON
would be captured torn. No ``fcntl`` — it trips the skill linter's
``platforms-gating`` rule, and single-process CLI invocations do not need it.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterator

SCHEMA_VERSION = 1

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
REFERENCE_FILE = ASSETS_DIR / "reference.json"
INITIAL_DIR = ASSETS_DIR / "initial"

JSON_FILES = ("tanks.json", "livestock.json", "inventory.json", "questions.json")
LOG_FILES = ("readings.ndjson", "events.ndjson")
VERSION_FILE = ".schema_version"


class AquaError(Exception):
    """Anything the user should see as a plain message, not a traceback."""


# --------------------------------------------------------------------------- #
# paths
# --------------------------------------------------------------------------- #

def data_dir(override: str | os.PathLike | None = None) -> Path:
    """Where the live data lives.

    Resolution order: explicit ``--data-dir`` → ``AQUA_DATA_DIR`` → ``HERMES_HOME``.

    Never relative. Under gateway multiplexing ``TERMINAL_CWD`` resolves to the
    *default* profile's home for every profile, so a relative path would land in
    the wrong persona's data. ``HERMES_HOME`` is correctly scoped per turn into
    tool subprocesses, so it is the one to trust.
    """
    if override:
        return Path(override).expanduser().resolve()
    env = os.environ.get("AQUA_DATA_DIR", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    home = os.environ.get("HERMES_HOME", "").strip()
    root = Path(home).expanduser() if home else Path.home() / ".hermes"
    return (root / "workspace" / "aquarium").resolve()


# --------------------------------------------------------------------------- #
# atomic IO
# --------------------------------------------------------------------------- #

def read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AquaError(f"{path.name} is unreadable: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    """Write atomically, so a concurrent backup tar sees old-or-new, never torn."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def append_ndjson(path: Path, record: dict) -> None:
    """Append one record as a single line.

    Append-only is the safest shape under a non-quiesced tar: the worst case is a
    truncated final line, which ``read_ndjson`` skips.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=False) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def read_ndjson(path: Path) -> Iterator[dict]:
    """Yield records, tolerating a truncated or malformed final line."""
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue  # torn tail from a backup, or a partial write
            if isinstance(record, dict):
                yield record


# --------------------------------------------------------------------------- #
# reference tier
# --------------------------------------------------------------------------- #

_reference_cache: dict | None = None


def reference() -> dict:
    global _reference_cache
    if _reference_cache is None:
        data = read_json(REFERENCE_FILE)
        if not isinstance(data, dict):
            raise AquaError(f"missing or invalid {REFERENCE_FILE}")
        _reference_cache = data
    return _reference_cache


# --------------------------------------------------------------------------- #
# seeding and schema
# --------------------------------------------------------------------------- #

def is_initialised(root: Path) -> bool:
    return any((root / name).exists() for name in JSON_FILES + LOG_FILES)


def initialise(root: Path, *, force: bool = False) -> bool:
    """Copy the one-time migration payload in. Returns True if anything was written.

    Refuses a populated directory unless ``force``. The payload is a bootstrap
    snapshot, not a mirror: it is correct on the day the skill shipped and goes
    stale from the first live reading onward, which is why ``status`` reports the
    age of the newest reading.
    """
    if is_initialised(root) and not force:
        return False
    root.mkdir(parents=True, exist_ok=True)
    if not INITIAL_DIR.is_dir():
        raise AquaError(f"no migration payload at {INITIAL_DIR}")
    for src in sorted(INITIAL_DIR.iterdir()):
        if src.is_file() and src.suffix in (".json", ".ndjson"):
            shutil.copyfile(src, root / src.name)
    (root / VERSION_FILE).write_text(f"{SCHEMA_VERSION}\n", encoding="utf-8")
    return True


def schema_version(root: Path) -> int:
    path = root / VERSION_FILE
    if not path.is_file():
        return 0
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def migrate(root: Path) -> list[str]:
    """Bring an older data directory up to ``SCHEMA_VERSION``.

    The CLI is replaced from the repo on every provision but the data is not, so a
    newer CLI will meet older data. There are no migrations yet; the plumbing is
    here because retrofitting it after a format change is the expensive way.
    """
    current = schema_version(root)
    steps: list[str] = []
    if current == SCHEMA_VERSION:
        return steps
    if current > SCHEMA_VERSION:
        raise AquaError(
            f"data is schema v{current}, this CLI understands v{SCHEMA_VERSION}. "
            "The skill is older than the data — re-provision the skill."
        )
    # future: while current < SCHEMA_VERSION: apply step, append to steps
    (root / VERSION_FILE).write_text(f"{SCHEMA_VERSION}\n", encoding="utf-8")
    steps.append(f"stamped schema v{SCHEMA_VERSION}")
    return steps


# --------------------------------------------------------------------------- #
# the store
# --------------------------------------------------------------------------- #

class Store:
    """Read/write access to one aquarium data directory."""

    def __init__(self, root: Path, *, auto_init: bool = True):
        self.root = root
        self.seeded = False
        if auto_init and not is_initialised(root):
            self.seeded = initialise(root)
        if is_initialised(root):
            migrate(root)

    # --- documents ---------------------------------------------------------
    def _doc(self, name: str, key: str) -> dict:
        data = read_json(self.root / name)
        if data is None:
            return {"schema_version": SCHEMA_VERSION, key: {} if key == "tanks" else []}
        return data

    def tanks(self) -> dict:
        return self._doc("tanks.json", "tanks").get("tanks", {})

    def save_tanks(self, tanks: dict) -> None:
        write_json(self.root / "tanks.json", {"schema_version": SCHEMA_VERSION, "tanks": tanks})

    def livestock(self) -> list[dict]:
        return self._doc("livestock.json", "animals").get("animals", [])

    def save_livestock(self, animals: list[dict]) -> None:
        write_json(
            self.root / "livestock.json",
            {"schema_version": SCHEMA_VERSION, "animals": animals},
        )

    def inventory(self) -> list[dict]:
        return self._doc("inventory.json", "items").get("items", [])

    def save_inventory(self, items: list[dict]) -> None:
        write_json(self.root / "inventory.json", {"schema_version": SCHEMA_VERSION, "items": items})

    def questions(self) -> list[dict]:
        return self._doc("questions.json", "questions").get("questions", [])

    def save_questions(self, questions: list[dict]) -> None:
        write_json(
            self.root / "questions.json",
            {"schema_version": SCHEMA_VERSION, "questions": questions},
        )

    # --- logs --------------------------------------------------------------
    def readings(self) -> list[dict]:
        return sorted(read_ndjson(self.root / "readings.ndjson"), key=lambda r: r.get("at", ""))

    def add_reading(self, record: dict) -> None:
        append_ndjson(self.root / "readings.ndjson", record)

    def events(self) -> list[dict]:
        return sorted(read_ndjson(self.root / "events.ndjson"), key=lambda r: r.get("at", ""))

    def add_event(self, record: dict) -> None:
        append_ndjson(self.root / "events.ndjson", record)

    # --- helpers -----------------------------------------------------------
    def tank(self, name: str) -> dict:
        tanks = self.tanks()
        if name not in tanks:
            known = ", ".join(sorted(tanks)) or "none"
            raise AquaError(f"unknown tank {name!r}. Known tanks: {known}")
        return tanks[name]

    def resolve_tank(self, name: str | None) -> str:
        """Resolve a tank name, accepting documented aliases.

        Refuses to guess when the answer would differ between tanks — the two
        differ 6x in volume, and SOUL.md's "Always know which tank" is the rule
        this enforces mechanically.
        """
        tanks = self.tanks()
        if not name:
            if len(tanks) == 1:
                return next(iter(tanks))
            raise AquaError(
                "which tank? " + ", ".join(sorted(tanks)) + " — they differ in volume, "
                "so the answer differs too."
            )
        key = name.strip().lower()
        if key in tanks:
            return key
        for tank_id, tank in tanks.items():
            aliases = [a.lower() for a in tank.get("aliases", [])]
            if key in aliases:
                return tank_id
        known = ", ".join(sorted(tanks)) or "none"
        raise AquaError(f"unknown tank {name!r}. Known tanks: {known}")
