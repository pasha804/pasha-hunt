# ⚙️ Pasha Hunt 2.0: End-to-End Pipeline Specification

> **Technical Blueprint of the Autonomous Job Discovery, Verification, Optimization, and Outreach Pipelines**  
> **Author & Chief Architect:** Muhammad Mubashar (*Pasha Dev*)  
> **Target Environment:** Windows 10 / Windows 11 (x64)  
> **Document Status:** Production-Ready Pipeline Specification  

---

## 1. Master 7-Stage End-to-End Pipeline Architecture

```mermaid
flowchart TD
    subgraph S1 ["Stage 1: Multi-Source Ingestion Pipeline"]
        A1["18 Concurrent Sourcing Feeds"] --> A2["Rate Limiting & Per-Host Throttling"]
        A2 --> A3["Raw JSON / RSS / HTML Normalization"]
    end

    subgraph S2 ["Stage 2: Filtering & Deduplication Pipeline"]
        A3 --> B1["Title Regex & Keyword AST Matcher"]
        B1 --> B2["Geolocation & Work Mode Classifier"]
        B2 --> B3["Experience Cap & Anti-Keyword Filter"]
        B3 --> B4["Global Job Hash & Cache Check"]
    end

    subgraph S3 ["Stage 3: Email Extraction & DNS Verification Pipeline"]
        B4 --> C1["Direct & Obfuscated Email Regex Parser"]
        C1 --> C2["Dummy & Placeholder Blacklist Interceptor"]
        C2 --> C3["Live Socket DNS MX Resolution"]
        C3 --> C4["Classification: Verified HR vs Company Portal"]
    end

    subgraph S4 ["Stage 4: CV Ingestion & ATS Optimization Pipeline"]
        D1["Candidate CV PDF Ingestion"] --> D2["pypdf Multi-Page Text Extraction"]
        D2 --> D3["Profile AST Normalization"]
        D3 --> D4["ATS 0-100 Deep Scoring Model"]
        D4 --> D5["Google XYZ Bullet Restructuring Engine"]
    end

    subgraph S5 ["Stage 5: Fact-Grounded AI Reasoning Pipeline"]
        C4 & D5 --> E1["Apinex / Gemini Multi-Model Hierarchy"]
        E1 --> E2["Strict Anti-Hallucination Guardrails"]
        E2 --> E3["Tailored Summary & Bullet Prioritization"]
        E3 --> E4["Cover Letter & Outreach Pitch Formulation"]
    end

    subgraph S6 ["Stage 6: Document Compilation & Outreach Pipeline"]
        E4 --> F1["A4 HTML5/Print CSS Dynamic Rendering"]
        F1 --> F2["Headless Edge/Chrome Print-to-PDF Engine"]
        F2 --> F3["RFC 2822 MIME Multipart Packaging"]
        F3 --> F4["Gmail IMAP [Gmail]/Drafts Injection"]
    end

    subgraph S7 ["Stage 7: Ledger & Bi-Directional Tracking Pipeline"]
        F4 --> G1["tracker.csv Audit Ledger Update"]
        G1 --> G2["Inbound Recruiter Response Polling Engine"]
        G2 --> G3["Sentiment & Interview Invitation Classifier"]
        G3 --> G4["Real-Time Dashboard KPI Synchronization"]
    end
```

---

## 2. Stage-by-Stage Detailed Engineering Breakdown

### Stage 1: Ingestion & Rate-Limiting Pipeline

```mermaid
flowchart LR
    S_Remote["Global Remote Feeds<br/>(RemoteOK, Himalayas, Remotive)"] --> Workers["Worker Pool<br/>(16 Concurrency)"]
    S_ATS["Direct ATS Portals<br/>(Greenhouse, Lever, Ashby)"] --> Workers
    S_PK["Pakistan Regional Software Houses<br/>(InvoZone, Systems Ltd, CureMD)"] --> Workers
    S_HN["Hacker News Who Is Hiring<br/>(Algolia API)"] --> Workers
    
    Workers --> TokenBucket["Token Bucket Rate Governor<br/>(Max 3 req/sec per host)"]
    TokenBucket --> Normalizer["Unified Job Dict Schema<br/>{title, company, body, email, url}"]
```

