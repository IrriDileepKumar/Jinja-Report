"""Render a preview HTML from a TemplateDraft using mock data."""

from __future__ import annotations

import json
from datetime import datetime, timezone as tz
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .models import TemplateDraft

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _load_mock_data() -> dict:
    path = _FIXTURES_DIR / "mock_section_data.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _make_ts_formatter(tz_name: str):
    """Build a format_ts filter."""

    def _format_ts(value, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return value
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=tz.utc)
            return value.strftime(fmt)
        return str(value)

    return _format_ts


def _format_number(value, decimals: int = 2) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def _format_metric(value, unit: str = "") -> str:
    if value is None:
        return "—"
    try:
        v = float(value)
    except (ValueError, TypeError):
        return str(value)

    if unit == "bytes":
        abs_val = abs(v)
        if abs_val >= 1e15:
            return f"{v / 1e15:.1f} PB"
        if abs_val >= 1e12:
            return f"{v / 1e12:.1f} TB"
        if abs_val >= 1e9:
            return f"{v / 1e9:.1f} GB"
        if abs_val >= 1e6:
            return f"{v / 1e6:.1f} MB"
        if abs_val >= 1e3:
            return f"{v / 1e3:.1f} KB"
        return f"{v:.0f} B"

    if abs(v) >= 1_000_000:
        body = f"{v / 1e6:.1f}M"
    elif abs(v) >= 10_000:
        body = f"{v / 1e3:.1f}K"
    elif abs(v) < 1 and v != 0:
        body = f"{v:.3f}"
    else:
        body = f"{v:,.1f}"
    return f"{body} {unit}".rstrip() if unit else body


def _signed_pct(value) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):+.1f}%"
    except (ValueError, TypeError):
        return str(value)


def _staleness_badge(staleness: str) -> str:
    colors = {
        "fresh": ("#16a34a", "#d1fae5"),
        "stale": ("#d97706", "#fef3c7"),
        "potentially_offline": ("#dc2626", "#fee2e2"),
    }
    fg, bg = colors.get(staleness, ("#6b7280", "#f3f4f6"))
    label = staleness.replace("_", " ").title()
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:3px;font-size:9px;font-weight:700;">{label}</span>'
    )


def render_preview(draft: TemplateDraft) -> str:
    """Render preview HTML for a draft using mock data.

    Args:
        draft: The template draft to preview.

    Returns:
        HTML string.
    """
    env = Environment(
        loader=FileSystemLoader(str(_FIXTURES_DIR)),
        autoescape=True,
    )
    env.filters["format_ts"] = _make_ts_formatter("UTC")
    env.filters["format_number"] = _format_number
    env.filters["format_metric"] = _format_metric
    env.filters["staleness_badge"] = _staleness_badge
    env.filters["signed_pct"] = _signed_pct

    cover = draft.cover
    # Build a wrapper template that extends _base.html.j2 and overrides blocks.
    wrapper_src = f"""{{% extends "_base.html.j2" %}}
{{% block eyebrow %}}{cover.eyebrow}{{% endblock %}}
{{% block report_title %}}{cover.report_title}{{% endblock %}}
{{% block report_subtitle %}}
{cover.report_subtitle}
{{% endblock %}}
{{% block accent_1 %}}{cover.accent_1}{{% endblock %}}
{{% block accent_2 %}}{cover.accent_2}{{% endblock %}}
{{% block accent_3 %}}{cover.accent_3}{{% endblock %}}
"""
    template = env.from_string(wrapper_src)

    mock = _load_mock_data()
    sections = mock["sections"]

    # Reorder mock sections to match draft order; pad missing sections.
    sections_by_id = {s["section"]["id"]: s for s in sections}
    ordered = []
    for sec in draft.sections:
        if sec.id in sections_by_id:
            ordered.append(sections_by_id[sec.id])
        else:
            ordered.append(
                {
                    "section": {
                        "id": sec.id,
                        "title": sec.title,
                        "data_hint": sec.data_hint,
                        "chart_type": sec.chart_type,
                    },
                    "availability": {
                        "staleness": "offline",
                        "warning": None,
                    },
                    "query_result": None,
                    "stats": None,
                    "chart_svg": None,
                    "chart_fallback_text": (
                        f"No mock data for section '{sec.title}'."
                    ),
                    "error": None,
                }
            )

    render_data = {
        "template": {
            "template_id": draft.template_id,
            "version": draft.version,
        },
        "request": {
            "time_range": {
                "start": datetime.fromisoformat("2024-06-01T00:00:00+00:00"),
                "end": datetime.fromisoformat("2024-06-11T00:00:00+00:00"),
            },
            "filters": [],
        },
        "sections": ordered,
        "generated_at": datetime.fromisoformat(
            mock.get("generated_at", "2024-06-11T12:00:00+00:00").replace("Z", "+00:00")
        ),
        "timezone": mock.get("timezone", "UTC"),
        "report_summary": mock.get("report_summary", {}),
    }

    return template.render(**render_data)
