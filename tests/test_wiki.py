"""Structure of the background wiki — spec 09.

The wiki is a third tier of prose inside a skill whose entire discipline is that prose
cannot hold a fact. `tests/test_no_drift.py` already scans these pages for tank-attributed
values and species ranges; this module covers the things that scan cannot see:

* a page nobody can find, because the index and the tree disagree
* a claim with no source behind it
* a page about a species `aqua` has never heard of
* a page so large that opening it costs more than the answer is worth

The routing matters as much as the content. Hermes loads a skill progressively — the system
prompt carries only a 60-character description, and every supporting file is a separate
`skill_view` round trip. Twenty pages the model has to hunt through make the agent slower,
not faster, which is the opposite of why the wiki exists.
"""

from __future__ import annotations

import json
import re

import pytest
from conftest import REPO_ROOT

SKILL_DIR = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor"
WIKI_DIR = SKILL_DIR / "assets" / "wiki"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCE = SKILL_DIR / "assets" / "reference.json"

CATEGORIES = {"species", "pest", "product", "method"}

# One page should be one cheap read. The generic tool-result spillover threshold is
# 100_000 chars, but that is a ceiling for catastrophe, not a budget: a page past this is
# a sign the subject wants splitting.
MAX_PAGE_BYTES = 9_000

INDEX_RE = re.compile(
    r"<!-- WIKI-INDEX START -->(.*?)<!-- WIKI-INDEX END -->", re.DOTALL
)


def wiki_pages() -> list:
    return sorted(WIKI_DIR.rglob("*.md"))


def frontmatter(path) -> dict:
    """Parse the page's frontmatter without a YAML dependency in the skill CI job."""
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.name}: no frontmatter")
    end = text.index("\n---\n", 3)
    return yaml.safe_load(text[4:end])


def indexed_paths() -> list[str]:
    match = INDEX_RE.search(SKILL_MD.read_text(encoding="utf-8"))
    assert match, "SKILL.md has no WIKI-INDEX block"
    return re.findall(r"`(assets/wiki/[^`]+\.md)`", match.group(1))


def pytest_ids(path) -> str:
    return str(path.relative_to(WIKI_DIR))


# --------------------------------------------------------------------------- #
# routing
# --------------------------------------------------------------------------- #

def test_there_are_pages_to_test():
    assert wiki_pages(), "no wiki pages found — the rest of this module would pass vacuously"


def test_every_page_is_indexed_in_the_skill():
    """The index is the one-hop path. SKILL.md is already loaded when the model needs to
    choose, so a page named there costs no extra round trip to find."""
    indexed = set(indexed_paths())
    on_disk = {str(p.relative_to(SKILL_DIR)) for p in wiki_pages()}
    missing = sorted(on_disk - indexed)
    assert not missing, (
        f"pages exist but are not in SKILL.md's WIKI-INDEX: {missing}. "
        "The model would have to hunt for them."
    )


def test_every_index_row_points_at_a_real_page():
    """The other direction. A dangling row sends the model to a file that is not there,
    and `skill_view` answers a miss with a directory listing — a wasted round trip."""
    on_disk = {str(p.relative_to(SKILL_DIR)) for p in wiki_pages()}
    dangling = sorted(set(indexed_paths()) - on_disk)
    assert not dangling, f"SKILL.md indexes pages that do not exist: {dangling}"


def test_the_index_is_not_duplicated():
    rows = indexed_paths()
    duplicates = sorted({p for p in rows if rows.count(p) > 1})
    assert not duplicates, f"page listed twice in the index: {duplicates}"


def test_skill_md_explains_the_three_tiers():
    """Without the split stated, the wiki becomes a second place to look for a number."""
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "assets/wiki/" in text
    for tier in ("**values**", "**reasoning**", "**background**"):
        assert tier in text, f"SKILL.md does not name the {tier} tier"


# --------------------------------------------------------------------------- #
# per-page structure
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", wiki_pages(), ids=pytest_ids)
def test_frontmatter_is_complete(path):
    meta = frontmatter(path)
    for field in ("title", "slug", "category", "summary", "sources"):
        assert meta.get(field) not in (None, "", []), f"{path.name}: {field!r} missing"
    assert meta["slug"] == path.stem, f"{path.name}: slug {meta['slug']!r} != filename"
    assert meta["category"] == path.parent.name, (
        f"{path.name}: category {meta['category']!r} != directory {path.parent.name!r}"
    )
    assert meta["category"] in CATEGORIES, f"{path.name}: unknown category"


