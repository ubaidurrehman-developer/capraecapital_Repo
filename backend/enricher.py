from typing import Dict, Any, List
import re

INDUSTRY_PATTERNS = {
    "B2B SaaS": [r"saas", r"software", r"platform", r"cloud", r"automation", r"api", r"workflow", r"crm"],
    "Logistics & Supply Chain": [r"freight", r"logistics", r"fleet", r"warehouse", r"transport", r"shipping", r"supply chain"],
    "Field Services & Industrial": [r"contractor", r"hvac", r"field service", r"plumbing", r"facility", r"manufacturing", r"equipment"],
    "HealthTech": [r"healthcare", r"clinical", r"patient", r"medical", r"telehealth", r"ehr", r"pharma"],
    "FinTech & InsurTech": [r"payment", r"banking", r"insurance", r"wealth", r"credit", r"accounting", r"invoicing"],
    "GovTech & Compliance": [r"compliance", r"security", r"audit", r"government", r"regulatory", r"certifications"]
}

def classify_industry(text: str) -> str:
    text_lower = text.lower()
    for ind, patterns in INDUSTRY_PATTERNS.items():
        for pat in patterns:
            if re.search(r'\b' + pat + r'\b', text_lower):
                return ind
    return "B2B Software"

def calculate_icp_score(company_data: Dict[str, Any]) -> int:
    score = 65  # Base score
    
    desc = (company_data.get("description") or "").lower()
    title = (company_data.get("title") or "").lower()
    tech = company_data.get("tech_stack") or []
    full_text = f"{desc} {title}"

    # Positive B2B signals
    if any(k in full_text for k in ["b2b", "enterprise", "business", "solution", "teams", "platform"]):
        score += 10
    if any(k in full_text for k in ["subscription", "pricing", "demo", "free trial", "customers"]):
        score += 8
    
    # Modern tech stack signals
    if any(t in tech for t in ["React", "Next.js", "Stripe", "HubSpot", "Segment"]):
        score += 7
    if "Cloudflare" in tech or "AWS" in tech:
        score += 3
        
    # Valid contact details presence
    if company_data.get("contact_email"):
        score += 5
    if company_data.get("linkedin_url"):
        score += 4

    # Cap between 45 and 98
    return min(98, max(45, score))

def detect_acquisition_signals(company_data: Dict[str, Any]) -> List[str]:
    signals = []
    text = (company_data.get("description") or "") + " " + (company_data.get("raw_text") or "")
    text_lower = text.lower()
    tech = company_data.get("tech_stack") or []

    if "WordPress" in tech or "Webflow" in tech:
        signals.append("High ROI on Modern Web App Re-architecture")
    elif "React" in tech or "Next.js" in tech:
        signals.append("Strong Modern Tech Foundation for AI Add-ons")

    if any(k in text_lower for k in ["pricing", "plans", "tier", "quote"]):
        signals.append("Expansion Potential in Multi-Tier Enterprise Pricing")
    else:
        signals.append("Opportunity for Monetization & Packaging Optimization")

    if any(k in text_lower for k in ["manual", "team", "support", "services", "custom"]):
        signals.append("High Potential for Post-Acquisition AI Operations Streamlining")
        
    if not signals:
        signals = [
            "Attractive Recurring B2B Profile",
            "Prime Candidate for 7-Year M&A-as-a-Service Value Creation",
            "High Potential for Post-Acquisition AI Operations Streamlining"
        ]
    return signals[:3]

def generate_ai_summary(company_name: str, industry: str, description: str, tech: List[str]) -> str:
    tech_str = ", ".join(tech[:3]) if tech else "modern web technologies"
    desc_clean = description[:160].strip() if description else "a tailored B2B service platform"
    return f"{company_name} is a {industry} platform leveraging {tech_str}. Strategic fit for acquisition or partnership: {desc_clean}"

