"""Functional API tests using httpx TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_catalog_sections() -> None:
    """FN-API-001: GET /api/catalog/sections returns >=20 items."""
    response = client.get("/api/catalog/sections")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 20


def test_catalog_keywords() -> None:
    """FN-API-002: GET /api/catalog/keywords returns non-empty list."""
    response = client.get("/api/catalog/keywords")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0


def test_validate_valid_draft() -> None:
    """FN-API-003: POST /api/templates/validate valid draft errors empty."""
    draft = {
        "template_id": "valid_api",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "E",
            "report_title": "T",
            "report_subtitle": "S",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
    response = client.post("/api/templates/validate", json=draft)
    assert response.status_code == 200
    result = response.json()
    assert result["errors"] == []


def test_validate_invalid_draft() -> None:
    """FN-API-004: POST /api/templates/validate invalid draft errors non-empty."""
    draft = {
        "template_id": "Bad-ID",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "E",
            "report_title": "T",
            "report_subtitle": "S",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
    response = client.post("/api/templates/validate", json=draft)
    assert response.status_code == 200
    result = response.json()
    assert result["errors"]


def test_generate() -> None:
    """FN-API-005: POST /api/templates/generate returns content with front-matter."""
    draft = {
        "template_id": "gen_api",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "E",
            "report_title": "T",
            "report_subtitle": "S",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
    response = client.post("/api/templates/generate", json=draft)
    assert response.status_code == 200
    data = response.json()
    assert "{# ---" in data["content"]


def test_preview() -> None:
    """FN-API-006: POST /api/templates/preview returns HTML with title."""
    draft = {
        "template_id": "prev_api",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "E",
            "report_title": "Preview Title",
            "report_subtitle": "S",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
    response = client.post("/api/templates/preview", json=draft)
    assert response.status_code == 200
    data = response.json()
    assert "Preview Title" in data["html"]


def test_draft_crud() -> None:
    """FN-API-007: PUT then GET draft returns same data."""
    draft = {
        "template_id": "test_draft",
        "version": "1.0",
        "layout": "base_extended",
        "cover": {
            "eyebrow": "E",
            "report_title": "T",
            "report_subtitle": "S",
        },
        "sections": [
            {"id": "cpu_usage", "title": "CPU", "data_hint": ["cpu"]},
        ],
    }
    put_resp = client.put("/api/templates/drafts/test_draft", json=draft)
    assert put_resp.status_code in (200, 201)

    get_resp = client.get("/api/templates/drafts/test_draft")
    assert get_resp.status_code == 200
    assert get_resp.json()["template_id"] == "test_draft"


def test_import_gpu_performance() -> None:
    """FN-API-008: POST /api/templates/import gpu_performance body returns 4 sections."""
    from pathlib import Path

    path = (
        Path(__file__).resolve().parent.parent.parent
        / "infra_agents"
        / "agents"
        / "report_agent"
        / "templates"
        / "gpu_performance.html.j2"
    )
    content = path.read_text(encoding="utf-8")
    response = client.post(
        "/api/templates/import",
        files={"file": ("gpu_performance.html.j2", content, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sections"]) == 4
