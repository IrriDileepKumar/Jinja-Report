"""Unit tests for validator.py."""

from __future__ import annotations

from backend.models import CoverConfig, SectionDef, TemplateDraft
from backend.validator import validate_draft, validate_html_j2


def test_invalid_template_id() -> None:
    """UT-VAL-001: invalid template_id produces error."""
    draft = TemplateDraft.model_construct(
        template_id="My-Report",
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
    result = validate_draft(draft)
    assert result.errors
    assert any("template_id" in e for e in result.errors)


def test_duplicate_section_ids() -> None:
    """UT-VAL-002: duplicate section ids produce error."""
    draft = TemplateDraft(
        template_id="dup_test",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(id="s1", title="S1", data_hint=["cpu"]),
            SectionDef(id="s1", title="S2", data_hint=["memory"]),
        ],
    )
    result = validate_draft(draft)
    assert result.errors
    assert any("Duplicate" in e for e in result.errors)


def test_empty_data_hint() -> None:
    """UT-VAL-003: empty data_hint produces error."""
    draft = TemplateDraft.model_construct(
        template_id="empty_hint",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef.model_construct(id="s1", title="S1", data_hint=[]),
        ],
    )
    result = validate_draft(draft)
    assert result.errors
    assert any("data_hint" in e for e in result.errors)


def test_empty_sections() -> None:
    """UT-VAL-004: empty sections list produces error."""
    draft = TemplateDraft.model_construct(
        template_id="empty_sec",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[],
    )
    result = validate_draft(draft)
    assert result.errors
    assert any("section" in e.lower() for e in result.errors)


def test_unknown_keyword_only() -> None:
    """UT-VAL-005: unknown keyword only produces warning + error."""
    draft = TemplateDraft(
        template_id="unk_only",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(
                id="s1", title="S1", data_hint=["zzznonexistent"]
            ),
        ],
    )
    result = validate_draft(draft)
    assert result.warnings
    assert result.errors
    assert any("unknown" in w.lower() for w in result.warnings)
    assert any("no known keywords" in e.lower() for e in result.errors)


def test_mixed_known_unknown_keywords() -> None:
    """UT-VAL-006: mix known/unknown produces warning only."""
    draft = TemplateDraft(
        template_id="mix_kw",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="E",
            report_title="T",
            report_subtitle="S",
        ),
        sections=[
            SectionDef(
                id="s1", title="S1", data_hint=["cpu", "zzzunknown"]
            ),
        ],
    )
    result = validate_draft(draft)
    assert result.warnings
    assert not result.errors


def test_valid_minimal_draft() -> None:
    """UT-VAL-007: valid minimal draft has no errors."""
    draft = TemplateDraft(
        template_id="valid",
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
    result = validate_draft(draft)
    assert not result.errors


def test_validate_html_j2_valid() -> None:
    """validate_html_j2 on valid generated content has no errors."""
    from backend.generator import generate_html_j2

    draft = TemplateDraft(
        template_id="html_val",
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
    result = validate_html_j2(content)
    assert not result.errors
