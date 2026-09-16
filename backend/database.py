import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leads.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")  # High concurrency
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            company_name TEXT NOT NULL,
            title TEXT,
            description TEXT,
            industry TEXT DEFAULT 'Software',
            location TEXT DEFAULT 'United States',
            estimated_revenue TEXT DEFAULT '$1M - $5M',
            employee_count TEXT DEFAULT '11-50',
            icp_score INTEGER DEFAULT 75,
            verification_status TEXT DEFAULT 'verified',
            tech_stack TEXT DEFAULT '[]',
            contact_email TEXT,
            phone TEXT,
            linkedin_url TEXT,
            twitter_url TEXT,
            ai_summary TEXT,
            acquisition_signals TEXT DEFAULT '[]',
            pipeline_stage TEXT DEFAULT 'New Target',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("PRAGMA table_info(leads);")
    existing_cols = {col["name"] for col in cursor.fetchall()}
    if "pipeline_stage" not in existing_cols:
        cursor.execute("ALTER TABLE leads ADD COLUMN pipeline_stage TEXT DEFAULT 'New Target';")
    if "notes" not in existing_cols:
        cursor.execute("ALTER TABLE leads ADD COLUMN notes TEXT DEFAULT '';")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_domain ON leads(domain);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_icp_score ON leads(icp_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_industry ON leads(industry);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(verification_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_stage ON leads(pipeline_stage);")
    conn.commit()
    conn.close()

def parse_lead_row(row: sqlite3.Row) -> Dict[str, Any]:
    item = dict(row)
    try:
        item["tech_stack"] = json.loads(item.get("tech_stack") or "[]")
    except Exception:
        item["tech_stack"] = []
    try:
        item["acquisition_signals"] = json.loads(item.get("acquisition_signals") or "[]")
    except Exception:
        item["acquisition_signals"] = []
    return item

def get_all_leads(
    query: Optional[str] = None,
    industry: Optional[str] = None,
    min_icp: Optional[int] = None,
    verification_status: Optional[str] = None,
    sort_by: str = "icp_score",
    sort_dir: str = "desc"
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if query:
        conditions.append("(company_name LIKE ? OR domain LIKE ? OR description LIKE ?)")
        search_pattern = f"%{query.strip()}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if industry and industry.lower() != "all":
        conditions.append("industry = ?")
        params.append(industry)

    if min_icp is not None and min_icp > 0:
        conditions.append("icp_score >= ?")
        params.append(min_icp)

    if verification_status and verification_status.lower() != "all":
        conditions.append("verification_status = ?")
        params.append(verification_status)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    valid_sorts = {
        "icp_score": "icp_score",
        "created_at": "created_at",
        "company_name": "company_name"
    }
    # Enforce strict allowlist to guarantee injection safety
    order_column = valid_sorts.get(sort_by, "icp_score")
    order_direction = "ASC" if str(sort_dir).strip().lower() == "asc" else "DESC"

    sql = f"SELECT * FROM leads{where_clause} ORDER BY {order_column} {order_direction}"  # nosec B608
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    leads = [parse_lead_row(r) for r in rows]
    conn.close()
    return leads

def get_lead_by_id(lead_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    return parse_lead_row(row) if row else None

def get_lead_by_domain(domain: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_domain = domain.lower().replace("https://", "").replace("http://", "").strip().strip("/")
    cursor.execute("SELECT * FROM leads WHERE domain = ?", (clean_domain,))
    row = cursor.fetchone()
    conn.close()
    return parse_lead_row(row) if row else None

def insert_or_update_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    domain = lead_data["domain"].lower().replace("https://", "").replace("http://", "").strip().strip("/")
    tech_stack_json = json.dumps(lead_data.get("tech_stack", []))
    signals_json = json.dumps(lead_data.get("acquisition_signals", []))

    cursor.execute("""
        INSERT INTO leads (
            domain, company_name, title, description, industry, location,
            estimated_revenue, employee_count, icp_score, verification_status,
            tech_stack, contact_email, phone, linkedin_url, twitter_url,
            ai_summary, acquisition_signals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(domain) DO UPDATE SET
            company_name = excluded.company_name,
            title = excluded.title,
            description = excluded.description,
            industry = excluded.industry,
            location = excluded.location,
            estimated_revenue = excluded.estimated_revenue,
            employee_count = excluded.employee_count,
            icp_score = excluded.icp_score,
            verification_status = excluded.verification_status,
            tech_stack = excluded.tech_stack,
            contact_email = excluded.contact_email,
            phone = excluded.phone,
            linkedin_url = excluded.linkedin_url,
            twitter_url = excluded.twitter_url,
            ai_summary = excluded.ai_summary,
            acquisition_signals = excluded.acquisition_signals;
    """, (
        domain,
        lead_data.get("company_name", domain.capitalize()),
        lead_data.get("title", ""),
        lead_data.get("description", ""),
        lead_data.get("industry", "Software"),
        lead_data.get("location", "United States"),
        lead_data.get("estimated_revenue", "$1M - $5M"),
        lead_data.get("employee_count", "11-50"),
        lead_data.get("icp_score", 75),
        lead_data.get("verification_status", "verified"),
        tech_stack_json,
        lead_data.get("contact_email"),
        lead_data.get("phone"),
        lead_data.get("linkedin_url"),
        lead_data.get("twitter_url"),
        lead_data.get("ai_summary"),
        signals_json
    ))
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    return get_lead_by_domain(domain) or {"id": lead_id, **lead_data}

def get_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM leads WHERE verification_status = 'verified'")
    verified = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(icp_score) FROM leads")
    avg_score = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT COUNT(*) FROM leads WHERE icp_score >= 80")
    high_priority = cursor.fetchone()[0] or 0

    cursor.execute("SELECT industry, COUNT(*) as cnt FROM leads GROUP BY industry ORDER BY cnt DESC LIMIT 5")
    ind_rows = cursor.fetchall()
    top_industries = {r["industry"]: r["cnt"] for r in ind_rows}

    conn.close()
    return {
        "total_leads": total,
        "verified_leads": verified,
        "avg_icp_score": round(float(avg_score), 1),
        "high_priority_targets": high_priority,
        "top_industries": top_industries
    }

def update_lead_metadata(lead_id: int, pipeline_stage: Optional[str] = None, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if pipeline_stage is not None:
        updates.append("pipeline_stage = ?")
        params.append(pipeline_stage)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if not updates:
        conn.close()
        return get_lead_by_id(lead_id)

    params.append(lead_id)
    # Target columns are exclusively static literal parameters ("pipeline_stage = ?", "notes = ?")
    sql = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"  # nosec B608
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return get_lead_by_id(lead_id)

def delete_lead(lead_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
