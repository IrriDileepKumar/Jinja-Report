"""Unit tests for importer.py and round-trip validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.generator import generate_html_j2
from backend.importer import import_html_j2
from backend.validator import validate_html_j2

_GPU_PERFORMANCE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "infra_agents"
    / "agents"
    / "report_agent"
    / "templates"
    / "gpu_performance.html.j2"
)


def test_import_gpu_performance() -> None:
    """UT-IMP-001: import gpu_performance has 4 sections, base_extended."""
    content = _GPU_PERFORMANCE_PATH.read_text(encoding="utf-8")
    draft = import_html_j2(content)
    assert draft.layout == "base_extended"
    assert len(draft.sections) == 4


def test_import_generate_validate_roundtrip() -> None:
    """UT-IMP-002: import -> generate -> validate has no errors."""
    content = _GPU_PERFORMANCE_PATH.read_text(encoding="utf-8")
    draft = import_html_j2(content)
    generated = generate_html_j2(draft)
    result = validate_html_j2(generated)
    assert not result.errors


def test_import_preserves_section_ids() -> None:
    """UT-IMP-003: imported section ids match source."""
    content = _GPU_PERFORMANCE_PATH.read_text(encoding="utf-8")
    draft = import_html_j2(content)
    expected_ids = [
        "gpu_utilization",
        "gpu_memory",
        "gpu_power",
        "gpu_temperature",
    ]
    assert [s.id for s in draft.sections] == expected_ids


def test_import_extracts_cover_blocks() -> None:
    """UT-IMP-004: imported cover eyebrow/title are non-empty."""
    content = _GPU_PERFORMANCE_PATH.read_text(encoding="utf-8")
    draft = import_html_j2(content)
    assert draft.cover.eyebrow.strip()
    assert draft.cover.report_title.strip()


def test_import_standalone_raises() -> None:
    """UT-IMP-005: standalone template raises ImportError."""
    standalone = """{# ---
template_id: standalone_test
version: "1.0"
sections:
  - id: s1
    title: S1
    data_hint: [a]
--- #}
<!DOCTYPE html>
<html><body>Hello</body></html>
"""
    with pytest.raises(ImportError):
        import_html_j2(standalone)
