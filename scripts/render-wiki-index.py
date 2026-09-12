#!/usr/bin/env python3
"""Regenerate SKILL.md's WIKI-INDEX block from the wiki pages themselves.

The index is what makes a background lookup cost one round trip instead of several:
SKILL.md is already loaded when the model has to choose a page, so a subject named there
is free to find. Keeping it by hand guarantees it rots, and a rotted index is worse than
none -- `tests/test_wiki.py` fails in both directions, but only after the damage.

Generated, not authoritative: the pages are the source. Run this after adding one.

    python3 scripts/render-wiki-index.py          # rewrite SKILL.md in place
    python3 scripts/render-wiki-index.py --check   # exit 1 if it would change
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "aquarium" / "aquarium-supervisor"
WIKI_DIR = SKILL_DIR / "assets" / "wiki"
SKILL_MD = SKILL_DIR / "SKILL.md"

START = "<!-- WIKI-INDEX START -->"
END = "<!-- WIKI-INDEX END -->"

# Order the model is most likely to need them in, not alphabetical.
CATEGORY_ORDER = ["species", "pest", "product", "method"]
CATEGORY_LABEL = {
    "species": "The animals",
    "pest": "Pests, disease and algae",
    "product": "What is in the bottle",
    "method": "How an instrument measures",
}


def frontmatter(path: pathlib.Path) -> dict:
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: no frontmatter")
    return yaml.safe_load(text[4 : text.index("\n---\n", 3)])


def render() -> str:
    by_category: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(WIKI_DIR.rglob("*.md")):
        meta = frontmatter(path)
        # The subject column is what the model matches a question against, so it carries
        # the words a keeper would actually use -- not just the taxonomic title.
        subject = ", ".join([meta["title"], *(meta.get("aliases") or [])])
        relative = path.relative_to(SKILL_DIR)
        by_category.setdefault(meta["category"], []).append((subject, str(relative)))

    lines = [START, "", "| Subject | Page |", "|---|---|"]
    for category in CATEGORY_ORDER:
        rows = by_category.pop(category, [])
        if not rows:
            continue
        lines.append(f"| **{CATEGORY_LABEL[category]}** | |")
        lines.extend(f"| {subject} | `{path}` |" for subject, path in sorted(rows))
    if by_category:
        raise SystemExit(f"unknown categories: {sorted(by_category)}")
    lines += ["", END]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if out of date")
    args = parser.parse_args()

    text = SKILL_MD.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"{SKILL_MD}: no {START} block to fill")

    updated = pattern.sub(lambda _: render(), text)
    if updated == text:
        print("SKILL.md wiki index is up to date")
        return 0
    if args.check:
        print("SKILL.md wiki index is STALE — run scripts/render-wiki-index.py", file=sys.stderr)
        return 1
    SKILL_MD.write_text(updated, encoding="utf-8")
    print(f"SKILL.md wiki index rewritten ({len(list(WIKI_DIR.rglob('*.md')))} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
