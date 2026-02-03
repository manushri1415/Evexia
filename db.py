import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_PATH = "app.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            hospital TEXT NOT NULL,
            category TEXT NOT NULL,
            data_json TEXT NOT NULL,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            clinician_summary TEXT,
            patient_summary TEXT,
            anomalies_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            scope_json TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id INTEGER NOT NULL,
            viewer_ip TEXT,
            provider_name TEXT,
            provider_org TEXT,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (token_id) REFERENCES share_tokens(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_patient(name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (name) VALUES (?)", (name,))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def get_patient(patient_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_patient_by_name(name: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_or_create_patient(name: str) -> int:
    patient = get_patient_by_name(name)
    if patient:
        return patient['id']
    return create_patient(name)

def add_record(patient_id: int, hospital: str, category: str, data: Dict, source_file: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO records (patient_id, hospital, category, data_json, source_file) VALUES (?, ?, ?, ?, ?)",
        (patient_id, hospital, category, json.dumps(data), source_file)
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_patient_records(patient_id: int, categories: List[str] = None, hospitals: List[str] = None) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM records WHERE patient_id = ?"
    params = [patient_id]
    
    if categories:
        placeholders = ','.join('?' * len(categories))
        query += f" AND category IN ({placeholders})"
        params.extend(categories)
    
    if hospitals:
        placeholders = ','.join('?' * len(hospitals))
        query += f" AND hospital IN ({placeholders})"
        params.extend(hospitals)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        record = dict(row)
        record['data'] = json.loads(record['data_json'])
        del record['data_json']
        result.append(record)
    return result

def clear_patient_records(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM summaries WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()

def save_summary(patient_id: int, clinician_summary: str, patient_summary: str, anomalies: List[Dict]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM summaries WHERE patient_id = ?", (patient_id,))
    cursor.execute(
        "INSERT INTO summaries (patient_id, clinician_summary, patient_summary, anomalies_json) VALUES (?, ?, ?, ?)",
        (patient_id, clinician_summary, patient_summary, json.dumps(anomalies))
    )
    conn.commit()
    conn.close()

def get_summary(patient_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM summaries WHERE patient_id = ? ORDER BY created_at DESC LIMIT 1", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['anomalies'] = json.loads(result['anomalies_json'])
        del result['anomalies_json']
        return result
    return None

def create_share_token(patient_id: int, token: str, scope: List[str], expires_at: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO share_tokens (patient_id, token, scope_json, expires_at) VALUES (?, ?, ?, ?)",
        (patient_id, token, json.dumps(scope), expires_at)
    )
    token_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return token_id

def get_share_token(token: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM share_tokens WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['scope'] = json.loads(result['scope_json'])
        del result['scope_json']
        return result
    return None

def get_patient_tokens(patient_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM share_tokens WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        token_data = dict(row)
        token_data['scope'] = json.loads(token_data['scope_json'])
        del token_data['scope_json']
        result.append(token_data)
    return result

def log_access(token_id: int, viewer_ip: str, provider_name: str = None, provider_org: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO access_logs (token_id, viewer_ip, provider_name, provider_org) VALUES (?, ?, ?, ?)",
        (token_id, viewer_ip, provider_name, provider_org)
    )

def get_patient_access_logs(patient_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT al.*, st.token, st.scope_json 
        FROM access_logs al
        JOIN share_tokens st ON al.token_id = st.id
        WHERE st.patient_id = ?
        ORDER BY al.accessed_at DESC
    ''', (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        log = dict(row)
        log['scope'] = json.loads(log['scope_json'])
        del log['scope_json']
        result.append(log)
    return result

init_db()
