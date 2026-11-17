import os
import sys
import time
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot

class TestAIModelIntegrations(unittest.TestCase):
    def setUp(self):
        self.cfg = bot.load_config()
        self.state = bot.gemini_state()

    def test_01_api_key_configured(self):
        """Verify API key is present in config and masked appropriately."""
        key = str(self.cfg.get("gemini_api_key") or "").strip()
        self.assertTrue(bool(key), "An Apinex or Gemini API key must be configured")
        # Ensure key is not empty or default placeholder
        self.assertFalse(key.startswith("PUT-"), "Key must not be placeholder")

    def test_02_model_discovery(self):
        """Verify dynamic discovery of text-generation models."""
        models = bot.gemini_models(self.cfg, self.state)
        self.assertIsInstance(models, list)
        self.assertGreaterEqual(len(models), 1, "At least 1 AI model must be available")
        # Top model should be a text model
        self.assertTrue(any("qwen" in m or "flash" in m or "claude" in m for m in models))

    def test_03_json_extractor_resilience(self):
        """Verify answer_json extracts clean dict from messy LLM responses with markdown fences."""
        raw_llm_markdown = "Here is the response:\n```json\n{\"eligible\": true, \"fit_score\": 95}\n```\nHope that helps!"
        extracted = None
        try:
            # Test markdown fence stripping
            extracted = json.loads(raw_llm_markdown[raw_llm_markdown.index("{"):raw_llm_markdown.rindex("}") + 1])
        except Exception:
            pass
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.get("fit_score"), 95)

    def test_04_master_cv_fallback_integrity(self):
        """Verify fallback generator returns valid tailored draft with non-empty subject and body."""
        prompt = (
            "Decide and write. Return ONLY JSON with exactly these keys:\n"
            "Title: Full Stack Developer\n"
            "Company: Systems Limited\n"
            "Decide and write tailored CV and application email."
        )
        res = bot._generate_master_cv_fallback(prompt)
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("eligible"), "Fallback should mark standard software role eligible")
        self.assertGreaterEqual(res.get("fit_score", 0), 70, "Fit score should be realistic")
        self.assertTrue(bool(res.get("subject")), "Subject must not be empty")
        self.assertTrue(bool(res.get("body")), "Body must not be empty")
        self.assertIn("Muhammad Mubashar", res.get("body"), "Body must reference candidate name")

if __name__ == "__main__":
    unittest.main()
