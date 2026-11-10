# 🏗️ Pasha Hunt 2.0: System Architecture & Technical Specification

> **Autonomous AI Career Agent, Direct-Email Sourcing Platform & High-Impact ATS Application Engine**  
> **Author & Chief Architect:** Muhammad Mubashar (*Pasha Dev*)  
> **Target Environment:** Windows 10 / Windows 11 (x64)  
> **Document Status:** Production-Ready Architectural Reference  

---

## 1. System Philosophy & High-Level Architecture

Pasha Hunt is engineered as a **local-first, autonomous desktop agent** designed to eliminate the algorithmic and operational friction of modern technical job hunting.

```mermaid
graph TB
    subgraph CLIENT_TIER ["1. Presentation Layer (Desktop UI)"]
        UI["Obsidian Void GUI (gui.py)<br/>Tkinter + Custom Styling"]
        DWM["Windows 11 DWM Dark Caption Bar<br/>ctypes dwmapi.dll"]
        HERO["Real-Time Hero KPI Dashboard<br/>ATS Score | Matches | Verified HR"]
        MODAL["ATS 95+ Interactive Modal Dialog"]
    end

    subgraph ENGINE_TIER ["2. Core Autonomous Engine (bot.py)"]
        DISPATCHER["Multi-Threaded Sourcing Dispatcher<br/>ThreadPoolExecutor"]
        MATCHER["Intelligent AST Token Matcher<br/>Role & Geo Pre-Filtering"]
        DNS_RESOLVER["Socket DNS MX Deliverability Verifier<br/>verify_email_domain()"]
        ATS_ENGINE["ATS 95+ Scorer & Google XYZ Optimizer<br/>calculate_ats_score()"]
        FALLBACK_GEN["Deterministic Master Profile Engine"]
    end

    subgraph AI_TIER ["3. Fact-Grounded Reasoning Tier"]
        ROUTER["LLM API Router & Fallback Chain"]
        M1["Tier 1: Apinex Gemini 3.8 Flash"]
        M2["Tier 2: DeepSeek V4.1 Flash"]
        M3["Tier 3: Google Gemini 2.5 Flash Native"]
        GUARD["Anti-Hallucination Fact Guardrail"]
    end

    subgraph COMPILER_TIER ["4. Headless Compilation & Outreach"]
        DOM_BUILDER["HTML5 / Print CSS A4 Template Builder (cv.py)"]
        EDGE_PRINT["Headless Chromium / Edge Engine<br/>msedge.exe --headless=new"]
        MIME_ENGINE["RFC 2822 Multipart MIME Assembler"]
        IMAP_CLIENT["Gmail IMAP4_SSL Client (imap.gmail.com:993)"]
    end

    subgraph STORAGE_TIER ["5. Local-First Storage Layer (%APPDATA%)"]
        CFG["config.json (Keys & Credentials)"]
        PROF["profile.json (Candidate Source of Truth)"]
        JOBS["jobs.json (Normalized Postings Cache)"]
        LOGS["tracker.csv (Application Ledger)"]
        PDFS["cvs/*.pdf (Compiled Tailored Resumes)"]
    end

    UI --> DISPATCHER
    DISPATCHER --> MATCHER --> DNS_RESOLVER
    DNS_RESOLVER --> ROUTER
    ROUTER --> M1 & M2 & M3
    M1 & M2 & M3 --> GUARD
    GUARD --> DOM_BUILDER
    DOM_BUILDER --> EDGE_PRINT --> MIME_ENGINE --> IMAP_CLIENT
    
    ATS_ENGINE <--> PROF
    IMAP_CLIENT --> LOGS
    EDGE_PRINT --> PDFS
    DWM --- UI
    HERO --- UI
    MODAL --- UI
```

---

## 2. Class & Module Architecture

