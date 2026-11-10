# 📋 Pasha Hunt 2.0: Product Requirements Document (PRD)

> **Autonomous AI Career Agent, Direct-Email Sourcing Platform & High-Impact ATS Application Engine**  
> **Author & Chief Architect:** Muhammad Mubashar (*Pasha Dev*)  
> **Target Platform:** Windows 10 & Windows 11 (x64)  
> **Product Version:** 2.0.0 (Production Release)  
> **Document Status:** Complete & Approved Specification  

---

## 1. Executive Summary & Product Vision

### 1.1 The Modern Hiring Crisis
The software engineering job application landscape in 2026 is broken across four core failure vectors:

```mermaid
flowchart TD
    subgraph CRISIS ["The 4 Modern Hiring Failure Points"]
        F1["🚫 The ATS Black Hole<br/>75%+ of CVs dropped by automated keyword filters before human eyes."]
        F2["📫 Ghost Postings & Dead Inboxes<br/>Applications sent to expired domains bounce with 550 errors."]
        F3["😫 Application Burnout<br/>Manual tailoring of 50+ applications/week causes fatigue and generic submissions."]
        F4["🔒 Cloud Privacy Leaks<br/>Web portals scrape and expose candidate resumes on multi-tenant servers."]
    end

    subgraph SOLUTION ["The Pasha Hunt 2.0 Breakthrough"]
        S1["🎯 ATS 95+ Google XYZ Optimization"]
        S2["⚡ Socket DNS MX Zero-Bounce Verification"]
        S3["🤖 Fact-Grounded Autonomous Tailoring"]
        S4["🛡️ 100% Local-First Privacy (Zero Cloud Leaks)"]
    end

    F1 ==> S1
    F2 ==> S2
    F3 ==> S3
    F4 ==> S4
```

> [!IMPORTANT]
> **Pasha Hunt Core Mission:** To act as an autonomous, local-first personal career agent for senior and high-growth software engineers. It continuously uncovers verified direct-recruiter opportunities, elevates resumes to a guaranteed 95–100 ATS score via the Google XYZ formula, compiles tailored A4 PDF resumes via headless Edge/Chromium, and injects ready-to-review drafts directly into Gmail.

---

## 2. Target Personas & User Archetypes

```mermaid
graph LR
    subgraph P1 ["Persona A: Elite Full Stack & AI Engineer"]
        P1_A["Tech: Next.js, Python, Laravel, AI Agents, Docker"]
        P1_B["Goals: $60k-$150k Remote US/EU or PKR 200k-350k+ Local"]
        P1_C["Need: Zero manual busywork, 100% deliverability"]
    end

    subgraph P2 ["Persona B: Active Career Accelerator"]
        P2_A["Tech: React, Node.js, SQL, TypeScript"]
        P2_B["Goals: Rapid placement in high-growth software houses"]
        P2_C["Need: High volume (30+ apps/week) with deep tailoring"]
    end

    subgraph P3 ["Persona C: Transitioning Hackathon Builder"]
        P3_A["Tech: AI/ML APIs, AgentOps, Python, Redis"]
        P3_B["Goals: Convert hackathon accolades into enterprise roles"]
        P3_C["Need: Highlight credentials & verified project impact"]
    end

    P1 --> Engine["Pasha Hunt 2.0 Autonomous Cockpit"]
    P2 --> Engine
    P3 --> Engine
```

### Persona Breakdown Matrix

| Attribute | Persona A (Primary: Pasha Archetype) | Persona B (Active Accelerator) | Persona C (Hackathon Builder) |
|---|---|---|---|
| **Experience Level** | 4+ Years Shipping Production Code | 2–4 Years Web / Mobile Development | 1–3 Years + Competitive Wins |
| **Key Technical Stacks** | Next.js, Python, Laravel, Gemini API, Docker | React, Node.js, TypeScript, PostgreSQL | Python, AgentOps, IBM WatsonX, Redis |
| **Target Role Types** | Full Stack Engineer, AI Systems Architect | Full Stack Developer, Frontend Lead | AI Engineer, Backend API Developer |
| **Primary Friction** | Lack of time to research recruiter emails | Rejection due to unquantified resume bullets | Resume overlooked without formal brand pedigree |
| **Pasha Hunt Value** | Automated verified direct HR email outreach | Instant ATS 100% Google XYZ optimization | Automatic hackathon credential verification |

