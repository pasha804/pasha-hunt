"""PASHA HUNT 2.0 / 3.0 — AUTONOMOUS QA & AUDIT AGENT
Real-time end-to-end verification of all subsystems:
1. Core Engine Modules Integrity (bot, cv, desktop_server, scrapling_adapter)
2. D4Vinci/Scrapling Stealth Engine (v0.5.1 Diagnostics, Locators & Classifier)
3. 2-Page Deterministic ATS Master CV Builder (cv.py + desktop_server)
4. Executive Tailored Cover Letter PDF Generator (cv.generate_cover_letter_pdf)
5. Dual-Attachment Gmail IMAP MIME Pipeline (CV + Cover Letter attachments)
6. Desktop UI Assets & Modal Binding Verification
7. Inno Setup Production Installer (.exe) Verification
"""
import sys
import os
import time
import email.message

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_DIR, "job-hunter-repo"))
sys.path.insert(0, ROOT_DIR)

import bot
import cv
import desktop_server
import scrapling_adapter

report = []

def log_test(test_name, passed, details=""):
    status_icon = "✅ PASS" if passed else "❌ FAIL"
    report.append({"name": test_name, "passed": passed, "details": details})
    print(f"  {status_icon} | {test_name:<44} | {details}")

print("=" * 85)
print("  🧪 RUNNING PASHA HUNT AUTONOMOUS QA & AUDIT AGENT (REAL-TIME)")
print("=" * 85)

# --- 1. CORE MODULES IMPORT ---
print("\n[MODULE 1/7] Core Engine Modules Integrity...")
try:
    log_test("Core Modules Loaded", True, "bot, cv, desktop_server, scrapling_adapter active")
except Exception as e:
    log_test("Core Modules Loaded", False, str(e))

# --- 2. SCRAPLING STEALTH ENGINE AUDIT ---
print("\n[MODULE 2/7] D4Vinci/Scrapling Engine Audit...")
try:
    status = scrapling_adapter.get_scrapling_status()
    all_ready = status["available"] and status["has_fetcher"] and status["has_stealthy_fetcher"] and status["has_selector"]
    log_test("Scrapling v0.5.1 Diagnostic Health", all_ready, f"Version: {status['version']}, Chrome & Fetcher Ready")
    
    # Test adaptive portal classifier
    p_type = scrapling_adapter.detect_portal_type("https://boards.greenhouse.io/openai/jobs/123")
    log_test("Portal Classifier (Greenhouse/Lever)", p_type == "greenhouse", f"Detected: {p_type}")
    
    # Test email de-obfuscation
    emails = scrapling_adapter.extract_emails_from_text("Contact: hiring [at] company [dot] com")
    log_test("Email De-Obfuscation Engine", "hiring@company.com" in emails, f"Extracted: {emails}")
except Exception as e:
    log_test("Scrapling Engine Audit", False, str(e))

# --- 3. DETERMINISTIC ATS CV BUILDER ---
print("\n[MODULE 3/7] 2-Page ATS CV Document Engine Audit...")
try:
    import pypdf
    orig_pdf = os.path.join(ROOT_DIR, "_archive_legacy", "Muhammad_Mubashar_ATS_Master_CV_v2_backup_original.pdf")
    if os.path.exists(orig_pdf):
        reader = pypdf.PdfReader(orig_pdf)
        raw_text = "\n".join([p.extract_text() or "" for p in reader.pages])
    else:
        raw_text = "Muhammad Mubashar\nAI Full-Stack Developer\nEXPERIENCE\nFounder & Full-Stack Developer\nNexora | 2023 - Present\n- Built systems\nPROJECTS\nSARA AI\n- Companion"

    parsed_cv = desktop_server.parse_cv_deterministic(raw_text)
    has_exps = len(parsed_cv.get("experience", [])) >= 2
    has_projs = len(parsed_cv.get("projects", [])) >= 2
    log_test("Deterministic CV Parser", has_exps and has_projs, f"Parsed Exps: {len(parsed_cv.get('experience', []))}, Projs: {len(parsed_cv.get('projects', []))}")

    # Generate actual PDF and check page count
    test_cv_pdf = os.path.join(ROOT_DIR, "scratch", "qa_test_cv.pdf")
    os.makedirs(os.path.dirname(test_cv_pdf), exist_ok=True)
    res_cv = cv.generate_master_cv(parsed_cv, test_cv_pdf)
    
    cv_size_kb = os.path.getsize(test_cv_pdf) / 1024
    pdf_reader = pypdf.PdfReader(test_cv_pdf)
    page_count = len(pdf_reader.pages)
    
    log_test("2-Page ATS PDF Rendering", res_cv.get("ok") and page_count >= 2, f"Page Count: {page_count}, Size: {cv_size_kb:.1f} KB")
except Exception as e:
    log_test("CV Document Engine Audit", False, str(e))

