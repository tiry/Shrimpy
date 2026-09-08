"""Unit tests for the aquarium CLI.

Stdlib only, no API key, no network. These cover the arithmetic that used to live
in prose — where getting it wrong is how the documented "32 gallons" and the 3.2 mL
Prime dose happened in the first place.

Every test uses a temp data directory, so nothing here can touch live data.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import REPO_ROOT

SCRIPTS = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor" / "scripts"
ASSETS = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor" / "assets"
AQUA = SCRIPTS / "aqua.py"

sys.path.insert(0, str(SCRIPTS))


@pytest.fixture()
def data_dir(tmp_path):
    return tmp_path / "aquarium"


def run(data_dir: Path, *args: str) -> subprocess.CompletedProcess:
    """Invoke the CLI exactly as the agent would."""
    return subprocess.run(
        [sys.executable, str(AQUA), "--data-dir", str(data_dir), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


# --------------------------------------------------------------------------- #
# volume and dosing — the arithmetic the prose got wrong
# --------------------------------------------------------------------------- #

def test_volume_is_computed_from_dimensions():
    import _calc as calc

    tank = {
        "dimensions_in": {"length": 32.0, "width": 15.0, "height": 14.0},
        "freeboard_gal": 2.1,
        "displacement_gal": 2.75,
    }
    assert calc.gross_volume_gal(tank) == pytest.approx(29.1, abs=0.1)
    assert calc.water_volume_gal(tank) == pytest.approx(24.2, abs=0.1)


def test_volume_never_comes_from_the_tanks_nominal_name():
    """The documented failure: dosing a ~24 gal tank as if it held 32.

    SKILL.md called 32 gallons wrong in one place and kept using it in five
    others. Nothing in the CLI can reach a nominal name — the only input is
    measured dimensions.
    """
    import _calc as calc

    tank = {
        "dimensions_in": {"length": 32.0, "width": 15.0, "height": 14.0},
        "freeboard_gal": 2.1,
        "displacement_gal": 2.75,
    }
    assert calc.water_volume_gal(tank) < 26.0


def test_prime_dose_scales_with_measured_volume():
    import _calc as calc

    display = {"dimensions_in": {"length": 32.0, "width": 15.0, "height": 14.0},
               "freeboard_gal": 2.1, "displacement_gal": 2.75}
    staging = {"dimensions_in": {"length": 17.0, "width": 6.6, "height": 9.5},
               "freeboard_gal": 0.5, "displacement_gal": 0.1}

    big = calc.dose("prime", display)
    small = calc.dose("prime", staging)

    # Label rate is 5 mL per 50 gal = 0.1 mL/gal.
    assert big["ml"] == pytest.approx(big["volume_gal"] * 0.1, abs=0.01)
    assert small["ml"] == pytest.approx(0.4, abs=0.05)
    assert small["drops"] == pytest.approx(8, abs=1)
    # The wrong answer, and the one the skill's own triage file still carried.
    assert big["ml"] < 3.0


def test_emergency_is_five_times_standard():
    import _calc as calc

    tank = {"dimensions_in": {"length": 17.0, "width": 6.6, "height": 9.5},
            "freeboard_gal": 0.5, "displacement_gal": 0.1}
    standard = calc.dose("prime", tank, "standard")["ml"]
    emergency = calc.dose("prime", tank, "emergency")["ml"]
    assert emergency == pytest.approx(standard * 5, abs=0.01)


def test_dose_output_always_shows_its_basis():
    """A dose with no stated volume is indistinguishable from a recalled one."""
    import _calc as calc

    tank = {"dimensions_in": {"length": 32.0, "width": 15.0, "height": 14.0},
            "freeboard_gal": 2.1, "displacement_gal": 2.75}
    line = calc.format_dose(calc.dose("prime", tank))
    assert "gal" in line and "estimated" in line and "Prime" in line


def test_sub_millilitre_doses_are_given_in_drops():
    """Pouring from the bottle into four gallons overdoses badly."""
    import _calc as calc

    tank = {"dimensions_in": {"length": 17.0, "width": 6.6, "height": 9.5},
            "freeboard_gal": 0.5, "displacement_gal": 0.1}
    assert "drops" in calc.format_dose(calc.dose("prime", tank))


def test_unknown_product_and_scenario_are_refused():
    import _calc as calc
    from _store import AquaError

    tank = {"dimensions_in": {"length": 10.0, "width": 10.0, "height": 10.0}}
    with pytest.raises(AquaError):
        calc.dose("nonexistent", tank)
    with pytest.raises(AquaError):
        calc.dose("prime", tank, "nonexistent")


# --------------------------------------------------------------------------- #
# conversions and heuristics
# --------------------------------------------------------------------------- #

def test_hardness_conversion_round_trips():
    import _calc as calc

    assert calc.ppm_to_degrees(161) == pytest.approx(9.0, abs=0.05)
    assert calc.ppm_to_degrees(46) == pytest.approx(2.6, abs=0.05)
    assert calc.degrees_to_ppm(calc.ppm_to_degrees(161)) == pytest.approx(161, abs=2)


def test_spectator_ion_matches_the_documented_figure():
    """TDS 255, GH 161, KH 46 gives 48 — the number SKILL.md carried as a constant."""
    import _calc as calc

    result = calc.spectator_ions(255, 161, 46)
    assert result["value"] == pytest.approx(48.0, abs=0.1)
    assert result["verdict"] == "normal"
    assert "trend" in result["caveat"].lower()


def test_spectator_ion_flags_accumulation():
    import _calc as calc

    assert "accumulating" in calc.spectator_ions(300, 161, 46)["verdict"]


def test_swap_projection_converges_on_the_source():
    """Each swap moves staging toward display water; the first clears the molt floor."""
    import _calc as calc

    projected = calc.swap_projection(current_ppm=62, source_ppm=161, fraction=0.15, swaps=5)
    assert projected == sorted(projected), "hardness must rise monotonically"
    assert calc.ppm_to_degrees(projected[0]) >= 4.0, "first swap should clear the 4 dGH molt floor"
    assert projected[-1] < 161


def test_dilution_matches_the_documented_worked_example():
    import _calc as calc

    assert calc.dilution(255, 3.75, 25) == pytest.approx(217, abs=1)


# --------------------------------------------------------------------------- #
# instrument trust
# --------------------------------------------------------------------------- #

def test_untrusted_instruments_are_excluded_from_trends():
    """The strip pH pad read <=6.2 against a calibrated probe's 6.86.

    Recording it is right — it is evidence the pad is unusable. Letting it drive a
    pH trend is not.
    """
    import _calc as calc

    assert calc.trusted_for("kactoily", "ph") is True
    assert calc.trusted_for("bacnunn", "ph") is False
    assert calc.trusted_for("advatec", "ph") is False
    assert calc.trusted_for("advatec", "ammonia") is True
    assert calc.trusted_for("bacnunn", "copper") is True


def test_series_filters_by_trust():
    import _calc as calc

    readings = [
        {"at": "2026-09-05", "tank": "display", "metric": "ph", "value": 6.2, "instrument": "bacnunn"},
        {"at": "2026-09-06", "tank": "display", "metric": "ph", "value": 6.86, "instrument": "kactoily"},
    ]
    assert len(calc.series(readings, "display", "ph")) == 1
    assert len(calc.series(readings, "display", "ph", trusted_only=False)) == 2


# --------------------------------------------------------------------------- #
# storage durability
# --------------------------------------------------------------------------- #

def test_writes_are_atomic(tmp_path):
    """A backup tars /opt/data live, without quiescing. A torn JSON would be
    captured as-is, so every write must be replace-in-place."""
    import _store as store

    target = tmp_path / "doc.json"
    store.write_json(target, {"a": 1})
    store.write_json(target, {"a": 2})
    assert json.loads(target.read_text()) == {"a": 2}
    assert not list(tmp_path.glob("*.tmp")), "temp file left behind"


def test_ndjson_tolerates_a_truncated_final_line(tmp_path):
    """The realistic tar failure: the last append caught mid-write."""
    import _store as store

    target = tmp_path / "readings.ndjson"
    store.append_ndjson(target, {"at": "2026-09-05", "value": 1})
    store.append_ndjson(target, {"at": "2026-09-06", "value": 2})
    with target.open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026-09-07", "val')  # torn
    records = list(store.read_ndjson(target))
    assert len(records) == 2
    assert records[-1]["value"] == 2


def test_data_dir_is_absolute_and_prefers_hermes_home(monkeypatch, tmp_path):
    """TERMINAL_CWD resolves to the default profile's home under multiplexing, so a
    relative path would write into the wrong persona's data."""
    import _store as store

    monkeypatch.delenv("AQUA_DATA_DIR", raising=False)
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    resolved = store.data_dir()
    assert resolved.is_absolute()
    assert resolved.parts[-2:] == ("workspace", "aquarium")

    monkeypatch.setenv("AQUA_DATA_DIR", str(tmp_path / "override"))
    assert store.data_dir().name == "override"
    assert store.data_dir("explicit").name == "explicit"