* **Rate Governance:** Prevents HTTP 429 rate-limiting by enforcing jittered sleep delays between calls to the same target host.
* **Standardized Schema:** All raw responses normalize into a single immutable dictionary structure before downstream transmission.

---

### Stage 2: Filtering & Deduplication Pipeline

```mermaid
flowchart TD
    RawJob["Normalized Job Entry"] --> TitleMatch{"Title Matches Target Roles?<br/>(Full Stack, Python, AI, Next.js)"}
    TitleMatch -- No --> Drop["Discard Record"]
    TitleMatch -- Yes --> ExcludeMatch{"Contains Anti-Keywords?<br/>(VP, Director, Staff Architect, 10+ yrs)"}
    ExcludeMatch -- Yes --> Drop
    ExcludeMatch -- No --> GeoMatch{"Matches Geolocation?<br/>(Worldwide Remote, Pakistan, Lahore)"}
    GeoMatch -- No --> Drop
    GeoMatch -- Yes --> FreshnessMatch{"Age <= 30 Days?"}
    FreshnessMatch -- No --> Drop
    FreshnessMatch -- Yes --> DedupHash{"Job Hash in jobs.json Cache?"}
    DedupHash -- Yes --> Drop
    DedupHash -- No --> Passed["Forward to Stage 3 Verification"]
```

---

### Stage 3: Email Extraction & DNS MX Resolution Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant Job as Filtered Job Posting
    participant Extractor as Regex Email Extractor
    participant Filter as Dummy Domain Blacklist
    participant Cache as In-Memory _domain_cache
    participant Socket as OS Socket Subsystem
    participant UI as Dashboard State

    Job->>Extractor: Parse body & headers for emails
    Extractor->>Filter: Matches dummy list? (company.com, etc.)
    
    alt Dummy Domain Detected
        Filter-->>Job: Blank out email (Discard)
        Job->>UI: Set email_verified = False (Portal Apply)
    else Legitimate Domain
        Filter->>Cache: Check domain cached?
        alt Cache Hit
            Cache-->>Job: Return cached boolean
        else Cache Miss
            Filter->>Socket: socket.getaddrinfo(domain, 80)
            alt Resolution Successful
                Socket-->>Filter: Valid socket endpoint
                Filter->>Cache: Save domain -> True
                Filter-->>Job: Set email_verified = True
                Job->>UI: Render [✔ Verified Recruiter Domain] in Neon Emerald
            else gaierror or Timeout
                Socket-->>Filter: Lookup Failed
                Filter->>Cache: Save domain -> False
                Filter-->>Job: Blank out email, set email_verified = False
                Job->>UI: Render [Apply on company portal link] in Vivid Amber
            end
        end
    end
```

---

### Stage 4: CV Ingestion & ATS Optimization Pipeline

```mermaid
flowchart LR
    PDF_In["Candidate PDF CV"] --> PyPDF["pypdf Stream Reader"]
    PyPDF --> TextNormalize["Text & Whitespace Normalizer"]
    TextNormalize --> ProfileMap["Profile Field Mapper"]
    
    ProfileMap --> ATS_Score["calculate_ats_score()<br/>Contact: 15 | Summary: 15<br/>Experience: 35 | Skills: 20 | Edu: 15"]
    
    ATS_Score --> Check{"Score >= 95?"}
    Check -- Yes --> Elite["Elite Status (Top 2% ATS Ready)"]
    Check -- No --> AutoXYZ["auto_optimize_bullets_ats()<br/>Google XYZ Bullet Rewriter"]
    AutoXYZ --> Elite
```

* **Formula:** $\text{Accomplished } [X] \text{ measured by } [Y] \text{ doing } [Z]$.
* **Outcome:** Transforms candidate achievements into enterprise ATS parseable records with verified quantifiable metrics.

---

### Stage 5: Fact-Grounded AI Reasoning Pipeline

```mermaid
flowchart TD
    Inputs["Verified Job Description + Candidate profile.json"] --> Router["Apinex / Gemini Model Router"]
    
    Router --> Primary["Tier 1: Apinex Gemini 3.8 Flash"]
    Primary -- Fail --> Fallback1["Tier 2: DeepSeek V4.1 Flash"]
    Fallback1 -- Fail --> Fallback2["Tier 3: Google Gemini 2.5 Flash Native"]
    Fallback2 -- Fail --> Fallback3["Tier 4: Offline Deterministic Fallback"]
    
    Primary & Fallback1 & Fallback2 & Fallback3 --> Guard["Zero-Hallucination Integrity Guard"]
    Guard --> Output["Structured Output:<br/>1. Tailored High-Impact Summary<br/>2. Top 3 Tech-Aligned Projects<br/>3. Prioritized XYZ Bullets<br/>4. Professional Outreach Pitch"]
