# Report Template Editor — POC

A standalone visual editor for building **Report Agent V2** `.html.j2` Jinja2 templates.  
Users compose report templates in a web UI; the backend renders the Jinja output. **No modifications to the core agent codebase are required.**

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup (Python / FastAPI)](#backend-setup-python--fastapi)
  - [Frontend Setup (React / Vite)](#frontend-setup-react--vite)
- [How the Preview Works](#how-the-preview-works)
- [API Reference](#api-reference)
- [Data Format — TemplateDraft](#data-format--templatedraft)
- [Frontend Component Map](#frontend-component-map)
- [Export Flow](#export-flow)
- [Project Structure](#project-structure)

---

## Architecture Overview

```
┌─────────────────────────────┐        ┌──────────────────────────────────┐
│  React + Vite (port 30001)  │  HTTP  │  FastAPI + Jinja2 (port 8091)    │
│                             │◄──────►│                                  │
│  - Edits TemplateDraft JSON │        │  - Renders preview HTML          │
│  - Shows live preview       │        │  - Generates .html.j2 output     │
│  - Exports .html.j2 file    │        │  - Validates draft               │
│  - Imports existing files   │        │  - Serves section catalog        │
└─────────────────────────────┘        └──────────────────────────────────┘
```

> **Key design principle:** The frontend only ever works with a JSON object (`TemplateDraft`).  
> All Jinja2 template rendering and generation happens entirely on the backend.

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| npm | ≥ 9 |

---

### Backend Setup (Python / FastAPI)

```bash
# 1. Install Python dependencies
pip install -e ".[dev]"

# 2. Start the API server on port 8091
uvicorn backend.main:app --port 8091 --reload
```

The API will be available at: `http://localhost:8091`  
Interactive docs (Swagger UI): `http://localhost:8091/docs`

---

### Frontend Setup (React / Vite)

```bash
# 1. Install Node dependencies (run from repo root)
npm install

# 2. Start the Vite dev server
npm run dev
```

The frontend will be available at: `http://localhost:30001`

> The Vite dev server is pre-configured to proxy all `/api/*` requests to `http://localhost:8091`.  
> **Both the backend and frontend must be running simultaneously** for the app to work.

---

## How the Preview Works

The frontend never interprets Jinja itself. The full flow is:

```
1. User edits draft (JSON) in React
        ↓  (debounced 400ms)
2. POST /api/templates/preview  { TemplateDraft }
        ↓
3. Python builds a Jinja2 wrapper, renders it with mock data
        ↓
4. Returns { html: "<rendered HTML string>" }
        ↓
5. React injects it into an <iframe srcDoc={html} />
```

Mock data for the preview lives in: `fixtures/mock_section_data.json`  
The base Jinja layout used for preview: `fixtures/_base.html.j2`

---

## API Reference

All endpoints are prefixed with `/api`.

### Catalog

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/catalog/sections?category=` | List available section types (optional category filter) |
| `GET` | `/api/catalog/keywords` | Sorted list of all autocomplete keywords |
| `GET` | `/api/catalog/layouts` | Available layout presets |

### Templates

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/api/templates/preview` | `TemplateDraft` | Render live preview HTML |
| `POST` | `/api/templates/validate` | `TemplateDraft` | Validate a draft, returns errors + warnings |
| `POST` | `/api/templates/generate` | `TemplateDraft` | Generate `.html.j2` file content |
| `POST` | `/api/templates/import` | `multipart/form-data` (file) | Parse an existing `.html.j2` into a `TemplateDraft` |

### Drafts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/templates/drafts` | List saved draft IDs |
| `GET` | `/api/templates/drafts/{id}` | Load a saved draft |
| `PUT` | `/api/templates/drafts/{id}` | Save / overwrite a draft |

---

## Data Format — TemplateDraft

This is the **single source of truth** for the entire editor. Everything the frontend does revolves around this JSON object.

```json
{
  "template_id": "my_report",
  "version": "1.0",
  "layout": "base_extended",

  "cover": {
    "eyebrow": "Infrastructure Intelligence",
    "report_title": "Operational Report",
    "report_subtitle": "Telemetry summary for the selected period.",
    "accent_1": "#22d3ee",
    "accent_2": "#6366f1",
    "accent_3": "#8b5cf6"
  },

  "sections": [
    {
      "id": "cpu_usage",
      "title": "CPU Utilization",
      "data_hint": ["node", "cpu", "utilization"],
      "chart_type": "auto"
    },
    {
      "id": "memory_usage",
      "title": "Memory Usage",
      "data_hint": ["node", "memory", "ram"],
      "chart_type": "auto"
    }
  ]
}
```

### Field Reference

#### Top-level

| Field | Type | Constraint | Description |
|-------|------|-----------|-------------|
| `template_id` | `string` | `^[a-z][a-z0-9_]*$` | Unique ID, used as the exported filename |
| `version` | `string` | — | Version label, e.g. `"1.0"` |
| `layout` | `string` | Only `"base_extended"` supported (Phase 1) | Layout type |
| `cover` | `object` | Required | Cover page branding |
| `sections` | `array` | Min 1 item | Ordered list of report sections |

#### `cover` object

| Field | Type | Description |
|-------|------|-------------|
| `eyebrow` | `string` | Small text above the title (e.g. team name) |
| `report_title` | `string` | Main heading on the cover page |
| `report_subtitle` | `string` | Secondary subtitle line |
| `accent_1` | `string` (hex) | Primary accent color |
| `accent_2` | `string` (hex) | Secondary accent color |
| `accent_3` | `string` (hex) | Tertiary accent color |

#### `sections[]` item

| Field | Type | Constraint | Description |
|-------|------|-----------|-------------|
| `id` | `string` | `^[a-z][a-z0-9_]*$` | Unique section ID |
| `title` | `string` | — | Display title for the section |
| `data_hint` | `string[]` | Min 1 item | Keywords describing the telemetry this section uses |
| `chart_type` | `string` | `auto`, `line`, `bar`, `area` | Chart rendering hint (`auto` = backend decides) |

### API Response Shapes

#### `POST /api/templates/preview` → Response
```json
{ "html": "<full rendered HTML string>" }
```

#### `POST /api/templates/validate` → Response
```json
{
  "errors": ["template_id is required", "..."],
  "warnings": ["section 'foo' has no mock data"]
}
```

#### `POST /api/templates/generate` → Response
```json
{
  "content": "{% extends \"_base.html.j2\" %}\n{% block eyebrow %}...{% endblock %}\n...",
  "filename": "my_report.html.j2"
}
```

#### `GET /api/catalog/sections` → Response
```json
{
  "items": [
    {
      "id": "cpu_usage",
      "title": "CPU Utilization",
      "category": "compute",
      "data_hint": ["cpu", "node"],
      "chart_type": "line"
    }
  ]
}
```

#### `GET /api/catalog/keywords` → Response
```json
{ "items": ["cpu", "memory", "disk", "network", "node", "..."] }
```

---

## Frontend Component Map

```
src/
├── App.tsx                  # Root — holds all draft state, debounced preview + validation
├── api/
│   └── client.ts            # All API calls (fetch wrappers), TypeScript types
└── components/
    ├── TemplateMetaForm.tsx  # Edits template_id, version, layout
    ├── CoverEditor.tsx       # Edits cover (title, subtitle, eyebrow, accent colors)
    ├── SectionList.tsx       # Drag-and-drop ordered list of sections (uses @dnd-kit)
    ├── SectionEditor.tsx     # Edits a single section (id, title, data_hint, chart_type)
    ├── SectionPicker.tsx     # Browse + pick sections from the catalog
    ├── PreviewPane.tsx       # <iframe srcDoc={html}> — displays rendered preview
    └── ExportPanel.tsx       # Export .html.j2 download + Import .html.j2 upload
```

### State flow in `App.tsx`

```
draft (TemplateDraft state)
  ├── onChange → re-renders all editor components
  ├── useEffect → debounced POST /api/templates/preview → setPreviewHtml
  └── useEffect → POST /api/templates/validate → setValidation (errors/warnings)
```

---

## Export Flow

1. User composes template (sections, cover, colors) in the UI.
2. Backend continuously validates the draft; **Export button is disabled while there are errors**.
3. User clicks **Export .html.j2** → calls `POST /api/templates/generate` → downloads `{template_id}.html.j2`.
4. Validate the exported file against the production parser:
   ```bash
   python scripts/validate_against_agent.py output/my_template.html.j2
   ```

---

## Project Structure

```
report-template-editor-poc/
├── backend/                  # FastAPI app
│   ├── main.py               # API routes
│   ├── models.py             # Pydantic models (TemplateDraft, CoverConfig, SectionDef)
│   ├── generator.py          # Draft → .html.j2 string
│   ├── preview_renderer.py   # Draft + mock data → rendered HTML (Jinja2)
│   ├── importer.py           # .html.j2 file → TemplateDraft
│   ├── validator.py          # Draft validation logic
│   └── catalog_loader.py     # Loads section_catalog.json / keyword_index.json
├── frontend/                 # React + TypeScript + Vite
│   ├── vite.config.ts        # Dev server (port 30001), proxy → localhost:8091
│   └── src/
│       ├── App.tsx           # Root component
│       ├── api/client.ts     # API layer + TypeScript types
│       └── components/       # UI components (see Component Map above)
├── catalog/
│   ├── section_catalog.json  # Available sections with metadata
│   └── keyword_index.json    # Autocomplete keyword list
├── fixtures/
│   ├── _base.html.j2         # Base Jinja layout used for preview rendering
│   └── mock_section_data.json# Fake telemetry data used in preview
├── output/
│   └── drafts/               # Saved draft JSON files (auto-created)
├── scripts/
│   ├── extract_catalog.py    # Regenerate section_catalog.json
│   ├── extract_keywords.py   # Regenerate keyword_index.json
│   └── validate_against_agent.py # Validate exported template
├── tests/                    # pytest test suite (L1–L3)
├── pyproject.toml            # Python dependencies
└── package.json              # Node dependencies + npm scripts
```

---

## Notes

- **Zero agent modifications**: This tool is fully standalone. No files inside `infra_agents/agents/report_agent/` are touched.
- **Jinja is backend-only**: The frontend never interprets or generates Jinja syntax — only the Python backend does.
- **Phase 1 scope**: Only the `base_extended` layout (`{% extends "_base.html.j2" %}`) is supported.
- Drafts are auto-saved to `output/drafts/{template_id}.json`.
