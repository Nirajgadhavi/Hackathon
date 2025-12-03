import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = "pa_copilot.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id TEXT PRIMARY KEY,
                drug_name TEXT NOT NULL,
                indication TEXT NOT NULL,
                description TEXT,
                criteria TEXT NOT NULL,
                guidelines TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                policy_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                extracted_data TEXT,
                criteria_evaluation TEXT,
                ai_recommendation TEXT,
                provider_letter TEXT,
                member_letter TEXT,
                final_decision TEXT,
                final_decision_notes TEXT,
                complexity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                decided_at TIMESTAMP,
                turnaround_minutes INTEGER,
                FOREIGN KEY (policy_id) REFERENCES policies(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        ''')
        
        conn.commit()

def get_all_policies() -> List[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM policies")
        rows = cursor.fetchall()
        policies = []
        for row in rows:
            policy = dict(row)
            policy['criteria'] = json.loads(policy['criteria'])
            policy['guidelines'] = json.loads(policy['guidelines'])
            policies.append(policy)
        return policies

def get_policy(policy_id: str) -> Optional[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
        row = cursor.fetchone()
        if row:
            policy = dict(row)
            policy['criteria'] = json.loads(policy['criteria'])
            policy['guidelines'] = json.loads(policy['guidelines'])
            return policy
        return None

def insert_policy(policy: Dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO policies (id, drug_name, indication, description, criteria, guidelines)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            policy['id'],
            policy['drug_name'],
            policy['indication'],
            policy.get('description', ''),
            json.dumps(policy['criteria']),
            json.dumps(policy['guidelines'])
        ))
        conn.commit()

def get_all_cases() -> List[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, p.drug_name, p.indication 
            FROM cases c 
            LEFT JOIN policies p ON c.policy_id = p.id 
            ORDER BY c.created_at DESC
        ''')
        rows = cursor.fetchall()
        cases = []
        for row in rows:
            case = dict(row)
            for field in ['extracted_data', 'criteria_evaluation', 'ai_recommendation']:
                if case.get(field):
                    try:
                        case[field] = json.loads(case[field])
                    except:
                        pass
            cases.append(case)
        return cases

def get_case(case_id: str) -> Optional[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, p.drug_name, p.indication, p.description as policy_description,
                   p.criteria as policy_criteria, p.guidelines as policy_guidelines
            FROM cases c 
            LEFT JOIN policies p ON c.policy_id = p.id 
            WHERE c.id = ?
        ''', (case_id,))
        row = cursor.fetchone()
        if row:
            case = dict(row)
            for field in ['extracted_data', 'criteria_evaluation', 'ai_recommendation', 'policy_criteria', 'policy_guidelines']:
                if case.get(field):
                    try:
                        case[field] = json.loads(case[field])
                    except:
                        pass
            return case
        return None

def insert_case(case: Dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cases (id, title, raw_text, policy_id, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            case['id'],
            case['title'],
            case['raw_text'],
            case['policy_id'],
            case.get('status', 'pending')
        ))
        conn.commit()

def update_case(case_id: str, updates: Dict):
    with get_db() as conn:
        cursor = conn.cursor()
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            else:
                values.append(value)
        values.append(case_id)
        
        query = f"UPDATE cases SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()

def add_audit_log(case_id: str, action: str, details: Optional[str] = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (case_id, action, details)
            VALUES (?, ?, ?)
        ''', (case_id, action, details))
        conn.commit()

def get_case_audit_logs(case_id: str) -> List[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM audit_logs WHERE case_id = ? ORDER BY timestamp DESC
        ''', (case_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_metrics() -> Dict:
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'pending'")
        pending_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'processed'")
        processed_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'decided'")
        decided_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(turnaround_minutes) FROM cases WHERE turnaround_minutes IS NOT NULL")
        avg_turnaround = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT final_decision, COUNT(*) FROM cases WHERE final_decision IS NOT NULL GROUP BY final_decision")
        decisions = dict(cursor.fetchall())
        
        cursor.execute("SELECT complexity, COUNT(*) FROM cases WHERE complexity IS NOT NULL GROUP BY complexity")
        complexity_dist = dict(cursor.fetchall())
        
        return {
            'total_cases': total_cases,
            'pending_cases': pending_cases,
            'processed_cases': processed_cases,
            'decided_cases': decided_cases,
            'avg_turnaround_minutes': round(avg_turnaround, 1),
            'decisions': decisions,
            'complexity_distribution': complexity_dist
        }
