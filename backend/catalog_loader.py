"""Load section catalog and keyword index from JSON files."""

from __future__ import annotations

import json
from pathlib import Path

_CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def load_section_catalog() -> list[dict]:
    """Return the full section catalog."""
    path = _CATALOG_DIR / "section_catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_keyword_index() -> set[str]:
    """Return the set of known keywords (lowercased)."""
    path = _CATALOG_DIR / "keyword_index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k.lower() for k in data.get("keywords", [])}


def list_catalog_categories() -> list[str]:
    """Return sorted list of unique categories."""
    catalog = load_section_catalog()
    cats = {entry.get("category", "other") for entry in catalog}
    return sorted(cats)
