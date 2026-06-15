"""Unit tests for generator.py."""

from __future__ import annotations

import re

import yaml

from backend.generator import generate_html_j2
from backend.models import CoverConfig, SectionDef, TemplateDraft

_FRONT_MATTER_RE = re.compile(
    r"\{#\s*---\s*\n(.*?)\n\s*---\s*#\}",
    re.DOTALL,
)


def test_generate_html_j2_minimal() -> None:
    """UT-GEN-001: output matches front-matter regex."""
    draft = TemplateDraft(
        template_id="test_report",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="Eyebrow",
            report_title="Title",
            report_subtitle="Sub",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu"]),
        ],
    )
    content = generate_html_j2(draft)
    assert _FRONT_MATTER_RE.search(content) is not None


def test_generate_front_matter_yaml() -> None:
    """UT-GEN-002: front-matter YAML contains template_id and sections."""
    draft = TemplateDraft(
        template_id="yaml_test",
        version="2.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="s1", title="S1", data_hint=["cpu"]),
        ],
    )
    content = generate_html_j2(draft)
    match = _FRONT_MATTER_RE.search(content)
    assert match is not None
    fm = yaml.safe_load(match.group(1))
    assert fm["template_id"] == "yaml_test"
    assert "sections" in fm
    assert len(fm["sections"]) == 1


def test_generate_extends_base() -> None:
    """UT-GEN-003: body contains extends _base.html.j2."""
    draft = TemplateDraft(
        template_id="extends_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="s1", title="S1", data_hint=["cpu"]),
        ],
    )
    content = generate_html_j2(draft)
    assert '{% extends "_base.html.j2" %}' in content


def test_generate_cover_blocks() -> None:
    """UT-GEN-004: cover block values appear in content."""
    draft = TemplateDraft(
        template_id="cover_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="MyEyebrow",
            report_title="MyTitle",
            report_subtitle="MySub",
        ),
        sections=[
            SectionDef(id="s1", title="S1", data_hint=["cpu"]),
        ],
    )
    content = generate_html_j2(draft)
    assert "MyEyebrow" in content
    assert "MyTitle" in content
    assert "MySub" in content


def test_generate_section_order() -> None:
    """UT-GEN-005: section ids in YAML match draft order."""
    draft = TemplateDraft(
        template_id="order_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="first", title="First", data_hint=["cpu"]),
            SectionDef(id="second", title="Second", data_hint=["memory"]),
            SectionDef(id="third", title="Third", data_hint=["disk"]),
        ],
    )
    content = generate_html_j2(draft)
    match = _FRONT_MATTER_RE.search(content)
    assert match is not None
    fm = yaml.safe_load(match.group(1))
    ids = [s["id"] for s in fm["sections"]]
    assert ids == ["first", "second", "third"]


def test_generate_chart_type_default() -> None:
    """UT-GEN-006: omitted chart_type defaults to auto in YAML."""
    draft = TemplateDraft(
        template_id="chart_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="s1", title="S1", data_hint=["cpu"]),
        ],
    )
    content = generate_html_j2(draft)
    match = _FRONT_MATTER_RE.search(content)
    assert match is not None
    fm = yaml.safe_load(match.group(1))
    assert fm["sections"][0]["chart_type"] == "auto"