```mermaid
classDiagram
    class PashaHuntGUI {
        +Tk root
        +StringVar search_var
        +StringVar model_var
        +List current_jobs
        +init_ui()
        +apply_dark_titlebar()
        +update_hero_metrics()
        +ats_optimizer()
        +draft_selected_job()
        +run_sweep_async()
    }

    class PashaBot {
        +dict config
        +dict profile
        +dict domain_cache
        +scrape_all_sources()
        +verify_email_domain(email)
        +calculate_ats_score(profile)
        +auto_optimize_bullets_ats(profile)
        +call_gemini(prompt, schema)
        +create_gmail_draft(job, cv_path)
        +check_inbound_replies()
    }

    class CVBuilder {
        +build_tailored_html(job, profile)
        +compile_pdf_headless(html_path, output_pdf)
        +verify_pdf_geometry(pdf_path)
    }

    class DNSResolver {
        +dict domain_cache
        +set dummy_domains
        +resolve_socket(domain)
        +is_deliverable(email)
    }

    class LocalStorage {
        +Path app_data_dir
        +load_json(file)
        +save_json_atomic(file, data)
        +append_tracker_csv(entry)
    }

    PashaHuntGUI --> PashaBot : Invokes
    PashaBot --> CVBuilder : Compiles Resumes
    PashaBot --> DNSResolver : Pre-validates Emails
    PashaBot --> LocalStorage : Reads/Writes State
    PashaHuntGUI --> LocalStorage : Reflects Metrics
```

---

## 3. Autonomous Sourcing Matrix (18 Concurrent Feeds)

```mermaid
flowchart LR
    subgraph REMOTE_FEEDS ["Global Remote Aggregators"]
        R1["Remotive API"]
        R2["RemoteOK API"]
        R3["Himalayas Feed"]
        R4["Arbeitnow API"]
        R5["Jobicy Feed"]
    end

    subgraph SPECIALIZED_FEEDS ["Specialized Tech Platforms"]
        S1["WeWorkRemotely"]
        S2["WorkingNomads"]
        S3["4DayWeek"]
        S4["Workew"]
    end

    subgraph ENTERPRISE_ATS ["Direct Enterprise ATS Scrapers"]
        E1["Greenhouse Boards"]
        E2["Lever Portals"]
        E3["Workday Jobs"]
        E4["Ashby Systems"]
    end

    subgraph REGIONAL_COMMUNITY ["Pakistan Regional Hubs"]
        P1["Lahore/PK Tech Houses<br/>(InvoZone, Systems Ltd, CureMD, etc.)"]
        P2["Facebook Developer Communities"]
        P3["Hacker News (Algolia Search)"]
        P4["Google Search (Gemini Live)"]
    end

    REMOTE_FEEDS & SPECIALIZED_FEEDS & ENTERPRISE_ATS & REGIONAL_COMMUNITY --> POOL["ThreadPoolExecutor (Concurrency: 16 Workers)"]
    POOL --> DEDUP["Global Key Deduplicator & Hash Store"]
```

---

## 4. Socket DNS MX Email Deliverability Engine

```mermaid
sequenceDiagram
    autonumber
    participant Scraper as Sourcing Feed
    participant Bot as Bot Engine
    participant Cache as In-Memory _domain_cache
    participant Socket as OS Socket Subsystem
    participant DNS as Local/Gateway DNS Server
    participant UI as Dashboard View

    Scraper->>Bot: Job Raw Record { company: 'InvoZone', email: 'careers@invozone.com' }
    Bot->>Bot: Extract FQDN -> 'invozone.com'
    Bot->>Bot: Check Dummy Blacklist (company.com, etc.)
    Bot->>Cache: Lookup 'invozone.com'
    
    alt Domain in Cache
        Cache-->>Bot: Return Cached Verdict (True/False)
    else Domain Uncached
        Bot->>Socket: socket.getaddrinfo('invozone.com', 80)
        Socket->>DNS: Resolve A / MX Records
        DNS-->>Socket: IP 104.21.58.12 (Resolved)
        Socket-->>Bot: Socket Address Tuple
        Bot->>Cache: Store 'invozone.com' -> True
    end
    
    alt Domain Deliverable
        Bot-->>UI: job.email = 'careers@invozone.com'<br/>job.email_verified = True
        UI-->>UI: Render [✔ Verified Recruiter Domain] in Neon Emerald
    else Resolution Failed
        Bot-->>UI: job.email = ''<br/>job.email_verified = False
        UI-->>UI: Render [Apply on company portal link] in Vivid Amber
    end
```

---

## 5. Multi-Model AI Routing & Zero-Hallucination Hierarchy

