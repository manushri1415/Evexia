import os
import re
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import db
import ai
import ingest

app = FastAPI(title="MedAgg - Patient Medical Data Aggregator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DISCLAIMER = "DISCLAIMER: This is informational only, not medical advice. AI summaries may be inaccurate. Always verify with original records and consult your healthcare provider."

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "disclaimer": DISCLAIMER
    })

@app.get("/patient", response_class=HTMLResponse)
async def patient_page(request: Request):
    return templates.TemplateResponse("patient.html", {
        "request": request,
        "disclaimer": DISCLAIMER,
        "hospitals": ["Banner Health", "Mayo Clinic", "Phoenician Medical Center"],
        "categories": ["vitals", "labs", "meds", "encounters"]
    })

@app.get("/provider", response_class=HTMLResponse)
async def provider_page(request: Request):
    return templates.TemplateResponse("provider.html", {
        "request": request,
        "disclaimer": DISCLAIMER
    })

@app.post("/api/load-sample-data")
async def load_sample_data(
    patient_name: str = Form(...),
    hospitals: List[str] = Form([]),
    categories: List[str] = Form([])
):
    if not patient_name:
        raise HTTPException(status_code=400, detail="Patient name is required")

    # Load sample data (returns dict with 'records' and 'patient_info')
    sample_data = ingest.load_sample_data(hospitals=hospitals, categories=categories)
    records = sample_data.get('records', [])
    patient_info = sample_data.get('patient_info')

    # Get or create patient with DOB from sample data if available
    date_of_birth = patient_info.get('date_of_birth') if patient_info else None
    patient_id = db.get_or_create_patient(patient_name, date_of_birth)

    db.clear_patient_records(patient_id)

    for record in records:
        db.add_record(
            patient_id=patient_id,
            hospital=record['hospital'],
            category=record['category'],
            data=record['data'],
            source_file=record.get('source_file')
        )

    anomalies = ingest.detect_anomalies(records)

    return JSONResponse({
        "success": True,
        "patient_id": patient_id,
        "records_loaded": len(records),
        "anomalies_detected": len(anomalies),
        "message": f"Loaded {len(records)} records from {len(set(r['hospital'] for r in records))} hospitals"
    })

@app.post("/api/upload-data")
async def upload_data(
    patient_name: str = Form(...),
    file: UploadFile = File(...)
):
    if not patient_name:
        raise HTTPException(status_code=400, detail="Patient name is required")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are accepted")

    content = await file.read()
    filename = file.filename  # Narrowed to str after check above

    ingest.save_uploaded_file(content, filename)

    records, errors = ingest.parse_uploaded_json(content, filename)
    
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))
    
    patient_id = db.get_or_create_patient(patient_name)
    
    for record in records:
        db.add_record(
            patient_id=patient_id,
            hospital=record['hospital'],
            category=record['category'],
            data=record['data'],
            source_file=record.get('source_file')
        )
    
    return JSONResponse({
        "success": True,
        "patient_id": patient_id,
        "records_loaded": len(records),
        "message": f"Uploaded {len(records)} records from {file.filename}"
    })

@app.get("/api/patient/{patient_id}/records")
async def get_patient_records(patient_id: int, categories: Optional[str] = None):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    cat_list = categories.split(',') if categories else None
    records = db.get_patient_records(patient_id, categories=cat_list)
    
    chart_data = ingest.extract_chart_data(records)
    
    return JSONResponse({
        "patient": patient,
        "records": records,
        "chart_data": chart_data
    })

@app.post("/api/patient/{patient_id}/generate-summary")
async def generate_summary(patient_id: int):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    records = db.get_patient_records(patient_id)
    
    if not records:
        return JSONResponse({
            "success": False,
            "error": "No records found. Please load data first."
        })
    
    summaries = ai.generate_summaries(records)
    
    db.save_summary(
        patient_id=patient_id,
        clinician_summary=summaries['clinician_summary'],
        patient_summary=summaries['patient_summary'],
        anomalies=summaries.get('anomalies', [])
    )
    
    return JSONResponse({
        "success": True,
        "clinician_summary": summaries['clinician_summary'],
        "patient_summary": summaries['patient_summary'],
        "anomalies": summaries.get('anomalies', []),
        "disclaimer": summaries.get('disclaimer', DISCLAIMER)
    })

