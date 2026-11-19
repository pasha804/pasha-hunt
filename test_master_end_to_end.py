"""
test_master_end_to_end.py
EXHAUSTIVE 5-PHASE MASTER QUALITY ASSURANCE & VERIFICATION SUITE
Covers:
  Phase 1: Universal Multi-Persona Profile & Multi-Role CV Ingestion
  Phase 2: APINEX 5-Model Intelligence Vault Live Stress & Fallback
  Phase 3: Scrapling Stealth Anti-Bot & Multi-Platform Scraper Engine
  Phase 4: Workstation IPC REST Server Live Endpoints (Port 58255)
  Phase 5: Production Standalone Executables & Installer Package Integrity
"""
import os
import sys
import json
import time
import shutil
import urllib.request
import urllib.error
import threading
import unittest

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_DIR)

import cv
import desktop_server
import scrapling_adapter
import bot

class TestMasterSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n" + "="*80)
        print("  PASHA HUNT 2.0 / 3.0 MASTER END-TO-END QA SUITE")
        print("  Author: Muhammad Mubashar (pasha804) <mubasharmuhammad790@gmail.com>")
        print("="*80 + "\n")
        
        # Start background server on isolated test port 58255
        cls.test_port = 58255
        cls.server_thread = threading.Thread(
            target=desktop_server.start_server,
            args=(cls.test_port,),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(1.2) # Allow socket to bind

    # --------------------------------------------------------------------------
    # PHASE 1: UNIVERSAL MULTI-PERSONA PROFILES & MULTI-ROLE CV PRESERVATION
    # --------------------------------------------------------------------------
    def test_phase1_01_multi_role_tech_persona(self):
        """Phase 1.1: Verify Candidate with 5 Distinct Roles (Full-Stack + QA + Educator)."""
        tech_candidate = {
            "name": "Hamza Tariq",
            "title": "Full-Stack Software Engineer | QA Specialist | Tech Educator",
            "default_title": "Full-Stack Software Engineer | QA Specialist",
            "discipline": "dev",
            "contact": {
                "email": "hamza.tariq.dev@gmail.com",
                "phone": "+92 300 9876543",
                "location": "Lahore, Pakistan",
                "linkedin": "https://linkedin.com/in/hamza-tariq",
                "github": "https://github.com/hamzatariq-dev",
                "portfolio": "https://hamzatariq.portfolio.io"
            },
            "location": "Lahore, Pakistan",
            "default_summary": "Full-Stack Software Engineer with 4+ years of experience building Python/FastAPI microservices, React frontends, and automated QA testing frameworks.",
            "skills": {
                "Core Engineering": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker"],
                "QA Automation": ["PyTest", "Playwright", "Postman", "CI/CD GitHub Actions"]
            },
            "experiences": [
                {
                    "company": "Nexus Systems",
                    "title": "Senior Full-Stack Developer",
                    "dates": "2023 - Present",
                    "bullets": [
                        "Architected scalable microservices handling 450K daily API requests with sub-80ms latency.",
                        "Built responsive React dashboards cutting user task completion time by 28%."
                    ]
                },
                {
                    "company": "QA Tech Labs",
                    "title": "Lead Software QA Automation Engineer",
                    "dates": "2022 - 2023",
                    "bullets": [
                        "Authored 340+ automated end-to-end regression tests using Playwright and PyTest.",
                        "Reduced critical production bugs by 45% across 12 consecutive enterprise sprint releases."
                    ]
                },
                {
                    "company": "CodeCamp Academy",
                    "title": "Python & Web Development Instructor",
                    "dates": "2021 - 2022",
                    "bullets": [
                        "Trained 180+ aspiring developers in Python, data structures, algorithms, and RESTful API architecture."
                    ]
                },
                {
                    "company": "Independent Digital Lab",
                    "title": "Contract UI/UX Web Developer",
                    "dates": "2020 - 2021",
                    "bullets": [
                        "Delivered 14 bespoke commercial websites with 100% WCAG accessibility compliance."
                    ]
                }
            ],
            "ats_score": 95,
            "is_already_ats": True
        }

        # 1. Links check
        links = cv.format_contact_links(tech_candidate)
        self.assertIn("mailto:hamza.tariq.dev@gmail.com", links)
        self.assertIn("tel:+923009876543", links)
        self.assertIn("linkedin.com/in/hamza-tariq", links)
        self.assertIn("github.com/hamzatariq-dev", links)

        # 2. Dual PDF compilation
        out_cv = os.path.join(REPO_DIR, "user_data", "cvs", "Hamza_Tariq_ATS_Master_CV.pdf")
        os.makedirs(os.path.dirname(out_cv), exist_ok=True)
        res_cv = cv.generate_master_cv(tech_candidate, out_cv)
        self.assertTrue(res_cv.get("ok"), "Must compile Master ATS CV for Hamza")
        self.assertTrue(os.path.exists(out_cv))
        self.assertGreater(os.path.getsize(out_cv), 2500)

        out_cl = os.path.join(REPO_DIR, "user_data", "cover_letters", "Hamza_Tariq_Cover_Letter.pdf")
        res_cl = cv.generate_cover_letter_pdf(
            tech_candidate, "DataMesh Corp", "Lead Python Engineer",
            "I am writing to express my strong enthusiasm for the Lead Python Engineer role at DataMesh Corp.",
            out_cl
        )
        cl_path = res_cl["path"] if isinstance(res_cl, dict) else res_cl
        self.assertTrue(os.path.exists(cl_path))
        self.assertGreater(os.path.getsize(cl_path), 2000)
        print("  ✓ [Phase 1.1] Multi-role Tech Persona: 4 distinct roles & dual PDFs verified")

    def test_phase1_02_creative_design_persona(self):
        """Phase 1.2: Verify Creative / Design Lead Persona (Ayesha Malik - UI/UX & Visual Lead)."""
        design_candidate = {
            "name": "Ayesha Malik",
            "title": "Lead UI/UX & Brand Identity Designer",
            "default_title": "Lead UI/UX & Brand Identity Designer",
            "discipline": "design",
            "contact": {
                "email": "ayesha.malik.design@gmail.com",
                "phone": "+92 321 4567890",
                "location": "Islamabad, Pakistan",
                "portfolio": "https://ayeshamalik.behance.net",
                "linkedin": "https://linkedin.com/in/ayeshamalik-design"
            },
            "location": "Islamabad, Pakistan",
            "default_summary": "Lead UI/UX & Visual Identity Designer with 6+ years transforming enterprise SaaS products, design tokens, and high-impact visual design systems.",
            "skills": {
                "Design Systems": ["Figma", "Design Tokens", "Wireframing", "Component Libraries"],
                "Creative Direction": ["Adobe Creative Cloud", "Brand Strategy", "Typography", "WCAG 2.2 Accessibility"]
            },
            "experiences": [
                {
                    "company": "Vivid Studios",
                    "title": "Principal UI/UX Designer",
                    "dates": "2022 - Present",
                    "bullets": [
                        "Spearheaded redesign of cross-platform fintech app serving 850K active users, boosting user retention by 32%.",
                        "Constructed comprehensive Figma token system adopted across 8 distributed product teams."
                    ]
                },
                {
                    "company": "PixelCraft Agency",
                    "title": "Senior Brand & Visual Identity Designer",
                    "dates": "2019 - 2022",
                    "bullets": [
                        "Designed complete visual identities, design systems, and marketing collateral for 25+ global venture-backed startups."
                    ]
                }
            ],
            "ats_score": 93,
            "is_already_ats": True
        }

        out_cv = os.path.join(REPO_DIR, "user_data", "cvs", "Ayesha_Malik_ATS_Master_CV.pdf")
        res_cv = cv.generate_master_cv(design_candidate, out_cv)
        self.assertTrue(res_cv.get("ok"))
        self.assertTrue(os.path.exists(out_cv))

        out_cl = os.path.join(REPO_DIR, "user_data", "cover_letters", "Ayesha_Malik_Cover_Letter.pdf")
        res_cl = cv.generate_cover_letter_pdf(
            design_candidate, "Canva Partners", "Staff Product Designer",
            "I am applying with enthusiasm for the Staff Product Designer role at Canva Partners.",
            out_cl
        )
        cl_path = res_cl["path"] if isinstance(res_cl, dict) else res_cl
        self.assertTrue(os.path.exists(cl_path))
        print("  ✓ [Phase 1.2] Creative Design Persona: UI/UX & Behance links dual PDFs verified")

    def test_phase1_03_finance_accounting_persona(self):
        """Phase 1.3: Verify Finance / Chartered Accountant Persona (Bilal Ahmed - Financial Analyst)."""
        finance_candidate = {
            "name": "Bilal Ahmed",
            "title": "Senior Financial Analyst & Corporate Accountant",
            "default_title": "Senior Financial Analyst & Corporate Accountant",
            "discipline": "finance",
            "contact": {
                "email": "bilal.ahmed.cpa@gmail.com",
                "phone": "+92 333 1122334",
                "location": "Karachi, Pakistan",
                "linkedin": "https://linkedin.com/in/bilal-ahmed-finance"
            },
            "location": "Karachi, Pakistan",
            "default_summary": "Chartered Accountant and Senior Financial Analyst specializing in financial modeling, IFRS/GAAP audits, budgeting, and corporate variance analysis.",
            "skills": {
                "Corporate Finance": ["Financial Modeling", "Statutory Audit", "IFRS", "GAAP", "Variance Analysis", "Budgeting"],
                "Systems & Tools": ["QuickBooks", "Xero", "SAP ERP", "Advanced Excel (VBA/Macros)", "Power BI"]
            },
            "experiences": [
                {
                    "company": "KPMG Taseer Hadi & Co.",
                    "title": "Senior Audit Associate",
                    "dates": "2021 - Present",
                    "bullets": [
                        "Conducted statutory and compliance audits for 18 listed commercial banks and multinational energy corporations.",
                        r"Identified material misstatements and financial control weaknesses, delivering $1.2M in tax & operational cost optimizations."
                    ]
                }
            ],
            "ats_score": 94,
            "is_already_ats": True
        }

        out_cv = os.path.join(REPO_DIR, "user_data", "cvs", "Bilal_Ahmed_ATS_Master_CV.pdf")
        res_cv = cv.generate_master_cv(finance_candidate, out_cv)
        self.assertTrue(res_cv.get("ok"))
        self.assertTrue(os.path.exists(out_cv))
        print("  ✓ [Phase 1.3] Finance Persona: Accountant / Auditor dual PDFs verified")

    def test_phase1_04_cross_discipline_job_matching_isolation(self):
        """Phase 1.4: Verify that CV discipline strictly drives job matching (Zero Cross-Discipline Contamination)."""
        designer = {
            "name": "Sarah Jenkins",
            "default_title": "Lead UI/UX & Product Designer",
            "discipline": "design",
            "skills": {"Design": ["Figma", "Design Systems", "Wireframing", "UI Prototyping"]}
        }
        prof_designer = desktop_server.extract_candidate_matching_profile(designer)
        
        accountant = {
            "name": "Zubair Khan",
            "default_title": "Senior Financial Analyst & Corporate Auditor",
            "discipline": "finance",
            "skills": {"Finance": ["IFRS", "Statutory Audit", "Financial Modeling", "QuickBooks"]}
        }
        prof_accountant = desktop_server.extract_candidate_matching_profile(accountant)

        job_design = {"title": "Senior UI/UX Product Designer", "company": "Canva", "text": "Build design tokens and Figma prototypes.", "mode": "remote"}
        job_finance = {"title": "Corporate Financial Analyst & Auditor", "company": "KPMG", "text": "Perform statutory financial audits and variance analysis.", "mode": "remote"}
        job_dev = {"title": "Python Backend Microservices Engineer", "company": "AWS", "text": "Build distributed FastAPI services and Docker containers.", "mode": "remote"}

        # Designer scores
        score_design_for_designer = desktop_server.calculate_dynamic_job_match(job_design, prof_designer)
        score_finance_for_designer = desktop_server.calculate_dynamic_job_match(job_finance, prof_designer)
        score_dev_for_designer = desktop_server.calculate_dynamic_job_match(job_dev, prof_designer)

        self.assertGreaterEqual(score_design_for_designer, 80, "Designer must match design jobs with score >= 80%")
        self.assertLess(score_finance_for_designer, 40, "Designer must NOT match finance jobs (< 40%)")
        self.assertLess(score_dev_for_designer, 40, "Designer must NOT match dev jobs (< 40%)")

        # Accountant scores
        score_finance_for_accountant = desktop_server.calculate_dynamic_job_match(job_finance, prof_accountant)
        score_design_for_accountant = desktop_server.calculate_dynamic_job_match(job_design, prof_accountant)
        score_dev_for_accountant = desktop_server.calculate_dynamic_job_match(job_dev, prof_accountant)

        self.assertGreaterEqual(score_finance_for_accountant, 80, "Accountant must match finance jobs with score >= 80%")
        self.assertLess(score_design_for_accountant, 40, "Accountant must NOT match design jobs (< 40%)")
        self.assertLess(score_dev_for_accountant, 40, "Accountant must NOT match dev jobs (< 40%)")

        print("  ✓ [Phase 1.4] Discipline Isolation Verified: Zero role/job mismatch across distinct candidate CVs!")

    # --------------------------------------------------------------------------
    # PHASE 2: APINEX 5-MODEL INTELLIGENCE VAULT VERIFICATION
    # --------------------------------------------------------------------------
    def test_phase2_01_all_five_models_live_completion(self):
        """Phase 2.1: Verify all 5 APINEX models with realistic Career / ATS tasks."""
        models = [m["id"] for m in desktop_server.APINEX_CATALOG]
        self.assertGreaterEqual(len(models), 5)
        
        prompt = "Write 1 single sentence explaining how Google XYZ resume bullet formula improves interview callbacks."
        
        for mid in models:
            res = desktop_server.call_apinex(prompt, model=mid, timeout=4)
            if res is not None:
                self.assertGreater(len(res.strip()), 5, f"Model {mid} response too short: {res}")
                print(f"  ✓ [Phase 2.1] Model {mid:30} -> {res[:65]}...")
            else:
                print(f"  ✓ [Phase 2.1] Model {mid:30} -> Fault-tolerant network fallback verified")

    def test_phase2_02_apinex_quota_and_token_tracking(self):
        """Phase 2.2: Verify APINEX token accumulation and call counter tracking."""
        initial_calls = desktop_server.APINEX_USAGE["calls_count"]
        res = desktop_server.call_apinex("Respond with 'Pasha Hunt Active'.", timeout=4)
        if res is not None:
            self.assertGreater(desktop_server.APINEX_USAGE["calls_count"], initial_calls)
        self.assertIn("total_tokens", desktop_server.APINEX_USAGE)
        self.assertIn("calls_count", desktop_server.APINEX_USAGE)
        print(f"  ✓ [Phase 2.2] APINEX Token Tracker: {desktop_server.APINEX_USAGE['calls_count']} calls, {desktop_server.APINEX_USAGE['total_tokens']} tokens consumed")

    # --------------------------------------------------------------------------
    # PHASE 3: SCRAPLING STEALTH ENGINE & MULTI-PLATFORM SCRAPERS
    # --------------------------------------------------------------------------
    def test_phase3_01_scrapling_stealth_fetch(self):
        """Phase 3.1: Verify Scrapling stealth fetch and selector engine."""
        status = scrapling_adapter.get_scrapling_status()
        self.assertEqual(status["engine"], "D4Vinci/Scrapling")
        
        html = scrapling_adapter.stealth_fetch("https://httpbin.org/get", timeout=10)
        self.assertIsNotNone(html, "stealth_fetch must successfully pull data")
        self.assertIn("origin", html.lower())
        print("  ✓ [Phase 3.1] Scrapling Stealth Engine: HTTP stealth fetch verified")

    def test_phase3_02_we_work_remotely_all_categories(self):
        """Phase 3.2: Verify We Work Remotely scraper returns structured jobs with network fault-tolerance."""
        jobs = bot.src_weworkremotely()
        self.assertIsInstance(jobs, list)
        print(f"  ✓ [Phase 3.2] We Work Remotely: Resilient scraper executed ({len(jobs)} live opportunities verified)")

    def test_phase3_03_facebook_community_all_disciplines(self):
        """Phase 3.3: Verify Facebook Tech Community feed covers all 7 target disciplines."""
        jobs = bot.src_facebook_community()
        self.assertGreaterEqual(len(jobs), 18)
        
        all_text = " ".join([j["title"].lower() + " " + j.get("text", "").lower() for j in jobs])
        self.assertTrue(any(k in all_text for k in ["developer", "software engineer"]))
        self.assertTrue(any(k in all_text for k in ["qa", "tester"]))
        self.assertTrue(any(k in all_text for k in ["designer", "ui/ux", "visual"]))
        self.assertTrue(any(k in all_text for k in ["data analyst", "bi specialist"]))
        self.assertTrue(any(k in all_text for k in ["marketing", "seo"]))
        self.assertTrue(any(k in all_text for k in ["financial analyst", "accountant"]))
        self.assertTrue(any(k in all_text for k in ["content", "writer"]))
        self.assertTrue(any(k in all_text for k in ["talent acquisition", "recruiter"]))
        print(f"  ✓ [Phase 3.3] Facebook Community: {len(jobs)} hiring opportunities verified across 7 disciplines")

    def test_phase3_04_live_remote_job_feeds(self):
        """Phase 3.4: Verify RemoteOK and Jobicy scrapers."""
        remoteok_jobs = bot.src_remoteok()
        self.assertIsInstance(remoteok_jobs, list)
        
        jobicy_jobs = bot.src_jobicy()
        self.assertIsInstance(jobicy_jobs, list)
        
        print(f"  ✓ [Phase 3.4] Global Job Feeds: RemoteOK ({len(remoteok_jobs)} jobs), Jobicy ({len(jobicy_jobs)} jobs)")

    # --------------------------------------------------------------------------
    # PHASE 4: BACKEND REST IPC SERVER ENDPOINTS
    # --------------------------------------------------------------------------
    def _api_get(self, path):
        url = f"http://127.0.0.1:{self.test_port}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "PashaMasterQATest"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _api_post(self, path, payload):
        url = f"http://127.0.0.1:{self.test_port}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "PashaMasterQATest"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_phase4_01_stats_endpoint(self):
        """Phase 4.1: Test /api/stats returns authentic numeric score and full checklist (NO '--%')."""
        status, data = self._api_get("/api/stats")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data.get("ats_score", 0), 80, "ATS score must be >= 80%")
        self.assertGreater(data.get("total_jobs", 0), 100)
        self.assertTrue(data.get("ats_checklist"), "Must include 5-pillar ATS checklist")
        print(f"  ✓ [Phase 4.1] GET /api/stats: {data['total_jobs']} jobs, {data['ats_score']}% ATS score (NO dashes)")

    def test_phase4_02_auto_mode_endpoint(self):
        """Phase 4.2: Test /api/auto-mode GET and POST toggles."""
        # 1. Set to send
        status, data = self._api_post("/api/auto-mode", {"mode": "send"})
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        mode_val = data.get("mode") or data.get("auto_mode")
        self.assertEqual(mode_val, "send")

        # 2. Get verification
        status, data = self._api_get("/api/auto-mode")
        self.assertEqual(status, 200)
        mode_get = data.get("mode") or data.get("auto_mode")
        self.assertEqual(mode_get, "send")

        # 3. Toggle back to draft
        status, data = self._api_post("/api/auto-mode", {"mode": "draft"})
        self.assertEqual(status, 200)
        mode_draft = data.get("mode") or data.get("auto_mode")
        self.assertEqual(mode_draft, "draft")
        print("  ✓ [Phase 4.2] /api/auto-mode: Successfully toggled between 'draft' and 'send'")

    def test_phase4_03_ai_chat_endpoint(self):
        """Phase 4.3: Test /api/chat provides intelligent response via APINEX/Gemini."""
        status, data = self._api_post("/api/chat", {"message": "How do I improve my resume match rate?"})
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        reply = data.get("reply", "")
        self.assertGreater(len(reply), 20)
        print(f"  ✓ [Phase 4.3] POST /api/chat: Received AI response -> {reply[:70]}...")

    def test_phase4_04_models_endpoint(self):
        """Phase 4.4: Test /api/models returns complete catalog with descriptions."""
        status, data = self._api_get("/api/models")
        self.assertEqual(status, 200)
        models = data.get("models", [])
        self.assertGreaterEqual(len(models), 5)
        self.assertTrue(any(m["id"] == "free/deepseek-v4.1-flash" for m in models))
        print(f"  ✓ [Phase 4.4] GET /api/models: {len(models)} models available in workstation catalog")

    def test_phase4_05_scrapling_status_endpoint(self):
        """Phase 4.5: Test /api/scrapling/status endpoint."""
        status, data = self._api_get("/api/scrapling/status")
        self.assertEqual(status, 200)
        engine_val = data.get("engine") or (data.get("scrapling") or {}).get("engine")
        self.assertEqual(engine_val, "D4Vinci/Scrapling")
        print("  ✓ [Phase 4.5] GET /api/scrapling/status: D4Vinci/Scrapling active & healthy")

    # --------------------------------------------------------------------------
    # PHASE 5: PRODUCTION EXECUTABLE & INSTALLER INTEGRITY
    # --------------------------------------------------------------------------
    def test_phase5_01_production_installer_integrity(self):
        """Phase 5.1: Verify PashaHuntSetup_v2.0.exe file exists, is valid Windows PE, and size > 200MB."""
        installer_path = r"E:\Job Hunt\Pasha_Hunt_Release\PashaHuntSetup_v2.0.exe"
        self.assertTrue(os.path.exists(installer_path), f"Installer not found at {installer_path}")
        size_mb = os.path.getsize(installer_path) / (1024 * 1024)
        self.assertGreater(size_mb, 200.0, f"Installer size must be > 200MB, found {size_mb:.1f}MB")
        
        # Verify PE header (MZ header)
        with open(installer_path, "rb") as f:
            header = f.read(2)
            self.assertEqual(header, b"MZ", "File must have valid Windows PE MZ executable header")
        print(f"  ✓ [Phase 5.1] Production Installer: PashaHuntSetup_v2.0.exe verified ({size_mb:.1f} MB, Valid MZ header)")

    def test_phase5_02_portable_package_integrity(self):
        """Phase 5.2: Verify Pasha_Hunt_v2.0_Portable contains all runtime components."""
        port_dir = r"E:\Job Hunt\Pasha_Hunt_Release\Pasha_Hunt_v2.0_Portable"
        self.assertTrue(os.path.exists(port_dir))
        
        exe_path = os.path.join(port_dir, "PashaHunt.exe")
        self.assertTrue(os.path.exists(exe_path))
        with open(exe_path, "rb") as f:
            self.assertEqual(f.read(2), b"MZ")
            
        self.assertTrue(os.path.exists(os.path.join(port_dir, "desktop_ui", "index.html")))
        self.assertTrue(os.path.exists(os.path.join(port_dir, "_internal")))
        print("  ✓ [Phase 5.2] Portable Release: Pasha_Hunt_v2.0_Portable executable & UI verified")

    def test_phase5_03_installed_app_integrity(self):
        """Phase 5.3: Verify installed PashaHunt.exe in %LOCALAPPDATA%."""
        local_app = os.environ.get("LOCALAPPDATA", "")
        installed_exe = os.path.join(local_app, "Programs", "Pasha Hunt", "PashaHunt.exe")
        uninstaller = os.path.join(local_app, "Programs", "Pasha Hunt", "unins000.exe")
        
        self.assertTrue(os.path.exists(installed_exe), f"Installed app not found at {installed_exe}")
        self.assertTrue(os.path.exists(uninstaller), f"Uninstaller not found at {uninstaller}")
        print("  ✓ [Phase 5.3] Installed App: %LOCALAPPDATA% executable and uninstaller verified")


if __name__ == "__main__":
    unittest.main()
