from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LeadBase(BaseModel):
    domain: str
    company_name: str
    title: Optional[str] = None
    description: Optional[str] = None
    industry: str = "Technology"
    location: Optional[str] = "United States"
    estimated_revenue: Optional[str] = "$1M - $5M"
    employee_count: Optional[str] = "11-50"
    icp_score: int = Field(default=75, ge=0, le=100)
    verification_status: str = "verified"  # verified, unverified, risky
    tech_stack: List[str] = Field(default_factory=list)
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    ai_summary: Optional[str] = None
    acquisition_signals: List[str] = Field(default_factory=list)

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    pipeline_stage: Optional[str] = None
    notes: Optional[str] = None

class Lead(LeadBase):
    id: int
    pipeline_stage: Optional[str] = "New Target"
    notes: Optional[str] = ""
    created_at: str

class ScrapeRequest(BaseModel):
    url_or_domain: str
    auto_enrich: bool = True

class OutreachRequest(BaseModel):
    lead_id: int
    outreach_type: str = "pe_acquisition"  # pe_acquisition, founder_to_founder, saas_growth
    custom_angle: Optional[str] = None

class OutreachResponse(BaseModel):
    subject: str
    body: str
    key_talking_points: List[str]
    suggested_follow_up_days: int

class StatsResponse(BaseModel):
    total_leads: int
    verified_leads: int
    avg_icp_score: float
    high_priority_targets: int
    top_industries: Dict[str, int]