@pytest.mark.parametrize("path", wiki_pages(), ids=pytest_ids)
def test_every_page_cites_a_source_with_a_date(path):
    """Original prose with citations is what keeps this repo clear of CC BY-SA
    share-alike, and it is the only thing that makes a background claim checkable.
    A page with no source is the model's own weights with a filename on top."""
    for source in frontmatter(path)["sources"]:
        assert source.get("url", "").startswith("http"), f"{path.name}: source has no URL"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source.get("consulted", ""))), (
            f"{path.name}: source {source.get('url')} has no valid consulted date"
        )


@pytest.mark.parametrize("path", wiki_pages(), ids=pytest_ids)
def test_aqua_key_resolves(path):
    """A page about a subject the CLI cannot answer for is a dead end: the model reads
    the background, then has nowhere to get the numbers."""
    meta = frontmatter(path)
    key = meta.get("aqua_key")
    if key is None:
        return
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    pool = {**reference.get("species", {}), **reference.get("products", {})}
    assert key in pool, (
        f"{path.name}: aqua_key {key!r} is in neither species nor products in "
        f"reference.json. Known: {sorted(pool)}"
    )


@pytest.mark.parametrize("path", wiki_pages(), ids=pytest_ids)
def test_page_is_within_budget(path):
    size = path.stat().st_size
    assert size <= MAX_PAGE_BYTES, (
        f"{path.name} is {size} bytes (cap {MAX_PAGE_BYTES}). Opening it costs a whole "
        "round trip; split the subject rather than growing the page."
    )


@pytest.mark.parametrize("path", wiki_pages(), ids=pytest_ids)
def test_page_sends_numbers_back_to_the_cli(path):
    """Mirrors test_the_skill_points_at_the_cli. Removing the values from a page is only
    correct if the page says where they went."""
    assert "aqua" in path.read_text(encoding="utf-8"), (
        f"{path.name} never mentions `aqua` — a reader who wants a number has nowhere "
        "to be sent"
    )


# --------------------------------------------------------------------------- #
# the instrument -> method link
# --------------------------------------------------------------------------- #

def test_every_instrument_names_a_method_page_that_exists():
    """Spec 09 replaced seven product pages with five method pages, because Wikipedia has
    no article on Kactoily or BACNUNN and because `reference.json` already holds every
    per-product fact. The link is what makes that substitution navigable."""
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    instruments = reference["instruments"]
    missing_key = sorted(k for k, v in instruments.items() if not v.get("method"))
    assert not missing_key, f"instruments with no `method` key: {missing_key}"

    available = {p.stem for p in (WIKI_DIR / "method").glob("*.md")}
    broken = sorted(
        f"{k} -> {v['method']}" for k, v in instruments.items()
        if v["method"] not in available
    )
    assert not broken, (
        f"instruments point at method pages that do not exist: {broken}. "
        f"Available: {sorted(available)}"
    )


def test_the_generated_index_matches_the_pages():
    """`scripts/render-wiki-index.py` writes the index; the pages are the source.

    Same contract as `evals/cases/schema.json`: generated for convenience, checked so the
    convenience cannot silently drift away from what it describes.
    """
    import subprocess

    result = subprocess.run(
        ["python3", str(REPO_ROOT / "scripts" / "render-wiki-index.py"), "--check"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "SKILL.md's wiki index is stale.\n"
        "Regenerate: python3 scripts/render-wiki-index.py\n" + result.stderr
    )


def test_every_page_offers_routing_words():
    """The index's subject column is what a question is matched against. A page listed
    only by its taxonomic name is unreachable by anyone asking about 'cherry shrimp'."""
    thin = []
    for path in wiki_pages():
        meta = frontmatter(path)
        if meta["category"] == "species" and not meta.get("aliases"):
            thin.append(path.name)
    assert not thin, (
        f"species pages with no `aliases` for routing: {thin}. A keeper asks about "
        "'cherry shrimp', not 'Neocaridina davidi'."
    )


def test_every_species_in_reference_json_has_a_reachable_page():
    """`aqua species <name>` derives the page path from the species key
    (`_store.wiki_page`), so a page whose filename does not match the key is invisible to
    the CLI even though it is indexed in SKILL.md and passes every other check here.

    Caught exactly that: `mystery-snail.md` against the key `mystery_snail`.
    """
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    unreachable = sorted(
        key for key in reference["species"]
        if not (WIKI_DIR / "species" / f"{key}.md").is_file()
    )
    assert not unreachable, (
        f"species in reference.json with no page `aqua species` can point at: "
        f"{unreachable}. The filename must equal the reference.json key."
    )