```

---

### Stage 6: Headless Compilation & Outreach Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Tailoring Engine
    participant CV as cv.py (A4 HTML Generator)
    participant Edge as msedge.exe --headless=new
    participant MIME as RFC 2822 Multipart Builder
    participant IMAP as imap.gmail.com:993
    participant Dev as Candidate

    Engine->>CV: Render A4 HTML DOM with embedded CSS & vector icons
    CV->>Edge: Execute headless PDF print
    Edge-->>CV: Generated tailored CV (e.g., cvs/InvoZone_Pasha_CV.pdf)
    CV->>MIME: Package From, To, Subject, Body, and PDF attachment
    MIME->>IMAP: Connect TLS & append to [Gmail]/Drafts with \Draft flag
    IMAP-->>Engine: Draft successfully injected
    Engine-->>Dev: Prompt: "Draft ready in Gmail. Review & Send!"
```

---

### Stage 7: Ledger Logging & Bi-Directional Inbound Tracking

```mermaid
stateDiagram-v2
    [*] --> Drafted: Injected into Gmail Drafts
    Drafted --> Sent: Candidate Dispatches Email
    
    Sent --> Inbound_Scan: Background IMAP Thread Checks Responses
    Inbound_Scan --> Neutral: Automated Acknowledgment
    Inbound_Scan --> Interview_Invite: Positive Sentiment Detected
    Inbound_Scan --> Assessment: Coding Challenge Detected
    Inbound_Scan --> Rejection: Unsuccessful Notice
    
    Interview_Invite --> Desktop_Alert: Native Windows Toast Notification
    Assessment --> Desktop_Alert
    Rejection --> Tracker_Update: Mark Status in tracker.csv
```

---

## 3. Failure Modes & Self-Healing Architecture

```mermaid
flowchart TD
    subgraph FAILURES ["Potential System Faults"]
        F1["LLM API Rate Limited (HTTP 429)"]
        F2["Recruiter Email Domain Unreachable"]
        F3["PDF Has Image-Only Scanned Text"]
        F4["Gmail App Password Revoked"]
    end

    subgraph HEALING ["Autonomous Recovery Actions"]
        H1["Activate _generate_master_cv_fallback() deterministically"]
        H2["Blank out email & route candidate to official company portal"]
        H3["Fallback regex parser extracts raw text; loads cached master profile"]
        H4["Compile PDF CV to disk & generate ready-to-copy email pitch in Notepad"]
    end

    F1 ==> H1
    F2 ==> H2
    F3 ==> H3
    F4 ==> H4
```

| Failure Scenario | Automatic Recovery Mechanism |
|---|---|
| **Apinex / LLM API Down or 429 Quota Exceeded** | Automatically activates `_generate_master_cv_fallback()` to deterministically tailor the application using master profile data without crashing. |
| **Recruiter Email Domain Down or Fails DNS** | Intercepts invalid domain, blanks out `email`, sets `email_verified=False`, and directs candidate to apply via official company web portal link. |
| **PDF Extraction Corrupted or Image-Only** | Fallback parser `_parse_cv_text_to_profile()` searches disk for cached master profile facts or regex-extracts candidate contact info from raw text. |
| **Chrome / Edge Browser Missing** | System checks standard installation paths for Microsoft Edge (installed by default on Windows 10/11) and Google Chrome; logs clear guidance if neither is found. |
| **Gmail Credentials Expired or App Password Revoked** | System detects auth failure, bypasses draft injection, compiles PDF resume to `cvs/` folder, and presents candidate with ready-to-send email copy in Notepad. |

---
*End of Pipeline Specification — Pasha Hunt 2.0*
