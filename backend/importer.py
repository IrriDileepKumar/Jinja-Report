"""Import an existing .html.j2 file into a TemplateDraft."""

from __future__ import annotations

import re

import yaml

from .models import CoverConfig, SectionDef, TemplateDraft

_FRONT_MATTER_RE = re.compile(
    r"\{#\s*---\s*\n(.*?)\n\s*---\s*#\}",
    re.DOTALL,
)

_BLOCK_RE = re.compile(
    r"{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}",
    re.DOTALL,
)


def import_html_j2(content: str) -> TemplateDraft:
    """Parse an exported .html.j2 and return a TemplateDraft.

    Args:
        content: The full file content.

    Returns:
        A TemplateDraft representing the imported template.

    Raises:
        ImportError: If the layout is not supported (standalone/grouped).
        ValueError: If front-matter is missing or malformed.
    """
    match = _FRONT_MATTER_RE.search(content)
    if not match:
        raise ValueError("No front-matter found.")

    fm = yaml.safe_load(match.group(1))
    if not isinstance(fm, dict):
        raise ValueError("Front-matter is not a valid YAML mapping.")

    template_id = fm.get("template_id", "imported_template")
    version = str(fm.get("version", "1.0"))
    raw_sections = fm.get("sections", [])

    sections = [
        SectionDef(
            id=s["id"],
            title=s.get("title", s["id"]),
            data_hint=s.get("data_hint", []),
            chart_type=s.get("chart_type", "auto"),
        )
        for s in raw_sections
    ]

    # Determine layout
    if '{% extends "_base.html.j2" %}' in content:
        layout = "base_extended"
    elif "{% extends" in content:
        raise ImportError(
            "Unsupported layout: only base_extended templates can be imported."
        )
    else:
        # Standalone / grouped layout
        raise ImportError(
            "Unsupported layout: standalone or grouped templates cannot be "
            "imported."
        )

    # Extract cover blocks
    blocks = dict(_BLOCK_RE.findall(content))
    cover = CoverConfig(
        eyebrow=blocks.get("eyebrow", "").strip(),
        report_title=blocks.get("report_title", "").strip(),
        report_subtitle=blocks.get("report_subtitle", "").strip(),
        accent_1=blocks.get("accent_1", "#22d3ee").strip(),
        accent_2=blocks.get("accent_2", "#6366f1").strip(),
        accent_3=blocks.get("accent_3", "#8b5cf6").strip(),
    )

    return TemplateDraft(
        template_id=template_id,
        version=version,
        layout=layout,
        cover=cover,
        sections=sections,
    )
