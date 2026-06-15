"""Pydantic models for template drafts and validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoverConfig(BaseModel):
    """Cover page branding blocks."""

    eyebrow: str = "Infrastructure Intelligence"
    report_title: str = "Report"
    report_subtitle: str = ""
    accent_1: str = "#22d3ee"
    accent_2: str = "#6366f1"
    accent_3: str = "#8b5cf6"


class SectionDef(BaseModel):
    """A single data section declaration."""

    id: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    title: str
    data_hint: list[str] = Field(..., min_length=1)
    chart_type: str = "auto"


class TemplateDraft(BaseModel):
    """User-editable draft state."""

    template_id: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    version: str = "1.0"
    layout: str = "base_extended"
    cover: CoverConfig
    sections: list[SectionDef] = Field(..., min_length=1)


class ValidationResult(BaseModel):
    """Result of draft or exported content validation."""

    errors: list[str] = []
    warnings: list[str] = []