```mermaid
flowchart TD
    Prompt["Tailoring Prompt (Job Description + Candidate Master Profile)"] --> Primary{"Try Tier 1:<br/>Apinex Gemini 3.8 Flash"}
    
    Primary -- Success --> ValidateResponse["Validate JSON Schema & Fact Guardrails"]
    Primary -- 429 / Timeout / Network Fail --> Secondary{"Try Tier 2:<br/>DeepSeek V4.1 Flash"}
    
    Secondary -- Success --> ValidateResponse
    Secondary -- Error --> Tertiary{"Try Tier 3:<br/>Google Gemini 2.5 Flash Native"}
    
    Tertiary -- Success --> ValidateResponse
    Tertiary -- Error --> OfflineFallback["Tier 4: Offline Deterministic Fallback<br/>(_generate_master_cv_fallback)"]
    
    ValidateResponse -- Fact Hallucination Detected --> RejectHallucination["Strip Unverified Claims / Revert to Master Profile"]
    ValidateResponse -- Valid --> ApprovedContent["Approved Tailored Resume & Pitch Content"]
    OfflineFallback --> ApprovedContent
```

> [!NOTE]
> **Anti-Hallucination Protocol:** The LLM is strictly constrained from inventing new companies, dates of employment, universities, or unverified technical skills. Its scope is restricted to:
> 1. Selecting the most relevant projects for the target role.
> 2. Re-ordering bullet points based on JD technology overlap.
> 3. Crafting a personalized introduction paragraph highlighting verified qualifications.

---

## 6. Headless Chromium / Edge Print Compilation Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant Tailor as AI Tailoring Engine
    participant CV as cv.py (DOM Builder)
    participant Temp as %TEMP%\pasha_hunt_sandbox\
    participant Edge as msedge.exe / chrome.exe
    participant FS as Local Filesystem (cvs/)

    Tailor->>CV: Structured Tailored Candidate JSON
    CV->>CV: Render HTML5 + Print CSS Template (A4 Dimensions)
    CV->>Temp: Write index.html with inline fonts & SVG icons
    CV->>Edge: Launch: msedge.exe --headless=new --print-to-pdf=dest.pdf --no-pdf-header-footer
    Edge->>Edge: Rasterize Layout & Embed Vector Fonts
    Edge->>FS: Write cvs/Company_Role_CV.pdf (<200KB)
    CV->>Temp: Cleanup temporary HTML sandbox
    CV-->>Tailor: Validated PDF Path Ready for MIME Attachment
```

---

## 7. Windows 11 DWM Immersive Dark Architecture

```mermaid
flowchart LR
    TkRoot["Tkinter Main Window (root)"] --> Win32Get["ctypes.windll.user32.GetParent(hwnd)"]
    Win32Get --> HWND["Native Top-Level Windows HWND"]
    
    HWND --> DWM_Dark["DWMWA_USE_IMMERSIVE_DARK_MODE (20)<br/>Value: TRUE"]
    HWND --> DWM_Color["DWMWA_CAPTION_COLOR (35)<br/>BGR: 0x00190F0B (Obsidian Void #0B0F19)"]
    
    DWM_Dark & DWM_Color --> DWM_API["DwmSetWindowAttribute() in dwmapi.dll"]
    DWM_API --> BeautifulUI["Seamless Windows 11 Obsidian Dark Frame"]
```

---

## 8. Build, Release & Packaging CI/CD Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Chief Architect / Agent
    participant PyI as PyInstaller Compiler
    participant Spec as PashaHunt.spec
    participant Sync as sync_release.ps1
    participant Inno as Inno Setup 6 (ISCC.exe)
    participant Git as GitHub Remote (origin/main)

    Dev->>PyI: pyinstaller --noconfirm PashaHunt.spec
    PyI->>Spec: Parse hooks, DLLs, hidden imports (pypdf, opencv, PIL)
    PyI-->>Dev: dist/PashaHunt/ (Standalone Windows Binaries)
    
    Dev->>Sync: powershell -ExecutionPolicy Bypass sync_release.ps1
    Sync-->>Sync: Kill active PashaHunt.exe processes
    Sync-->>Sync: Sync binaries to Pasha_Hunt_Release/ and Local Programs
    Sync-->>Dev: Portable folder, desktop shortcut & start menu synced
    
    Dev->>Inno: ISCC.exe installer/PashaHunt.iss
    Inno-->>Dev: PashaHuntSetup_v2.0.exe (Enterprise Setup Installer)
    
    Dev->>Git: git add & git commit & git push origin main
    Git-->>Dev: Remote Repository Fully Synchronized
```

---
*End of System Architecture Specification — Pasha Hunt 2.0*
