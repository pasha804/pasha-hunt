# Privacy Policy — Pasha Hunt

**Last Updated:** November 17, 2026  
**Effective Date:** November 17, 2026  
**Author & Data Controller:** Muhammad Mubashar ([@pasha804](https://github.com/pasha804))  
**Contact Email:** [mubasharmuhammad790@gmail.com](mailto:mubasharmuhammad790@gmail.com)  
**Project Repository:** [https://github.com/pasha804/pasha-hunt](https://github.com/pasha804/pasha-hunt)

---

## 1. Overview & Core Philosophy

**Pasha Hunt** ("the Software", "Pasha Hunt 2.0 / 3.0", "Pasha Hunt Anna Edition") is engineered from the ground up as a **Local-First, Zero-Telemetry Autonomous Career Workstation**.

We believe your career data, professional resume, personal identity, and recruiter outreach communications belong exclusively to **you**. Unlike traditional SaaS platforms that ingest your resume into central databases to train third-party models or sell candidate data to recruitment brokers, Pasha Hunt runs locally on your own machine.

---

## 2. Information We Handle & How It Is Handled

### 2.1. Candidate Profile Data (`profile.json`)
* **What is stored:** Full name, contact email, phone number, location, portfolio links, work experience history, education, projects, and technical skills.
* **Storage Location:** Strictly stored on your local disk in `profile.json`.
* **Data Transmission:** This data is never sent to any central Pasha Hunt analytics or tracking server. When tailoring resumes or cover letters, relevant fragments are transmitted strictly to your chosen AI model provider (e.g. Google Gemini API via official endpoints) using your private API key.

### 2.2. Credentials & API Keys (`config.json`)
* **What is stored:** Google Gemini API keys, Apinex API keys, Gmail IMAP/SMTP credentials (App Passwords).
* **Storage Location:** Stored exclusively in local plaintext/environment configurations on your local filesystem.
* **Protection:** These files are protected by `.gitignore` to prevent inadvertent source code repository commits. Credentials are never mirrored, harvested, or proxied through any external servers.

### 2.3. Gmail IMAP / SMTP Integration
* **Limited Scope:** Pasha Hunt interacts with Gmail solely to search for recruiter responses (`Recruiter Radar`) and to prepare pre-populated application drafts (`Drafts Folder`).
* **Human-in-the-Loop Principle:** Pasha Hunt **never sends emails automatically without explicit user intervention**. All emails are created as local drafts in your personal Gmail account so you retain 100% review and approval control prior to submission.
* **Google API Compliance:** Pasha Hunt complies with Google API Services User Data Policy, adhering strictly to the principle of least privilege.

### 2.4. Stealth Web Crawling & Public Job Feeds (Scrapling Engine)
* **What is gathered:** Publicly available job postings, corporate recruiter email endpoints (e.g., `careers@`, `talent@`), and job descriptions from public web pages.
* **Scope:** The scraper extracts publicly listed job parameters solely to match opportunities against your local candidate preferences.

---

## 3. Third-Party Services & Integrations

Pasha Hunt connects to the following external APIs solely at your direction:
1. **Google Gemini API / Google AI Studio:** Used for LLM-based structured resume tailoring, job keyword alignment, and interview battle-pack synthesis. Subject to [Google AI Terms of Service and Privacy Policy](https://policies.google.com/privacy).
2. **Public Job Ingestion Endpoints (RSS / APIs):** Hacker News Algolia, Remotive, Jobicy, RemoteOK, Arbeitnow, Himalayas, and public ATS portals (Greenhouse, Lever, Workday).
3. **Anna AI OS (For Anna Edition App Users):** When invoked as an Anna Executa / Tool inside the Anna AI OS ecosystem, execution follows the Anna AI OS sandboxed capability declarations. No unprompted local filesystem access or background surveillance is executed.

---

## 4. Telemetry, Tracking & Analytics

* **No Tracking Cookies:** Pasha Hunt desktop and web workstation interfaces contain zero tracking cookies, marketing pixels, or fingerprinting scripts.
* **No Diagnostic Uploads:** Crash logs and audit reports (`run_qa_audit.py`, `runs.log`) reside locally on your device and are never automatically transmitted to any remote logging service.

---

## 5. Data Retention & Deletion

Because all candidate databases, jobs history (`jobs.json`), cover letters (`cover_letters.json`), and generated PDFs are stored locally on your device:
* You have absolute control over data retention.
* To permanently erase all Pasha Hunt data, simply delete the local application folder or configuration files (`config.json`, `profile.json`, `jobs.json`, `cvs/`).

---

## 6. Security

* **Local Sandbox:** Pasha Hunt executes within your operating system's standard user permissions.
* **Encryption in Transit:** All external communication (Gemini API, IMAP/SMTP mail servers, HTTPS job feeds) uses industry-standard TLS/SSL encryption.
* **Private Repositories:** Proprietary user code and configuration files are fully supported within private repositories; no public disclosure of proprietary intellectual property is required.

---

## 7. Compliance

* **GDPR (General Data Protection Regulation):** Users retain the right of access, rectification, portability, and erasure since all personal data is held locally by the user (data subject is the sole controller).
* **CCPA / CPRA:** We do not sell, rent, or monetize personal information. Zero data brokerage.

---

## 8. Contact & Inquiries

For any questions, concerns, or inquiries regarding this Privacy Policy or Pasha Hunt's architecture, contact:

* **Maintainer:** Muhammad Mubashar
* **Email:** [mubasharmuhammad790@gmail.com](mailto:mubasharmuhammad790@gmail.com)
* **GitHub Issues:** [https://github.com/pasha804/pasha-hunt/issues](https://github.com/pasha804/pasha-hunt/issues)
* **Discord Community:** [Anna AI OS Builder Discord](https://discord.gg/7ftTdsdMMz) (`@PASHA X ARAIN`)
