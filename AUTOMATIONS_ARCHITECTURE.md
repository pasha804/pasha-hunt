# 🚀 Pasha Hunt 2.0 — Autonomous Automations Architecture Guide
### Integrating `awesome-n8n-templates` & `Scrapli` Workflows

---

## 📌 Executive Summary
`awesome-n8n-templates` (by Enes Cingöz) provides production-tested, low-code automation workflows connecting AI reasoning models with enterprise webhooks, email servers, databases, and scrapers.

In **Pasha Hunt 2.0**, we leverage these blueprints alongside **Scrapli** to deliver an enterprise-grade autonomous job hunting and application engine that runs 24/7 in the background without user intervention.

---

## 🏗️ The 3 Core Autonomous Pipelines

```
               +-------------------------------------------------+
               |              Pasha Hunt 2.0 Engine              |
               +-------------------------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                |                               |
       v                                v                               v
+------------------+         +---------------------+        +--------------------+
|  Pipeline 1:     |         |  Pipeline 2:        |        |  Pipeline 3:       |
|  Autonomous Cold |         |  Autonomous Web     |        |  Recruiter Email   |
|  Emailing &      |         |  Job Scraper &      |        |  Enrichment & MX   |
|  Follow-Up Loop  |         |  Scrapli Harvester  |        |  Verification      |
+------------------+         +---------------------+        +--------------------+
       |                                |                               |
       v                                v                               v
- Match Detection            - Multi-source Cron Feeds       - Domain Synthesis
- Tailored Gmail Draft       - Greenhouse / Lever Scraper    - DNS MX Verification
- 3-Day Polite Nudge         - Anti-Deduplication Cache     - Zero-Bounce Guarantee
- Auto-Stop on Reply         - Real-Time JSON Ingestion      - Recruiter Directory
```

---

## 1. 📧 Pipeline 1: Autonomous Cold Emailing & Smart Follow-Up Sequence

### 🎯 Objective:
Eliminate manual outreach. Automatically drafts or sends hyper-personalized job applications with the candidate's ATS CV attached, monitors the candidate's Gmail inbox via IMAP, and sends timed follow-ups until a reply is detected.

### ⚙️ Workflow Node Breakdown:
1. **Trigger Node (Schedule / Webhook):**
   - Fires every 4 hours or on-demand when new high-match (>85%) jobs are indexed.
2. **AI Personalization Node (Gemini 2.5 Flash / Apinex Qwen-3.8-Max):**
   - Input: Candidate profile (`profile.json`) + Job description (`jobs.json`).
   - Formula: Applies Google XYZ framework (*"Accomplished [X] as measured by [Y] by doing [Z]"*).
   - Generates subject line and 3-paragraph punchy pitch.
3. **IMAP Draft / Send Node:**
   - Connects securely to `imap.gmail.com:993` with Gmail App Passwords.
   - Attaches `{Candidate_Name}-ATS-CV.pdf` (zero hardcoding).
   - Records application state into `tracker.csv` with status `draft-attached`.
4. **Follow-Up Decision Engine (Wait & Check):**
   - **T + 3 Days:** Checks IMAP inbox for any reply from the recruiter domain. If no reply, creates a polite follow-up nudge highlighting recent project achievements.
   - **T + 7 Days:** If still no reply, drafts a final graceful closing follow-up.
   - **Stop Trigger:** If candidate receives an email from the recruiter, the sequence is instantly terminated and flagged as `🎉 Reply Received`.

---

## 2. 🕷️ Pipeline 2: Full Web Job Scraper & Scrapli Portal Harvester

### 🎯 Objective:
Continuously ingest high-paying remote, hybrid, and onsite jobs from 16+ portals, Facebook developer communities, and software house career pages.

### ⚙️ Scrapli & Harvester Nodes:
1. **Feed Aggregator Nodes:**
   - Ingests public RSS & REST APIs: Remotive, RemoteOK, Arbeitnow, Jobicy, Himalayas, We Work Remotely.
2. **Scrapli / Headless Crawler Nodes:**
   - Targets company career boards (Greenhouse, Lever, Ashby, Workday).
   - Extracts structured metadata:
     * `title`: Target role name.
     * `company`: Verified company name.
     * `location`: Remote / Worldwide / Regional eligibility.
     * `email`: Discovered direct recruiter emails.
     * `text`: Full raw job description.
3. **Anti-Duplication & Normalization:**
   - Generates unique deterministic hashes (`cid-tid`) to prevent duplicate listings.
   - Ingests cleanly into `jobs.json` with humanized timestamps.

---

## 3. 🔍 Pipeline 3: Recruiter Email Enrichment & MX Deliverability Validator

### 🎯 Objective:
Turn generic portal application links into direct decision-maker emails (Founders, CTOs, HR Directors, Talent Acquisition Leads) with a 0% bounce rate guarantee.

### ⚙️ Deliverability & Verification Nodes:
1. **Domain Extraction Node:**
   - Parses the company domain from job URLs (e.g., `capslock.global`, `superside.com`).
2. **Email Synthesis Engine:**
   - Tests standard executive email patterns:
     * `careers@{domain}`
     * `talent@{domain}`
     * `jobs@{domain}`
     * `hr@{domain}`
     * `hello@{domain}`
3. **Real DNS MX Validation:**
   - Performs authentic DNS lookup (`dns.resolver.resolve(domain, 'MX')`).
   - Verifies whether the mail exchanger exists and accepts incoming SMTP traffic.
   - Rejects dead domains or disposable mail providers before any email is queued.

---

## 📋 Integration with Pasha Hunt 2.0 Backend

Pasha Hunt exposes standard REST webhooks on `http://127.0.0.1:58241`:
- `POST /api/scan`: Triggers autonomous job sweep across all platforms.
- `POST /api/create-draft`: Directly compiles ATS CV and appends Gmail draft.
- `POST /api/auto-draft`: High-match batch processor.
- `POST /api/extract-email`: Real-time MX enrichment for missing emails.
- `GET /api/cv/render-html`: Delivers the exact side-by-side ATS CV view.
- `GET /api/cv/save-to-downloads`: Auto-saves the compiled PDF to the user's Downloads folder.

These webhooks can be triggered directly by n8n HTTP Request nodes, Python scripts, or command-line automations!
