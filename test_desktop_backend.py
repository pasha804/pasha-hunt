import json
import unittest
import urllib.request
import threading
import time
from desktop_server import start_server, stop_server

class TestDesktopServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=start_server, args=(58241,), daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    def test_stats_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:58241/api/stats")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("total_jobs", data)
        self.assertGreater(data["total_jobs"], 0)
        self.assertIn("candidate", data)

    def test_jobs_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:58241/api/jobs")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("title", data[0])

    def test_chat_endpoint(self):
        req = urllib.request.Request(
            "http://127.0.0.1:58241/api/chat",
            data=json.dumps({"message": "Hello Pasha Bot"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        self.assertEqual(res.status, 200)
        data = json.loads(res.read().decode("utf-8"))
        self.assertIn("reply", data)
        self.assertTrue(len(data["reply"]) > 0)

    def test_tailor_endpoint(self):
        req = urllib.request.Request(
            "http://127.0.0.1:58241/api/tailor",
            data=json.dumps({"bullet": "Worked on backend Python APIs"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        self.assertEqual(res.status, 200)
        data = json.loads(res.read().decode("utf-8"))
        self.assertIn("optimized", data)

    def test_profile_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:58241/api/profile")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("name", data)
        self.assertTrue(len(data["name"]) > 0)

    def test_cover_letter_endpoint(self):
        req = urllib.request.Request(
            "http://127.0.0.1:58241/api/cover-letter",
            data=json.dumps({"company": "Systems Limited", "title": "Full Stack Developer"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        self.assertEqual(res.status, 200)
        data = json.loads(res.read().decode("utf-8"))
        self.assertIn("letter", data)
        self.assertIn("Systems Limited", data["letter"])

    def test_drafts_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:58241/api/drafts")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIsInstance(data, list)

    def test_contacts_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:58241/api/contacts")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

if __name__ == "__main__":
    unittest.main()