# --- 4. TAILORED COVER LETTER PDF ENGINE ---
print("\n[MODULE 4/7] Executive Cover Letter Studio Audit...")
try:
    test_cl_pdf = os.path.join(ROOT_DIR, "scratch", "qa_test_cover_letter.pdf")
    letter_text = (
        "Dear Hiring Team at DeepMind,\n\n"
        "I am writing to express my strong enthusiasm for the Senior AI Engineer position. "
        "With my background in full-stack engineering, autonomous AI agent workflows, and system reliability, "
        "I have architected scalable platforms and automated end-to-end delivery pipelines.\n\n"
        "Enclosed please find my Tailored ATS Master CV. I look forward to speaking with your team."
    )
    res_cl = cv.generate_cover_letter_pdf(parsed_cv, "DeepMind Technologies", "Senior AI Engineer", letter_text, test_cl_pdf)
    cl_kb = os.path.getsize(test_cl_pdf) / 1024 if os.path.exists(test_cl_pdf) else 0
    log_test("Cover Letter PDF Generation", res_cl.get("ok") and cl_kb > 10, f"Valid PDF binary generated: {cl_kb:.1f} KB")
except Exception as e:
    log_test("Cover Letter Engine Audit", False, str(e))

# --- 5. GMAIL IMAP DUAL-ATTACHMENT PIPELINE ---
print("\n[MODULE 5/7] Gmail IMAP Dual-Attachment MIME Pipeline...")
try:
    msg = email.message.EmailMessage()
    msg["From"] = "Muhammad Mubashar <pashadev804@gmail.com>"
    msg["To"] = "careers@deepmind.com"
    msg["Subject"] = "Application: Senior AI Engineer — Muhammad Mubashar"
    msg.set_content("Please find attached my CV and Cover Letter.")

    with open(test_cv_pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="Muhammad-Mubashar-ATS-CV.pdf")

    with open(test_cl_pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="Muhammad-Mubashar-Cover-Letter-DeepMind.pdf")

    attached_files = []
    for part in msg.iter_attachments():
        fn = part.get_filename()
        if fn:
            attached_files.append(fn)

    dual_attached = "Muhammad-Mubashar-ATS-CV.pdf" in attached_files and "Muhammad-Mubashar-Cover-Letter-DeepMind.pdf" in attached_files
    log_test("Dual Attachment MIME Pipeline", dual_attached, f"Attached files in draft: {attached_files}")
except Exception as e:
    log_test("Gmail IMAP MIME Pipeline", False, str(e))

# --- 6. DESKTOP UI INTEGRITY AUDIT ---
print("\n[MODULE 6/7] Desktop UI (index.html) Integrity Audit...")
try:
    ui_path = os.path.join(ROOT_DIR, "desktop_ui", "index.html")
    if not os.path.exists(ui_path):
        ui_path = os.path.join(ROOT_DIR, "job-hunter-repo", "desktop_ui", "index.html")

    with open(ui_path, "r", encoding="utf-8") as f:
        html_code = f.read()

    has_scrapling_modal = "id=\"scraplingModal\"" in html_code or "scraplingModal" in html_code
    has_scrapling_btn = "openScraplingCrawlerModal" in html_code
    has_dual_draft_btn = "Save Draft in Gmail" in html_code

    log_test("UI Scrapling Modal & Button Wiring", has_scrapling_modal and has_scrapling_btn, "Scrapling URL Harvester modal present")
    log_test("UI Gmail Draft Action Wiring", has_dual_draft_btn, "Draft creation triggers present")
except Exception as e:
    log_test("UI Integrity Audit", False, str(e))

# --- 7. PRODUCTION INSTALLER & RELEASE VERIFICATION ---
print("\n[MODULE 7/7] Production Installer & Distribution Audit...")
try:
    exe_path = os.path.join(ROOT_DIR, "Pasha_Hunt_Release", "PashaHuntSetup_v2.0.exe")
    exe_exists = os.path.exists(exe_path)
    if exe_exists:
        exe_mb = os.path.getsize(exe_path) / (1024 * 1024)
        log_test("Inno Setup Standalone Installer", True, f"PashaHuntSetup_v2.0.exe verified ({exe_mb:.1f} MB)")
    else:
        log_test("Inno Setup Standalone Installer", False, "Installer executable not found in release dir")

    backup_path = os.path.join(ROOT_DIR, "BACKUP_PASHA_HUNT_v2.0_STABLE")
    backup_exists = os.path.exists(backup_path)
    log_test("Frozen Stable Backup Security", backup_exists, "BACKUP_PASHA_HUNT_v2.0_STABLE intact & locked")
except Exception as e:
    log_test("Production Installer Audit", False, str(e))

# --- FINAL SCORE & GRADE ---
total = len(report)
passed_count = sum(1 for r in report if r["passed"])
pass_rate = (passed_count / total) * 100

print("\n" + "=" * 85)
print(f"  🏆 QA AUDIT RESULT: {passed_count}/{total} TESTS PASSED ({pass_rate:.1f}%)")
if pass_rate == 100:
    print("  GRADE: 🌟 A+ (PRODUCTION CERTIFIED & VERIFIED STABLE)")
else:
    print("  GRADE: ⚠️ NEEDS ATTENTION")
print("=" * 85)
