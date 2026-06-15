"""Unit tests for preview_renderer.py."""

from __future__ import annotations

from backend.models import CoverConfig, SectionDef, TemplateDraft
from backend.preview_renderer import render_preview


def test_preview_returns_html() -> None:
    """UT-PRV-001: render_preview returns non-empty HTML."""
    draft = TemplateDraft(
        template_id="prev_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="Preview",
            report_subtitle="Sub",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
            SectionDef(
                id="memory_usage",
                title="Memory",
                data_hint=["memory"],
            ),
        ],
    )
    html = render_preview(draft)
    assert html
    assert "<html" in html.lower()


def test_preview_contains_section_titles() -> None:
    """UT-PRV-002: each section title appears in HTML."""
    draft = TemplateDraft(
        template_id="prev_titles",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
            SectionDef(
                id="memory_usage",
                title="Memory",
                data_hint=["memory"],
            ),
        ],
    )
    html = render_preview(draft)
    assert "CPU" in html
    assert "Memory" in html


def test_preview_contains_cover_title() -> None:
    """UT-PRV-003: cover report_title in HTML."""
    draft = TemplateDraft(
        template_id="prev_cover",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="My Cover Title",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
        ],
    )
    html = render_preview(draft)
    assert "My Cover Title" in html


def test_preview_contains_chart_placeholder() -> None:
    """UT-PRV-004: HTML contains chart container or section id."""
    draft = TemplateDraft(
        template_id="prev_chart",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
        ],
    )
    html = render_preview(draft)
    assert "cpu_usage" in html or "chart" in html.lower()


def test_preview_reordered_sections() -> None:
    """UT-PRV-005: preview TOC order matches draft order."""
    draft = TemplateDraft(
        template_id="prev_order",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(
                id="memory_usage",
                title="Memory",
                data_hint=["memory"],
            ),
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
        ],
    )
    html = render_preview(draft)
    # _base.html.j2 renders sections in order; check that Memory
    # appears before CPU in the section list (after the TOC).
    toc_end = html.find('class="toc"')
    mem_pos = html.find("Memory", toc_end)
    cpu_pos = html.find("CPU", toc_end)
    assert mem_pos < cpu_pos
