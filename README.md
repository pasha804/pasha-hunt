# 🦅 Pasha Hunt 2.0: Autonomous AI Career Agent & Job Hunter Platform

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white)](#installation--setup)
[![AI Core](https://img.shields.io/badge/AI%20Core-Gemini%202.5%20%2F%20Apinex-8E75B2.svg?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![UI Architecture](https://img.shields.io/badge/UI-Luxury%20Royal%20Dark%20Tkinter-540D6E.svg?style=for-the-badge)](#-bespoke-user-interface)
[![Build Status](https://img.shields.io/badge/Build-Production%20v2.0-06D6A0.svg?style=for-the-badge)](#installation--setup)

**An autonomous, production-grade desktop AI career agent that continuously aggregates live tech opportunities from 16+ channels, discovers verified recruiter inboxes, fact-grounds tailored ATS resumes & cover letters, and automates Gmail application pipelines.**

[Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Installation & Setup](#-installation--setup) • [Configuration Guide](#-configuration-guide) • [Security & Privacy](#-security--privacy-first)

---

</div>

## 📌 Executive Summary

Job hunting in modern tech is broken: candidate portals are flooded with opaque ATS filters, third-party job boards intentionally strip direct contact emails, and generic AI cover letters trigger automatic rejections.

**Pasha Hunt 2.0** solves this paradigm by operating as a local, autonomous desktop career intelligence agent. It monitors 16+ live channels concurrently, uses socket-level DNS lookups to recover corporate domains, executes strict fact-grounded LLM inference to craft mathematically verified ATS resumes, and pre-populates tailored application emails directly into your Gmail drafts for single-click review and submission.

---

## ⚡ Key Features

### 1. 🌐 Multi-Channel Autonomous Sourcing Engine
* **16+ Concurrent Ingestion Feeds**: Continuously polls Hacker News (*Who is hiring?* Algolia thread), Remotive, Jobicy, RemoteOK, Arbeitnow, Himalayas, WeWorkRemotely, WorkingNomads, TheMuse, and community RSS feeds.
* **AI-Ground Google Search**: Integrates Gemini-powered Google Search to discover unlisted tech openings across Pakistan (Lahore, Karachi, Islamabad) and worldwide remote ecosystems (LinkedIn, Indeed, software houses).
* **Seeker Discard Protocol**: Built-in AST filters automatically purge "Seeking Work" / "Freelancer Available" noise, indexing exclusively verified employers.

### 2. 🛡️ Fact-Grounded Anti-Hallucination ATS Engine
* **Mathematical Fact Grounding**: Unlike generic chatbots that hallucinate metrics and experiences, Pasha Hunt's validation layer compares every generated resume bullet against your raw `profile.json` facts. Any unverified skill or inflated claim is stripped automatically.
* **Pixel-Perfect PDF Generation**: Uses headless browser print pipelines to compile clean, ATS-compliant, single-page or two-page PDF resumes and tailored cover letters with proper typographic hierarchy.
* **Role-Specific Keywords**: Dynamically surfaces relevant skills and experience bullets tailored to the target role's tech stack.

### 3. ✉️ 1-Click Direct Email Application & DNS Crawler
* **Company Domain Recovery**: If a job board strips the company URL, Pasha Hunt resolves the company name to its real corporate domain (`.com`, `.io`, `.ai`, `.com.pk`, `.pk`) via asynchronous DNS socket queries.
* **Recruiter Inbox Discovery**: Crawls company career and contact endpoints to find real hiring emails (`careers@`, `jobs@`, `hr@`, `talent@`), enabling direct recruiter outreach and skipping saturated web portals.
* **Seamless Gmail Integration**: Generates complete application drafts—tailored subject line, custom cover letter body, and attached tailored PDF CV—straight into your personal Gmail drafts folder via IMAP/SMTP.

### 4. 📡 Real-Time Recruiter Response Radar (IMAP Tracker)
* **Live Status Monitoring**: Monitors your Gmail inbox in real time, detecting incoming recruiter responses, interview invitations, or application status updates.
* **Interactive Dashboard**: Color-coded tracking tags (`🎉 Reply Received`, `📤 Sent`, `✉ Drafted`, `✅ Applied`) keep your pipeline organized without manual spreadsheets.

### 5. 🎯 AI Interview Battle-Pack & Quick Apply Pack
* **AI Interview Battle-Pack**: Generates a tailored 60-second elevator pitch, top 5 behavioral/technical STAR questions & answers, and smart questions to ask the interviewer.
* **Quick Apply Profile Pack**: One-click clipboard copy buttons for rapid online form filling (Name, Phone, Portfolio, LinkedIn, GitHub, Short Bio, Tech Stack).

### 6. 💎 Bespoke User Interface
* **Windows 11 Luxury Theme**: Hand-crafted 5-color dark luxury palette:
  - `Royal Violet (#540D6E)` • `Jungle Mint (#06D6A0)` • `Coral Red (#EE4266)` • `Vivid Gold (#FFD23F)` • `Obsidian (#0E0917)`
* **High-DPI Adaptive**: Pure Tkinter with native Windows DPI awareness, custom Canvas badges, and responsive layouts—zero heavy Electron or webview bloat.

---

## 🏗 System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             PASHA HUNT 2.0 AGENT CORE                            │
└──────────────────────────────────────────────────────────────────────────────────┘
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
 ┌───────────────┐                                                ┌───────────────┐
 │ 16+ Job Feeds │ (HN Algolia, RemoteOK, Remotive, WWR...)       │ Gemini Search │ (Google Grounding, PK Tech)
 └───────┬───────┘                                                └───────┬───────┘
         │                                                                │
         └───────────────────────────────┬────────────────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │       Deduplication & Prefilter Engine        │
                 │ (Title Match, Work Mode, YOE, Country Filter) │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │          DNS & Email Crawler Pipeline         │
                 │  - Socket Domain Resolution (socket.gethost)  │
                 │  - Regex Crawler (careers@, hr@, talent@)     │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │       Fact-Grounded AI Tailoring Engine       │
                 │  - Strict Zero-Hallucination JSON Validator   │
                 │  - Dynamic ATS Keyword Alignment              │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │           Headless Browser PDF Engine         │
                 │  - Pixel-Perfect ATS-Friendly CV & Letter     │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │          Gmail IMAP / SMTP Integration        │
                 │  - Pre-populates Gmail Draft + PDF Attachment │
                 │  - Recruiter Response Radar & Reply Tracker   │
                 └───────────────────────────────────────────────┘
```

---

## 🚀 Installation & Setup

### Option 1: Standalone Windows Installer (Recommended)
Download and run the official Windows installer:
* **Installer**: `PashaHuntSetup_v2.0.exe`
* Automatically installs desktop shortcuts, Start Menu integration, and native Windows visual manifests.

### Option 2: Portable Windows Binary
Download the pre-compiled portable package:
* Extract `Pasha_Hunt_v2.0_Portable.zip`
* Launch `PashaHunt.exe` directly—no Python installation or dependencies required!

### Option 3: Run From Source (Developers)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/pasha804/pasha-hunt.git
   cd pasha-hunt
   ```

2. **Set Up Python Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   copy config.example.json config.json
   copy profile.example.json profile.json
   ```

4. **Launch Pasha Hunt**:
   ```bash
   python jobhunter.py
   ```

---

## ⚙ Configuration Guide

Pasha Hunt is designed to be fully configurable through `config.json` and the in-app settings UI:

```json
{
  "gmail_address": "your.email@gmail.com",
  "gmail_app_password": "xxxx xxxx xxxx xxxx",
  "imap_host": "imap.gmail.com",
  "gemini_api_key": "YOUR_GEMINI_OR_APINEX_API_KEY",
  "gemini_model": "gemini-2.5-flash",
  "work_modes": ["remote", "hybrid", "onsite"],
  "keywords": [
    "Full Stack Developer",
    "Software Engineer",
    "Python Developer",
    "FastAPI",
    "React Developer",
    "AI Agent Developer"
  ],
  "exclude_keywords": ["PHP", "WordPress", "Magento"],
  "keywords_in_title": true,
  "max_job_age_days": 30,
  "max_years_required": 4,
  "my_region_words": ["lahore", "pakistan", "worldwide"],
  "search_google": true
}
```

> **Note on Gmail App Passwords:** Standard Gmail passwords will not work with IMAP/SMTP. Generate a 16-character **App Password** from your Google Account settings: `Security -> 2-Step Verification -> App Passwords`.

---

## 🔒 Security & Privacy First

* **100% Local Execution**: All parsing, filtering, PDF compilation, and IMAP communications run strictly on your local machine.
* **No Unsolicited Automated Sending**: Pasha Hunt **never sends emails automatically**. It drafts emails into your Gmail account so you maintain 100% human-in-the-loop control over what gets sent.
* **Credential Protection**: All API keys, tokens, and app passwords are stored strictly on your local filesystem and ignored by `.gitignore`.

---

## 🛠 Tech Stack

| Domain | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core agentic loops, threading, network protocols |
| **Desktop GUI** | Tkinter / TTK Canvas | Native Windows 11 luxury dark-themed UI, zero heavy webview |
| **AI Inference** | Google Gemini 2.5 Flash / Apinex | High-speed, structured resume tailoring and job grounding |
| **PDF Generation** | Headless Chromium / MS Edge | High-fidelity ATS-compliant PDF document compilation |
| **Email Protocol** | IMAP4 / SMTP (SSL/TLS) | Draft creation, folder synchronization, recruiter response parsing |
| **Packaging** | PyInstaller + Inno Setup 6 | Native Windows single-file portable and setup installer |

---

## 👨‍💻 Author & Credits

**Muhammad Mubashar**
* **GitHub**: [@pasha804](https://github.com/pasha804)
* **LinkedIn**: [linkedin.com/in/pasha-dev](https://linkedin.com/in/pasha-dev)
* **Portfolio**: [pasha-portfolio-v6.netlify.app](https://pasha-portfolio-v6.netlify.app)
* **Role**: AI Agentic Developer & Full-Stack Software Engineer

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to customize, fork, and build upon it!