# --------------------------------------------------------------------------- #
# seeding and schema
# --------------------------------------------------------------------------- #

def test_init_seeds_an_empty_directory(data_dir):
    result = run(data_dir, "init")
    assert result.returncode == 0, result.stderr
    for name in ("tanks.json", "livestock.json", "inventory.json", "readings.ndjson"):
        assert (data_dir / name).is_file()


def test_init_refuses_to_clobber_live_data(data_dir):
    """The migration payload is a bootstrap, not a mirror. Re-running it over real
    data would silently replace months of readings."""
    run(data_dir, "init")
    run(data_dir, "log", "ph", "7.01", "-t", "display", "-i", "kactoily")
    before = (data_dir / "readings.ndjson").read_text()

    result = run(data_dir, "init")
    assert result.returncode == 1
    assert "refusing" in result.stdout
    assert (data_dir / "readings.ndjson").read_text() == before


def test_schema_is_stamped(data_dir):
    import _store as store

    run(data_dir, "init")
    assert store.schema_version(data_dir) == store.SCHEMA_VERSION


def test_data_newer_than_the_cli_fails_closed(data_dir):
    """The CLI is replaced on every provision but the data is not, so an older
    skill can meet newer data. Guessing at it would corrupt the data."""
    import _store as store
    from _store import AquaError

    run(data_dir, "init")
    (data_dir / store.VERSION_FILE).write_text("999\n", encoding="utf-8")
    with pytest.raises(AquaError, match="older than the data"):
        store.migrate(data_dir)


