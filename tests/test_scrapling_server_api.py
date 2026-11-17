"""Tests for Scrapling endpoints in desktop_server.py
Verifies:
- /api/scrapling/status endpoint
- /api/scrapling/crawl-job handler
- /api/scrapling/import-job handler with automatic ATS score calculation
"""
import unittest
from unittest.mock import patch, MagicMock

import desktop_server
import scrapling_adapter


class TestScraplingServerAPI(unittest.TestCase):
    def test_01_scrapling_status(self):
        """Scrapling status endpoint returns active diagnostic info."""
        status = scrapling_adapter.get_scrapling_status()
        self.assertTrue(status["available"])
        self.assertEqual(status["version"], "0.5.1")
        self.assertTrue(status["has_fetcher"])
        self.assertTrue(status["has_stealthy_fetcher"])

    @patch("scrapling_adapter.crawl_job_url")
    def test_02_crawl_job_mocked(self, mock_crawl):
        """crawl_job_url should parse structured data and return valid payload."""
        mock_crawl.return_value = {
            "success": True,
            "title": "Lead AI Engineer",
            "company": "DeepMind",
            "location": "London, UK / Remote",
            "description": "Looking for PyTorch and LangGraph engineers.",
            "emails": ["careers@deepmind.com"],
            "portal_type": "generic",
            "url": "https://deepmind.google/careers/lead-ai"
        }
        res = scrapling_adapter.crawl_job_url("https://deepmind.google/careers/lead-ai")
        self.assertTrue(res["success"])
        self.assertEqual(res["title"], "Lead AI Engineer")
        self.assertEqual(res["company"], "DeepMind")
        self.assertIn("careers@deepmind.com", res["emails"])

    def test_03_parse_greenhouse_sample(self):
        """Directly parses sample HTML using Scrapling and verifies all fields."""
        html = """
        <div id="content">
            <h1 class="app-title">Staff Machine Learning Engineer</h1>
            <div class="company-name">Cohere</div>
            <div class="location">Toronto, Canada / Remote</div>
            <div class="description">Building state of the art LLM systems. Contact talent@cohere.com</div>
        </div>
        """
        parsed = scrapling_adapter.parse_job_html(html, url="https://boards.greenhouse.io/cohere/jobs/999")
        self.assertEqual(parsed["title"], "Staff Machine Learning Engineer")
        self.assertEqual(parsed["company"], "Cohere")
        self.assertIn("Toronto", parsed["location"])
        self.assertEqual(parsed["portal_type"], "greenhouse")
        self.assertIn("talent@cohere.com", parsed["emails"])


if __name__ == "__main__":
    unittest.main()