def enrich_scraped_data(scraped: Dict[str, Any]) -> Dict[str, Any]:
    text_corpus = f"{scraped.get('title', '')} {scraped.get('description', '')} {scraped.get('company_name', '')}"
    industry = classify_industry(text_corpus)
    icp_score = calculate_icp_score(scraped)
    signals = detect_acquisition_signals(scraped)
    summary = generate_ai_summary(scraped["company_name"], industry, scraped.get("description", ""), scraped.get("tech_stack", []))

    return {
        **scraped,
        "industry": industry,
        "location": "United States",
        "estimated_revenue": "$2M - $6M ARR",
        "employee_count": "15-45 employees",
        "icp_score": icp_score,
        "acquisition_signals": signals,
        "ai_summary": summary
    }

def generate_outreach_email(lead: Dict[str, Any], outreach_type: str = "pe_acquisition", custom_angle: str = None) -> Dict[str, Any]:
    company = lead.get("company_name", "your company")
    industry = lead.get("industry", "B2B")
    tech_lead = lead.get("tech_stack", ["modern software"])[0] if lead.get("tech_stack") else "software"
    custom_part = f" In particular, our team noted: '{custom_angle}'." if custom_angle else ""

    if outreach_type == "pe_acquisition":
        subject = f"Strategic inquiry regarding {company} - Caprae Capital Partners"
        body = f"""Hi {company} Leadership Team,

I came across {company} while researching innovative leaders in the {industry} sector. We were impressed by your platform and current footprint across {tech_lead}.{custom_part}

At Caprae Capital, we operate differently than traditional private equity firms. We are founder-operators first, partnering with niche market leaders on a multi-year horizon to inject hands-on AI operational systems and software scalability—not financial engineering.

Given your market standing and growth indicators, I would value a brief 10-minute introductory conversation to learn more about your long-term goals and explore whether there is potential for a strategic partnership or founder recapitalization.

Are you available for a brief call this Thursday or Friday?

Best regards,

Investment & Partnerships Team
Caprae Capital Partners
https://capraecapital.com"""
        talking_points = [
            f"Acknowledge their stronghold in {industry}",
            "Highlight Caprae's operator-first / #BleedandBuild approach vs traditional Wall Street PE",
            "Focus on 7-year AI modernization & MaaS (M&A as a Service) value creation"
        ]
        follow_up_days = 4

    elif outreach_type == "founder_to_founder":
        subject = f"Connecting founder-to-founder / {company}"
        body = f"""Hi {company} Team,

I've been following {company}'s trajectory in {industry}. The way you've scaled your product experience is remarkable.{custom_part}

As fellow operators, we love connecting with entrepreneurs building durable software businesses. We frequently share operational blueprints around automated lead generation, sales efficiency, and AI workflows.

Would you be open to a casual 15-minute founder exchange next week to swap notes on what’s working in {industry}?

Cheers,

Principal Operator
Caprae Capital"""
        talking_points = [
            "Peer-level respect and operational curiosity",
            "Zero pressure exchange on go-to-market and AI automation",
            "Open-ended relationship building"
        ]
        follow_up_days = 5

    else:  # saas_growth
        subject = f"Accelerating outbound & AI efficiency for {company}"
        body = f"""Hi {company} Team,

We conducted a preliminary analysis of your public web presence and tech stack ({tech_lead}). We identified a few immediate operational levers where AI lead intelligence could double outbound response rates in {industry}.{custom_part}

We built our proprietary tool SaaSquatch to automate this exact workflow for our portfolio companies.

Would you like me to send over a 2-minute custom teardown with 3 actionable lead-sourcing signals we pulled for {company}?

Best,

Growth Team
Caprae Capital Partners"""
        talking_points = [
            f"Specific reference to their {tech_lead} setup",
            "Offer immediate value with zero upfront commitment",
            "Demonstrate SaaSquatch AI lead intelligence capabilities"
        ]
        follow_up_days = 3

    return {
        "subject": subject,
        "body": body,
        "key_talking_points": talking_points,
        "suggested_follow_up_days": follow_up_days
    }