---

## 3. High-Level System Architecture & Flow

```mermaid
flowchart TD
    subgraph INGESTION ["1. Autonomous Sourcing Matrix (18 Feeds)"]
        A1["Global Remote (RemoteOK, Himalayas, Remotive)"]
        A2["Specialized (WWR, WorkingNomads, 4DayWeek)"]
        A3["Enterprise ATS (Lever, Greenhouse, Ashby)"]
        A4["Hacker News (Who Is Hiring Algolia API)"]
        A5["Pakistan Regional Tech Houses & Communities"]
        A6["Google Live Sourcing (Apinex / Gemini)"]
    end

    subgraph FILTERING ["2. Intelligent Prefilter Engine"]
        B1["Keyword AST Matcher"]
        B2["Geolocation Filter (Lahore / PK / Remote)"]
        B3["Experience Cap Heuristic"]
        B4["Age Freshness (<= 30 Days)"]
    end

    subgraph VALIDATION ["3. Network Socket DNS MX Engine"]
        C1["Regex & Obfuscation Parser"]
        C2["Dummy Domain Blacklist Interceptor"]
        C3["Live Socket Resolution (socket.getaddrinfo)"]
        C4["UI Badge: Verified HR vs Company Portal"]
    end

    subgraph ATS_OPTIMIZER ["4. ATS 95+ Resume Scorer & Optimizer"]
        D1["pypdf Multi-Page Streaming Ingestion"]
        D2["5-Category Scorecard (0-100 pts)"]
        D3["Google XYZ Bullet Restructuring"]
    end

    subgraph REASONING ["5. Fact-Grounded AI Reasoning"]
        E1["Apinex / Gemini LLM Hierarchy"]
        E2["Zero-Hallucination Guardrails"]
        E3["Dynamic Tailored Summary & Bullet Selection"]
    end

    subgraph DISPATCH ["6. Headless Compilation & Outreach"]
        F1["Headless Edge/Chrome Print-to-PDF"]
        F2["RFC 2822 Multipart MIME Packaging"]
        F3["Gmail IMAP [Gmail]/Drafts Injection"]
        F4["Real-Time tracker.csv Ledger"]
    end

    INGESTION --> FILTERING --> VALIDATION
    ATS_OPTIMIZER --> REASONING
    VALIDATION & REASONING --> DISPATCH
```

---

## 4. User Journey & Core Operating Workflows

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Software Engineer (User)
    participant UI as Pasha Hunt Dashboard
    participant Disc as 18-Source Radar
    participant Net as DNS MX Verifier
    participant ATS as ATS 95+ Engine
    participant AI as Fact-Grounded LLM
    participant Chrome as Headless Edge/Chrome
    participant Mail as Gmail IMAP Server
    actor HR as Recruiter / Hiring Manager

    Dev->>UI: Launch App & Upload Master CV PDF
    UI->>ATS: Ingest & Compute Baseline Score
    ATS-->>UI: Baseline Score (e.g., 73/100 Qualified)
    Dev->>UI: Click [Optimize All Bullets (Google XYZ)]
    ATS-->>UI: Score Elevated to 100/100 Elite Tier!
    
    Dev->>UI: Click [Scan for Jobs Now]
    UI->>Disc: Sweep 18 Feeds Concurrently
    Disc-->>Net: Raw Opportunities with Extracted Emails
    Net->>Net: Socket DNS MX Resolution (verify_email_domain)
    Net-->>UI: Display Jobs with [✔ Verified Recruiter Domain] Badges
    
    Dev->>UI: Select Verified Job & Click [Draft Email + CV]
    UI->>AI: Reason over Job Description + Master Profile
    AI-->>UI: Tailored Summary & Impact Bullets
    UI->>Chrome: Compile Clean A4 HTML to PDF
    Chrome-->>UI: Tailored_CV.pdf Generated (<1.5s)
    UI->>Mail: Append RFC 2822 Message to [Gmail]/Drafts
    Mail-->>UI: Draft Created Successfully!
    
    Dev->>Mail: Review Draft in Gmail Mobile/Desktop & Click Send
    Mail->>HR: Delivered Directly to Recruiter Inbox (0% Bounce)