@app.get("/api/patient/{patient_id}/summary")
async def get_summary(patient_id: int):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    summary = db.get_summary(patient_id)
    
    if not summary:
        return JSONResponse({
            "success": False,
            "error": "No summary generated yet"
        })
    
    return JSONResponse({
        "success": True,
        "clinician_summary": summary['clinician_summary'],
        "patient_summary": summary['patient_summary'],
        "anomalies": summary.get('anomalies', []),
        "disclaimer": DISCLAIMER
    })

@app.post("/api/patient/{patient_id}/create-token")
async def create_share_token(
    patient_id: int,
    scope: List[str] = Form([]),
    expiry_hours: int = Form(24)
):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if not scope:
        scope = ["vitals", "labs", "meds", "encounters"]
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=expiry_hours)
    
    db.create_share_token(
        patient_id=patient_id,
        token=token,
        scope=scope,
        expires_at=expires_at.isoformat()
    )
    
    return JSONResponse({
        "success": True,
        "token": token,
        "scope": scope,
        "expires_at": expires_at.isoformat(),
        "expiry_hours": expiry_hours
    })

@app.get("/api/patient/{patient_id}/tokens")
async def get_patient_tokens(patient_id: int):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    tokens = db.get_patient_tokens(patient_id)
    
    return JSONResponse({
        "success": True,
        "tokens": tokens
    })

@app.get("/api/patient/{patient_id}/access-logs")
async def get_access_logs(patient_id: int):
    patient = db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    logs = db.get_patient_access_logs(patient_id)
    
    return JSONResponse({
        "success": True,
        "logs": logs
    })

@app.post("/api/provider/access")
async def provider_access(
    request: Request,
    token: str = Form(...),
    patient_name: str = Form(...),
    date_of_birth: str = Form(...)
):
    # Validate DOB format (YYYY-MM-DD)
    dob_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(dob_pattern, date_of_birth):
        raise HTTPException(
            status_code=400,
            detail="Invalid date of birth format. Use YYYY-MM-DD"
        )

    # Validate DOB is not in the future
    try:
        dob_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
        if dob_date > datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Date of birth cannot be in the future"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date of birth. Use YYYY-MM-DD format"
        )

    # Validate token exists
    token_data = db.get_share_token(token)
    if not token_data:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Check token expiration
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expires_at:
        raise HTTPException(status_code=403, detail="Token has expired")

    # Verify patient identity
    verification = db.verify_patient_identity(
        token_data['patient_id'],
        patient_name,
        date_of_birth
    )
    if not verification['success']:
        raise HTTPException(status_code=403, detail=verification['error'])

    patient = db.get_patient(token_data['patient_id'])
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    client_ip = request.client.host if request.client else "unknown"
    db.log_access(token_data['id'], client_ip, patient_name, None)

    scope = token_data['scope']

    records = db.get_patient_records(token_data['patient_id'], categories=scope)

    summary = db.get_summary(token_data['patient_id'])

    chart_data = ingest.extract_chart_data(records)

    return JSONResponse({
        "success": True,
        "patient_name": patient['name'],
        "date_of_birth": patient.get('date_of_birth'),
        "scope": scope,
        "records": records,
        "summary": summary,
        "chart_data": chart_data,
        "disclaimer": DISCLAIMER
    })

@app.get("/api/patient/lookup")
async def lookup_patient(name: str):
    patient = db.get_patient_by_name(name)
    if patient:
        records = db.get_patient_records(patient['id'])
        summary = db.get_summary(patient['id'])
        chart_data = ingest.extract_chart_data(records)
        tokens = db.get_patient_tokens(patient['id'])
        logs = db.get_patient_access_logs(patient['id'])
        
        return JSONResponse({
            "success": True,
            "patient": patient,
            "records": records,
            "summary": summary,
            "chart_data": chart_data,
            "tokens": tokens,
            "access_logs": logs
        })
    
    return JSONResponse({
        "success": False,
        "message": "Patient not found"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
