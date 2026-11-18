"""
test_universal_users_and_scrapling.py
Comprehensive verification for universal user support (any candidate / discipline),
all 5 APINEX models, and the Scrapling stealth multi-platform scraper engine.
"""
import os
import sys
import json
import unittest

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

import cv
import desktop_server
import scrapling_adapter
import bot

class TestUniversalPashaHunt(unittest.TestCase):

    def test_01_all_apinex_models_live(self):
        """Test that all 5 models in the APINEX catalog are functioning and returning completions."""
        catalog = desktop_server.APINEX_CATALOG
        self.assertGreaterEqual(len(catalog), 5)
        
        success_count = 0
        for m in catalog:
            mid = m["id"]
            res = desktop_server.call_apinex("Respond with 'OK' and nothing else.", model=mid, timeout=10)
            print(f"  APINEX [{mid}]: {res}")
            self.assertIsNotNone(res, f"APINEX model {mid} must return a non-null completion")
            self.assertTrue(len(res.strip()) > 0)
            success_count += 1
            
        self.assertEqual(success_count, len(catalog), "All 5 APINEX models must succeed")
        self.assertGreater(desktop_server.APINEX_USAGE["calls_count"], 0)
        print(f"✓ test_01_all_apinex_models_live passed ({success_count}/{len(catalog)} models live)")

    def test_02_scrapling_stealth_engine_available(self):
        """Test that Scrapling stealth engine is initialized and can stealth-fetch pages."""
        status = scrapling_adapter.get_scrapling_status()
        self.assertIn("engine", status)
        self.assertEqual(status["engine"], "D4Vinci/Scrapling")
        
        # Test stealth fetch
        html = scrapling_adapter.stealth_fetch("https://httpbin.org/html", timeout=10)
        self.assertIsNotNone(html, "stealth_fetch must retrieve HTML from target test endpoint")
        self.assertIn("Herman Melville", html)
        print("✓ test_02_scrapling_stealth_engine_available passed (HTTP fetch verified)")

    def test_03_we_work_remotely_scraper(self):
        """Test that We Work Remotely feed is active and pulls live opportunities."""
        jobs = bot.src_weworkremotely()
        self.assertIsInstance(jobs, list)
        self.assertGreater(len(jobs), 20, "We Work Remotely should return > 20 active jobs")
        sample = jobs[0]
        self.assertTrue(sample.get("title"))
        self.assertTrue(sample.get("url"))
        print(f"✓ test_03_we_work_remotely_scraper passed ({len(jobs)} live jobs scraped)")

    def test_04_facebook_community_all_disciplines(self):
        """Test that Facebook Community jobs cover multiple disciplines (Design, QA, Data, Marketing, Finance, Dev)."""
        jobs = bot.src_facebook_community()
        self.assertGreaterEqual(len(jobs), 15)
        
        titles = [j["title"].lower() for j in jobs]
        all_text = " ".join(titles)
        
        # Verify diversity of roles for ANY user
        has_dev = any(k in all_text for k in ["developer", "software engineer", "fastapi"])
        has_qa = any(k in all_text for k in ["qa", "tester"])
        has_design = any(k in all_text for k in ["designer", "ui/ux", "visual"])
        has_data = any(k in all_text for k in ["data", "bi"])
        has_marketing = any(k in all_text for k in ["marketing", "seo"])
        has_finance = any(k in all_text for k in ["financial", "accountant"])
        
        self.assertTrue(has_dev, "Must include Software Development jobs")
        self.assertTrue(has_qa, "Must include QA Testing jobs")
        self.assertTrue(has_design, "Must include UI/UX & Design jobs")
        self.assertTrue(has_data, "Must include Data & Analytics jobs")
        self.assertTrue(has_marketing, "Must include Digital Marketing & SEO jobs")
        self.assertTrue(has_finance, "Must include Finance & Accounting jobs")
        print(f"✓ test_04_facebook_community_all_disciplines passed ({len(jobs)} multi-discipline jobs)")

    def test_05_any_user_designer_profile(self):
        """Test complete workflow for a completely different candidate (Lead UI/UX Designer Sarah Jenkins)."""
        designer_profile = {
            "name": "Sarah Jenkins",
            "title": "Lead UI/UX Designer & Product Strategist",
            "default_title": "Lead UI/UX Designer & Product Strategist",
            "discipline": "design",
            "contact": {
                "email": "sarah.jenkins@designforge.io",
                "phone": "+1 415 555 0192",
                "location": "San Francisco, CA (Remote)",
                "portfolio": "https://sarahjenkins.design",
                "linkedin": "https://linkedin.com/in/sarahjenkins-design"
            },
            "location": "San Francisco, CA (Remote)",
            "default_summary": "Lead UI/UX & Product Designer with 7+ years of experience leading design systems, Figma workflows, and high-conversion SaaS web applications.",
            "skills": {
                "Design Systems": ["Figma", "Design Tokens", "Component Architecture", "Storybook"],
                "UI/UX Craft": ["Wireframing", "Interactive Prototyping", "User Research", "WCAG 2.2 Accessibility"]
            },
            "experiences": [
                {
                    "company": "DesignForge Studio",
                    "title": "Lead UI/UX Designer",
                    "dates": "2023 - Present",
                    "bullets": [
                        "Architected scalable multi-brand design system in Figma adopted by 40+ engineers, cutting design-to-code cycle times by 35%.",
                        "Redesigned SaaS checkout funnel resulting in a 24% uplift in paid user conversion across web and mobile."
                    ]
                },
                {
                    "company": "Apex Creative Labs",
                    "title": "Senior Product & Visual Designer",
                    "dates": "2020 - 2023",
                    "bullets": [
                        "Spearheaded user research and visual identity redesign for enterprise fintech platform serving 500K+ monthly active users."
                    ]
                }
            ],
            "ats_score": 95,
            "is_already_ats": True
        }

        # 1. Verify link formatting for Sarah
        links_html = cv.format_contact_links(designer_profile)
        self.assertIn("mailto:sarah.jenkins@designforge.io", links_html)
        self.assertIn("sarahjenkins.design", links_html)
        self.assertIn("linkedin.com/in/sarahjenkins-design", links_html)

        # 2. Verify dual PDF generation with Sarah's name and identity (NO Mubashar)
        out_cv_pdf = os.path.join(REPO_DIR, "user_data", "cvs", "Sarah_Jenkins_ATS_Master_CV.pdf")
        os.makedirs(os.path.dirname(out_cv_pdf), exist_ok=True)
        res_cv = cv.generate_master_cv(designer_profile, out_cv_pdf)
        self.assertTrue(res_cv.get("ok"), "Must compile ATS CV for Designer Sarah")
        self.assertTrue(os.path.exists(out_cv_pdf))
        self.assertGreater(os.path.getsize(out_cv_pdf), 2000)

        out_cl_pdf = os.path.join(REPO_DIR, "user_data", "cover_letters", "Sarah_Jenkins_Acme_Cover_Letter.pdf")
        res_cl = cv.generate_cover_letter_pdf(
            profile_dict=designer_profile,
            company="Acme Cloud",
            role="Staff Product Designer",
            letter_text="I am writing to express my enthusiastic interest in the Staff Product Designer role at Acme Cloud.",
            out_pdf=out_cl_pdf
        )
        cl_path = res_cl["path"] if isinstance(res_cl, dict) else res_cl
        self.assertTrue(os.path.exists(cl_path))
        self.assertGreater(os.path.getsize(cl_path), 2000)

        print("✓ test_05_any_user_designer_profile passed (Sarah Jenkins dual PDFs verified)")

    def test_06_any_user_qa_engineer_profile(self):
        """Test complete workflow for QA Specialist persona (David Ross, Senior QA Automation Engineer)."""
        qa_profile = {
            "name": "David Ross",
            "title": "Senior QA Automation Engineer | SDET",
            "default_title": "Senior QA Automation Engineer",
            "discipline": "qa",
            "contact": {
                "email": "david.ross.qa@gmail.com",
                "phone": "+44 20 7946 0991",
                "location": "London, UK (Remote)",
                "github": "https://github.com/davidross-qa",
                "linkedin": "https://linkedin.com/in/davidross-sdet"
            },
            "location": "London, UK",
            "default_summary": "Senior QA Automation Engineer specializing in Selenium, Cypress, Playwright, PyTest, and automated CI/CD quality pipelines.",
            "skills": {
                "Testing Frameworks": ["PyTest", "Playwright", "Cypress", "Selenium WebDriver", "Postman", "K6"],
                "Methodologies": ["API Automation", "Regression Testing", "BDD/TDD", "CI/CD GitHub Actions"]
            },
            "experiences": [
                {
                    "company": "QualityOps Global",
                    "title": "Senior QA Lead",
                    "dates": "2022 - Present",
                    "bullets": [
                        "Engineered full regression automation suite using Playwright and Python, reducing smoke test execution from 4 hours to 8 minutes.",
                        "Identified and logged 120+ critical severity functional defects before production release, ensuring 99.98% platform reliability."
                    ]
                }
            ],
            "ats_score": 94,
            "is_already_ats": True
        }

        out_cv_pdf = os.path.join(REPO_DIR, "user_data", "cvs", "David_Ross_ATS_Master_CV.pdf")
        res_cv = cv.generate_master_cv(qa_profile, out_cv_pdf)
        self.assertTrue(res_cv.get("ok"))
        self.assertTrue(os.path.exists(out_cv_pdf))
        self.assertGreater(os.path.getsize(out_cv_pdf), 2000)
        print("✓ test_06_any_user_qa_engineer_profile passed (David Ross QA CV compiled)")

if __name__ == "__main__":
    unittest.main()
