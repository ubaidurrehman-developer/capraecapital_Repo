import os
import io
import csv
import re
from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from backend.models import (
    Lead, LeadUpdate, ScrapeRequest, OutreachRequest, OutreachResponse, StatsResponse
)
from backend.database import (
    init_db, get_all_leads, get_lead_by_id, insert_or_update_lead,
    get_stats, delete_lead, update_lead_metadata
)
from backend.scraper import scrape_domain_metadata, is_safe_target_domain, clean_domain
from backend.enricher import enrich_scraped_data, generate_outreach_email

# Initialize DB on startup
init_db()

app = FastAPI(
    title="SaaSquatch Next - Caprae Capital AI Lead Generation Platform",
    description="Production-grade AI Lead Sourcing, Scraping, and M&A Qualification Engine",
    version="2.0.0"
)

# CORS Policy: Safe wildcard configuration without credential exposure
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; "
        "img-src 'self' data: https:;"
    )
    return response

def sanitize_csv_cell(val: Any) -> Any:
    """Neutralize CSV formula injection attacks (CWE-1236)."""
    if isinstance(val, str):
        if val.startswith(("=", "+", "-", "@", "\t", "\r")):
            return f"'{val}"
    return val

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/api/stats", response_model=StatsResponse)
def get_dashboard_stats():
    return get_stats()

@app.get("/api/leads")
def list_leads(
    query: Optional[str] = None,
    industry: Optional[str] = None,
    min_icp: Optional[int] = Query(None, ge=0, le=100),
    verification_status: Optional[str] = None,
    sort_by: str = Query("icp_score", pattern="^(icp_score|created_at|company_name)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc|ASC|DESC)$")
):
    leads = get_all_leads(
        query=query,
        industry=industry,
        min_icp=min_icp,
        verification_status=verification_status,
        sort_by=sort_by,
        sort_dir=sort_dir
    )
    return {"leads": leads, "count": len(leads)}

@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/api/leads/scrape")
def scrape_and_save_lead(req: ScrapeRequest):
    raw_input = req.url_or_domain.strip() if req.url_or_domain else ""
    if not raw_input or len(raw_input) < 3:
        raise HTTPException(status_code=400, detail="Invalid domain or URL")

    target_domain = clean_domain(raw_input)
    # Validate domain structure (anti-malformed input)
    if not re.match(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$', target_domain):
        raise HTTPException(status_code=400, detail="Invalid domain format. Enter a valid domain (e.g. company.com).")

    # Anti-SSRF check before network dispatch
    if not is_safe_target_domain(target_domain):
        raise HTTPException(status_code=400, detail="Security restriction: Private and loopback addresses cannot be queried.")

    # 1. Scrape metadata & contacts
    scraped = scrape_domain_metadata(target_domain)

    # 2. AI Enrichment & ICP scoring
    if req.auto_enrich:
        final_data = enrich_scraped_data(scraped)
    else:
        final_data = scraped

    # 3. Save to database with deduplication on domain
    saved = insert_or_update_lead(final_data)
    return {
        "status": "success",
        "message": f"Successfully processed and stored {saved.get('domain')}",
        "lead": saved
    }

@app.post("/api/leads/{lead_id}/enrich")
def re_enrich_lead(lead_id: int):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    enriched = enrich_scraped_data(lead)
    saved = insert_or_update_lead(enriched)
    return {"status": "success", "lead": saved}

@app.post("/api/leads/{lead_id}/outreach", response_model=OutreachResponse)
def create_outreach_email(lead_id: int, req: OutreachRequest):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    result = generate_outreach_email(
        lead=lead,
        outreach_type=req.outreach_type,
        custom_angle=req.custom_angle
    )
    return result

@app.patch("/api/leads/{lead_id}")
def update_lead(lead_id: int, req: LeadUpdate):
    lead = update_lead_metadata(lead_id, pipeline_stage=req.pipeline_stage, notes=req.notes)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success", "lead": lead}

@app.delete("/api/leads/{lead_id}")
def remove_lead(lead_id: int):
    success = delete_lead(lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "deleted", "id": lead_id}

@app.get("/api/export/csv")
def export_csv(
    query: Optional[str] = None,
    industry: Optional[str] = None,
    min_icp: Optional[int] = None
):
    leads = get_all_leads(query=query, industry=industry, min_icp=min_icp)
    output = io.StringIO()
    fieldnames = [
        "id", "domain", "company_name", "industry", "location",
        "estimated_revenue", "employee_count", "icp_score", "verification_status",
        "contact_email", "phone", "linkedin_url", "ai_summary"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for lead in leads:
        # Sanitize cells to prevent CSV formula injection (CWE-1236)
        safe_row = {k: sanitize_csv_cell(v) for k, v in lead.items()}
        writer.writerow(safe_row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=saasquatch_leads_export.csv"}
    )

@app.get("/api/export/json")
def export_json(
    query: Optional[str] = None,
    industry: Optional[str] = None,
    min_icp: Optional[int] = None
):
    leads = get_all_leads(query=query, industry=industry, min_icp=min_icp)
    return leads

# Mount static frontend
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.api_route("/", methods=["GET", "HEAD"])
    def serve_home():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.api_route("/styles.css", methods=["GET", "HEAD"])
    def serve_css():
        return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"), media_type="text/css")

    @app.api_route("/app.js", methods=["GET", "HEAD"])
    def serve_js():
        return FileResponse(os.path.join(FRONTEND_DIR, "app.js"), media_type="application/javascript")
