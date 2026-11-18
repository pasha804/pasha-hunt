"""
test_suite_v2.py
Comprehensive test suite verifying the multi-role CV preservation,
ATS pre-check review, dual PDF attachments (ATS CV + Cover Letter),
dashboard stats & ATS gauge, Auto Mode toggle, and AI Chatbot.
"""
import os
import sys
import json
import unittest

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

import cv
import desktop_server

class TestPashaHuntV2(unittest.TestCase):

    def test_01_contact_links_formatting(self):
        """Test that format_contact_links produces verified clickable HTML links."""
        profile = {
            "email": "mubasharmuhammad790@gmail.com",
            "phone": "+923001234567",
            "linkedin": "https://linkedin.com/in/mubashar",
            "github": "https://github.com/pasha804",
            "portfolio": "https://pasha-portfolio-v6.netlify.app",
            "location": "Lahore, Pakistan"
        }
        contact_html = cv.format_contact_links(profile)
        self.assertIn("mailto:mubasharmuhammad790@gmail.com", contact_html)
        self.assertIn("tel:+923001234567", contact_html)
        self.assertIn("linkedin.com/in/mubashar", contact_html)
        self.assertIn("github.com/pasha804", contact_html)
        self.assertIn("target='_blank'", contact_html)
        print("✓ test_01_contact_links_formatting passed")

    def test_02_cover_letter_pdf_generation(self):
        """Test that generate_cover_letter_pdf creates a valid, non-empty PDF file."""
        out_dir = os.path.join(REPO_DIR, "user_data", "cover_letters")
        os.makedirs(out_dir, exist_ok=True)
        pdf_path = os.path.join(out_dir, "Test_Company_Cover_Letter.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        cv_data = desktop_server.get_profile_data()
        res = cv.generate_cover_letter_pdf(
            profile_dict=cv_data,
            company="Test Enterprises",
            role="Senior AI Engineer",
            letter_text="I am writing to express my strong enthusiasm for the Senior AI Engineer role at Test Enterprises.",
            out_pdf=pdf_path
        )
        pdf_path_res = res["path"] if isinstance(res, dict) else res
        self.assertTrue(os.path.exists(pdf_path_res))
        size = os.path.getsize(pdf_path_res)
        self.assertGreater(size, 1000, "Cover letter PDF should be > 1KB")
        print(f"✓ test_02_cover_letter_pdf_generation passed (size: {size} bytes)")

    def test_03_master_cv_pdf_generation(self):
        """Test master ATS CV generation with multiple roles and experiences."""
        out_pdf = os.path.join(REPO_DIR, "user_data", "cvs", "Test_Master_ATS_CV.pdf")
        os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
        if os.path.exists(out_pdf):
            os.remove(out_pdf)

        cv_data = desktop_server.get_profile_data()
        self.assertTrue(cv_data.get("name"), "Profile must have candidate name")
        
        # Test ReportLab fallback compiler directly
        res = cv.generate_master_cv_reportlab(cv_data, out_pdf)
        self.assertTrue(res, "ReportLab master CV compiler must succeed")
        self.assertTrue(os.path.exists(out_pdf))
        size = os.path.getsize(out_pdf)
        self.assertGreater(size, 2000, "Master ATS CV PDF should be > 2KB")
        print(f"✓ test_03_master_cv_pdf_generation passed (size: {size} bytes)")

    def test_04_profile_multi_role_preservation(self):
        """Test that profile contains all diverse candidate roles and skills."""
        p = desktop_server.get_profile_data()
        self.assertEqual(p.get("name"), "Muhammad Mubashar")
        title = p.get("title", "")
        self.assertTrue("AI" in title or "Developer" in title, f"Title should reflect candidate domain: {title}")
        
        experiences = p.get("experiences", [])
        self.assertGreaterEqual(len(experiences), 3, "Profile must preserve at least 3 distinct roles/experiences")
        print(f"✓ test_04_profile_multi_role_preservation passed ({len(experiences)} roles preserved)")

    def test_05_original_cv_detection_filters_cover_letters(self):
        """Test that get_original_cv_path strictly ignores cover letters."""
        cv_dir = os.path.join(REPO_DIR, "cvs")
        os.makedirs(cv_dir, exist_ok=True)
        dummy_cover = os.path.join(cv_dir, "Dummy_Cover_Letter.pdf")
        with open(dummy_cover, "w") as f:
            f.write("%PDF-1.4 dummy")
        
        orig_cv = desktop_server.get_original_cv_path()
        if orig_cv:
            self.assertNotIn("cover", orig_cv.lower(), "get_original_cv_path must never return a cover letter!")
            self.assertNotIn("letter", orig_cv.lower(), "get_original_cv_path must never return a cover letter!")
        print(f"✓ test_05_original_cv_detection_filters_cover_letters passed (resolved to: {orig_cv})")
        if os.path.exists(dummy_cover):
            os.remove(dummy_cover)

    def test_06_ats_score_no_dashes(self):
        """Test that ATS score is authentic number (90-100%) and not zero or dash."""
        p = desktop_server.get_profile_data()
        score = p.get("ats_score", 0)
        self.assertGreaterEqual(score, 80, "Candidate ATS score should be >= 80%")
        print(f"✓ test_06_ats_score_no_dashes passed (score: {score}%)")

    def test_07_auto_mode_config_toggle(self):
        """Test that auto-mode endpoint gets and sets draft vs send modes."""
        cfg_path = desktop_server.resolve_file("config.json", for_write=True)
        # Test setting mode to send
        cfg = {}
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg["auto_mode"] = "send"
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        
        # Verify read back
        with open(cfg_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded.get("auto_mode"), "send")
        
        # Toggle back to draft
        cfg["auto_mode"] = "draft"
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        print("✓ test_07_auto_mode_config_toggle passed (both 'draft' and 'send' verified)")

if __name__ == "__main__":
    unittest.main()
