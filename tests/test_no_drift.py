"""Anti-drift: no facts about these specific tanks in the skill's prose.

This is the check that makes spec 06 stick. Before it, ~150 of ~400 facts were
restatements and eight had already contradicted each other — the ammonia gap
asserted both open and closed in six places each, a live 3.2 mL dose in the
emergency runbook that two other files called a 30% overdose, and a "do not add
coral" caution applied to the tank that needed coral.

None of that was caught by review, because each individual sentence was fine. The
only durable fix is to make the prose incapable of holding a fact: measurements,
counts, volumes and doses come from `aqua`, and a number reappearing here fails
the build.

The rules target **attribution**, not units. A skill about water chemistry has to
be able to say "17.86", "below about 4 dGH" and "Neocaridina prefer 6-12 dGH" —
those are relationships and species biology. What it must not say is what *these*
tanks measured, which in practice means a value tied to a tank name, an
instrument, or a date. Plus doses, volumes and counts, which now have no
legitimate reason to appear in prose at all: `aqua` computes every one.
"""

from __future__ import annotations

import re

import pytest

from conftest import REPO_ROOT, body

SKILL_DIR = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor"
PROSE_FILES = [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").glob("*.md"))]

# A number with a unit. Harmless on its own; the attribution is what matters.
VALUE = (
    r"\b\d+(?:\.\d+)?\s*(?:ppm|mV|dGH|dKH|uS/cm|°C|C)\b"
    r"|\bpH\s*\d\.\d{1,2}\b"
)

# Words that tie a value to *these* tanks rather than to a species or a formula.
TANKS = r"\b(?:display|staging|quarantine)\b"
INSTRUMENTS = r"\b(?:HI735|HI775|Kactoily|Advatec|BACNUNN|SmartLife|the probe|probe read)\b"

# Things that are always an observation, never a rule.
ALWAYS_FORBIDDEN = [
    (r"\b\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b",
     "a date — observations belong in `aqua`, not in prose"),
    (r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b", "a date"),
    (r"\b\d+(?:\.\d+)?\s*m[lL]\b", "a dose in mL — `aqua dose` computes every one"),
    (r"\b\d+(?:\.\d+)?\s*(?:gal|gallons)\b", "a tank volume — run `aqua tanks`"),
    (r"\b(?:one|two|three|four|five|six|nine|eighteen|\d+)\s+"
     r"(?:shrimp|snails?|guppies|nerites|mystery snails|otos)\b",
     "a livestock count — run `aqua livestock`"),
    (r"\b\d+\s*[x×]\s*\d+\s*g\b", "a product quantity — run `aqua inventory`"),
]

# A value is only an observation when something attributes it.
ATTRIBUTED = [
    (TANKS, "a value attributed to a specific tank — run `aqua readings`"),
    (INSTRUMENTS, "a value attributed to an instrument — run `aqua readings`"),
]

# Lines exempt from the scan: fenced code blocks are CLI examples, and a line
# citing the CLI is showing what to run, not asserting a value.
CLI_MARKERS = ("$AQUA", "aqua.py", "aquadirector")


def scan(path) -> list[str]:
    """Return human-readable descriptions of every offending line."""
    findings: list[str] = []
    in_fence = False
    for number, line in enumerate(body(path).splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or any(marker in line for marker in CLI_MARKERS):
            continue

        for pattern, why in ALWAYS_FORBIDDEN:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                findings.append(f"{path.name}:{number}: {match.group(0)!r} — {why}\n    {stripped[:100]}")

        value = re.search(VALUE, line, re.IGNORECASE)
        if value:
            for pattern, why in ATTRIBUTED:
                anchor = re.search(pattern, line, re.IGNORECASE)
                if anchor:
                    findings.append(
                        f"{path.name}:{number}: {value.group(0)!r} next to "
                        f"{anchor.group(0)!r} — {why}\n    {stripped[:100]}"
                    )
    return findings


@pytest.mark.parametrize("path", PROSE_FILES, ids=lambda p: p.name)
def test_no_tank_specific_measurements_in_prose(path):
    findings = scan(path)
    assert not findings, (
        "the skill's prose states values that belong in the data:\n\n"
        + "\n".join(findings)
        + "\n\nThese go stale the moment a reading is logged, and a second copy is "
        "how the eight documented contradictions happened. Move them to the CLI."
    )


def test_the_scan_actually_catches_things(tmp_path):
    """A guard that cannot fire is not a guard.

    Uses the real sentences that were in the skill and had already drifted.
    """
    sample = tmp_path / "SKILL.md"
    for offender in (
        "The display tank measured GH 161 ppm on 5 Sep.",
        "Dose Prime (~3.2 mL) and increase surface agitation.",
        "Staging sits at 3.5 dGH, below the line.",
        "Water volume is approximately 25 gal.",
        "There are nine shrimp in the staging tank.",
        "The probe read pH 6.86, and the strips disagreed.",
        "| Display | 161 ppm | 46 ppm |",
        "Coral went in on 29 Aug 2026.",
        "HI735 gave 62 ppm.",
    ):
        sample.write_text(f"---\nname: x\n---\n\n{offender}\n", encoding="utf-8")
        assert scan(sample), f"scan missed: {offender}"


def test_the_scan_permits_mechanism_and_biology(tmp_path):
    """Over-strict is its own failure: it would push real reasoning out of the skill."""
    sample = tmp_path / "SKILL.md"
    for allowed in (
        "German degrees and ppm as CaCO3 relate by 17.86.",
        "Below about 4 dGH there is not enough dissolved calcium to calcify a cuticle.",
        "Neocaridina tolerate 18-29C and prefer GH 6-12 dGH.",
        "Aragonite dissolution stalls around 7.2-7.5.",
        "A tank can carry 1 ppm ammonia at 400 mV.",
        "Molt roughly every 3-4 weeks.",
        "Distilled water reading pH 5.5-5.8 in the jug is normal atmospheric CO2.",
        "Match change water within about 1 C and 20 ppm TDS.",
        "Nitrite above zero is an emergency.",
        "Run `$AQUA dose prime --tank display` — it computed 2.4 mL for 24.2 gal.",
    ):
        sample.write_text(f"---\nname: x\n---\n\n{allowed}\n", encoding="utf-8")
        assert not scan(sample), f"scan false-positived on: {allowed}"


def test_the_skill_points_at_the_cli():
    """Removing the facts is only half the job — the prose has to say where they went."""
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "${HERMES_SKILL_DIR}/scripts/aqua.py" in text, (
        "SKILL.md must define the CLI using ${HERMES_SKILL_DIR}: it is substituted "
        "before the model sees the text and is the only form correct under named "
        "profiles"
    )
    assert "aqua status" in text
    for reference in sorted((SKILL_DIR / "references").glob("*.md")):
        assert "aqua" in reference.read_text(encoding="utf-8"), (
            f"{reference.name} states no values and points at no CLI — where does the "
            "reader get the numbers?"
        )


def test_description_carries_no_specifics():
    """DESCRIPTION.md is rendered into the system prompt and cannot be regenerated.

    A count or volume stated there goes stale silently and the agent has no way to
    correct it.
    """
    findings = scan(REPO_ROOT / "skills" / "aquarium" / "DESCRIPTION.md")
    assert not findings, "DESCRIPTION.md is in the prompt and cannot be refreshed:\n" + "\n".join(findings)


def test_soul_carries_no_specifics():
    findings = scan(REPO_ROOT / "SOUL.md")
    assert not findings, (
        "SOUL.md states tank specifics, contradicting its own closing line that facts "
        "live in the skill:\n" + "\n".join(findings)
    )
