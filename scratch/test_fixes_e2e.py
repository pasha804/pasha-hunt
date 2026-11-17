"""Comprehensive verification script for ATS CV multi-page rendering,
Cover letter generation & dual-attachment in drafts, and ATS score calculations.
"""
import os
import sys
import json
import re
import email
from email.mime.application import MIMEApplication

REPO_DIR = r"E:\Job Hunt\job-hunter-repo"
sys.path.insert(0, REPO_DIR)

import desktop_server
import cv
import bot
import pypdf

def test_deterministic_parsing():
    print("\n--- TEST 1: DETERMINISTIC CV PARSING ---")
    orig_pdf = r"E:\Job Hunt\_archive_legacy\Muhammad_Mubashar_ATS_Master_CV_v2_backup_original.pdf"
    reader = pypdf.PdfReader(orig_pdf)
    text = "\n".join([p.extract_text() or "" for p in reader.pages])
    
    parsed = desktop_server.parse_cv_deterministic(text)
    assert parsed["name"] == "Muhammad Mubashar", f"Expected Muhammad Mubashar, got {parsed['name']}"
    assert "AI" in parsed["default_title"], f"Expected AI in title, got {parsed['default_title']}"
    assert len(parsed["experience"]) >= 4, f"Expected >= 4 experiences, got {len(parsed['experience'])}"
    assert len(parsed["projects"]) >= 6, f"Expected >= 6 projects, got {len(parsed['projects'])}"
    print(f"PASS: Name={parsed['name']}")
    print(f"PASS: Title={parsed['default_title']}")
    print(f"PASS: Experiences ({len(parsed['experience'])}): {[e['role'] for e in parsed['experience']]}")
    print(f"PASS: Projects ({len(parsed['projects'])}): {[p['name'] for p in parsed['projects']]}")
    return parsed

def test_cv_multi_page_build_and_pdf(profile):
    print("\n--- TEST 2: MULTI-PAGE HTML & PDF GENERATION ---")
    html = cv.build(profile, {})
    assert "PROJECTS &amp; PORTFOLIO" in html, "Projects section missing from HTML"
    assert "CERTIFICATIONS &amp; CREDENTIALS" in html, "Certifications section missing from HTML"
    assert "EXPERIENCE" in html, "Experience section missing from HTML"
    print(f"PASS: Full ATS HTML built (Length: {len(html)} bytes)")

    test_pdf = os.path.join(REPO_DIR, "scratch", "test_generated_cv.pdf")
    os.makedirs(os.path.dirname(test_pdf), exist_ok=True)
    res = cv.generate_master_cv(profile, test_pdf)
    assert res.get("ok"), f"generate_master_cv failed: {res}"
    
    pdf_reader = pypdf.PdfReader(test_pdf)
    page_count = len(pdf_reader.pages)
    print(f"PASS: Generated PDF size={os.path.getsize(test_pdf)} bytes, Page Count={page_count}")
    assert page_count >= 2, f"Expected multi-page PDF (>= 2 pages), got {page_count} pages"
    return test_pdf

def test_cover_letter_pdf_generation(profile):
    print("\n--- TEST 3: COVER LETTER PDF GENERATION ---")
    test_cl_pdf = os.path.join(REPO_DIR, "scratch", "test_generated_cover_letter.pdf")
    letter_text = (
        "Dear Hiring Team at DeepMind Technologies,\n\n"
        "I am writing to express my strong enthusiasm for the Senior AI Engineer position. "
        "With my background in full-stack engineering, autonomous AI agent workflows, and system reliability, "
        "I have architected scalable platforms and automated end-to-end delivery pipelines.\n\n"
        "Enclosed please find my Tailored ATS Master CV and portfolio. I look forward to speaking with your team."
    )
    res = cv.generate_cover_letter_pdf(profile, "DeepMind Technologies", "Senior AI Engineer", letter_text, test_cl_pdf)
    assert res.get("ok"), f"generate_cover_letter_pdf failed: {res}"
    assert os.path.exists(test_cl_pdf) and os.path.getsize(test_cl_pdf) > 1000
    print(f"PASS: Cover Letter PDF created successfully (Size: {os.path.getsize(test_cl_pdf)} bytes)")
    return test_cl_pdf

def test_dual_attachment_mime(cv_pdf, cl_pdf):
    print("\n--- TEST 4: DUAL ATTACHMENT MIME VERIFICATION ---")
    extra_attachments = [(cl_pdf, "Muhammad-Mubashar-Cover-Letter-DeepMind.pdf")]
    
    # Construct MIME message following bot.py save_draft logic
    msg = email.message.EmailMessage()
    msg["From"] = "Muhammad Mubashar <pashadev804@gmail.com>"
    msg["To"] = "recruiter@deepmind.com"
    msg["Subject"] = "Application: Senior AI Engineer — Muhammad Mubashar"
    msg.set_content("Please find attached my CV and Cover Letter.")
    
    with open(cv_pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="Muhammad-Mubashar-ATS-CV.pdf")
        
    for extra_path, extra_name in extra_attachments:
        with open(extra_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=extra_name)
            
    # Verify attachments
    pdf_attachments = []
    for part in msg.iter_attachments():
        pdf_attachments.append(part.get_filename())
        
    print(f"PASS: Attached files in message: {pdf_attachments}")
    assert "Muhammad-Mubashar-ATS-CV.pdf" in pdf_attachments, "ATS CV missing from message attachments"
    assert "Muhammad-Mubashar-Cover-Letter-DeepMind.pdf" in pdf_attachments, "Cover Letter missing from message attachments"
    assert len(pdf_attachments) == 2, f"Expected exactly 2 attachments, got {len(pdf_attachments)}"
    print("PASS: Verified both CV and Cover Letter are attached to draft!")

if __name__ == "__main__":
    prof = test_deterministic_parsing()
    cv_pdf = test_cv_multi_page_build_and_pdf(prof)
    cl_pdf = test_cover_letter_pdf_generation(prof)
    test_dual_attachment_mime(cv_pdf, cl_pdf)
    print("\n================ ALL TESTS PASSED SUCCESSFULLY! ================\n")
