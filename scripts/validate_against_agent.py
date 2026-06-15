"""Validate a generated .html.j2 against the production parser."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from infra_agents.agents.report_agent.template_registry import parse_template


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a template against the agent parser."
    )
    parser.add_argument("path", help="Path to .html.j2 file")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    meta = parse_template(path)
    if meta is None:
        print("parse_template() returned None — validation failed.", file=sys.stderr)
        return 1

    print(f"template_id: {meta.template_id}")
    print(f"sections: {len(meta.sections)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