```

---

## 5. Detailed Functional Requirements (FR)

### FR-1: Autonomous 18-Source Sourcing Matrix
* **Requirement:** Asynchronously ingest, normalize, and parse job opportunities from 18 distinct sources.
* **Architecture:** Executed using Python `ThreadPoolExecutor` with per-domain rate limiting to prevent IP throttling.
* **Sources Covered:**
  * Remotive, RemoteOK, Himalayas, Arbeitnow, Jobicy, WeWorkRemotely, WorkingNomads, 4DayWeek, Workew.
  * Enterprise ATS Portals: Greenhouse, Lever, Workday, BambooHR, Ashby, SmartRecruiters.
  * Hacker News Algolia Search API (`src_hn`).
  * Dedicated Pakistan Tech Houses (`src_pakistan_tech`): InvoZone, Systems Ltd, Rolustech, CureMD, Emumba, Conrad Labs, Confiz, Educative, Tintash, Programmers Force, Folio3, VentureDive.
  * Developer Community Channels (`src_facebook_community`).
  * Live Google Sourcing (`src_google`) powered by Apinex / Gemini.

### FR-2: Intelligent Prefiltering & Geolocation Governance
* **Requirement:** Filter postings using deterministic AST token rules to guarantee relevancy before presentation.
* **Filtering Rules:**
  * Match target roles (`Full Stack Developer`, `Python Engineer`, `AI Engineer`, `Next.js Developer`).
  * Disqualify senior leadership filters (`VP`, `Director`, `Staff Architect`, `10+ years`, `PhD`).
  * Geolocation unlocking: Accept Global Worldwide Remote, Pakistan Remote, and Lahore/Islamabad Hybrid/Onsite.
  * Age restriction: Reject listings published over 30 calendar days ago.

### FR-3: Socket DNS MX Email Deliverability Engine
* **Requirement:** Guarantee zero 550 *"Address not found"* email bounces by verifying domains at the network socket layer.

```mermaid
flowchart TD
    Start["Extracted Email (e.g., hr@domain.com)"] --> RegexCheck{"Valid RFC 5322 Format?"}
    RegexCheck -- No --> Reject["Drop Email / Mark Portal Apply"]
    RegexCheck -- Yes --> BlacklistCheck{"In DUMMY_DOMAINS?<br/>(company.com, example.com, etc.)"}
    BlacklistCheck -- Yes --> Reject
    BlacklistCheck -- No --> CacheCheck{"Domain in _domain_cache?"}
    CacheCheck -- Yes --> UseCached["Return Cached Verdict in O(1)"]
    CacheCheck -- No --> SocketCall["socket.getaddrinfo(domain, 80)"]
    SocketCall -- Success (A/MX Resolved) --> MarkVerified["email_verified = True<br/>Cache True"]
    SocketCall -- gaierror / Timeout --> MarkInvalid["email = ''<br/>email_verified = False<br/>Cache False"]
    MarkVerified --> GreenBadge["UI Badge: ✔ Verified Recruiter Domain (Deliverable)"]
    MarkInvalid --> AmberBadge["UI Badge: Apply on company portal link"]
```

### FR-4: ATS 95+ Resume Scorer & Google XYZ Bullet Optimization Engine
* **Requirement:** Evaluate candidate profiles across 5 categories (100-point rubric) and provide one-click restructuring into the Google XYZ formula:
  $$\text{Accomplished } [X] \text{ measured by } [Y] \text{ doing } [Z]$$

```mermaid
flowchart LR
    subgraph RUBRIC ["100-Point ATS Rubric"]
        C1["Contact & Links<br/>15 Pts"]
        C2["Summary Depth<br/>15 Pts"]
        C3["Experience & Metrics<br/>35 Pts"]
        C4["Skills Taxonomy<br/>20 Pts"]
        C5["Education & Certs<br/>15 Pts"]
    end

    subgraph BANDS ["Score Tiers"]
        T1["95 - 100: Elite (Top 2% ATS Ready)"]
        T2["85 - 94: Competitive (Top 10%)"]
        T3["70 - 84: Qualified (Average)"]
        T4["0 - 69: Sub-Optimal (Rejection Risk)"]
    end

    C1 & C2 & C3 & C4 & C5 --> Calculate["calculate_ats_score()"]
    Calculate --> BANDS
