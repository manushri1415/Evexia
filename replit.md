# MedAgg - Patient Medical Data Aggregator

## Project Overview
MedAgg is a hackathon prototype for patient-controlled medical data aggregation. It allows patients to consolidate records from multiple Arizona hospitals, generate AI-powered health summaries, and securely share specific data categories with healthcare providers using token-based access.

## Project Structure
```
/
├── main.py              # FastAPI application with all routes and API endpoints
├── db.py                # SQLite database helpers, schema, and CRUD operations
├── ai.py                # OpenAI integration with deterministic mock fallback
├── ingest.py            # Data loading, normalization, and anomaly detection
├── templates/           # Jinja2 HTML templates
│   ├── index.html       # Landing page with role selection
│   ├── patient.html     # Full patient portal with data, charts, sharing
│   └── provider.html    # Provider portal for token-based access
├── static/              # Static assets
│   ├── styles.css       # Application styling
│   └── charts.js        # Chart.js visualization logic
├── sample_data/         # Sample medical records from Arizona hospitals
│   ├── hospital_a.json  # Phoenix hospital data
│   ├── hospital_b.json  # Tucson hospital data
│   └── hospital_c.json  # Scottsdale hospital data
├── uploads/             # User-uploaded JSON files
├── app.db               # SQLite database (auto-created)
└── README.md            # Setup and testing documentation
```

## Technology Stack
- **Backend**: Python 3.11, FastAPI, Jinja2
- **Database**: SQLite (app.db)
- **AI**: OpenAI via Replit AI Integrations (no API key required, billed to credits)
- **Frontend**: Vanilla JavaScript, Chart.js for visualizations
- **Server**: Uvicorn on port 5000

## Key Features
1. **Patient Portal**: Load/upload medical data, generate AI summaries, view charts, create share tokens
2. **Provider Portal**: Access patient data via tokens with scope enforcement
3. **Anomaly Detection**: Rules-based flagging of duplicates, missing dates, outliers
4. **Access Logging**: Track all provider access with timestamps and IPs

## Running the Application
The app runs on port 5000 with: `uvicorn main:app --host 0.0.0.0 --port 5000`

## Architecture Decisions
- Single FastAPI app for simplicity (hackathon prototype)
- SQLite for portable, zero-config database
- Token-based sharing (no OAuth complexity)
- AI fallback to mock summaries ensures demo works without API keys
- All medical disclaimers prominently displayed

## Recent Changes
- Initial implementation: Feb 2, 2026
  - Full FastAPI backend with patient/provider flows
  - SQLite database with patients, records, summaries, tokens, access logs
  - OpenAI integration with Replit AI Integrations
  - Sample data from 3 Arizona hospitals
  - Chart.js visualizations for health metrics
  - Token-based sharing with scope and expiry
