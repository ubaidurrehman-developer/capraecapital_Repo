import json
import csv
import os
import sys

# Add parent directory to path so we can import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import init_db, insert_or_update_lead

SEED_LEADS = [
    {
        "domain": "freightpulse.io",
        "company_name": "FreightPulse Technologies",
        "title": "FreightPulse | Next-Gen Dispatch & Fleet Telematics Platform",
        "description": "FreightPulse provides mid-market carrier fleets with real-time dispatch, route optimization, and electronic logging compliance in one unified cloud system.",
        "industry": "Logistics & Supply Chain",
        "location": "Dallas, TX, United States",
        "estimated_revenue": "$4.2M ARR",
        "employee_count": "28 employees",
        "icp_score": 94,
        "verification_status": "verified",
        "tech_stack": ["React", "Next.js", "Cloudflare", "Stripe", "AWS", "Google Analytics"],
        "contact_email": "partnerships@freightpulse.io",
        "phone": "+1 (214) 555-0192",
        "linkedin_url": "https://linkedin.com/company/freightpulse",
        "twitter_url": "https://twitter.com/freightpulse",
        "ai_summary": "FreightPulse is a Logistics SaaS platform generating ~$4.2M ARR with high gross margins. Strong fit for Caprae Capital 7-year M&A post-acquisition AI optimization.",
        "acquisition_signals": [
            "Sticky mid-market freight contracts with 96% net revenue retention",
            "High upside in automating broker communications via AI voice/text",
            "Prime candidate for expansion into enterprise brokerage tiers"
        ]
    },
    {
        "domain": "hvaccommander.com",
        "company_name": "HVAC Commander",
        "title": "HVAC Commander | Field Service & Dispatch Software for Contractors",
        "description": "All-in-one dispatching, invoicing, GPS tracking, and equipment history software designed specifically for commercial HVAC and refrigeration contractors.",
        "industry": "Field Services & Industrial",
        "location": "Columbus, OH, United States",
        "estimated_revenue": "$2.8M ARR",
        "employee_count": "18 employees",
        "icp_score": 91,
        "verification_status": "verified",
        "tech_stack": ["Vue.js", "Stripe", "AWS", "Segment", "Intercom"],
        "contact_email": "sales@hvaccommander.com",
        "phone": "+1 (614) 555-0814",
        "linkedin_url": "https://linkedin.com/company/hvac-commander",
        "twitter_url": "https://twitter.com/hvaccommander",
        "ai_summary": "HVAC Commander dominates regional commercial HVAC dispatch with steady recurring subscription cashflow. Ripe for AI predictive maintenance add-ons.",
        "acquisition_signals": [
            "Low churn niche B2B market with founder bottleneck in sales",
            "High ROI on implementing automated lead nurturing and digital quotes",
            "Opportunity to modernize backend into modern serverless architecture"
        ]
    },
    {
        "domain": "mediroute.tech",
        "company_name": "MediRoute Health",
        "title": "MediRoute | Non-Emergency Medical Transportation Dispatch ERP",
        "description": "Cloud-native dispatching and Medicaid billing platform for NEMT fleet providers, healthcare systems, and private patient transport networks.",
        "industry": "HealthTech",
        "location": "Atlanta, GA, United States",
        "estimated_revenue": "$3.6M ARR",
        "employee_count": "24 employees",
        "icp_score": 89,
        "verification_status": "verified",
        "tech_stack": ["React", "Next.js", "HubSpot", "Cloudflare", "Stripe"],
        "contact_email": "info@mediroute.tech",
        "phone": "+1 (404) 555-0371",
        "linkedin_url": "https://linkedin.com/company/mediroute-tech",
        "twitter_url": "https://twitter.com/mediroute",
        "ai_summary": "MediRoute delivers specialized compliance and dispatching for Medicaid transport. High regulatory moat with stable enterprise contracts.",
        "acquisition_signals": [
            "Complex Medicaid state reimbursement rules create defensive competitive moat",
            "Automated claims processing can reduce manual auditing costs by 40%",
            "Untapped geographic expansion across adjacent southern states"
        ]
    },
    {
        "domain": "cleanforceops.com",
        "company_name": "CleanForce Operations",
        "title": "CleanForce | Commercial Janitorial & Facility Management SaaS",
        "description": "Field time tracking, client quality inspection checklists, and automated supply reordering for mid-market commercial cleaning contractors.",
        "industry": "Field Services & Industrial",
        "location": "Charlotte, NC, United States",
        "estimated_revenue": "$1.9M ARR",
        "employee_count": "14 employees",
        "icp_score": 86,
        "verification_status": "verified",
        "tech_stack": ["WordPress", "Stripe", "Google Analytics", "Tailwind CSS"],
        "contact_email": "contact@cleanforceops.com",
        "phone": "+1 (704) 555-0143",
        "linkedin_url": "https://linkedin.com/company/cleanforce-ops",
        "twitter_url": None,
        "ai_summary": "CleanForce Operations serves commercial janitorial firms with steady MRR. Substantial upside through modern UI re-architecture and enterprise packaging.",
        "acquisition_signals": [
            "Legacy tech stack provides immediate high-ROI modernization opportunity",
            "Owner-operator seeking transition/succession pathway",
            "Unoptimized pricing tiers ripe for value-based restructuring"
        ]
    },
    {
        "domain": "complianceiq.co",
        "company_name": "ComplianceIQ",
        "title": "ComplianceIQ | Automated SOC2 & HIPAA Readiness for Startups",
        "description": "Continuous cloud compliance monitoring, vendor risk assessment, and auditor-ready evidence collection for emerging B2B cloud companies.",
        "industry": "GovTech & Compliance",
        "location": "Denver, CO, United States",
        "estimated_revenue": "$5.1M ARR",
        "employee_count": "32 employees",
        "icp_score": 92,
        "verification_status": "verified",
        "tech_stack": ["React", "Next.js", "Segment", "HubSpot", "AWS", "Stripe"],
        "contact_email": "security@complianceiq.co",
        "phone": "+1 (303) 555-0988",
        "linkedin_url": "https://linkedin.com/company/compliance-iq",
        "twitter_url": "https://twitter.com/complianceiq",
        "ai_summary": "High-growth cybersecurity and compliance SaaS with exceptional renewal rates. High synergy for cross-selling across PE portfolio companies.",
        "acquisition_signals": [
            "High net revenue retention (115%) in mission-critical security category",
            "Strong partner channel with regional cybersecurity auditors",
            "Natural fit to deploy automated LLM policy questionnaire responses"
        ]
    },
    {
        "domain": "buildflowhq.com",
        "company_name": "BuildFlow HQ",
        "title": "BuildFlow | Commercial Subcontractor Bid Management Platform",
        "description": "Streamlining plan room takeoffs, subcontractor invitation-to-bids, and material cost estimation for commercial general contracting firms.",
        "industry": "B2B SaaS",
        "location": "Austin, TX, United States",
        "estimated_revenue": "$3.1M ARR",
        "employee_count": "21 employees",
        "icp_score": 88,
        "verification_status": "verified",
        "tech_stack": ["React", "Cloudflare", "Intercom", "Google Analytics"],
        "contact_email": "hello@buildflowhq.com",
        "phone": "+1 (512) 555-0266",
        "linkedin_url": "https://linkedin.com/company/buildflow-hq",
        "twitter_url": "https://twitter.com/buildflowhq",
        "ai_summary": "Construction takeoff software with deep contractor penetration. Strong candidate for introducing automated blueprint PDF parsing via AI.",
        "acquisition_signals": [
            "High gross margin software business with minimal paid acquisition spend",
            "Expansion potential into computerized materials purchasing workflows",
            "Founder interested in growth equity or majority recapitalization"
        ]
    },
    {
        "domain": "propertysync.io",
        "company_name": "PropertySync",
        "title": "PropertySync | HOA & Multifamily Community Operations Portal",
        "description": "Resident maintenance ticketing, architectural review committee workflows, and digital dues processing for property management associations.",
        "industry": "B2B SaaS",
        "location": "Phoenix, AZ, United States",
        "estimated_revenue": "$2.4M ARR",
        "employee_count": "16 employees",
        "icp_score": 85,
        "verification_status": "verified",
        "tech_stack": ["Vue.js", "Stripe", "AWS", "Google Analytics"],
        "contact_email": "team@propertysync.io",
        "phone": "+1 (602) 555-0639",
        "linkedin_url": "https://linkedin.com/company/propertysync",
        "twitter_url": None,
        "ai_summary": "PropertySync offers deeply embedded HOA workflow management with near-zero annual customer churn across property managers.",
        "acquisition_signals": [
            "Substantial payment processing float and transaction fee revenue upside",
            "Opportunity to roll up fragmented regional property tech competitors",
            "Operational upside through AI-powered resident customer support"
        ]
    },
    {
        "domain": "claimsight.net",
        "company_name": "ClaimSight Systems",
        "title": "ClaimSight | Property & Casualty Claims Intake Automation",
        "description": "AI-assisted insurance claims triage, document ingestion, and first notice of loss (FNOL) routing for third-party administrators.",
        "industry": "FinTech & InsurTech",
        "location": "Chicago, IL, United States",
        "estimated_revenue": "$6.2M ARR",
        "employee_count": "38 employees",
        "icp_score": 95,
        "verification_status": "verified",
        "tech_stack": ["React", "Next.js", "AWS", "Cloudflare", "Segment"],
        "contact_email": "exec@claimsight.net",
        "phone": "+1 (312) 555-0722",
        "linkedin_url": "https://linkedin.com/company/claimsight",
        "twitter_url": "https://twitter.com/claimsight",
        "ai_summary": "Enterprise claims ingestion platform serving regional insurers. Outstanding contract durability and high annual contract values ($80k+ ACV).",
        "acquisition_signals": [
            "High ACV enterprise contracts with 3-year recurring commitments",
            "Direct alignment with Caprae's proprietary AI automation playbooks",
            "Founder looking to de-risk while participating in secondary upside"
        ]
    },
    {
        "domain": "aquaflowcrm.com",
        "company_name": "AquaFlow CRM",
        "title": "AquaFlow | Water Treatment & Filtration Route Management",
        "description": "Salt delivery routing, filter replacement scheduling, and recurring customer billing software tailored for residential and industrial water treatment dealers.",
        "industry": "Field Services & Industrial",
        "location": "Tampa, FL, United States",
        "estimated_revenue": "$1.5M ARR",
        "employee_count": "11 employees",
        "icp_score": 83,
        "verification_status": "verified",
        "tech_stack": ["Webflow", "Stripe", "Google Analytics"],
        "contact_email": "support@aquaflowcrm.com",
        "phone": "+1 (813) 555-0455",
        "linkedin_url": "https://linkedin.com/company/aquaflow-crm",
        "twitter_url": None,
        "ai_summary": "Hyper-niche route management CRM for water treatment dealers with high customer loyalty. Prime candidate for modernized web app re-architecture.",
        "acquisition_signals": [
            "Extremely defensive niche with virtually no venture-backed competition",
            "Opportunity to modernize from Webflow frontend to full-featured SaaS",
            "Low-hanging fruit in digital payments and automated SMS notifications"
        ]
    },
    {
        "domain": "staffbeacon.com",
        "company_name": "StaffBeacon Technologies",
        "title": "StaffBeacon | Light Industrial & Shift Staffing Platform",
        "description": "On-demand shift dispatch, geofenced mobile time tracking, and instant payroll disbursement for logistics and manufacturing staffing agencies.",
        "industry": "B2B SaaS",
        "location": "Indianapolis, IN, United States",
        "estimated_revenue": "$4.7M ARR",
        "employee_count": "29 employees",
        "icp_score": 90,
        "verification_status": "verified",
        "tech_stack": ["React", "AWS", "Stripe", "Intercom", "Google Analytics"],
        "contact_email": "partners@staffbeacon.com",
        "phone": "+1 (317) 555-0931",
        "linkedin_url": "https://linkedin.com/company/staffbeacon",
        "twitter_url": "https://twitter.com/staffbeacon",
        "ai_summary": "High-velocity staffing technology with embedded fintech payroll solutions. Strong market position across Midwest industrial hubs.",
        "acquisition_signals": [
            "Embedded wage-advance and payout transaction margins enhance unit economics",
            "High demand for automated candidate resume & skills screening via AI",
            "Well-suited for platform add-on acquisitions in regional markets"
        ]
    }
]

def seed():
    print("Initializing database...")
    init_db()

    data_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "leads.json")
    csv_path = os.path.join(data_dir, "leads.csv")

    # Insert into DB
    print(f"Seeding {len(SEED_LEADS)} high-impact B2B / PE leads into SQLite...")
    inserted_records = []
    for lead in SEED_LEADS:
        rec = insert_or_update_lead(lead)
        inserted_records.append(rec)

    # Save to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(inserted_records, f, indent=2)
    print(f"Saved JSON dataset to {json_path}")

    # Save to CSV
    keys = [
        "domain", "company_name", "title", "industry", "location",
        "estimated_revenue", "employee_count", "icp_score", "verification_status",
        "contact_email", "phone", "linkedin_url", "ai_summary"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for rec in inserted_records:
            writer.writerow(rec)
    print(f"Saved CSV dataset to {csv_path}")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
