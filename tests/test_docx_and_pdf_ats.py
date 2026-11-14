import os
import sys
import docx
import io
import json
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

import desktop_server
import cv

def test_word_doc_cv():
    # 1. Create a sample .docx in memory
    doc = docx.Document()
    doc.add_heading("Muhammad Hasnain", level=0)
    doc.add_paragraph("Graphic Designer & Brand Identity Specialist")
    doc.add_paragraph("Email: hasnain@testagency.com | Phone: +92 336 7763874 | Lahore, Pakistan")
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph("Detail-oriented Graphic Designer with 2+ years of experience in branding, UI/UX, and marketing assets.")
    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Graphic Designer - Digital Creative Studio (2023 - Present)")
    doc.add_paragraph("• Created social media posts, branding guidelines, and visual assets for 20+ clients.")
    doc.add_paragraph("• Designed high-fidelity prototypes and UI kits using Figma and Illustrator.")
    doc.add_paragraph("• Managed multiple marketing design sprints under strict deadlines.")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("BS in Computer Science - University of Lahore")

    bio = io.BytesIO()
    doc.save(bio)
    docx_bytes = bio.getvalue()

    # 2. Extract paragraphs and tables like _handle_cv_upload does
    doc_read = docx.Document(io.BytesIO(docx_bytes))
    paragraphs = [p.text for p in doc_read.paragraphs if p.text.strip()]
    extracted_text = "\n".join(paragraphs)

    print("Extracted from Word Docx:")
    print(extracted_text[:200])

    # 3. Parse with Gemini ATS Engine
    parsed = desktop_server.parse_cv_with_gemini(extracted_text)
    print("\nParsed Result:")
    print("Name:", parsed.get("name"))
    print("Title:", parsed.get("default_title"))
    print("ATS Score:", parsed.get("ats_score"))
    print("Bullets:")
    for b in parsed.get("experience", [{}])[0].get("bullets", []):
        print("  -", b)

    assert parsed.get("name")
    assert parsed.get("ats_score") == 96
    assert len(parsed.get("experience", [])) > 0
    assert len(parsed["experience"][0]["bullets"]) > 0

    # 4. Generate Master PDF
    out_pdf = os.path.join(HERE, "test_generated_master_cv.pdf")
    res = cv.generate_master_cv(parsed, out_pdf)
    print("\nPDF Generation:", res)
    assert os.path.exists(out_pdf)
    size = os.path.getsize(out_pdf)
    print(f"Generated PDF size: {size} bytes")
    assert size > 1000

    print("\nWORD DOCX CV ATS CONVERSION VERIFIED 100%!")

if __name__ == "__main__":
    test_word_doc_cv()
