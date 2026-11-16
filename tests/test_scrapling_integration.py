"""Unit and Integration Tests for Scrapling Stealth Engine in Pasha Hunt
Verifies D4Vinci/Scrapling integration:
- Fetcher availability
- StealthyFetcher initialization
- Adaptive Selector parsing for job boards (Title, Company, Location, Description, Emails)
- Career portal type detection (Greenhouse, Lever, Workday, Ashby, LinkedIn)
"""
import unittest
from unittest.mock import patch, MagicMock

import scrapling_adapter


class TestScraplingEngine(unittest.TestCase):
    def test_01_scrapling_availability(self):
        """Scrapling engine must be detected and available."""
        self.assertTrue(scrapling_adapter.is_scrapling_available(), "Scrapling library should be installed and available")
        status = scrapling_adapter.get_scrapling_status()
        self.assertTrue(status["available"])
        self.assertTrue(status["has_fetcher"])
        self.assertTrue(status["has_stealthy_fetcher"])
        self.assertEqual(status["version"], "0.5.1")

    def test_02_selector_job_extraction(self):
        """Selector must deterministically extract structured job fields from portal HTML."""
        sample_greenhouse_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Senior AI Engineer - TechCorp</title></head>
        <body>
            <div id="content">
                <h1 class="app-title">Senior AI Engineer</h1>
                <div class="company-name">TechCorp Global</div>
                <div class="location">Remote, US / Worldwide</div>
                <div id="job-description">
                    <p>We are seeking a Senior AI Engineer experienced in LangGraph, Python, and Scrapling.</p>
                    <p>Questions? Reach out to hiring.tech@techcorp.com or team@techcorp.com</p>
                </div>
                <a href="https://boards.greenhouse.io/techcorp/jobs/12345#apply" class="apply-button">Apply for this job</a>
            </div>
        </body>
        </html>
        """
        extracted = scrapling_adapter.parse_job_html(sample_greenhouse_html, url="https://boards.greenhouse.io/techcorp/jobs/12345")
        
        self.assertEqual(extracted["title"], "Senior AI Engineer")
        self.assertEqual(extracted["company"], "TechCorp Global")
        self.assertIn("Remote", extracted["location"])
        self.assertIn("LangGraph", extracted["description"])
        self.assertEqual(extracted["portal_type"], "greenhouse")
        self.assertIn("hiring.tech@techcorp.com", extracted["emails"])

    def test_03_portal_type_detection(self):
        """Portal type detection must accurately classify job board domains."""
        self.assertEqual(scrapling_adapter.detect_portal_type("https://jobs.lever.co/stripe/abc-123"), "lever")
        self.assertEqual(scrapling_adapter.detect_portal_type("https://boards.greenhouse.io/anthropic/jobs/456"), "greenhouse")
        self.assertEqual(scrapling_adapter.detect_portal_type("https://myworkdayjobs.com/nvidia/en-US/career"), "workday")
        self.assertEqual(scrapling_adapter.detect_portal_type("https://jobs.ashbyhq.com/openai/789"), "ashby")
        self.assertEqual(scrapling_adapter.detect_portal_type("https://linkedin.com/jobs/view/101"), "linkedin")
        self.assertEqual(scrapling_adapter.detect_portal_type("https://startup.com/careers"), "generic")

    def test_04_email_extraction_and_deobfuscation(self):
        """Must extract both plain and obfuscated recruiter emails."""
        obfuscated_html = """
        <div>
            Contact our talent lead at: jobs [at] frontier [dot] ai
            Or email direct: careers@frontier.ai
            Ignore: invalid.image.png and tracking@sentry.io
        </div>
        """
        emails = scrapling_adapter.extract_emails_from_text(obfuscated_html)
        self.assertIn("jobs@frontier.ai", emails)
        self.assertIn("careers@frontier.ai", emails)
        self.assertNotIn("tracking@sentry.io", emails)
        self.assertFalse(any(e.endswith(".png") for e in emails))


if __name__ == "__main__":
    unittest.main()
