# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Evexia is a hackathon prototype for patient-controlled medical data aggregation. Patients consolidate records from multiple Arizona hospitals, generate AI-powered health summaries, and share specific data categories with healthcare providers using token-based access.

## Commands

```bash
# Run the application
uv run uvicorn main:app --host 0.0.0.0 --port 5000

# Or directly via Python
uv run python main.py

# Install dependencies
uv sync
```

No test suite exists. Manual testing via the test checklist in README.md.

## Architecture

**Backend (Python 3.11+ / FastAPI)**

- `main.py` - FastAPI app with all routes. Two portals: patient (`/patient`) and provider (`/provider`). REST API under `/api/`.
- `db.py` - SQLite wrapper with auto-init. Tables: `patients`, `records`, `summaries`, `share_tokens`, `access_logs`. All CRUD ops here.
- `ai.py` - OpenAI GPT-4o integration via Replit AI Integrations. Falls back to deterministic mock summaries if AI unavailable. Generates clinician and patient-friendly summaries + anomaly detection.
- `ingest.py` - Loads sample data, parses uploads, normalizes records across hospitals, detects anomalies (duplicates, missing dates, outliers), extracts chart data.

**Frontend (Vanilla JS + Jinja2)**

- `templates/` - Jinja2 templates: landing, patient portal, provider portal
- `static/charts.js` - Chart.js visualization for BMI, cholesterol, A1C trends
- `static/styles.css` - Application styling

**Data Flow**

1. Patient loads sample data or uploads JSON → `ingest.py` normalizes → stored in SQLite
2. Patient generates summary → `ai.py` processes records → stored in SQLite
3. Patient creates share token → `secrets.token_urlsafe(32)` → stored with scope/expiry
4. Provider enters token → validated → scoped records returned with access logged

## Key Design Decisions

- Name-based patient lookup (no auth - hackathon prototype)
- Token-based sharing with configurable scope (vitals/labs/meds/encounters) and expiry
- AI fallback ensures app works fully without API keys
- All medical disclaimers required in summaries
- SQLite `app.db` auto-created on first run

## Data Format

JSON uploads must follow structure in `sample_data/hospital_*.json`:
```json
{
  "hospital": "Hospital Name",
  "records": {
    "vitals": { "entries": [...] },
    "labs": { "entries": [...] },
    "meds": { "entries": [...] },
    "encounters": { "entries": [...] }
  }
}
```
