# Evexia - Patient Medical Data Aggregator

A hackathon prototype for patient-controlled medical data aggregation from multiple Arizona hospitals with AI-powered summaries and secure provider sharing.

## Overview

MedAgg allows patients to:
- Load/upload medical records from multiple hospitals (Banner Health, Mayo Clinic, and Phoenician Medical Center in Arizona)
- View AI-generated health summaries (both clinical and patient-friendly)
- See interactive health metric charts (BMI, cholesterol, A1C)
- Create secure share tokens with scoped access and expiration
- Track who has accessed their shared data

Providers can:
- Access patient records using share tokens
- View summaries and health metrics within authorized scope
- All access is logged for patient transparency

## Features

### Patient Portal
- Load sample data from 3 Arizona hospitals
- Upload custom JSON medical records
- AI-powered summary generation with anomaly detection
- Interactive Chart.js visualizations
- Token-based sharing with configurable scope and expiry
- Access log viewing

### Provider Portal
- Token-based access to patient records
- Scoped viewing (only authorized data categories)
- Clinical summaries and anomaly flags
- Health metric charts

### Security Features
- Token generation uses `secrets.token_urlsafe(32)`
- Token expiry enforcement
- Scope enforcement (providers only see authorized categories)
- Access logging with IP and timestamp
- Input validation (JSON only for uploads)

## Setup

### Requirements
- Python 3.11+
- FastAPI, Jinja2, uvicorn (installed automatically)

### Running the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

Or simply use the Replit Run button.

### AI Integration

This app uses Replit's AI Integration for OpenAI access:
- No API key required
- Charges are billed to your Replit credits
- If AI is unavailable, the app falls back to deterministic mock summaries

The app will work fully end-to-end even without AI - mock summaries provide realistic output for demonstration.

## Project Structure

```
/
├── main.py              # FastAPI app with routes and API endpoints
├── db.py                # SQLite database helpers and schema
├── ai.py                # OpenAI integration with mock fallback
├── ingest.py            # Data loading, normalization, anomaly detection
├── templates/
│   ├── index.html       # Landing page
│   ├── patient.html     # Patient portal
│   └── provider.html    # Provider portal
├── static/
│   ├── styles.css       # Application styles
│   └── charts.js        # Chart.js visualization code
├── sample_data/
│   ├── banner_health.json  # Sample data from Banner Health (Phoenix)
│   ├── mayo_clinic.json  # Sample data from Mayo Clinic (Tucson)
│   └── phoenician_medical_center.json  # Sample data from Phoenician Medical Center (Scottsdale)
├── uploads/             # Uploaded JSON files (created on first upload)
├── app.db               # SQLite database (created on first run)
└── README.md            # This file
```

## Manual Test Checklist (Happy Path)

### Patient Flow
1. [ ] Navigate to `/` - Landing page loads with Patient/Provider buttons
2. [ ] Click "Enter as Patient" - Patient portal loads
3. [ ] Enter patient name (e.g., "John Doe")
4. [ ] Verify all hospitals (A, B, C) are checked
5. [ ] Verify all categories (vitals, labs, meds, encounters) are checked
6. [ ] Click "Load Sample Data" - Success message appears
7. [ ] Verify charts section appears with BMI, Cholesterol, A1C graphs
8. [ ] Click "Generate Summary" - Loading spinner appears
9. [ ] Verify clinical summary appears with bullet points
10. [ ] Verify patient-friendly summary appears
11. [ ] Verify anomaly flags appear (if any)
12. [ ] Verify disclaimer is displayed
13. [ ] Select sharing scope (e.g., vitals and labs only)
14. [ ] Select token expiry (e.g., 24 hours)
15. [ ] Click "Create Share Token" - Token displayed
16. [ ] Click "Copy" button - Token copied to clipboard
17. [ ] Note the token for provider testing

### Provider Flow
18. [ ] Navigate to `/provider`
19. [ ] Paste the share token from step 17
20. [ ] Click "Access Records" - Success message
21. [ ] Verify patient name is displayed
22. [ ] Verify scope shows only authorized categories
23. [ ] Verify clinical summary is displayed
24. [ ] Verify charts show only authorized metrics
25. [ ] Click through record tabs - only authorized categories visible
26. [ ] Verify disclaimer is displayed

### Access Log Verification
27. [ ] Return to patient portal (same patient name)
28. [ ] Scroll to Access Log section
29. [ ] Verify provider access is logged with timestamp and IP

### Upload Flow
30. [ ] Create a test JSON file matching sample_data format
31. [ ] Enter patient name
32. [ ] Click "Upload JSON File" and select the file
33. [ ] Verify success message with record count

## Sample Data Format

JSON files should follow this structure:

```json
{
  "hospital": "Hospital Name",
  "hospital_location": "City, Arizona",
  "patient_id": "DEMO-001",
  "records": {
    "vitals": {
      "entries": [
        {
          "date": "2024-01-15",
          "blood_pressure": "128/82",
          "heart_rate": 72,
          "bmi": 26.5
        }
      ]
    },
    "labs": {
      "entries": [
        {
          "date": "2024-01-15",
          "total_cholesterol": 215,
          "a1c": 6.2
        }
      ]
    },
    "meds": {
      "entries": [
        {
          "medication": "Lisinopril",
          "dose": "10mg",
          "frequency": "Once daily"
        }
      ]
    },
    "encounters": {
      "entries": [
        {
          "date": "2024-01-15",
          "type": "Annual Physical",
          "provider": "Dr. Smith"
        }
      ]
    }
  }
}
```

## Important Disclaimers

- **This is informational only, not medical advice.**
- **AI summaries may be inaccurate; verify original records.**
- **Always consult your healthcare provider for medical decisions.**

## Technology Stack

- **Backend**: FastAPI + Python 3.11
- **Database**: SQLite
- **Templates**: Jinja2
- **Frontend**: Vanilla JavaScript + Chart.js
- **AI**: OpenAI via Replit AI Integrations (with mock fallback)

## Limitations (Prototype)

- No user authentication (name-based patient lookup)
- Single SQLite database file
- No production-grade security hardening
- No HIPAA compliance (demonstration only)
- Limited to JSON file format for uploads
