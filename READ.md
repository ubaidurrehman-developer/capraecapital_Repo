# SaaSquatch Leads — Local Setup & Installation Guide

A high-performance B2B Lead Intelligence & Deal Sourcing Platform featuring automated web scraping, ICP scoring, deal inspection, and CRM data exports.

---

## 📋 Prerequisites

Before running the project locally, ensure you have:
* **Python**: `3.10` or higher ([python.org](https://www.python.org/downloads/))
* **Git**: Installed and configured ([git-scm.com](https://git-scm.com/))
* **Modern Web Browser**: Chrome, Firefox, Safari, or Edge

---

## 🚀 Step-by-Step Installation & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ubaidurrehman-developer/capraecapital_Repo.git
cd capraecapital_Repo
```

---

### 2. Create and Activate a Virtual Environment

Isolate the project dependencies from your global Python environment:

* **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **On Windows (Command Prompt / PowerShell):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

---

### 3. Install Required Dependencies

Install the core FastAPI, Uvicorn, Pydantic, and scraping libraries:

```bash
pip install -r requirements.txt
```

*(Alternatively, if installing manually without `requirements.txt`:)*
```bash
pip install fastapi uvicorn pydantic requests beautifulsoup4
```

---

### 4. Initialize Database & Seed Sample Records

Populate the local SQLite database (`data/leads.db`) with curated B2B SaaS target data:

```bash
python data/seed_data.py
```

> **Note:** This initializes the database schema with WAL (Write-Ahead Logging) mode, B-Tree indexes, and preloads 10+ qualified SaaS prospects.

---

### 5. Launch the Platform Server

Start the FastAPI ASGI application server:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8080 --reload
```

You should see output similar to:
```text
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

---

### 6. Access the Dashboard & API

* **Web Dashboard UI**: Open your browser and navigate to:
  👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

* **Interactive API Documentation (Swagger / OpenAPI)**:
  👉 **[http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)**

---

## 🧪 Running Automated Tests

Run the platform test suite (API validation, data filtering, scraping, security headers, SSRF protections, and CSV sanitization):

```bash
python -m unittest discover tests
```

Expected output:
```text
Ran 10 tests in 0.45s
OK
```

---

## 📂 Project Architecture

```text
├── backend/
│   ├── database.py       # SQLite WAL repository, indexing, deduplication & queries
│   ├── enricher.py       # ICP qualification heuristics & outreach email generator
│   ├── main.py           # FastAPI server, static file hosting, security middlewares
│   ├── models.py         # Pydantic validation schemas
│   └── scraper.py        # SSRF-protected metadata, tech stack & contact extractor
├── data/
│   ├── leads.csv         # Verified starter dataset in CSV format
│   ├── leads.db          # Indexed SQLite database
│   ├── leads.json        # Curated starter dataset in JSON format
│   └── seed_data.py      # Automated database and file seeder
├── frontend/
│   ├── app.js            # Reactive client controller & slide-over deal drawer
│   ├── index.html        # Semantic HTML5 dashboard interface
│   └── styles.css        # Bespoke institutional dark-mode design system
├── tests/
│   ├── test_platform.py  # End-to-end platform & API unit tests
│   └── test_security.py  # Security & vulnerability regression tests
├── requirements.txt      # Python dependencies list
└── READ.md               # Local installation and clone guide
```

---

## 🛠️ Key Features Included

1. **Lead Ingestion & Live Scraper**: Enter any company domain (e.g. `slack.com`, `stripe.com`) to extract meta-data, tech signatures, and verified contacts in real time with built-in SSRF protection.
2. **Dynamic ICP Scoring**: 0–100 algorithmic scoring based on revenue signals, employee headcount, tech sophistication, and domain maturity.
3. **Pipeline Deal Inspector**: Click any lead row to inspect company details, add analyst notes, and transition pipeline stages (*New Lead*, *Contacted*, *In Diligence*, *Won*, *Passed*).
4. **Caprae Outreach Generator**: One-click generation of tailored, operator-first cold emails.
5. **Instant Export**: Export filtered subsets directly into clean, injection-safe CSV or JSON.

---

## ❓ Troubleshooting

* **Port 8080 already in use:**
  Run on an alternate port:
  ```bash
  uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
  ```
  Then open `http://127.0.0.1:8000`.

* **Database locked / permission issues:**
  Ensure your user has write permissions in the `data/` folder, or re-run `python data/seed_data.py`.