```

#### Google XYZ Formula Transformation Samples

> [!TIP]
> **Before (Baseline Score: 73):**
> *"Built full stack web applications with Next.js and Laravel."*  
> **After Google XYZ Optimization (Elite Score: 100):**
> *"Architected and deployed 15+ production full-stack web applications using Next.js, Laravel, and PostgreSQL, maintaining 99.9% uptime for 50,000+ monthly active users."*

> [!TIP]
> **Before (Baseline Score: 73):**
> *"Worked with Gemini AI to build tools."*  
> **After Google XYZ Optimization (Elite Score: 100):**
> *"Engineered autonomous AI agent workflows leveraging Gemini API and AgentOps, slashing repetitive business data-processing times by 65%."*

### FR-5: Robust Multi-Page PDF CV Ingestion
* **Requirement:** Ingest user resumes from standard PDF files using pure-Python `pypdf`, eliminating legacy `fitz` (PyMuPDF) DLL collisions on Windows 10/11.
* **Extraction:** Iterates across all pages, normalizes whitespace, and parses contact info, skills, experience, and education via structured AI structuring or deterministic token fallback.

### FR-6: Fact-Grounded AI Reasoning & Tailoring Engine
* **Requirement:** Re-prioritize bullet points and write tailored company introductions while strictly prohibiting the invention of false facts.
* **Model Hierarchy:**
  1. *Tier 1:* Apinex / Gemini 3.8 Flash (`free/gemini-3.8-flash`).
  2. *Tier 2:* DeepSeek V4.1 Flash (`free/deepseek-v4.1-flash`).
  3. *Tier 3:* Native Google Gemini 2.5 Flash API.
  4. *Tier 4:* Deterministic offline master profile injection (100% offline capability).

### FR-7: Headless Chromium / Edge PDF Compilation
* **Requirement:** Render publication-grade, ATS-parsable A4 PDFs using native Windows Microsoft Edge (`msedge.exe`) or Google Chrome.
* **Print Specification:**
  * Page Size: A4 (`210mm × 297mm`), `15mm` margins.
  * Layout Engine: `--headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=<dest>`.
  * CSS Rules: `break-inside: avoid;` on all work experience blocks to prevent orphaned headers.

### FR-8: Gmail IMAP Draft Injection & Outreach Hub
* **Requirement:** Stage applications in `[Gmail]/Drafts` with attached tailored PDFs for one-click candidate review and sending.
* **Security:** Connects via TLS to `imap.gmail.com:993` using candidate's local Gmail App Password; zero credentials transmitted to cloud servers.

### FR-9: Modern Dark Dashboard UI (Obsidian Void Design System)
* **Requirement:** Modern desktop UI featuring native Windows 11 DWM dark titlebar interop, real-time Hero KPI metrics, and dedicated modal dialogs.

```mermaid
graph TD
    subgraph UI_MOCKUP ["Pasha Hunt 2.0 Desktop Dashboard"]
        TOP["Toolbar: [📤 Upload CV]  [🎯 ATS 95+ Optimizer]  [👤 My Profile]  [AI Model Selector ▾]"]
        HERO["Hero KPI Banner: 📊 ATS Score: 100% (Elite) | 🎯 Matches: 24 | ✉️ Verified HR: 18 | 🚀 Ready: 12"]
        TABLE["Job Stream Grid: Status | Fit | Company | Role | Deliverable Email"]
        DETAIL["Action Pane: Verified Recruiter Domain Badge | [✉ Draft Email + CV]  [📄 Make PDF]  [🌐 Open URL]"]
        LOG["Real-Time Execution Log Console"]
    end

    TOP --> HERO --> TABLE --> DETAIL --> LOG