# --------------------------------------------------------------------------- #
# the seeded snapshot itself
# --------------------------------------------------------------------------- #

def test_reference_and_seed_are_valid_json():
    json.loads((ASSETS / "reference.json").read_text(encoding="utf-8"))
    for path in sorted((ASSETS / "initial").glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((ASSETS / "initial").glob("*.ndjson")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)


def test_doctor_is_clean_on_the_seed(data_dir):
    result = run(data_dir, "doctor")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ERROR" not in result.stdout


def test_seed_contains_no_contradiction_the_prose_had(data_dir):
    """The eight documented contradictions, resolved in one place each.

    Any of these appearing twice with different values is the failure the whole
    exercise exists to prevent.
    """
    run(data_dir, "init")
    readings = [json.loads(line) for line in
                (data_dir / "readings.ndjson").read_text().splitlines() if line.strip()]

    # Ammonia was asserted both open and closed in six places each. It is measured.
    ammonia = [r for r in readings if r["metric"] == "ammonia"]
    assert len(ammonia) == 2, "one ammonia reading per tank"
    assert all(r["value"] == 0.0 for r in ammonia)

    # One value per (tank, metric, timestamp, instrument) — no restatements.
    keys = [(r["tank"], r["metric"], r["at"], r.get("instrument")) for r in readings]
    assert len(keys) == len(set(keys)), "the same reading is recorded twice"

    # Staging coral went in on 3 Sep, not 28-29 Aug as triage.md claimed.
    tanks = json.loads((data_dir / "tanks.json").read_text())["tanks"]
    assert tanks["staging"]["media"][0]["installed"] == "2026-09-03"
    assert tanks["display"]["media"][0]["installed"] == "2026-08-29"

    # Open question 1 was answered 380 lines above where it was still listed.
    questions = json.loads((data_dir / "questions.json").read_text())["questions"]
    assert questions[0]["status"] == "answered"


# --------------------------------------------------------------------------- #
# the log contract
# --------------------------------------------------------------------------- #

def test_log_reports_the_prior_reading_and_delta(data_dir):
    """SOUL.md: "one reading is not a trend. Ask for the previous one." Returning it
    unprompted makes that mechanical rather than hopeful."""
    run(data_dir, "init")
    result = run(data_dir, "log", "ph", "6.91", "-t", "display", "-i", "kactoily")
    assert result.returncode == 0, result.stderr
    assert "prior 6.86" in result.stdout
    assert "0.05" in result.stdout


def test_log_says_when_there_is_no_trend_yet(data_dir):
    run(data_dir, "init")
    result = run(data_dir, "log", "ec", "600", "-t", "staging", "-i", "kactoily")
    assert "no prior reading" in result.stdout


def test_log_warns_when_the_instrument_is_not_trusted(data_dir):
    run(data_dir, "init")
    result = run(data_dir, "log", "ph", "6.3", "-t", "display", "-i", "bacnunn")
    assert "not trusted" in result.stdout


def test_log_flags_a_reading_outside_target(data_dir):
    run(data_dir, "init")
    result = run(data_dir, "log", "temperature", "27.5", "-t", "display", "-i", "kactoily")
    assert "above target" in result.stdout


def test_log_is_append_only(data_dir):
    run(data_dir, "init")
    before = len((data_dir / "readings.ndjson").read_text().splitlines())
    run(data_dir, "log", "ph", "6.9", "-t", "display", "-i", "kactoily")
    after = len((data_dir / "readings.ndjson").read_text().splitlines())
    assert after == before + 1


# --------------------------------------------------------------------------- #
# the two-tank rule, enforced mechanically
# --------------------------------------------------------------------------- #

def test_an_ambiguous_tank_is_refused_not_guessed(data_dir):
    """The tanks differ 6x in volume. SOUL.md's "Always know which tank" is a rule
    the CLI can enforce rather than hope for."""
    import _store as store

    run(data_dir, "init")
    st = store.Store(data_dir)
    with pytest.raises(store.AquaError, match="which tank"):
        st.resolve_tank(None)


def test_tank_aliases_resolve(data_dir):
    import _store as store

    run(data_dir, "init")
    st = store.Store(data_dir)
    for alias in ("display", "big", "25g", "DISPLAY"):
        assert st.resolve_tank(alias) == "display"
    for alias in ("staging", "quarantine", "qt", "little"):
        assert st.resolve_tank(alias) == "staging"
    with pytest.raises(store.AquaError, match="unknown tank"):
        st.resolve_tank("pond")


# --------------------------------------------------------------------------- #
# staleness — the honest half of a bootstrap snapshot
# --------------------------------------------------------------------------- #

def test_stale_data_is_announced():
    import _calc as calc

    assert calc.stale_summary([]) == "no readings logged at all"
    assert calc.stale_summary([{"at": "2020-01-01"}]).startswith("newest reading is")
    assert "historical" in calc.stale_summary([{"at": "2020-01-01"}])
    assert calc.stale_summary([{"at": calc.now_iso()}]) is None


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #

def test_export_writes_openable_csv(data_dir):
    run(data_dir, "init")
    result = run(data_dir, "export")
    assert result.returncode == 0, result.stderr
    readings_csv = data_dir / "export" / "readings.csv"
    assert readings_csv.is_file()
    header = readings_csv.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("at,tank,metric,value")


def test_plot_produces_a_real_png(data_dir):
    pytest.importorskip("PIL")
    run(data_dir, "init")
    run(data_dir, "log", "ph", "6.90", "-t", "display", "-i", "kactoily")
    result = run(data_dir, "plot", "ph", "-t", "display")
    assert result.returncode == 0, result.stderr
    png = data_dir / "export" / "display-ph.png"
    assert png.is_file()
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    from PIL import Image

    with Image.open(png) as image:
        assert image.size == (720, 260)
        # More than a handful of colours means something was actually drawn.
        assert len(image.convert("RGB").getcolors(maxcolors=100000)) > 10


def _line_profile(png_path) -> list[tuple[int, float]]:
    """Where the plotted line sits, column by column.

    Returns (x, mean_y) for every column containing line-coloured pixels. The
    line colour is the one _report.py draws with; PIL's draw.line is not
    anti-aliased, so an exact match is reliable.
    """
    from PIL import Image

    line_rgb = (31, 92, 160)
    with Image.open(png_path) as image:
        pixels = image.convert("RGB").load()
        width, height = image.size
        profile = []
        for x in range(width):
            ys = [y for y in range(height) if pixels[x, y] == line_rgb]
            if ys:
                profile.append((x, sum(ys) / len(ys)))
    return profile


def _log_series(data_dir, values, metric="ph", tank="display"):
    """Log a series on consecutive days so the chart has a known shape."""
    for index, value in enumerate(values):
        day = f"2026-08-0{index + 1}" if index < 9 else f"2026-08-{index + 1}"
        run(data_dir, "log", metric, str(value), "-t", tank,
            "-i", "kactoily", "--at", f"{day}T09:00")


def test_the_plotted_line_follows_the_data(data_dir):
    """The chart must actually depict the readings.

    "A PNG was produced" is not a test of a chart — a blank canvas passes it.
    This reads the rendered pixels back and checks the line goes the way the
    numbers do. Image y grows downward, so a rising series must trend to a
    *smaller* y.
    """
    pytest.importorskip("PIL")
    run(data_dir, "init")
    _log_series(data_dir, [6.60, 6.70, 6.80, 6.90, 7.00, 7.10, 7.20])

    png = data_dir / "rising.png"
    result = run(data_dir, "plot", "ph", "-t", "display", "--out", str(png))
    assert result.returncode == 0, result.stderr

    profile = _line_profile(png)
    assert len(profile) > 100, "the line barely covers the canvas"
    first_y = profile[0][1]
    last_y = profile[-1][1]
    assert last_y < first_y - 40, (
        f"a rising pH series should render as a rising line; y went {first_y:.0f} -> {last_y:.0f}"
    )


def test_a_falling_series_renders_falling(data_dir):
    """The mirror of the above. Without it, a chart that ignores its input and
    always draws the same slope would pass."""
    pytest.importorskip("PIL")
    run(data_dir, "init")
    _log_series(data_dir, [7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60])

    png = data_dir / "falling.png"
    run(data_dir, "plot", "ph", "-t", "display", "--out", str(png))
    profile = _line_profile(png)
    assert profile[-1][1] > profile[0][1] + 40, "a falling series should render as a falling line"


def test_the_target_band_is_drawn_where_the_target_is(data_dir):
    """The shaded band is the reason the chart answers "is this OK", not just
    "what is the number". If it were drawn in the wrong place it would say the
    opposite of the truth, convincingly."""
    pytest.importorskip("PIL")
    from PIL import Image

    run(data_dir, "init")
    _log_series(data_dir, [6.60, 6.80, 7.00, 7.20, 7.40])

    png = data_dir / "band.png"
    run(data_dir, "plot", "ph", "-t", "display", "--out", str(png))

    band_rgb = (232, 244, 234)
    with Image.open(png) as image:
        pixels = image.convert("RGB").load()
        width, height = image.size
        column = width // 2
        band_rows = [y for y in range(height) if pixels[column, y] == band_rgb]

    assert band_rows, "no target band was shaded"
    # The display pH target is 6.8-7.4 against a plotted range of 6.6-7.4 plus
    # padding, so the band must cover a large slice but not the whole canvas.
    coverage = len(band_rows) / height
    assert 0.25 < coverage < 0.95, f"target band covers {coverage:.0%} of the chart"


def test_report_is_self_contained(data_dir):
    """One file you can open or send. An external reference would break both."""
    run(data_dir, "init")
    run(data_dir, "log", "ph", "6.90", "-t", "display", "-i", "kactoily")
    result = run(data_dir, "report")
    assert result.returncode == 0, result.stderr
    html = (data_dir / "export" / "report.html").read_text(encoding="utf-8")
    assert "<title>Aquarium report</title>" in html
    assert 'src="http' not in html and "src='http" not in html
    assert "data:image/png;base64," in html or "<svg" in html


# --------------------------------------------------------------------------- #
# the CLI contract the skill documents
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "argv",
    [
        ["status"],
        ["tanks"],
        ["livestock"],
        ["inventory"],
        ["questions"],
        ["check"],
        ["doctor"],
        ["readings", "ph", "-t", "display"],
        ["dose", "prime", "-t", "display"],
        ["dose", "stability", "-t", "staging", "--scenario", "day1"],
    ],
    ids=lambda a: "-".join(a[:2]),
)
def test_documented_read_commands_succeed(data_dir, argv):
    result = run(data_dir, *argv)
    assert result.returncode == 0, f"{argv} failed:\n{result.stdout}\n{result.stderr}"
    assert result.stdout.strip(), f"{argv} produced no output"


