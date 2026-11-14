import os
import sys
import json
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

import bot
import desktop_server


class TestAtsAndScraperFixes(unittest.TestCase):

    def test_enhance_cv_to_ats_produces_google_xyz(self):
        sample_profile = {
            "name": "Muhammad Hasnain",
            "default_title": "Graphic Designer",
            "discipline": "design",
            "contact": {"email": "hasnain@example.com", "phone": "+92 336 7763874"},
            "experience": [
                {
                    "company": "Creative Agency",
                    "role": "Graphic Designer",
                    "years": "2023 - Present",
                    "bullets": [
                        "Designed social media posts and branding.",
                        "Created marketing banners in Figma."
                    ]
                }
            ],
            "skills": {"Design Tools": ["Figma", "Illustrator"]}
        }
        enhanced = desktop_server.enhance_cv_to_ats(sample_profile)
        self.assertEqual(enhanced["ats_score"], 96)
        self.assertIn("raw_experience", enhanced)
        self.assertEqual(len(enhanced["raw_experience"]), 1)
        self.assertEqual(len(enhanced["experience"]), 1)
        bullets = enhanced["experience"][0]["bullets"]
        self.assertGreater(len(bullets), 0)
        # Check that bullets contain action verbs and quantified metrics (% or numbers)
        has_quantified = any("%" in b or any(ch.isdigit() for ch in b) for b in bullets)
        self.assertTrue(has_quantified, f"Bullets should be quantified: {bullets}")

    def test_no_synthesized_fake_emails(self):
        # A job with a company website but NO email in text
        job = {
            "id": "job-test-dummy",
            "company": "RandomFakeCompanyXYZ",
            "title": "Lead Designer",
            "url": "https://www.randomfakecompanyxyz123987.com/careers/job-1",
            "text": "We are seeking a senior designer. Apply on our website link above.",
            "apply": "https://www.randomfakecompanyxyz123987.com/careers/job-1"
        }
        em, src = bot.pick_email(job)
        # MUST BE NONE, NOT synthesized careers@
        self.assertIsNone(em, f"Should not synthesize fake email, got: {em}")

    def test_real_email_in_job_text_is_found(self):
        job = {
            "id": "job-test-real",
            "company": "Confiz",
            "title": "UI Designer",
            "url": "https://confiz.com/careers",
            "text": "Send your portfolio and CV to careers@confiz.com before next Friday."
        }
        em, src = bot.pick_email(job)
        self.assertEqual(em, "careers@confiz.com")

    def test_src_all_callable(self):
        self.assertTrue(hasattr(bot, "src_all"))
        self.assertTrue(callable(bot.src_all))

    def test_discipline_isolation_matching(self):
        designer_prof = {
            "name": "Muhammad Hasnain",
            "default_title": "Graphic Designer",
            "discipline": "design",
            "skills": {"Design": ["Figma", "Photoshop", "Branding", "UI/UX"]}
        }
        prof_kw = desktop_server.extract_candidate_matching_profile(designer_prof)

        design_job = {
            "title": "Senior Visual & Graphic Designer",
            "company": "Canva",
            "location": "Remote",
            "text": "Looking for Figma, Adobe Suite, social media marketing designs and brand identity."
        }
        score_design = desktop_server.calculate_dynamic_job_match(design_job, prof_kw)
        self.assertGreaterEqual(score_design, 75, f"Design job match should be >= 75%, got {score_design}")

        dev_job = {
            "title": "Senior C++ Backend Core Systems Architect",
            "company": "FinTech Corp",
            "location": "Lahore",
            "text": "Requires 8 years C++, Linux kernel, low latency networking."
        }
        score_dev = desktop_server.calculate_dynamic_job_match(dev_job, prof_kw)
        self.assertLessEqual(score_dev, 40, f"Unrelated dev job match should be <= 40%, got {score_dev}")


if __name__ == "__main__":
    unittest.main()
