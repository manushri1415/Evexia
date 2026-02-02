import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

SAMPLE_DATA_DIR = "sample_data"
UPLOADS_DIR = "uploads"

VALID_CATEGORIES = ["vitals", "labs", "meds", "medications", "encounters"]
VALID_HOSPITALS = ["Hospital A", "Hospital B", "Hospital C"]

def load_sample_data(hospitals: List[str] = None, categories: List[str] = None) -> List[Dict]:
    if hospitals is None:
        hospitals = VALID_HOSPITALS
    
    if categories is None:
        categories = VALID_CATEGORIES
    
    records = []
    
    if not os.path.exists(SAMPLE_DATA_DIR):
        return records
    
    for filename in os.listdir(SAMPLE_DATA_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(SAMPLE_DATA_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            hospital = data.get('hospital', 'Unknown')
            if hospital not in hospitals:
                continue
            
            for category, category_data in data.get('records', {}).items():
                if category.lower() in [c.lower() for c in categories]:
                    normalized = normalize_record(hospital, category, category_data, filename)
                    records.append(normalized)
        
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            continue
    
    return records

def parse_uploaded_json(content: bytes, filename: str) -> Tuple[List[Dict], List[str]]:
    errors = []
    records = []
    
    try:
        data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {e}")
        return records, errors
    
    if not isinstance(data, dict):
        errors.append("JSON must be an object with 'hospital' and 'records' fields")
        return records, errors
    
    hospital = data.get('hospital', 'Unknown Hospital')
    
    if 'records' not in data:
        errors.append("Missing 'records' field in JSON")
        return records, errors
    
    for category, category_data in data.get('records', {}).items():
        normalized = normalize_record(hospital, category, category_data, filename)
        records.append(normalized)
    
    return records, errors

def normalize_record(hospital: str, category: str, data: Any, source_file: str) -> Dict:
    normalized_category = category.lower()
    if normalized_category == "medications":
        normalized_category = "meds"
    
    entries = []
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        if 'entries' in data:
            entries = data['entries']
        else:
            entries = [data]
    
    normalized_entries = []
    for entry in entries:
        normalized_entry = normalize_entry(entry, normalized_category)
        normalized_entries.append(normalized_entry)
    
    return {
        "hospital": hospital,
        "category": normalized_category,
        "data": {"entries": normalized_entries},
        "source_file": source_file
    }

def normalize_entry(entry: Dict, category: str) -> Dict:
    normalized = dict(entry)
    
    date_fields = ['date', 'recorded_date', 'test_date', 'encounter_date', 'start_date']
    for field in date_fields:
        if field in entry and field != 'date':
            normalized['date'] = entry[field]
            break
    
    if category == 'vitals':
        if 'weight_lbs' in entry and 'height_inches' in entry and 'bmi' not in entry:
            weight = entry['weight_lbs']
            height = entry['height_inches']
            if height > 0:
                normalized['bmi'] = round((weight / (height ** 2)) * 703, 1)
    
    if category == 'labs':
        if 'hemoglobin_a1c' in entry:
            normalized['a1c'] = entry['hemoglobin_a1c']
        if 'cholesterol_total' in entry:
            normalized['total_cholesterol'] = entry['cholesterol_total']
    
    return normalized

def detect_anomalies(records: List[Dict]) -> List[Dict]:
    anomalies = []
    
    seen_entries = {}
    for record in records:
        category = record.get('category')
        hospital = record.get('hospital')
        
        for entry in record.get('data', {}).get('entries', []):
            date = entry.get('date')
            
            if date:
                key = (category, date, hospital)
                if key in seen_entries:
                    anomalies.append({
                        "type": "duplicate",
                        "description": f"Duplicate {category} entry from {hospital} on {date}",
                        "severity": "low",
                        "record": entry
                    })
                seen_entries[key] = entry
    
    for record in records:
        category = record.get('category')
        
        for entry in record.get('data', {}).get('entries', []):
            if 'date' not in entry or not entry.get('date'):
                anomalies.append({
                    "type": "missing_date",
                    "description": f"Missing date in {category} record from {record.get('hospital')}",
                    "severity": "medium",
                    "record": entry
                })
    
    for record in records:
        category = record.get('category')
        hospital = record.get('hospital')
        
        for entry in record.get('data', {}).get('entries', []):
            if category == 'vitals':
                bmi = entry.get('bmi')
                if bmi and (bmi < 10 or bmi > 60):
                    anomalies.append({
                        "type": "outlier",
                        "description": f"Unusual BMI value ({bmi}) from {hospital}",
                        "severity": "high",
                        "record": entry
                    })
                
                bp = entry.get('blood_pressure', '')
                if bp:
                    try:
                        systolic = int(bp.split('/')[0])
                        if systolic > 200 or systolic < 70:
                            anomalies.append({
                                "type": "outlier",
                                "description": f"Unusual blood pressure ({bp}) from {hospital}",
                                "severity": "high",
                                "record": entry
                            })
                    except (ValueError, IndexError):
                        pass
            
            elif category == 'labs':
                a1c = entry.get('a1c')
                if a1c and (a1c < 3 or a1c > 15):
                    anomalies.append({
                        "type": "outlier",
                        "description": f"Unusual A1C value ({a1c}%) from {hospital}",
                        "severity": "high",
                        "record": entry
                    })
                
                chol = entry.get('total_cholesterol')
                if chol and (chol < 50 or chol > 500):
                    anomalies.append({
                        "type": "outlier",
                        "description": f"Unusual cholesterol value ({chol} mg/dL) from {hospital}",
                        "severity": "high",
                        "record": entry
                    })
    
    return anomalies

def extract_chart_data(records: List[Dict]) -> Dict[str, List]:
    chart_data = {
        "bmi": [],
        "cholesterol": [],
        "a1c": []
    }
    
    for record in records:
        category = record.get('category')
        
        for entry in record.get('data', {}).get('entries', []):
            date = entry.get('date', 'Unknown')
            
            if category == 'vitals' and entry.get('bmi'):
                chart_data['bmi'].append({
                    "date": date,
                    "value": entry['bmi'],
                    "hospital": record.get('hospital')
                })
            
            elif category == 'labs':
                if entry.get('total_cholesterol'):
                    chart_data['cholesterol'].append({
                        "date": date,
                        "value": entry['total_cholesterol'],
                        "hospital": record.get('hospital')
                    })
                
                if entry.get('a1c'):
                    chart_data['a1c'].append({
                        "date": date,
                        "value": entry['a1c'],
                        "hospital": record.get('hospital')
                    })
    
    for key in chart_data:
        chart_data[key].sort(key=lambda x: x.get('date', ''))
    
    return chart_data

def save_uploaded_file(content: bytes, filename: str) -> str:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(UPLOADS_DIR, safe_filename)
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    return filepath
