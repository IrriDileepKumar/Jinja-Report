"""Pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.models import CoverConfig, SectionDef, TemplateDraft


@pytest.fixture
def sample_draft() -> TemplateDraft:
    """Return a valid minimal draft."""
    return TemplateDraft(
        template_id="fleet_health",
        version="1.0",
        layout="base_extended",
        cover=CoverConfig(
            eyebrow="Infra",
            report_title="Fleet Health",
            report_subtitle="Operational telemetry.",
        ),
        sections=[
            SectionDef(id="cpu_usage", title="CPU", data_hint=["cpu", "node"]),
            SectionDef(
                id="memory_usage",
                title="Memory",
                data_hint=["memory", "ram"],
            ),
        ],
    )


@pytest.fixture
def invalid_draft_bad_id() -> dict:
    """Return a draft dict with an invalid template_id."""
    return {
        "template_id": "Bad-ID",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "Test",
            "report_title": "Title",
            "report_subtitle": "Sub",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
