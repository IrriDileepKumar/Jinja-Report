"""Extract section catalog from Report Agent V2 templates.

Mines front-matter from 5 source templates and writes
report-template-editor-poc/catalog/section_catalog.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATES_DIR = (
    _REPO_ROOT / "infra_agents" / "agents" / "report_agent" / "templates"
)
_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "catalog" / "section_catalog.json"

_FRONT_MATTER_RE = re.compile(
    r"\{#\s*---\s*\n(.*?)\n\s*---\s*#\}",
    re.DOTALL,
)

_SOURCE_FILES = [
    _TEMPLATES_DIR / "datacenter_health.html.j2",
    _TEMPLATES_DIR / "gpu_performance.html.j2",
    _TEMPLATES_DIR / "power_analysis.html.j2",
    _TEMPLATES_DIR / "infra_usage_report.html.j2",
    _TEMPLATES_DIR / "custom" / "infra_usage_report.html.j2",
]

_KEYWORD_CATEGORIES = {
    "compute": ["cpu", "core", "processor", "compute", "utilization", "usage"],
    "gpu": ["gpu", "cuda", "vram", "graphics"],
    "power": ["power", "consumption", "watts", "psu", "voltage", "efficiency"],
    "network": ["network", "interface", "traffic", "transmit", "receive", "bytes"],
    "storage": ["disk", "storage", "filesystem", "drive", "wear", "io"],
    "health": ["health", "temperature", "thermal", "fan", "rpm", "sensor", "idrac"],
}


def _infer_category(data_hint: list[str]) -> str:
    """Infer category from data_hint keywords."""
    hint_set = {h.lower() for h in data_hint}
    scores = {}
    for category, keywords in _KEYWORD_CATEGORIES.items():
        scores[category] = sum(1 for k in keywords if k in hint_set)
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "other"


def _extract_front_matter(text: str) -> dict | None:
    match = _FRONT_MATTER_RE.search(text)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def main() -> None:
    """Run catalog extraction."""
    catalog: list[dict] = []

    for path in _SOURCE_FILES:
        if not path.exists():
            print(f"Warning: {path} not found, skipping")
            continue
        text = path.read_text(encoding="utf-8")
        fm = _extract_front_matter(text)
        if fm is None:
            print(f"Warning: no front-matter in {path.name}")
            continue
        rel = path.relative_to(_TEMPLATES_DIR)
        parts = rel.with_suffix("").with_suffix("").parts
        source_template = "_".join(parts)
        for raw in fm.get("sections", []):
            sid = raw["id"]
            entry = {
                "catalog_id": sid,
                "title": raw.get("title", sid),
                "default_data_hint": raw.get("data_hint", []),
                "default_chart_type": raw.get("chart_type", "auto"),
                "category": _infer_category(raw.get("data_hint", [])),
                "source_template": source_template,
            }
            catalog.append(entry)

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT_PATH.write_text(
        json.dumps(catalog, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(catalog)} entries to {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
