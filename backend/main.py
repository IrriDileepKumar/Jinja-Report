"""FastAPI backend for the Report Template Editor POC."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .catalog_loader import (
    load_keyword_index,
    load_section_catalog,
    list_catalog_categories,
)
from .generator import generate_html_j2
from .importer import import_html_j2
from .models import TemplateDraft, ValidationResult
from .preview_renderer import render_preview
from .validator import validate_draft, validate_html_j2

app = FastAPI(title="Report Template Editor POC")

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_DRAFTS_DIR = Path(__file__).resolve().parent.parent / "output" / "drafts"
_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/api/catalog/sections")
def get_catalog_sections(category: str = "") -> dict:
    """Return section catalog, optionally filtered by category."""
    catalog = load_section_catalog()
    if category:
        catalog = [c for c in catalog if c.get("category") == category]
    return {"items": catalog}


@app.get("/api/catalog/keywords")
def get_catalog_keywords() -> dict:
    """Return the full keyword autocomplete list."""
    keywords = sorted(load_keyword_index())
    return {"items": keywords}


@app.get("/api/catalog/layouts")
def get_catalog_layouts() -> dict:
    """Return available layout presets."""
    path = (
        Path(__file__).resolve().parent.parent
        / "catalog"
        / "layout_presets.json"
    )
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    return {"items": data.get("presets", [])}


@app.post("/api/templates/import")
async def import_template(file: UploadFile) -> dict:
    """Import an .html.j2 file and return a TemplateDraft."""
    content = (await file.read()).decode("utf-8")
    try:
        draft = import_html_j2(content)
    except (ValueError, ImportError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return draft.model_dump()


@app.post("/api/templates/validate")
def validate_template(payload: dict) -> ValidationResult:
    """Validate a TemplateDraft from raw JSON.

    Accepts a dict so that invalid fields (e.g. bad template_id) can be
    validated and reported as errors rather than rejected at the HTTP layer.
    """
    try:
        draft = TemplateDraft.model_validate(payload)
    except Exception as exc:
        return ValidationResult(
            errors=[f"Schema validation error: {exc}"], warnings=[]
        )
    return validate_draft(draft)


@app.post("/api/templates/generate")
def generate_template(draft: TemplateDraft) -> dict:
    """Generate .html.j2 content from a draft."""
    try:
        content = generate_html_j2(draft)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    filename = f"{draft.template_id}.html.j2"
    return {"content": content, "filename": filename}


@app.post("/api/templates/preview")
def preview_template(draft: TemplateDraft) -> dict:
    """Render preview HTML for a draft."""
    try:
        html = render_preview(draft)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Preview render failed: {exc}"
        ) from exc
    return {"html": html}


@app.get("/api/templates/drafts")
def list_drafts() -> dict:
    """List saved draft IDs."""
    ids = [p.stem for p in _DRAFTS_DIR.glob("*.json")]
    return {"ids": sorted(ids)}


@app.get("/api/templates/drafts/{draft_id}")
def get_draft(draft_id: str) -> dict:
    """Load a saved draft."""
    path = _DRAFTS_DIR / f"{draft_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")
    import json

    return json.loads(path.read_text(encoding="utf-8"))


@app.put("/api/templates/drafts/{draft_id}")
def save_draft(draft_id: str, draft: TemplateDraft) -> JSONResponse:
    """Save a draft JSON file."""
    path = _DRAFTS_DIR / f"{draft_id}.json"
    path.write_text(
        draft.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return JSONResponse(
        status_code=200, content={"id": draft_id, "saved": True}
    )