```

---

## 6. Entity-Relationship Data Model

```mermaid
erDiagram
    CANDIDATE_PROFILE ||--o{ WORK_EXPERIENCE : contains
    CANDIDATE_PROFILE ||--o{ PROJECT : builds
    CANDIDATE_PROFILE ||--o{ CERTIFICATION : holds
    CANDIDATE_PROFILE ||--o{ EDUCATION : completes
    JOB_POSTING ||--o{ APPLICATION_DRAFT : generates
    APPLICATION_DRAFT ||--|| COMPILED_PDF : attaches
    APPLICATION_DRAFT ||--|| TRACKER_RECORD : records

    CANDIDATE_PROFILE {
        string name
        string email
        string phone
        string title
        string location
        int ats_score
        string ats_tier
    }

    WORK_EXPERIENCE {
        string company
        string role
        string period
        list bullets_xyz
    }

    JOB_POSTING {
        string job_id
        string company
        string role
        string email
        boolean email_verified
        string source
        string url
    }

    APPLICATION_DRAFT {
        string draft_id
        string recipient_email
        string subject
        string cover_letter
        datetime timestamp
    }

    TRACKER_RECORD {
        datetime date
        string company
        string role
        string email
        string status
    }
```

---

## 7. State Machine: Application Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Ingested: Scraped from 18 Sources
    
    Ingested --> Prefiltered: Passed AST Role & Geo Filter
    Ingested --> Discarded: Failed Keywords / Too Old
    
    Prefiltered --> DNS_Resolving: Extract Email
    DNS_Resolving --> Verified_HR: Domain Resolves via Socket
    DNS_Resolving --> Portal_Apply: Domain Fails / Blacklisted
    
    Verified_HR --> AI_Reasoning: Candidate Requests Application
    Portal_Apply --> Manual_Apply: Candidate Opens Portal Link
    
    AI_Reasoning --> PDF_Compiled: Headless Edge Generates A4 CV
    PDF_Compiled --> Drafted_Gmail: IMAP Appends to [Gmail]/Drafts
    
    Drafted_Gmail --> Sent: Candidate Clicks Send in Gmail
    Sent --> Recruiter_Replied: IMAP Tracker Detects Interview
    Sent --> Archived: No Reply after 30 Days
```

---

## 8. Non-Functional Requirements (NFR)

```mermaid
graph LR
    subgraph NFR ["Core Non-Functional Pillars"]
        N1["⚡ Performance<br/>Startup <1.8s<br/>PDF Gen <1.5s<br/>18 Feeds <20s"]
        N2["🛡️ Security<br/>Zero Cloud Storage<br/>Local %APPDATA%<br/>Strict .gitignore"]
        N3["🔌 Portability<br/>Standalone .exe<br/>Inno Setup Installer<br/>Zero Python Prerequisite"]
        N4["🔄 Resilience<br/>Socket DNS Cache<br/>Deterministic Fallback<br/>Clean Process Exit"]
    end
```

* **NFR-1 (Performance):** UI thread remains 100% responsive during background sweeps; PDF compilation generates publication-grade documents under 1.5 seconds.
* **NFR-2 (Privacy & Security):** Zero cloud telemetry. All API keys and email credentials remain in local `%APPDATA%\Job Hunter\config.json`.
* **NFR-3 (Portability):** Packages into a standalone Windows binary via PyInstaller and an enterprise Windows setup wizard via Inno Setup 6.
* **NFR-4 (Fault Tolerance):** If LLM APIs are offline or rate-limited (HTTP 429), the application seamlessly generates deterministic applications using the candidate's master profile without crashing.

---

## 9. Release Milestones & Strategic Roadmap

```mermaid
flowchart LR
    v1["v1.0 Foundation<br/>- Multi-source scraper<br/>- Regex filters<br/>- Basic ReportLab CV"]
    
    v2["v2.0 Production (Current)<br/>- Socket DNS MX Engine<br/>- ATS 95+ Google XYZ Rewriter<br/>- Headless Chromium A4 PDF<br/>- Obsidian Dark DWM Theme<br/>- pypdf Streaming Ingestion"]
    
    v2_1["v2.1 Alert Intel (Next)<br/>- Real-time WhatsApp/Telegram Recruiter Alerts<br/>- 5-Day Automated Follow-Up Drafter"]
    
    v3["v3.0 Autonomous Agent<br/>- Playwright Web Form Autofill (Greenhouse/Lever)<br/>- Voice AI Mock Interview Simulator"]

    v1 --> v2 --> v2_1 --> v3
```

---
*End of Product Requirements Document (PRD) — Pasha Hunt 2.0*
