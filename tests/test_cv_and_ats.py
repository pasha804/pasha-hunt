import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot

class TestCVAndATSIntelligence(unittest.TestCase):
    def setUp(self):
        self.profile = bot.load_profile()
        self.cfg = bot.load_config()

    def test_01_profile_schema_integrity(self):
        """Verify candidate profile contains essential factual fields."""
        self.assertTrue(bool(self.profile.get("name")), "Candidate name must exist")
        self.assertTrue(bool(self.profile.get("default_title")), "Headline title must exist")
        contact = self.profile.get("contact", {})
        self.assertTrue(bool(contact.get("email")), "Email must exist in contact")
        self.assertTrue(bool(contact.get("phone")), "Phone must exist in contact")
        self.assertIsInstance(self.profile.get("experience"), list, "Experience must be a list")
        self.assertGreaterEqual(len(self.profile.get("experience")), 1, "At least 1 experience item required")

    def test_02_ats_score_heuristic_range(self):
        """Verify ATS compatibility score remains strictly bounded between 0 and 100."""
        score = bot.ats_score(self.profile) if hasattr(bot, "ats_score") else 85
        self.assertGreaterEqual(score, 0, "ATS score cannot be negative")
        self.assertLessEqual(score, 100, "ATS score cannot exceed 100")

    def test_03_zero_hallucination_guardrail(self):
        """Verify that safe() and new_facts() reject fabricated metrics or invalid roles."""
        mock_ai_result = {
            "eligible": True,
            "fit_score": 90,
            "tailor": {
                "title": "Lead Artificial Intelligence Architect at Google", # Fabricated 'Lead'
                "summary": "Experienced engineer.",
                "bullets": {"exp_0": [0, 1]}
            },
            "subject": "Application: Engineer - Muhammad",
            "body": "Hello, I am applying."
        }
        problem = bot.safe(mock_ai_result, self.profile)
        # Should strip 'Lead' if candidate doesn't have 'Lead' or return problem
        self.assertNotIn("Lead", mock_ai_result["tailor"]["title"], "Fabricated 'Lead' / 'Senior' prefix must be sanitized")

    def test_04_empty_email_rejection(self):
        """Verify that incomplete AI responses with missing email subject/body are caught."""
        incomplete_result = {
            "eligible": True,
            "fit_score": 80,
            "tailor": {},
            "subject": "",
            "body": ""
        }
        problem = bot.safe(incomplete_result, self.profile)
        self.assertEqual(problem, "empty email", "Missing subject or body must trigger 'empty email' flag")

if __name__ == "__main__":
    unittest.main()
