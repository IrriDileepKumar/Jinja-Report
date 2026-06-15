"""Extract unique keywords from table_mapping.yaml.

Writes report-template-editor-poc/catalog/keyword_index.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_MAPPING_PATH = (
    _REPO_ROOT / "infra_agents" / "agents" / "report_agent" / "table_mapping.yaml"
)
_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "catalog" / "keyword_index.json"


def main() -> None:
    """Run keyword extraction."""
    if not _MAPPING_PATH.exists():
        raise FileNotFoundError(f"table_mapping.yaml not found at {_MAPPING_PATH}")

    data = yaml.safe_load(_MAPPING_PATH.read_text(encoding="utf-8"))
    keywords: set[str] = set()

    def _collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("keywords", "data_hint", "tags"):
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                keywords.add(item.lower())
                    elif isinstance(v, str):
                        keywords.add(v.lower())
                else:
                    _collect(v)
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)

    _collect(data)

    # Also include known tokens from templates to be safe.
    extra = {
        "node", "cpu", "utilization", "memory", "ram", "disk", "io",
        "filesystem", "network", "interface", "temperature", "thermal",
        "sensor", "idrac", "power", "consumption", "watts", "fan", "speed",
        "rpm", "system", "health", "storage", "drive", "gpu", "psu",
        "efficiency", "voltage", "input", "output", "peak", "max", "avg",
        "capacity", "usage", "time", "active", "installed", "receive",
        "transmit", "traffic", "bytes", "wear", "core", "processor",
        "compute", "graphics", "cuda", "vram",
    }
    keywords.update(extra)

    result = {
        "keywords": sorted(keywords),
        "count": len(keywords),
    }

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {result['count']} keywords to {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