def test_json_output_is_valid_where_offered(data_dir):
    run(data_dir, "init")
    result = run(data_dir, "--json", "dose", "prime", "-t", "display")
    assert result.returncode == 0
    payload = json.loads(result.stdout[result.stdout.index("{"):])
    assert payload["ml"] > 0 and payload["volume_gal"] > 0


def test_cli_is_stdlib_only():
    """"Adding the skill is enough" only holds if nothing needs installing.

    Checked against ``sys.stdlib_module_names`` rather than a hand-written
    allowlist, which was the bug the first version had: ruff modernised
    ``typing.Iterator`` to ``collections.abc.Iterator`` and the test rejected
    ``collections`` as third-party.

    Pillow is the single permitted exception. It is a core Hermes dependency
    (pyproject.toml:245) and is imported lazily, so a missing one degrades the
    charts to stdlib SVG rather than failing.
    """
    import ast

    local = {"_calc", "_store", "_report"}
    allowed = set(sys.stdlib_module_names) | local | {"PIL"}

    for path in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # relative import, necessarily local
                    continue
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            for name in names:
                assert name in allowed, (
                    f"{path.name} imports {name!r}, which is neither stdlib, a "
                    f"sibling module, nor Pillow. The skill must install with no "
                    f"dependencies of its own."
                )
