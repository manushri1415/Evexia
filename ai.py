import json
from typing import Dict, List, Any

try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False
    client = None

DISCLAIMER = "DISCLAIMER: This is informational only, not medical advice. AI summaries may be inaccurate. Always verify with original records and consult your healthcare provider."

def generate_summaries(records: List[Dict]) -> Dict[str, Any]:
    if not records:
        return {
            "clinician_summary": "No medical records available for analysis.",
            "patient_summary": "No medical records have been loaded yet.",
            "anomalies": [],
            "disclaimer": DISCLAIMER
        }
    
    records_text = format_records_for_ai(records)
    
    if AI_AVAILABLE and client:
        try:
            return generate_ai_summaries(records_text, records)
        except Exception as e:
            print(f"AI generation failed, using mock: {e}")
            return generate_mock_summaries(records)
    else:
        return generate_mock_summaries(records)

def format_records_for_ai(records: List[Dict]) -> str:
    formatted = []
    for record in records:
        hospital = record.get('hospital', 'Unknown')
        category = record.get('category', 'Unknown')
        data = record.get('data', {})
        formatted.append(f"Hospital: {hospital}\nCategory: {category}\nData: {json.dumps(data, indent=2)}\n")
    return "\n---\n".join(formatted)

def generate_ai_summaries(records_text: str, records: List[Dict]) -> Dict[str, Any]:
    prompt = f"""You are a medical data analyst. Analyze the following patient medical records from multiple hospitals.

IMPORTANT RULES:
1. You CANNOT delete or exclude any data - only analyze what's provided
2. Flag any anomalies (duplicates, missing dates, outliers) but do not remove them
3. Include a disclaimer that this is not medical advice

Records:
{records_text}

Provide your analysis in the following JSON format:
{{
    "clinician_summary": "Bullet-point clinical summary for healthcare providers with key findings, trends, and concerns",
    "patient_summary": "Plain language explanation for the patient about their health data",
    "anomalies": [
        {{"type": "anomaly type", "description": "description", "severity": "low/medium/high"}}
    ]
}}

Focus on:
- Vital trends (BMI, blood pressure)
- Lab results (cholesterol, A1C, kidney function)
- Medication history and potential interactions
- Any data quality issues or discrepancies between hospitals
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a medical data analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    result = json.loads(content)
    result["disclaimer"] = DISCLAIMER
    return result

def generate_mock_summaries(records: List[Dict]) -> Dict[str, Any]:
    vitals = []
    labs = []
    meds = []
    encounters = []
    
    for record in records:
        category = record.get('category', '').lower()
        data = record.get('data', {})
        hospital = record.get('hospital', 'Unknown')
        
        if category == 'vitals':
            vitals.extend(data.get('entries', []))
        elif category == 'labs':
            labs.extend(data.get('entries', []))
        elif category == 'meds' or category == 'medications':
            meds.extend(data.get('entries', []))
        elif category == 'encounters':
            encounters.extend(data.get('entries', []))
    
    anomalies = []
    
    bmi_values = [v.get('bmi') for v in vitals if v.get('bmi')]
    if bmi_values:
        if any(b > 30 for b in bmi_values):
            anomalies.append({
                "type": "health_flag",
                "description": "BMI above 30 detected, indicating obesity classification",
                "severity": "medium"
            })
        if any(b < 18.5 for b in bmi_values):
            anomalies.append({
                "type": "health_flag", 
                "description": "BMI below 18.5 detected, indicating underweight classification",
                "severity": "medium"
            })
    
    a1c_values = [l.get('a1c') for l in labs if l.get('a1c')]
    if a1c_values:
        if any(a > 6.5 for a in a1c_values):
            anomalies.append({
                "type": "health_flag",
                "description": "A1C above 6.5% detected, may indicate diabetes",
                "severity": "high"
            })
    
    chol_values = [l.get('total_cholesterol') for l in labs if l.get('total_cholesterol')]
    if chol_values:
        if any(c > 240 for c in chol_values):
            anomalies.append({
                "type": "health_flag",
                "description": "Total cholesterol above 240 mg/dL detected (high)",
                "severity": "medium"
            })
    
    dates_seen = {}
    for record in records:
        data = record.get('data', {})
        for entry in data.get('entries', []):
            date = entry.get('date')
            if date:
                key = (record.get('category'), date)
                if key in dates_seen:
                    anomalies.append({
                        "type": "duplicate",
                        "description": f"Duplicate entry found for {record.get('category')} on {date}",
                        "severity": "low"
                    })
                dates_seen[key] = True
    
    clinician_bullets = []
    if vitals:
        latest_bp = next((v for v in reversed(vitals) if v.get('blood_pressure')), None)
        latest_bmi = next((v for v in reversed(vitals) if v.get('bmi')), None)
        if latest_bp:
            clinician_bullets.append(f"Latest BP: {latest_bp.get('blood_pressure')}")
        if latest_bmi:
            clinician_bullets.append(f"Latest BMI: {latest_bmi.get('bmi')}")
    
    if labs:
        latest_a1c = next((l for l in reversed(labs) if l.get('a1c')), None)
        latest_chol = next((l for l in reversed(labs) if l.get('total_cholesterol')), None)
        if latest_a1c:
            clinician_bullets.append(f"Latest A1C: {latest_a1c.get('a1c')}%")
        if latest_chol:
            clinician_bullets.append(f"Latest Total Cholesterol: {latest_chol.get('total_cholesterol')} mg/dL")
    
    if meds:
        med_names = list(set(m.get('medication', m.get('name', 'Unknown')) for m in meds))
        clinician_bullets.append(f"Current medications: {', '.join(med_names[:5])}")
    
    if encounters:
        clinician_bullets.append(f"Total encounters on file: {len(encounters)}")
    
    if anomalies:
        high_sev = sum(1 for a in anomalies if a['severity'] == 'high')
        if high_sev:
            clinician_bullets.append(f"ALERT: {high_sev} high-severity anomaly/anomalies detected")
    
    clinician_summary = "\n".join([f"• {b}" for b in clinician_bullets]) if clinician_bullets else "No significant clinical findings."
    
    patient_parts = []
    if vitals:
        patient_parts.append("Your vital signs have been recorded from your hospital visits.")
    if labs:
        patient_parts.append("Lab results including blood sugar and cholesterol tests are on file.")
    if meds:
        patient_parts.append(f"Your medication history shows {len(meds)} medication entries.")
    if encounters:
        patient_parts.append(f"We have records of {len(encounters)} healthcare visits.")
    
    if anomalies:
        patient_parts.append(f"Note: {len(anomalies)} item(s) were flagged for review by your healthcare provider.")
    
    patient_summary = " ".join(patient_parts) if patient_parts else "No medical records have been analyzed yet."
    
    return {
        "clinician_summary": clinician_summary,
        "patient_summary": patient_summary,
        "anomalies": anomalies,
        "disclaimer": DISCLAIMER
    }
