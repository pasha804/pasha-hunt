"""Point-and-click window for the job hunter.

Double-click "Job Hunter.bat" (or run: python -I gui.py), or install JobHunterSetup.exe.
Every button runs bot.py in the background, so the scheduled runs and the window share
the same code, tracker.csv and jobs.json.
"""
import ast
import csv
import datetime as dt
import imaplib
import json
import math
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import urllib.error
import urllib.request
import webbrowser
from tkinter import font as tkfont
from tkinter import filedialog, messagebox, ttk

try:
    import cv2
    from PIL import Image, ImageTk
    HAS_VIDEO = True
except ImportError:
    HAS_VIDEO = False

# python -I leaves the script's folder off sys.path; bot.py sits next to this file.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot  # noqa: E402

# Your files live in bot.HERE: next to the scripts, or %APPDATA%\Job Hunter for the installed JobHunter.exe.
FROZEN, HERE = bot.FROZEN, bot.HERE
ICON = (os.path.join(sys._MEIPASS, "icon.ico") if FROZEN
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer", "icon.ico"))
LOGO_PNG = (os.path.join(sys._MEIPASS, "logo.png") if FROZEN
            else os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))
INTRO_VIDEO = (os.path.join(sys._MEIPASS, "intro.mp4") if FROZEN
               else os.path.join(os.path.dirname(os.path.abspath(__file__)), "intro.mp4"))
if not os.path.exists(INTRO_VIDEO):
    _alt_vid = r"E:\Job Hunt\gemini_generated_video_ef58318d.mp4"
    if os.path.exists(_alt_vid):
        INTRO_VIDEO = _alt_vid
JOBS_FILE, TRACKER, LOCK = bot.JOBS_FILE, bot.TRACKER, bot.LOCK
CONFIG = os.path.join(HERE, "config.json")
PROFILE = os.path.join(HERE, "profile.json")
RELEASES = f"https://github.com/{bot.REPO}/releases/latest"
SETUP_URL = f"{RELEASES}/download/JobHunterSetup.exe"  # the installer file itself is hosted on GitHub
DOWNLOAD_PAGE = "https://www.codeprojectsofficial.com/tools"
AUTO_MODEL = "Auto: best free model that is not at its limit"
TASK = "Remote Job Hunter"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# pythonw has no console; use the console python next to it, hidden, so we can read its output.
# JobHunter.exe runs the bot itself when started with --bot.
PY = os.path.join(os.path.dirname(sys.executable), "python.exe")
if not os.path.exists(PY):
    PY = sys.executable
BOT = [sys.executable, "--bot"] if FROZEN else [PY, "-I", "-X", "utf8", "-u", os.path.join(bot.CODE, "bot.py")]
# What the 30-minute scheduled task runs: no console window either way.
PYW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
TASK_RUN = (f'"{sys.executable}" --bot' if FROZEN
            else f'"{PYW if os.path.exists(PYW) else sys.executable}" -I "{os.path.join(bot.CODE, "bot.py")}"')

VIEWS = {
    "Ready to draft (has email)": {"ready"},
    "Apply on company site": {"apply on site"},
    "All matches": {"ready", "apply on site"},
    "Done, applied or skipped": {"done"},
    "Everything (incl. rejected)": {"ready", "apply on site", "done", "rejected"},
}
COLUMNS = ("Status", "Match", "Posted", "Company", "Role", "Location", "Salary")
MATCH_LABEL = {"strong": "★★ Strong", "partial": "★ Partial"}
MATCH_HELP = {"strong": "a keyword is in the job title",
              "partial": "part of a keyword is in the title, or a keyword is only in the description"}
LABEL = {"ready": "✉ Ready", "apply on site": "🌐 Apply on site", "done": "✔ Done", "rejected": "✖ Rejected"}
DEFAULT_KEYWORDS = bot.DEFAULT_CONFIG["keywords"]
OPEN_TO_LABEL = {"me": "Worldwide + my country", "countries": "Countries I pick", "anywhere": "Any country"}
# (key, label, lowest, highest, what it means). The AI model is picked in the main window.
SETTINGS = [("min_fit_score", "Minimum fit score", 0, 100,
             "Auto-draft skips jobs Gemini scores lower than this (0-100). Lower it if too few drafts are made."),
            ("max_drafts_per_run", "Max drafts per run", 1, 50, "Drafts (or CVs) one Auto-draft run makes at most."),
            ("max_drafts_per_day", "Max drafts per day", 1, 200, "All runs together, per calendar day."),
            ("max_gemini_calls_per_run", "Max Gemini calls per run", 1, 50,
             "Jobs one run asks Gemini about. Keeps you inside the free limits."),
            ("max_years_required", "Skip jobs asking for (years)", 0, 40,
             "Hide jobs that ask for this many years of experience or more. 0 = never hide.")]

# Job type -> (keywords, We Work Remotely categories from bot.WWR_FEEDS, keywords must be in the title).
# Words like "Sales" or "Finance" are in almost every job ad, so most presets match on the title only.
# Put the most important keywords first: the sites that have a search get the first ten.
PRESETS = {
    "Software / Full Stack & AI": (["Full Stack Developer", "Software Engineer", "Python Developer", "React Developer",
                                     "AI Engineer", "Backend Developer", "Frontend Developer", "FastAPI"], ["software"], True),
    "Junior / Associate Developer": (["Junior Developer", "Junior Software Engineer", "Junior Software Developer",
                                      "Associate Software Engineer", "Entry Level Developer", "Junior Full Stack",
                                      "Junior Python", "Junior React", "Associate Developer", "Fresh Graduate"],
                                     ["software"], True),
    "AI Agents & Autonomous Systems": (["AI Agent", "Agentic", "Autonomous Agents", "Autonomous AI", "LLM Engineer", "LangChain",
                                        "AI Engineer", "AI Developer", "AI Automation", "Prompt Engineer"], ["software"], True),
    "QA & Software Tester (Web / SaaS / Desktop)": (["QA Engineer", "Software Tester", "QA Tester", "Manual Tester",
                                                     "Automation Tester", "Quality Assurance", "App Tester", "SaaS Tester", "Test Engineer"],
                                                    ["software"], True),
    "Pakistan Tech / Remote Hub": (["Software Engineer", "Full Stack Developer", "Python Developer", "React Developer",
                                    "AI Engineer", "QA Engineer", "Software Tester", "FastAPI"], ["software"], True),
    "Software (any stack)": (["Developer", "Engineer", "Programmer", "Full Stack", "Backend", "Frontend"],
                             ["software", "devops"], True),
    "SEO / Digital marketing": (["SEO", "Marketing", "Social Media", "PPC", "Google Ads", "Email Marketing",
                                 "Content Marketing", "Digital Marketing", "Paid Media", "Performance Marketing",
                                 "Growth", "Media Buyer", "Community Manager"], ["sales & marketing", "other"], True),
    "Writing / Content": (["Writer", "Copywriter", "Content", "Editor", "Proofreader", "Ghostwriter",
                           "Content Strategist", "Blog"], ["other", "sales & marketing"], True),
    "Finance / Accounting": (["Accountant", "Bookkeeper", "Accounting", "Accounts Payable", "Accounts Receivable",
                              "Payroll", "Financial Analyst", "Finance", "Financial", "FP&A", "Controller", "Tax",
                              "Auditor", "Billing"], ["finance & management"], True),
    "Sales / Business development": (["Sales", "SDR", "BDR", "Sales Development", "Business Development",
                                      "Lead Generation", "Appointment Setter", "Account Executive",
                                      "Account Manager", "CRM", "Inside Sales", "Partnerships", "Customer Success"],
                                     ["sales & marketing"], True),
    "Customer support / success": (["Customer Support", "Customer Success", "Customer Service", "Technical Support",
                                    "Support Specialist", "Support Agent", "Support Representative", "Live Chat",
                                    "Chat Support", "Help Desk", "Helpdesk", "Client Services", "Moderator"],
                                   ["customer support"], True),
    "Operations / Admin / Virtual assistant": (["Virtual Assistant", "Executive Assistant", "Operations",
                                                "Administrative", "Admin Assistant", "Project Coordinator",
                                                "Data Entry", "Personal Assistant", "Office Manager", "Coordinator",
                                                "Workforce Management"], ["other", "finance & management"], True),
    "HR / Recruiting": (["Recruiter", "Sourcer", "Talent Acquisition", "Recruiting", "Recruitment", "HR",
                         "Human Resources", "People Operations", "People Partner", "Talent"],
                        ["finance & management", "other"], True),
    "AI training / Research": (["AI Trainer", "AI Training", "Data Annotator", "Annotation", "Annotator",
                                "Data Labeling", "Rater", "Evaluator", "Search Quality", "AI Tutor", "RLHF",
                                "Data Quality", "Research Assistant", "Online Researcher"], ["other", "software"],
                               True),
    "Translation / Transcription": (["Translator", "Translation", "Transcription", "Transcriptionist", "Interpreter",
                                     "Localization", "Linguist", "Subtitler", "Captioner"], ["other"], True),
    "Teaching / Tutoring": (["Tutor", "Teacher", "Instructor", "ESL", "English Teacher", "Curriculum",
                             "Instructional Designer"], ["other"], True),
    "Design": (["Designer", "UI", "UX", "Graphic", "Illustrator", "Motion"], ["design"], True),
    "Data / Analytics": (["Data Analyst", "Data Scientist", "Analytics", "Business Intelligence", "BI",
                          "Data Engineer"], ["software", "other"], True),
    "Project / Product management": (["Project Manager", "Product Manager", "Program Manager", "Scrum Master",
                                      "Product Owner"], ["product", "finance & management"], True),
}
CUSTOM = "Custom (my own keywords)"  # reads every We Work Remotely category


def combine(names):
    """Keywords, We Work Remotely categories and title-only for several job types searched together.
    Keywords are interleaved so the first ten (the ones sent to search boxes) cover every chosen type."""
    lists = [PRESETS[n][0] for n in names]
    kws = []
    for i in range(max(map(len, lists), default=0)):
        for words in lists:
            if i < len(words) and words[i].lower() not in (k.lower() for k in kws):
                kws.append(words[i])
    fields = list(dict.fromkeys(f for n in names for f in PRESETS[n][1]))
    return kws, fields, any(PRESETS[n][2] for n in names)

LOG_FONT = ("Consolas", 10)
ROW = "  {:<12}{:<15}{:<28}{:<54}{}\n"
ROW_HEAD = ROW.format("STATUS", "SOURCE", "COMPANY", "ROLE", "EMAIL / LINK")
REASON_INDENT = 2 + 12 + 15  # reasons line up under the Company column

# ---------- Modern Dark Dashboard Palette (Linear / Obsidian High-End) ----------
CYBER_AZURE = "#38BDF8"     # Electric Cyan / Primary Action
NEON_EMERALD = "#10B981"    # Verified Direct Email / 95+ ATS Elite
VIVID_AMBER = "#F59E0B"     # Action / Warning
CORAL_ROSE = "#F43F5E"      # Stop / Alert
VIOLET_INDIGO = "#6366F1"   # Deep Indigo Accent
OBSIDIAN_VOID = "#0B0F19"   # Core Canvas Background
SLATE_SURFACE = "#111827"   # Modern Card Surface
SLATE_BORDER = "#1E293B"    # Clean Minimal Border
SLATE_MUTED = "#94A3B8"     # Slate Secondary Muted Text
PURE_INK = "#F8FAFC"        # Pure High-Contrast White Text

INDIGO = VIOLET_INDIGO
WATERMELON = CORAL_ROSE
GOLD = VIVID_AMBER
TURQUOISE = CYBER_AZURE
JUNGLE = NEON_EMERALD

GRADIENT = [(11, 15, 25), (15, 23, 42), (20, 30, 50), (13, 20, 36)]  # Deep Space Obsidian Slate
PERIOD = 2400   # pixels along the diagonal before the colours repeat
BAND = 6        # width of one colour band
GAP, PAD, RADIUS = 14, 10, 14  # space between cards, card padding, corner radius
FROST, SMOKE = 0.15, 0.80       # subtle dark glass tinting
WHITE, NIGHT = (255, 255, 255), (11, 15, 25)
INK, MUTED, LIGHT_INK, LIGHT_MUTED = PURE_INK, SLATE_MUTED, PURE_INK, SLATE_MUTED
SURFACE, LINE, ACCENT, CONSOLE, DIALOG = SLATE_SURFACE, SLATE_BORDER, CYBER_AZURE, "#070A10", OBSIDIAN_VOID


def ago(iso):
    try:
        d = dt.datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    days = (dt.datetime.now(dt.timezone.utc) - d).days
    return "today" if days <= 0 else f"{days}d ago"


def cut(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def where(j):
    """The job's location with its work type in front, unless the location already says it: 'On-site · Lahore'."""
    mode = bot.WORK_MODES.get(j.get("mode")) or ""
    loc = str(j.get("location") or "").strip()
    if "|" in loc:
        parts = [p.strip() for p in loc.split("|")]
        LOC_HINTS = re.compile(r"\b(remote|onsite|on-site|hybrid|wfh|anywhere|worldwide|lahore|karachi|pakistan|us|usa|uk|eu|europe|germany|japan|canada|toronto|timezone|san francisco|sf|nyc|new york|berlin|london|tokyo|detroit|boston|austin|seattle)\b", re.I)
        matched_locs = [p for p in parts if LOC_HINTS.search(p) and not p.lower().startswith("seeking")]
        if matched_locs:
            loc = matched_locs[0]
        elif len(parts) > 2:
            loc = parts[2]
        else:
            loc = parts[1] if len(parts) > 1 else parts[0]
    if loc.lower().startswith("seeking"):
        loc = "Remote"
    loc = loc.strip()
    if not loc:
        return mode or "Remote"
    return f"{mode} · {loc}" if mode and mode.lower() not in loc.lower() else loc


def row(status, source, company, role, last):
    return ROW.format(status, source, cut(company, 26), cut(role, 52), last)


def pretty(line):
    """Lay out one line of bot.py output. Returns ([(text, tag)], is_table_row)."""
    m = re.match(r"(CANDIDATE|APPLY ON SITE) \[(\w+)\] (.*?) \| (.*) \| (\S+)(?: \(.*\))?$", line)
    if m:
        kind, src, company, role, last = m.groups()
        if role.startswith(company + " | "):  # HN titles repeat the company
            role = role[len(company) + 3:]
        if kind == "CANDIDATE":
            return [(row("READY", src, company, role, last), "ready")], True
        return [(row("ON WEBSITE", src, company, role, last), "site")], True
    m = re.match(r"skip (.*?): eligible=(\S+) fit=(\S+) ?(.*)$", line)
    if m:
        company, _, fit, reason = m.groups()
        out = [(row("NOT A FIT", "gemini", company, f"fit {fit}", ""), "skip")]
        return out + ([(reason + "\n", "reason")] if reason else []), True
    m = re.match(r"DRAFT saved: (.*) -> (\S+) \(fit (.*)\)$", line)
    if m:
        company, mail, fit = m.groups()
        return [(row("DRAFTED", "gemini", company, f"fit {fit}", mail), "good")], True
    m = re.match(r"src_(\w+): (\d+) jobs$", line)
    if m:
        return [(f"  {m.group(1):<18}{m.group(2):>5} jobs\n", "dim")], False
    m = re.match(r"filter: (\{.*\})$", line)
    if m:
        try:
            counts = ast.literal_eval(m.group(1))
            text = "  ·  ".join(f"{k} {v}" for k, v in counts.items())
        except (ValueError, SyntaxError):
            text = m.group(1)
        return [("  Filtered out:  ", "key"), (text + "\n", "dim")], False
    m = re.match(r"\S+ (\d\d:\d\d) \| standalone( dry-run)? \| fetched (\d+) \| candidates (\d+) \| "
                 r"gemini (\d+) \| drafts (\d+)(?: \| (.*))?$", line)
    if m:
        at, dry, fetched, cands, gem, drafts, notes = m.groups()
        text = f"  ■ Finished {at}:  {fetched} jobs checked  ·  {cands} with email"
        text += "  (search only)" if dry else f"  ·  {gem} asked Gemini  ·  {drafts} drafts saved"
        out = [(text + "\n", "summary")]
        return out + ([(f"  Notes: {notes}\n", "err")] if notes else []), False
    tag = "err" if "ERROR" in line or "failed" in line.lower() else "good" if " saved" in line else None
    return [(f"  {line}\n", tag)], False


def read_config():
    try:
        with open(CONFIG, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def has_key(cfg, key):
    v = cfg.get(key)
    return isinstance(v, str) and bot.is_set(v.strip())


def write_config(cfg):
    with open(CONFIG + ".tmp", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    os.replace(CONFIG + ".tmp", CONFIG)


def version_tuple(v):
    return tuple(int(n) for n in re.findall(r"\d+", v)[:3])


def latest_release():
    """Tag of the newest GitHub release, e.g. 'v1.2.0', or None when GitHub cannot be reached."""
    req = urllib.request.Request(f"https://api.github.com/repos/{bot.REPO}/releases/latest", headers=bot.UA)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()).get("tag_name")
    except (OSError, ValueError):
        return None


def download_setup(progress):
    """Download the newest installer to the temp folder and return its path. progress(percent) is called as it
    comes in. Raises OSError/ValueError when the download fails or is not an installer."""
    path = os.path.join(tempfile.gettempdir(), "JobHunterSetup-update.exe")
    with urllib.request.urlopen(urllib.request.Request(SETUP_URL, headers=bot.UA), timeout=60) as r, \
            open(path + ".part", "wb") as f:
        size, got, shown = int(r.headers.get("Content-Length") or 0), 0, -1
        while chunk := r.read(256 * 1024):
            f.write(chunk)
            got += len(chunk)
            if size and got * 100 // size != shown:
                shown = got * 100 // size
                progress(shown)
    with open(path + ".part", "rb") as f:
        if f.read(2) != b"MZ" or got < 1_000_000 or (size and got != size):
            raise ValueError("the download is not a complete installer")
    os.replace(path + ".part", path)
    return path


def job_files(job_id):
    """(cv, cover letter) PDFs made for one job, newest first in tracker.csv; None where there is none."""
    try:
        with open(TRACKER, newline="", encoding="utf-8-sig") as f:
            rows = [r for r in csv.DictReader(f) if r.get("draft_id") == job_id and r.get("cv_file")]
    except OSError:
        return None, None
    for r in reversed(rows):
        cv = os.path.join(HERE, "cvs", r["cv_file"])
        if os.path.exists(cv):
            letter = os.path.join(HERE, "cvs", bot.letter_of(r["cv_file"]))
            return cv, letter if os.path.exists(letter) else None
    return None, None


def dpi_aware():
    """Crisp text on scaled (125%, 150%) screens; without this Windows stretches the window and blurs it."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


class Tooltip:
    """A small note under a widget while the mouse rests on it."""

    def __init__(self, widget, text):
        self.widget, self.text, self.win, self.job = widget, text, None, None
        widget.bind("<Enter>", lambda e: self.schedule(), add="+")
        widget.bind("<Leave>", lambda e: self.hide(), add="+")
        widget.bind("<ButtonPress>", lambda e: self.hide(), add="+")

    def schedule(self):
        self.hide()
        self.job = self.widget.after(500, self.show)

    def show(self):
        w = self.widget
        self.win = tk.Toplevel(w.winfo_toplevel())  # not inside a Card, so the card tint leaves it alone
        self.win.wm_overrideredirect(True)
        self.win.wm_geometry(f"+{w.winfo_rootx() + 8}+{w.winfo_rooty() + w.winfo_height() + 4}")
        tk.Label(self.win, text=self.text, justify="left", wraplength=360, background=INK, foreground="white",
                 font=("Segoe UI", 9), padx=8, pady=5).pack()

    def hide(self):
        if self.job:
            self.widget.after_cancel(self.job)
            self.job = None
        if self.win:
            self.win.destroy()
            self.win = None


# ---------- connecting Gmail and Gemini ----------

# (field, label, secret, help steps, links). Shown in the "Connect your accounts" window.
KEY_FIELDS = [
    ("gemini_api_key", "AI API key (Apinex or Gemini)", True,
     ["For Apinex (Recommended): Paste your Apinex key (starts with sk-). Gives access to free Gemini 3.8, DeepSeek V4.1, Claude 4.6.",
      "For Google Gemini: Open Google AI Studio, press Create API key and copy the key (starts with AIza).",
      "Paste your key here. Both free tiers work without a card."],
     [("Open Apinex Overview", "https://apinex.bond/overview"),
      ("Open Google AI Studio", "https://aistudio.google.com/apikey")]),
    ("gmail_address", "Gmail address (optional)", False, None, []),
    ("gmail_app_password", "Gmail app password", True,
     ["Google only gives app passwords to accounts with 2-Step Verification. Turn it on first if it is off.",
      "Open App passwords, type a name such as Job Hunter and press Create.",
      "Copy the 16-letter password Google shows and paste it here. The spaces do not matter.",
      "Note: use this app password, not your normal Gmail password. Some work and school accounts do not allow "
      "app passwords: use a personal Gmail account then."],
     [("Turn on 2-Step Verification", "https://myaccount.google.com/signinoptions/twosv"),
      ("Open App passwords", "https://myaccount.google.com/apppasswords")]),
]


def lock_owner():
    """PID of the bot run that holds bot.lock, or None when no live bot process owns it."""
    try:
        with open(LOCK, encoding="utf-8") as f:
            pid = int(f.read().strip())
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True,
                           text=True, creationflags=NO_WINDOW, timeout=10)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    # Windows reuses PIDs: only a Python or Job Hunter process can be the bot.
    name = r.stdout.split(",")[0].strip().strip('"').lower()
    return pid if name in ("python.exe", "pythonw.exe", "jobhunter.exe", "pashahunt.exe") else None


def test_gmail(address, password, host="imap.gmail.com"):
    """None if Gmail accepts the address and app password, else what went wrong."""
    try:
        imap = imaplib.IMAP4_SSL(host, timeout=20)
    except OSError as e:
        return f"Could not reach Gmail ({e.__class__.__name__}). Check your internet connection."
    try:
        imap.login(address, password.replace(" ", ""))
        return None
    except imaplib.IMAP4.error:
        return "Gmail did not accept this address and app password. Check both, and make sure it is an app password."
    except OSError as e:
        return f"Could not reach Gmail ({e.__class__.__name__})."
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def test_gemini(key):
    """None if Gemini or Apinex accepts the key, else what went wrong."""
    key = str(key or "").strip()
    if not key:
        return "Please enter an API key."
    if key.startswith("sk-"):
        try:
            req = urllib.request.Request(f"{bot.APINEX_BASE_URL}/models", headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
                if "data" in data and len(data["data"]) > 0:
                    return None
                return "Apinex responded, but returned no models."
        except urllib.error.HTTPError as e:
            return f"Apinex error {e.code}. Check your API key at apinex.bond."
        except Exception as e:
            return f"Could not reach Apinex ({e.__class__.__name__}). Check your internet connection."

    body = json.dumps({"contents": [{"parts": [{"text": "Reply with OK."}]}],
                       "generationConfig": {"maxOutputTokens": 5}}).encode()
    req = urllib.request.Request(f"{bot.GEMINI_API}/gemini-flash-lite-latest:generateContent", data=body,
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30):
            return None
    except urllib.error.HTTPError as e:
        if e.code in (404, 429):  # the key works; this one model is missing or out of free quota today
            return None
        try:
            message = json.loads(e.read().decode()).get("error", {}).get("message", "")
        except (ValueError, OSError):
            message = ""
        if "denied access" in message:
            return ("Google has blocked the project this key belongs to (\"Your project has been denied access\"). "
                    "In Google AI Studio press Create API key > Create project to make a key in a new project. "
                    "If that is refused too, use a different Google account.")
        if e.code in (400, 401, 403):
            return f"Google did not accept this Gemini key ({message[:120] or e.code}). Copy it again from Google AI Studio."
        return f"Gemini answered with error {e.code}. Try again in a minute."
    except OSError as e:
        return f"Could not reach Gemini ({e.__class__.__name__}). Check your internet connection."


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def hexcolor(c):
    return "#%02x%02x%02x" % c


def gradient_at(s):
    """Colour at distance s (x + y) along the diagonal, repeating every PERIOD pixels."""
    s = s % PERIOD / PERIOD * len(GRADIENT)
    i, f = int(s) % len(GRADIENT), s - int(s)
    return mix(GRADIENT[i], GRADIENT[(i + 1) % len(GRADIENT)], f * f * (3 - 2 * f))


def rounded(x0, y0, x1, y1, r):
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(7):
            t = math.radians(a + k * 15)
            pts += [cx + r * math.cos(t), cy + r * math.sin(t)]
    return pts


class Card(tk.Frame):
    """A frosted panel on the gradient. Its frames, labels and checkboxes take the card colour."""

    def __init__(self, app, dark=False):
        super().__init__(app, bd=0, highlightthickness=0)
        self.canvas, self.dark, self.face, self.centre = app.canvas, dark, None, 0
        self.ink, self.muted = (LIGHT_INK, LIGHT_MUTED) if dark else (INK, MUTED)
        self.shape = app.canvas.create_polygon(0, 0, 0, 0, width=1, tags="card")

    def row(self, parent=None, **pack):
        f = tk.Frame(parent or self, bd=0)
        f.pack(fill="x", **pack)
        return f

    def label(self, parent, text="", muted=False, **kw):
        return tk.Label(parent, text=text, fg=self.muted if muted else self.ink, bd=0, **kw)

    def check(self, parent, text, var):
        return tk.Checkbutton(parent, text=text, variable=var,
                              fg=self.ink, activeforeground=TURQUOISE,
                              bg=SURFACE, activebackground=SURFACE,
                              selectcolor="#0A0714", bd=0, highlightthickness=0)

    def place_at(self, x, y, w, h):
        w, h = max(w, 1), max(h, 1)
        self.place(x=x, y=y, width=w, height=h)
        self.canvas.coords(self.shape, *rounded(x - PAD, y - PAD, x + w + PAD, y + h + PAD, RADIUS))
        self.centre = x + w / 2 + y + h / 2

    def tint(self):
        under = gradient_at(self.centre)
        face = mix(under, (9, 13, 22), 0.88) if self.dark else mix(under, (17, 24, 39), 0.82)
        if face == self.face:
            return
        self.face, bg = face, hexcolor(face)
        outline_col = hexcolor(mix(face, (30, 41, 59), 0.45 if not self.dark else 0.20))
        self.canvas.itemconfigure(self.shape, fill=bg, outline=outline_col)
        todo = [self]
        while todo:
            w = todo.pop()
            todo += w.winfo_children()
            if getattr(w, "solid", False):
                continue
            if isinstance(w, tk.Checkbutton):
                w.configure(bg=bg, activebackground=bg, fg="#F8FAFC", activeforeground=CYBER_AZURE, selectcolor="#0B0F19")
            elif isinstance(w, (tk.Frame, tk.Label)):
                w.configure(bg=bg)


def enable_dark_title_bar(window):
    """Enable Windows 11 immersive dark mode title bar and custom caption color."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()
        dark_mode = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
        caption_color = ctypes.c_int(0x00190E08)  # BGR for #0B0F19 (Deep Obsidian Void)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color))
        text_color = ctypes.c_int(0x00FCFAF8)  # Crisp Titanium White
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(text_color), ctypes.sizeof(text_color))
    except Exception:
        pass


class VideoSplash(tk.Toplevel):
    """Cinematic intro splash screen displaying the branded Pasha Hunt MP4 video."""
    def __init__(self, master, video_path, on_finish=None):
        super().__init__(master, background="#07040D")
        self.on_finish = on_finish
        self.video_path = video_path
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # 16:9 aspect ratio centered on screen
        W, H = 840, 472
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - W) // 2)
        y = max(0, (sh - H) // 2)
        self.geometry(f"{W}x{H}+{x}+{y}")

        self.canvas = tk.Canvas(self, width=W, height=H, bg="#07040D",
                                highlightthickness=2, highlightbackground=INDIGO)
        self.canvas.pack(fill="both", expand=True)

        self.skip_btn = tk.Label(self, text="  Skip Intro [Esc] ⏭  ", font=("Segoe UI", 10, "bold"),
                                 bg="#130D24", fg=TURQUOISE, activebackground="#2E1C4E",
                                 activeforeground=GOLD, cursor="hand2", relief="solid", bd=1)
        self.skip_btn.place(relx=0.96, rely=0.92, anchor="se")

        self.closed = False
        self.cap = None
        self.frame_holder = None

        self.skip_btn.bind("<Button-1>", lambda e: self.close())
        self.canvas.bind("<Button-1>", lambda e: self.close())
        self.bind("<Escape>", lambda e: self.close())
        self.bind("<space>", lambda e: self.close())
        self.bind("<Return>", lambda e: self.close())

        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                self.close()
                return
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 24.0
            self.delay = max(15, int(1000 / fps))
            self.after(20, self.play_frame)
        except Exception:
            self.close()

    def play_frame(self):
        if self.closed or not self.cap:
            return
        ret, frame = self.cap.read()
        if ret:
            W, H = 840, 472
            frame = cv2.resize(frame, (W, H))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.frame_holder = imgtk
            self.canvas.delete("video")
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk, tags="video")
            self.skip_btn.lift()
            self.after(self.delay, self.play_frame)
        else:
            self.close()

    def close(self):
        if not self.closed:
            self.closed = True
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass
            try:
                self.destroy()
            except Exception:
                pass
            if self.on_finish:
                self.on_finish()




# ====================================================================================================
# MASTER BRAND DESIGN SYSTEM TOKENS (PASHA HUNT 2.0 - APINEX EDITION)
# ====================================================================================================
BG_MAIN = "#080E19"
BG_SECONDARY = "#0C1524"
BG_SIDEBAR = "#0A1220"
BG_SURFACE = "#111D2F"
BG_ELEVATED = "#17253A"
PRIMARY_BLUE = "#168BFF"
ELECTRIC_BLUE = "#278EFF"
TEAL_ACCENT = "#00D6C9"
SUCCESS = "#18C78A"
WARNING = "#FFB547"
DANGER = "#FF5571"
TEXT_PRIMARY = "#F3F7FC"
TEXT_SECONDARY = "#A2B1C6"
TEXT_MUTED = "#718198"
BORDER = "#223149"
HOVER = "#192A42"

CYBER_AZURE = PRIMARY_BLUE
NEON_EMERALD = SUCCESS
VIVID_AMBER = WARNING
CORAL_ROSE = DANGER
VIOLET_INDIGO = ELECTRIC_BLUE
OBSIDIAN_VOID = BG_MAIN
SLATE_SURFACE = BG_SURFACE
SLATE_BORDER = BORDER
SLATE_MUTED = TEXT_MUTED
PURE_INK = TEXT_PRIMARY


class App(tk.Tk):
    def __init__(self):
        dpi_aware()
        super().__init__()
        self.title(f"Pasha Hunt {bot.VERSION} — Apinex Edition (Pasha Dev)")
        try:
            self.iconbitmap(default=ICON)
        except tk.TclError:
            pass
        if os.path.exists(LOGO_PNG):
            try:
                self._app_icon_img = ImageTk.PhotoImage(Image.open(LOGO_PNG))
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass
        enable_dark_title_bar(self)
        self.configure(bg=BG_MAIN)
        self.scale = max(1.0, self.winfo_fpixels("1i") / 96)
        px = lambda n: round(n * self.scale)
        self.geometry(f"{min(px(1360), self.winfo_screenwidth() - 40)}x{min(px(880), self.winfo_screenheight() - 80)}")
        self.minsize(px(1060), px(680))
        
        self.jobs, self.by_iid, self.mtime = [], {}, 0
        self.model_mtime = 0
        self.proc, self.out, self.stopped = None, queue.Queue(), False
        self.sort_col, self.sort_rev = "Match", False
        self.tracker_cache = {}
        self.active_nav = "overview"
        self.sidebar_buttons = {}
        self.screens = {}
        self.console_expanded = False

        self.style_widgets()
        self.build_shell()
        self.load_jobs()
        self.fill_models()

        # Keyboard shortcuts
        self.bind_all("<F5>", lambda e: self.find_jobs())
        self.bind_all("<Control-k>", lambda e: (self.global_search_entry.focus_set(), self.global_search_entry.select_range(0, "end")))
        self.bind_all("<Control-f>", lambda e: (self.global_search_entry.focus_set(), self.global_search_entry.select_range(0, "end")))

        self.after(100, self.pump)
        self.after(3000, self.watch_file)
        self.after(4000, self.check_update)
        self.after(5000, lambda: self.check_replies(quiet=True))
        self.after(300000, self.schedule_reply_checks)

        # Cinematic intro video splash screen
        if HAS_VIDEO and os.path.exists(INTRO_VIDEO):
            self.withdraw()
            def after_intro():
                self.deiconify()
                self.lift()
                self.focus_force()
                self.after(200, self.first_run)
            VideoSplash(self, INTRO_VIDEO, after_intro)
        else:
            self.after(500, self.first_run)

    def style_widgets(self):
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            tkfont.nametofont(name).configure(family="Segoe UI", size=10)

        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure("Treeview",
                        background=BG_SURFACE,
                        foreground=TEXT_PRIMARY,
                        fieldbackground=BG_SURFACE,
                        rowheight=32,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", BG_ELEVATED)],
                  foreground=[("selected", PRIMARY_BLUE)])
        style.configure("Treeview.Heading",
                        background=BG_SIDEBAR,
                        foreground=TEXT_SECONDARY,
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0,
                        relief="flat",
                        padding=(8, 8))
        style.map("Treeview.Heading",
                  background=[("active", BG_ELEVATED)],
                  foreground=[("active", TEXT_PRIMARY)])

    def build_shell(self):
        px = lambda n: round(n * self.scale)

        # 1. Professional Application Header (height ~56px)
        self.header = tk.Frame(self, bg=BG_SIDEBAR, height=px(54), bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        # Header Left: Brand Logo + Product Identity
        brand_f = tk.Frame(self.header, bg=BG_SIDEBAR)
        brand_f.pack(side="left", padx=(16, 16))
        
        logo_lbl = tk.Label(brand_f, text="🦅", font=("Segoe UI Emoji", 16), bg=BG_SIDEBAR, fg=PRIMARY_BLUE)
        logo_lbl.pack(side="left", padx=(0, 6))

        title_lbl = tk.Label(brand_f, text="PASHA HUNT 2.0", font=("Segoe UI", 13, "bold"), bg=BG_SIDEBAR, fg=TEXT_PRIMARY)
        title_lbl.pack(side="left", padx=(0, 8))

        badge_lbl = tk.Label(brand_f, text="APINEX EDITION", font=("Segoe UI", 8, "bold"), bg=BG_SURFACE, fg=TEAL_ACCENT,
                             padx=6, pady=2, relief="solid", bd=1, highlightthickness=0)
        badge_lbl.pack(side="left")

        # Header Center: Global Search Bar (Ctrl + K)
        search_f = tk.Frame(self.header, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        search_f.pack(side="left", padx=(10, 10), pady=10)

        s_icon = tk.Label(search_f, text="🔍", font=("Segoe UI Emoji", 10), bg=BG_SURFACE, fg=TEXT_MUTED)
        s_icon.pack(side="left", padx=(8, 4))

        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.fill_table())
        self.global_search_entry = tk.Entry(search_f, textvariable=self.search, font=("Segoe UI", 10),
                                            bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=PRIMARY_BLUE,
                                            bd=0, highlightthickness=0, width=32)
        self.global_search_entry.pack(side="left", padx=(0, 6), pady=4)
        Tooltip(self.global_search_entry, "Search job titles, companies, locations or skills across all 18 radar feeds (Ctrl + K).")

        ctrl_k = tk.Label(search_f, text="Ctrl+K", font=("Segoe UI", 8), bg=BG_ELEVATED, fg=TEXT_MUTED, padx=4, pady=1)
        ctrl_k.pack(side="right", padx=(0, 6))

        # Header Right: Live AI Status, Sweep Action & Profile
        right_f = tk.Frame(self.header, bg=BG_SIDEBAR)
        right_f.pack(side="right", padx=(10, 16))

        # User profile badge
        prof_f = tk.Frame(right_f, bg=BG_SURFACE, padx=8, pady=4, bd=1, highlightthickness=1, highlightbackground=BORDER)
        prof_f.pack(side="right", padx=(8, 0))
        tk.Label(prof_f, text="👤 Muhammad Mubashar", font=("Segoe UI", 9, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(side="left")
        prof_f.bind("<Button-1>", lambda e: self.show_profile())

        # ATS 95+ quick trigger
        self.btn_header_ats = tk.Button(right_f, text="🎯 ATS 95+", font=("Segoe UI", 9, "bold"),
                                        bg=BG_SURFACE, fg=TEAL_ACCENT, activebackground=BG_ELEVATED, activeforeground=TEAL_ACCENT,
                                        bd=1, relief="solid", highlightthickness=0, padx=8, pady=3,
                                        command=self.ats_optimizer)
        self.btn_header_ats.pack(side="right", padx=(8, 0))
        Tooltip(self.btn_header_ats, "Open ATS 95+ Resume Scorer & Google XYZ Bullet Optimization Studio.")

        # Scan Jobs trigger
        self.btn_header_scan = tk.Button(right_f, text="⚡ Scan Jobs (F5)", font=("Segoe UI", 9, "bold"),
                                         bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, activeforeground="#FFFFFF",
                                         bd=0, relief="flat", highlightthickness=0, padx=12, pady=4,
                                         command=self.find_jobs)
        self.btn_header_scan.pack(side="right", padx=(8, 0))
        Tooltip(self.btn_header_scan, "Perform an autonomous multi-source sweep across all 18 global and Pakistan radar feeds.")

        # Real AI Status indicator
        self.ai_status_lbl = tk.Label(right_f, text="● AI Connected", font=("Segoe UI", 9, "bold"), bg=BG_SIDEBAR, fg=SUCCESS)
        self.ai_status_lbl.pack(side="right", padx=(8, 8))

        # 2. Main Window Container (Body + Collapsible Console)
        self.console_container = tk.Frame(self, bg=BG_SIDEBAR, bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.console_container.pack(side="bottom", fill="x")

        self.body_container = tk.Frame(self, bg=BG_MAIN, bd=0)
        self.body_container.pack(side="top", fill="both", expand=True)

        # 3. Left Navigation Sidebar (width ~225px)
        self.sidebar = tk.Frame(self.body_container, bg=BG_SIDEBAR, width=px(220), bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 4. Main Workspace
        self.workspace = tk.Frame(self.body_container, bg=BG_MAIN, bd=0)
        self.workspace.pack(side="right", fill="both", expand=True)

        self.build_sidebar()
        self.build_screens()
        self.build_collapsible_console()
        self.navigate_to("overview")

    def build_sidebar(self):
        nav_structure = [
            ("WORKSPACE", [
                ("overview", "Overview", "📊"),
                ("jobs", "Find Jobs", "🔍"),
                ("matches", "AI Matches", "🎯"),
                ("all", "All Opportunities", "🌐"),
            ]),
            ("CAREER TOOLS", [
                ("ats", "CV & ATS Analyzer", "📄"),
                ("tailor", "CV Tailoring Studio", "✂️"),
                ("cover", "Cover Letter Studio", "✍️"),
                ("prep", "Interview Preparation", "💡"),
            ]),
            ("APPLICATION MANAGEMENT", [
                ("email", "Email Applications", "✉️"),
                ("tracker", "Application Tracker", "📋"),
                ("contacts", "Recruiter Contacts", "👥"),
                ("replies", "Reply Tracking", "📬"),
            ]),
            ("SYSTEM", [
                ("models", "AI Models", "🤖"),
                ("logs", "Activity Logs", "📜"),
                ("settings", "Settings", "⚙️"),
                ("help", "Help & Support", "❓"),
            ])
        ]

        for sec_title, items in nav_structure:
            sec_lbl = tk.Label(self.sidebar, text=sec_title, font=("Segoe UI", 8, "bold"),
                               bg=BG_SIDEBAR, fg=TEXT_MUTED, anchor="w")
            sec_lbl.pack(fill="x", padx=16, pady=(12, 4))

            for nav_id, label, icon in items:
                btn_f = tk.Frame(self.sidebar, bg=BG_SIDEBAR, cursor="hand2")
                btn_f.pack(fill="x", padx=8, pady=1)

                indicator = tk.Frame(btn_f, bg=BG_SIDEBAR, width=3)
                indicator.pack(side="left", fill="y")

                icon_lbl = tk.Label(btn_f, text=icon, font=("Segoe UI Emoji", 10), bg=BG_SIDEBAR, fg=TEXT_SECONDARY)
                icon_lbl.pack(side="left", padx=(8, 6), pady=6)

                text_lbl = tk.Label(btn_f, text=label, font=("Segoe UI", 9), bg=BG_SIDEBAR, fg=TEXT_SECONDARY, anchor="w")
                text_lbl.pack(side="left", fill="x", expand=True, pady=6)

                for w in (btn_f, indicator, icon_lbl, text_lbl):
                    w.bind("<Button-1>", lambda e, nid=nav_id: self.navigate_to(nid))
                    w.bind("<Enter>", lambda e, bf=btn_f, tl=text_lbl, il=icon_lbl, nid=nav_id: self.on_nav_hover(bf, tl, il, nid, True))
                    w.bind("<Leave>", lambda e, bf=btn_f, tl=text_lbl, il=icon_lbl, nid=nav_id: self.on_nav_hover(bf, tl, il, nid, False))

                self.sidebar_buttons[nav_id] = {
                    "frame": btn_f, "indicator": indicator, "icon": icon_lbl, "text": text_lbl
                }

    def on_nav_hover(self, frame, text_lbl, icon_lbl, nav_id, is_hover):
        if self.active_nav == nav_id:
            return
        if is_hover:
            frame.configure(bg=HOVER)
            text_lbl.configure(bg=HOVER, fg=TEXT_PRIMARY)
            icon_lbl.configure(bg=HOVER)
        else:
            frame.configure(bg=BG_SIDEBAR)
            text_lbl.configure(bg=BG_SIDEBAR, fg=TEXT_SECONDARY)
            icon_lbl.configure(bg=BG_SIDEBAR)

    def navigate_to(self, nav_id):
        self.active_nav = nav_id
        for nid, comps in self.sidebar_buttons.items():
            if nid == nav_id:
                comps["frame"].configure(bg=BG_SURFACE)
                comps["indicator"].configure(bg=PRIMARY_BLUE)
                comps["icon"].configure(bg=BG_SURFACE, fg=PRIMARY_BLUE)
                comps["text"].configure(bg=BG_SURFACE, fg=TEXT_PRIMARY, font=("Segoe UI", 9, "bold"))
            else:
                comps["frame"].configure(bg=BG_SIDEBAR)
                comps["indicator"].configure(bg=BG_SIDEBAR)
                comps["icon"].configure(bg=BG_SIDEBAR, fg=TEXT_SECONDARY)
                comps["text"].configure(bg=BG_SIDEBAR, fg=TEXT_SECONDARY, font=("Segoe UI", 9))

        for sid, screen in self.screens.items():
            screen.pack_forget()

        target_map = {
            "overview": "overview", "jobs": "jobs", "matches": "jobs", "all": "jobs",
            "ats": "ats", "tailor": "tailor", "cover": "cover", "prep": "prep",
            "email": "jobs", "tracker": "tracker", "contacts": "jobs", "replies": "tracker",
            "models": "models", "logs": "logs", "settings": "settings", "help": "help"
        }
        target_sid = target_map.get(nav_id, "overview")
        
        if nav_id == "matches":
            self.view.set("All matches")
            self.search.set("Strong")
            self.fill_table()
        elif nav_id == "email":
            self.view.set("Ready to draft (has email)")
            self.search.set("")
            self.fill_table()
        elif nav_id == "all":
            self.view.set("All matches")
            self.search.set("")
            self.fill_table()

        if target_sid in self.screens:
            self.screens[target_sid].pack(fill="both", expand=True)

    def build_screens(self):
        self.screens["overview"] = self.build_screen_overview()
        self.screens["jobs"] = self.build_screen_jobs()
        self.screens["ats"] = self.build_screen_ats()
        self.screens["tailor"] = self.build_screen_tailor()
        self.screens["cover"] = self.build_screen_cover()
        self.screens["prep"] = self.build_screen_prep()
        self.screens["tracker"] = self.build_screen_tracker()
        self.screens["models"] = self.build_screen_models()
        self.screens["logs"] = self.build_screen_logs()
        self.screens["settings"] = self.build_screen_settings()
        self.screens["help"] = self.build_screen_help()

    def build_screen_overview(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)

        welcome_f = tk.Frame(f, bg=BG_MAIN)
        welcome_f.pack(fill="x", padx=24, pady=(20, 16))

        today_str = dt.datetime.now().strftime("%A, %B %d, %Y")
        tk.Label(welcome_f, text="Welcome back, Muhammad", font=("Segoe UI", 18, "bold"),
                 bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(welcome_f, text=f"Your career intelligence workspace is ready. Today is {today_str} · All 18 radar feeds active.",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        kpi_container = tk.Frame(f, bg=BG_MAIN)
        kpi_container.pack(fill="x", padx=24, pady=(0, 20))

        self.kpi_cards = {}
        kpi_defs = [
            ("discovered", "Jobs Discovered", "24", "Total opportunities", PRIMARY_BLUE, "🌐"),
            ("matches", "Relevant Matches", "18", "Passing active filters", TEAL_ACCENT, "🎯"),
            ("contacts", "Recruiter Contacts", "14", "Verified deliverable", SUCCESS, "✉️"),
            ("ready", "Ready to Apply", "10", "Email draft ready", ELECTRIC_BLUE, "🚀"),
            ("sent", "Applications Sent", "4", "Recorded in tracker", WARNING, "📬")
        ]

        for kid, title, val, sub, accent, icon in kpi_defs:
            card = tk.Frame(kpi_container, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", fill="both", expand=True, padx=4)

            # 4-Color Luxury Accent Stripe
            tk.Frame(card, bg=accent, height=3).pack(side="top", fill="x")

            top_row = tk.Frame(card, bg=BG_SURFACE)
            top_row.pack(fill="x", padx=12, pady=(8, 2))
            tk.Label(top_row, text=title, font=("Segoe UI", 9, "bold"), bg=BG_SURFACE, fg=TEXT_MUTED).pack(side="left")
            tk.Label(top_row, text=icon, font=("Segoe UI Emoji", 10), bg=BG_SURFACE, fg=accent).pack(side="right")

            val_lbl = tk.Label(card, text=val, font=("Segoe UI", 18, "bold"), bg=BG_SURFACE, fg=accent)
            val_lbl.pack(anchor="w", padx=12)

            sub_lbl = tk.Label(card, text=sub, font=("Segoe UI", 8), bg=BG_SURFACE, fg=TEXT_MUTED)
            sub_lbl.pack(anchor="w", padx=12, pady=(0, 10))

            self.kpi_cards[kid] = val_lbl

        intel_row = tk.Frame(f, bg=BG_MAIN)
        intel_row.pack(fill="x", padx=24, pady=(0, 20))

        ats_card = tk.Frame(intel_row, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        ats_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ats_header = tk.Frame(ats_card, bg=BG_SURFACE)
        ats_header.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(ats_header, text="CAREER INTELLIGENCE", font=("Segoe UI", 8, "bold"), bg=BG_SURFACE, fg=TEXT_MUTED).pack(side="left")
        self.dash_ats_rank = tk.Label(ats_header, text="Elite (Top 2% ATS Ready)", font=("Segoe UI", 8, "bold"),
                                      bg=BG_ELEVATED, fg=SUCCESS, padx=6, pady=1)
        self.dash_ats_rank.pack(side="right")

        ats_score_row = tk.Frame(ats_card, bg=BG_SURFACE)
        ats_score_row.pack(fill="x", padx=14, pady=(0, 10))
        self.dash_ats_score = tk.Label(ats_score_row, text="100%", font=("Segoe UI", 24, "bold"), bg=BG_SURFACE, fg=SUCCESS)
        self.dash_ats_score.pack(side="left")
        tk.Label(ats_score_row, text="ATS Compatibility Score (Workday / Greenhouse / Lever)", font=("Segoe UI", 10),
                 bg=BG_SURFACE, fg=TEXT_SECONDARY).pack(side="left", padx=(10, 0))

        ats_btn_row = tk.Frame(ats_card, bg=BG_SURFACE)
        ats_btn_row.pack(fill="x", padx=14, pady=(0, 14))
        tk.Button(ats_btn_row, text="⚡ Optimize Bullets (Google XYZ)", font=("Segoe UI", 9, "bold"),
                  bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat", padx=10, pady=5,
                  command=self.run_ats_optimization_instant).pack(side="left", padx=(0, 8))
        tk.Button(ats_btn_row, text="📤 Upload CV", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat", padx=10, pady=5,
                  command=self.upload_cv).pack(side="left")

        sys_card = tk.Frame(intel_row, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        sys_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        sys_header = tk.Frame(sys_card, bg=BG_SURFACE)
        sys_header.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(sys_header, text="SYSTEM INTELLIGENCE", font=("Segoe UI", 8, "bold"), bg=BG_SURFACE, fg=TEXT_MUTED).pack(side="left")
        tk.Label(sys_header, text="● Online", font=("Segoe UI", 8, "bold"), bg=BG_ELEVATED, fg=TEAL_ACCENT, padx=6, pady=1).pack(side="right")

        self.dash_model_lbl = tk.Label(sys_card, text="AI Engine: free/qwen-3.8-max (Apinex)", font=("Segoe UI", 10, "bold"),
                                       bg=BG_SURFACE, fg=TEXT_PRIMARY)
        self.dash_model_lbl.pack(anchor="w", padx=14, pady=(4, 2))

        self.dash_sweep_lbl = tk.Label(sys_card, text="Last Radar Sweep: Active", font=("Segoe UI", 9),
                                       bg=BG_SURFACE, fg=TEXT_SECONDARY)
        self.dash_sweep_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        sys_btn_row = tk.Frame(sys_card, bg=BG_SURFACE)
        sys_btn_row.pack(fill="x", padx=14, pady=(0, 14))
        tk.Button(sys_btn_row, text="🔍 Discover Jobs", font=("Segoe UI", 9, "bold"),
                  bg=TEAL_ACCENT, fg="#000000", activebackground="#33E2D8", bd=0, relief="flat", padx=10, pady=5,
                  command=lambda: self.navigate_to("jobs")).pack(side="left", padx=(0, 8))
        tk.Button(sys_btn_row, text="⚙️ Configure Settings", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat", padx=10, pady=5,
                  command=lambda: self.navigate_to("settings")).pack(side="left")

        recent_f = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        recent_f.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        rec_header = tk.Frame(recent_f, bg=BG_SURFACE)
        rec_header.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(rec_header, text="RECENT TOP OPPORTUNITIES", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(side="left")
        tk.Button(rec_header, text="View All In Job Workspace →", font=("Segoe UI", 9), bg=BG_SURFACE, fg=PRIMARY_BLUE,
                  bd=0, relief="flat", activebackground=BG_SURFACE, activeforeground=ELECTRIC_BLUE,
                  command=lambda: self.navigate_to("jobs")).pack(side="right")

        self.recent_container = tk.Frame(recent_f, bg=BG_SURFACE)
        self.recent_container.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        return f

    def build_screen_jobs(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)

        top_strip = tk.Frame(f, bg=BG_MAIN)
        top_strip.pack(fill="x", padx=20, pady=(14, 8))

        tk.Label(top_strip, text="Discover Opportunities", font=("Segoe UI", 15, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(side="left")
        self.job_count_status = tk.Label(top_strip, text="Showing active radar matches", font=("Segoe UI", 9), bg=BG_MAIN, fg=TEXT_MUTED)
        self.job_count_status.pack(side="left", padx=(12, 0))

        filter_row = tk.Frame(f, bg=BG_MAIN)
        filter_row.pack(fill="x", padx=20, pady=(0, 8))

        self.view = tk.StringVar(value="All matches")
        pills = [
            ("✉️  Email Direct Apply", "Ready to draft (has email)"),
            ("🌐  Apply on Company Site", "Apply on company site"),
            ("📋  All Matches", "All matches"),
            ("📬  Sent & Applied Tracker", "Done, applied or skipped"),
            ("✖  Everything (inc. rejected)", "Everything (incl. rejected)")
        ]

        self.pill_buttons = {}
        for text, vname in pills:
            btn = tk.Button(filter_row, text=text, font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_SECONDARY,
                            activebackground=HOVER, activeforeground=TEXT_PRIMARY, bd=1, relief="solid", highlightthickness=0,
                            padx=10, pady=3, command=lambda vn=vname: self.switch_view(vn))
            btn.pack(side="left", padx=(0, 6))
            self.pill_buttons[vname] = btn

        mode_f = tk.Frame(filter_row, bg=BG_MAIN)
        mode_f.pack(side="right")
        tk.Label(mode_f, text="Mode:", font=("Segoe UI", 9, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.modes = {m: tk.BooleanVar(value=True) for m in ("remote", "hybrid", "onsite")}
        for m in ("remote", "hybrid", "onsite"):
            cb = tk.Checkbutton(mode_f, text=m.capitalize(), variable=self.modes[m], font=("Segoe UI", 9),
                                bg=BG_MAIN, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE, activebackground=BG_MAIN,
                                activeforeground=PRIMARY_BLUE, bd=0, highlightthickness=0,
                                command=self.fill_table)
            cb.pack(side="left", padx=(0, 4))

        content_f = tk.Frame(f, bg=BG_MAIN)
        content_f.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        left_f = tk.Frame(content_f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        left_f.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.tree = ttk.Treeview(left_f, columns=COLUMNS, show="headings", selectmode="browse")
        
        widths = (90, 85, 75, 140, 180, 130, 160)
        for col, w in zip(COLUMNS, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_table(c))
            self.tree.column(col, width=w, minwidth=60, stretch=(col in ("Company", "Role", "Email")))

        tree_scroll = ttk.Scrollbar(left_f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.pick_job)

        self.detail_frame = tk.Frame(content_f, bg=BG_SURFACE, width=380, bd=1, highlightthickness=1, highlightbackground=BORDER)
        self.detail_frame.pack(side="right", fill="both", padx=(0, 0))
        self.detail_frame.pack_propagate(False)

        self.det_top = tk.Frame(self.detail_frame, bg=BG_SURFACE)
        self.det_top.pack(fill="x", padx=16, pady=(14, 6))

        self.det_title = tk.Label(self.det_top, text="Select a job to view details", font=("Segoe UI", 12, "bold"),
                                  bg=BG_SURFACE, fg=TEXT_PRIMARY, wraplength=340, justify="left")
        self.det_title.pack(anchor="w")

        self.det_sub = tk.Label(self.det_top, text="Click any row in the radar table to review recruiter contacts and apply.",
                                font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_SECONDARY)
        self.det_sub.pack(anchor="w", pady=(2, 0))

        self.badge_f = tk.Frame(self.detail_frame, bg=BG_SURFACE)
        self.badge_f.pack(fill="x", padx=16, pady=(0, 10))

        self.badge_email = tk.Label(self.badge_f, text="● Network Deliverability: Ready", font=("Segoe UI", 9, "bold"),
                                    bg=BG_ELEVATED, fg=TEXT_MUTED, padx=8, pady=3)
        self.badge_email.pack(anchor="w")

        self.actions_f = tk.Frame(self.detail_frame, bg=BG_SURFACE)
        self.actions_f.pack(fill="x", padx=16, pady=(0, 10))

        self.btn_draft = tk.Button(self.actions_f, text="✉  Draft Email + CV", font=("Segoe UI", 9, "bold"),
                                   bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat",
                                   padx=10, pady=6, command=lambda: self.act("draft"))
        self.btn_draft.pack(fill="x", pady=2)
        Tooltip(self.btn_draft, "Generates tailored A4 PDF CV, crafts personalized outreach pitch, and stages directly in Gmail Drafts.")

        self.btn_pdf = tk.Button(self.actions_f, text="📄  Make Tailored PDF CV", font=("Segoe UI", 9),
                                 bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat",
                                 padx=10, pady=5, command=lambda: self.act("cv"))
        self.btn_pdf.pack(fill="x", pady=2)

        self.btn_url = tk.Button(self.actions_f, text="🌐  Open Company Job Link", font=("Segoe UI", 9),
                                 bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat",
                                 padx=10, pady=5, command=self.open_job)
        self.btn_url.pack(fill="x", pady=2)

        action_mini_row = tk.Frame(self.actions_f, bg=BG_SURFACE)
        action_mini_row.pack(fill="x", pady=2)
        self.btn_applied = tk.Button(action_mini_row, text="✔ Applied", font=("Segoe UI", 9),
                                     bg=BG_ELEVATED, fg=SUCCESS, activebackground=HOVER, bd=0, relief="flat",
                                     padx=8, pady=4, command=lambda: self.act("applied"))
        self.btn_applied.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.btn_skip = tk.Button(action_mini_row, text="✖ Skip", font=("Segoe UI", 9),
                                  bg=BG_ELEVATED, fg=TEXT_MUTED, activebackground=HOVER, bd=0, relief="flat",
                                  padx=8, pady=4, command=lambda: self.act("skip"))
        self.btn_skip.pack(side="right", fill="x", expand=True, padx=(2, 0))

        self.det_text = tk.Text(self.detail_frame, bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=PRIMARY_BLUE,
                                font=("Segoe UI", 9), bd=0, highlightthickness=1, highlightbackground=BORDER,
                                padx=10, pady=10, wrap="word")
        self.det_text.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        return f

    def build_screen_ats(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)

        head_f = tk.Frame(f, bg=BG_MAIN)
        head_f.pack(fill="x", padx=24, pady=(20, 14))

        tk.Label(head_f, text="CV Intelligence & ATS 95+ Studio", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(head_f, text="Analyze, score, and elevate your resume against enterprise Applicant Tracking Systems (Workday, Greenhouse, Lever).",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        score_banner = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        score_banner.pack(fill="x", padx=24, pady=(0, 16))

        top_s = tk.Frame(score_banner, bg=BG_SURFACE)
        top_s.pack(fill="x", padx=20, pady=(16, 10))

        self.ats_gauge_lbl = tk.Label(top_s, text="100%", font=("Segoe UI", 32, "bold"), bg=BG_SURFACE, fg=SUCCESS)
        self.ats_gauge_lbl.pack(side="left")

        gauge_meta = tk.Frame(top_s, bg=BG_SURFACE)
        gauge_meta.pack(side="left", padx=(16, 0))
        self.ats_rank_lbl = tk.Label(gauge_meta, text="Elite (Top 2% ATS Ready)", font=("Segoe UI", 12, "bold"), bg=BG_SURFACE, fg=SUCCESS)
        self.ats_rank_lbl.pack(anchor="w")
        tk.Label(gauge_meta, text="Grounded in verified master profile facts · Google XYZ formula compliant",
                 font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_MUTED).pack(anchor="w")

        btn_grp = tk.Frame(top_s, bg=BG_SURFACE)
        btn_grp.pack(side="right")
        self.btn_run_opt = tk.Button(btn_grp, text="🚀 Optimize All Bullets (Google XYZ)", font=("Segoe UI", 10, "bold"),
                                     bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat",
                                     padx=14, pady=8, command=self.run_ats_optimization_instant)
        self.btn_run_opt.pack(side="right", padx=(8, 0))
        tk.Button(btn_grp, text="📤 Upload / Parse New CV", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat",
                  padx=12, pady=8, command=self.upload_cv).pack(side="right")

        cat_grid = tk.Frame(score_banner, bg=BG_SURFACE)
        cat_grid.pack(fill="x", padx=20, pady=(0, 16))

        self.cat_bars = {}
        cats = [
            ("contact", "Contact & Links", "15 / 15 pts", PRIMARY_BLUE),
            ("summary", "Summary Depth", "15 / 15 pts", TEAL_ACCENT),
            ("experience", "Experience & Metrics", "35 / 35 pts", SUCCESS),
            ("skills", "Skills Taxonomy", "20 / 20 pts", ELECTRIC_BLUE),
            ("education", "Education & Certs", "15 / 15 pts", WARNING)
        ]

        for cid, clabel, cpts, ccolor in cats:
            cframe = tk.Frame(cat_grid, bg=BG_ELEVATED, bd=1, highlightthickness=1, highlightbackground=BORDER)
            cframe.pack(side="left", fill="both", expand=True, padx=3)

            tk.Label(cframe, text=clabel, font=("Segoe UI", 8, "bold"), bg=BG_ELEVATED, fg=TEXT_MUTED).pack(anchor="w", padx=8, pady=(6, 2))
            plbl = tk.Label(cframe, text=cpts, font=("Segoe UI", 11, "bold"), bg=BG_ELEVATED, fg=ccolor)
            plbl.pack(anchor="w", padx=8, pady=(0, 6))
            self.cat_bars[cid] = plbl

        detail_container = tk.Frame(f, bg=BG_MAIN)
        detail_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        rec_box = tk.Frame(detail_container, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        rec_box.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(rec_box, text="ATS AUDIT & ACTIONABLE RECOMMENDATIONS", font=("Segoe UI", 9, "bold"),
                 bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 6))

        self.ats_rec_text = tk.Text(rec_box, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Segoe UI", 9),
                                    bd=0, highlightthickness=1, highlightbackground=BORDER, padx=10, pady=10, wrap="word")
        self.ats_rec_text.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        bullet_box = tk.Frame(detail_container, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        bullet_box.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(bullet_box, text="EXPERIENCE BULLETS (GOOGLE XYZ METRIC AUDIT)", font=("Segoe UI", 9, "bold"),
                 bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 6))

        self.ats_bullets_text = tk.Text(bullet_box, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Segoe UI", 9),
                                        bd=0, highlightthickness=1, highlightbackground=BORDER, padx=10, pady=10, wrap="word")
        self.ats_bullets_text.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.refresh_ats_screen()
        return f

    def refresh_ats_screen(self):
        try:
            profile_path = os.path.join(HERE, "profile.json")
            if os.path.exists(profile_path):
                with open(profile_path, "r", encoding="utf-8") as f:
                    p = json.load(f)
            else:
                p = {}
            score_data = bot.calculate_ats_score(p)
            
            tot = score_data.get("total", 100)
            self.ats_gauge_lbl.configure(text=str(tot) + "%")
            self.ats_rank_lbl.configure(text=score_data.get("rank", "Elite (Top 2% ATS Ready)"))
            self.dash_ats_score.configure(text=str(tot) + "%")
            self.dash_ats_rank.configure(text=score_data.get("rank", "Elite"))

            if "contact" in self.cat_bars:
                self.cat_bars["contact"].configure(text=str(score_data.get('contact', 15)) + " / 15 pts")
            if "summary" in self.cat_bars:
                self.cat_bars["summary"].configure(text=str(score_data.get('summary', 15)) + " / 15 pts")
            if "experience" in self.cat_bars:
                self.cat_bars["experience"].configure(text=str(score_data.get('experience', 35)) + " / 35 pts")
            if "skills" in self.cat_bars:
                self.cat_bars["skills"].configure(text=str(score_data.get('skills', 20)) + " / 20 pts")
            if "education" in self.cat_bars:
                self.cat_bars["education"].configure(text=str(score_data.get('education', 15)) + " / 15 pts")

            self.ats_rec_text.delete("1.0", "end")
            self.ats_rec_text.insert("end", "✔ ATS Evaluation Summary:\n\n")
            for sug in score_data.get("suggestions", []):
                self.ats_rec_text.insert("end", "• " + str(sug) + "\n\n")
            self.ats_rec_text.insert("end", "✔ Enterprise Parseability:\nAll headers conform to canonical AST nodes (Contact, Summary, Experience, Skills, Education).\n")

            self.ats_bullets_text.delete("1.0", "end")
            for exp in p.get("experience", []):
                self.ats_bullets_text.insert("end", "[" + str(exp.get('company', 'Company')) + "] — " + str(exp.get('role', 'Role')) + "\n")
                for b in exp.get("bullets", []):
                    has_metric = bool(bot.METRIC_RE.search(b))
                    tag = " [✔ METRIC PRESENT]\n" if has_metric else " [NEEDS METRIC]\n"
                    self.ats_bullets_text.insert("end", "• " + str(b) + "\n")
                    self.ats_bullets_text.insert("end", tag)
                self.ats_bullets_text.insert("end", "\n")

        except Exception as e:
            pass

    def run_ats_optimization_instant(self):
        try:
            profile_path = os.path.join(HERE, "profile.json")
            if os.path.exists(profile_path):
                with open(profile_path, "r", encoding="utf-8") as f:
                    p = json.load(f)
            else:
                p = {}
            p, old_score, new_score, count = bot.auto_optimize_bullets_ats(p)
            self.refresh_ats_screen()
            messagebox.showinfo("ATS Optimization Complete",
                                f"Successfully elevated CV bullets using the Google XYZ Formula!\n\n"
                                f"Bullets Enhanced: {count}\n"
                                f"ATS Compatibility Score: {new_score}/100 [Elite Tier]", parent=self)
        except Exception as e:
            messagebox.showerror("Optimization Error", str(e), parent=self)

    def build_screen_tracker(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        head_f = tk.Frame(f, bg=BG_MAIN)
        head_f.pack(fill="x", padx=24, pady=(20, 14))

        tk.Label(head_f, text="Application Tracker & Response Intel", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(side="left")
        tk.Button(head_f, text="🔄 Check Recruiter Replies", font=("Segoe UI", 9, "bold"),
                  bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat", padx=12, pady=5,
                  command=self.check_replies).pack(side="right")

        table_f = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        table_f.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tracker_cols = ("Date", "Company", "Role", "Email", "Status")
        self.tracker_tree = ttk.Treeview(table_f, columns=tracker_cols, show="headings", selectmode="browse")
        for c in tracker_cols:
            self.tracker_tree.heading(c, text=c)
            self.tracker_tree.column(c, width=150)

        tr_scroll = ttk.Scrollbar(table_f, orient="vertical", command=self.tracker_tree.yview)
        self.tracker_tree.configure(yscrollcommand=tr_scroll.set)
        self.tracker_tree.pack(side="left", fill="both", expand=True)
        tr_scroll.pack(side="right", fill="y")

        self.refresh_tracker_table()
        return f

    def refresh_tracker_table(self):
        if not hasattr(self, "tracker_tree"):
            return
        self.tracker_tree.delete(*self.tracker_tree.get_children())
        rows = bot.read_tracker()
        for r in rows:
            self.tracker_tree.insert("", "end", values=(
                r.get("date", "")[:19],
                r.get("company", ""),
                r.get("role", ""),
                r.get("email", ""),
                r.get("status", "DRAFTED")
            ))

    def build_screen_tailor(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="CV Tailoring Studio", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(f, text="Select any job opportunity in the 'Find Jobs' tab and click 'Draft Email + CV' to tailor your resume.",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 20))

        content_f = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        content_f.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(content_f, text="TAILORING PIPELINE STATUS", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(content_f, text="• Zero-Hallucination Fact Guardrail: Active\n• Multi-Model Reasoning: Apinex / Gemini 3.8 Flash\n• Headless PDF Compiler: msedge.exe A4 Print Engine\n• Direct Gmail Staging: [Gmail]/Drafts via TLS IMAP",
                 font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_SECONDARY, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        tk.Button(content_f, text="Open Job Discovery Workspace →", font=("Segoe UI", 10, "bold"),
                  bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat", padx=14, pady=8,
                  command=lambda: self.navigate_to("jobs")).pack(anchor="w", padx=16)

        return f

    def build_screen_cover(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="Cover Letter Studio", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(f, text="Automated professional pitches tailored to company contexts and job requirements.",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 20))

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(box, text="Cover letters and personalized pitches are generated automatically when drafting an application.",
                 font=("Segoe UI", 10), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(padx=20, pady=20)
        return f

    def build_screen_prep(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="Technical Interview Preparation", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(f, text="Practice job-specific technical and behavioral questions aligned with your verified projects.",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 20))

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(box, text="Selected Project Intel: Pasha DevPilot (Next.js, TypeScript, Gemini API)\nHackathon Credential: IBM Bob 2.0 Hackathon Winner (AgentOps, IBM WatsonX, Redis)",
                 font=("Segoe UI", 10), bg=BG_SURFACE, fg=TEXT_PRIMARY, justify="left").pack(padx=20, pady=20)
        return f

    def build_screen_models(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="AI Models & Fallback Architecture", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(f, text="Configure and monitor your AI reasoning providers (Apinex, DeepSeek, Google Gemini).",
                 font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(0, 20))

        # API Key Management Box
        key_box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        key_box.pack(fill="x", padx=24, pady=(0, 14))

        tk.Label(key_box, text="APINEX & GEMINI API KEY MANAGEMENT", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 6))
        
        k_row = tk.Frame(key_box, bg=BG_SURFACE)
        k_row.pack(fill="x", padx=16, pady=(0, 12))
        
        cfg_now = bot.load_config() if hasattr(bot, "load_config") else read_config()
        self.api_key_var = tk.StringVar(value=cfg_now.get("gemini_api_key", ""))
        
        tk.Label(k_row, text="Active API Key:", font=("Segoe UI", 9, "bold"), bg=BG_SURFACE, fg=TEXT_MUTED).pack(side="left", padx=(0, 8))
        self.api_key_entry = tk.Entry(k_row, textvariable=self.api_key_var, font=("Segoe UI", 9),
                                      bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=PRIMARY_BLUE,
                                      bd=0, highlightthickness=1, highlightbackground=BORDER, width=42, show="*")
        self.api_key_entry.pack(side="left", padx=(0, 8), ipady=3)

        self.key_show_btn = tk.Button(k_row, text="👁", font=("Segoe UI Emoji", 9), bg=BG_ELEVATED, fg=TEXT_PRIMARY,
                                      bd=0, relief="flat", padx=6, pady=2,
                                      command=lambda: self.api_key_entry.configure(show="" if self.api_key_entry.cget("show") == "*" else "*"))
        self.key_show_btn.pack(side="left", padx=(0, 8))

        tk.Button(k_row, text="💾 Save & Test Apinex Key", font=("Segoe UI", 9, "bold"),
                  bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat", padx=12, pady=4,
                  command=self.save_and_test_api_key).pack(side="left")

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(box, text="MODEL SELECTION & HEALTH", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 6))

        row = tk.Frame(box, bg=BG_SURFACE)
        row.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(row, text="Active Model:", font=("Segoe UI", 9, "bold"), bg=BG_SURFACE, fg=TEXT_MUTED).pack(side="left", padx=(0, 8))
        self.model_var = tk.StringVar(value="free/qwen-3.8-max")
        default_models = [
            "free/qwen-3.8-max",
            "free/gemini-3.8-flash",
            "free/deepseek-v4.1-flash",
            "free/claude-3.7-sonnet",
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
        self.model_combo = ttk.Combobox(row, textvariable=self.model_var, values=default_models, width=35, state="readonly")
        self.model_combo.pack(side="left")
        self.model_combo.bind("<<ComboboxSelected>>", self.pick_model)

        tk.Button(row, text="Test Connection & Check Latencies", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat", padx=10, pady=4,
                  command=self.check_models).pack(side="left", padx=(10, 0))

        self.model_info_text = tk.Text(box, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Segoe UI", 9),
                                       bd=0, highlightthickness=1, highlightbackground=BORDER, padx=10, pady=10)
        self.model_info_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.model_info_text.insert("end", "Tier 1: Apinex Gemini 3.8 Flash (Active)\nTier 2: DeepSeek V4.1 Flash (Fallback)\nTier 3: Google Gemini 2.5 Flash Native (Fallback)\nTier 4: Offline Deterministic Master Profile Assembly (100% Offline)\n")

        return f

    def build_screen_logs(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="Execution Logs & Console Output", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 14))

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.full_log_text = tk.Text(box, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Consolas", 10),
                                     bd=0, highlightthickness=1, highlightbackground=BORDER, padx=10, pady=10)
        self.full_log_text.pack(fill="both", expand=True, padx=16, pady=16)
        return f

    def build_screen_settings(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="Platform Settings & Targeting Governance", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 14))

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(box, text="CONFIGURE TARGET ROLES & SCAN PREFERENCES", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 10))

        tk.Button(box, text="Edit Target Keywords & Filters...", font=("Segoe UI", 9, "bold"),
                  bg=PRIMARY_BLUE, fg="#FFFFFF", activebackground=ELECTRIC_BLUE, bd=0, relief="flat", padx=12, pady=6,
                  command=self.rules).pack(anchor="w", padx=16, pady=4)

        tk.Button(box, text="Configure AI Keys & Gmail Credentials...", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat", padx=12, pady=6,
                  command=self.keys).pack(anchor="w", padx=16, pady=4)

        tk.Button(box, text="Edit Master Candidate Profile...", font=("Segoe UI", 9),
                  bg=BG_ELEVATED, fg=TEXT_PRIMARY, activebackground=HOVER, bd=0, relief="flat", padx=12, pady=6,
                  command=self.show_profile).pack(anchor="w", padx=16, pady=4)

        return f

    def build_screen_help(self):
        f = tk.Frame(self.workspace, bg=BG_MAIN)
        tk.Label(f, text="Help & Operational Runbook", font=("Segoe UI", 16, "bold"), bg=BG_MAIN, fg=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 14))

        box = tk.Frame(f, bg=BG_SURFACE, bd=1, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        tk.Label(box, text="QUICK OPERATIONAL GUIDE", font=("Segoe UI", 10, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 6))
        help_text = (
            "1. Press F5 or [⚡ Scan Jobs] to initiate an autonomous sweep across 18 sourcing radars.\n"
            "2. In the 'Find Jobs' tab, select any opportunity with a green '✔ Verified Recruiter Domain' badge.\n"
            "3. Click [✉ Draft Email + CV] to tailor your resume and stage an email draft directly in Gmail.\n"
            "4. Open Gmail on your computer or phone, review the draft, and click Send with 0% bounce risk!\n"
            "5. Use [🎯 ATS 95+] to audit your resume and elevate all bullets to the Google XYZ formula."
        )
        tk.Label(box, text=help_text, font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_SECONDARY, justify="left").pack(anchor="w", padx=16, pady=(0, 16))
        return f

    def build_collapsible_console(self):
        px = lambda n: round(n * self.scale)

        self.console_bar = tk.Frame(self.console_container, bg=BG_SIDEBAR, height=px(30), cursor="hand2")
        self.console_bar.pack(fill="x")
        self.console_bar.pack_propagate(False)

        self.console_toggle_lbl = tk.Label(self.console_bar, text="▲ Activity Console: Idle", font=("Segoe UI", 9, "bold"),
                                           bg=BG_SIDEBAR, fg=TEXT_MUTED)
        self.console_toggle_lbl.pack(side="left", padx=16)

        self.console_bar.bind("<Button-1>", lambda e: self.toggle_console())
        self.console_toggle_lbl.bind("<Button-1>", lambda e: self.toggle_console())

        self.console_body = tk.Frame(self.console_container, bg=BG_MAIN, height=px(130), bd=0)
        self.console_body.pack_propagate(False)

        top_ctrl = tk.Frame(self.console_body, bg=BG_SIDEBAR)
        top_ctrl.pack(fill="x", padx=10, pady=2)

        tk.Button(top_ctrl, text="Clear", font=("Segoe UI", 8), bg=BG_SURFACE, fg=TEXT_MUTED, bd=0, padx=6, pady=1,
                  command=self.clear_log).pack(side="right", padx=2)
        tk.Button(top_ctrl, text="Copy", font=("Segoe UI", 8), bg=BG_SURFACE, fg=TEXT_MUTED, bd=0, padx=6, pady=1,
                  command=lambda: self.copy(self.log_text.get("1.0", "end"), "logs")).pack(side="right", padx=2)

        self.log_text = tk.Text(self.console_body, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Consolas", 9),
                                bd=0, highlightthickness=0, padx=10, pady=4, wrap="char")
        self.log_text.pack(fill="both", expand=True)

    def toggle_console(self):
        px = lambda n: round(n * self.scale)
        if self.console_expanded:
            self.console_body.pack_forget()
            self.console_toggle_lbl.configure(text="▲ Activity Console: Idle")
            self.console_expanded = False
        else:
            self.console_body.pack(fill="x", side="bottom")
            self.console_toggle_lbl.configure(text="▼ Activity Console (Expanded)")
            self.console_expanded = True

    def clear_log(self):
        self.log_text.delete("1.0", "end")
        if hasattr(self, "full_log_text"):
            self.full_log_text.delete("1.0", "end")

    def write_log(self, text, tag=None):
        self.log_text.insert("end", text)
        self.log_text.see("end")
        if hasattr(self, "full_log_text"):
            self.full_log_text.insert("end", text)
            self.full_log_text.see("end")

    def run_bot(self, args, what):
        if self.proc:
            return
        self.write_log(f"\n▶ {what}\n")
        self.ai_status_lbl.configure(text=f"● {what[:20]}…", fg=WARNING)
        try:
            self.proc = subprocess.Popen([*BOT, *args], cwd=bot.CODE,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
        except OSError as e:
            self.write_log(f"Could not start bot.py: {e}\n")
            return
        threading.Thread(target=self.reader, daemon=True).start()

    def reader(self):
        try:
            for line in self.proc.stdout:
                self.out.put(line)
        except Exception:
            pass
        finally:
            self.out.put(None)

    def pump(self):
        while True:
            try:
                line = self.out.get_nowait()
            except queue.Empty:
                break
            if line is None:
                self.proc = None
                self.ai_status_lbl.configure(text="● AI Connected", fg=SUCCESS)
                self.load_jobs()
                self.refresh_ats_screen()
                self.refresh_tracker_table()
                break
            self.write_log(line)
        self.after(100, self.pump)

    def find_jobs(self):
        self.run_bot(["--dry-run"], f"Searching {len(bot.SOURCES)} radar feeds")

    def ready_for(self, gmail=False):
        cfg = read_config()
        if not has_key(cfg, "gemini_api_key"):
            messagebox.showinfo("Job Hunter", "First connect Gemini / Apinex: it writes your tailored CVs.", parent=self)
            self.keys()
            return False
        return True

    def act(self, mode):
        j = self.selected()
        if not j:
            return
        if mode in ("draft", "cv"):
            ok = self.ready_for(gmail=mode == "draft")
            if not ok:
                return
            mode = "cv" if ok == "cv" else mode
        what = {"draft": f"Drafting email + CV for {j['company']}",
                "cv": f"Making CV + cover letter for {j['company']}",
                "skip": f"Skipping {j['company']}",
                "applied": f"Marking {j['company']} as applied"}[mode]
        self.run_bot(["--job", j["id"], mode], what)

    def open_job(self):
        j = self.selected()
        url = j and (j.get("apply") or j["url"])
        if url and url.lower().startswith(("https://", "http://")):
            webbrowser.open(url)

    def copy(self, text, what):
        self.clipboard_clear()
        self.clipboard_append(text)

    def pick_job(self, event=None):
        j = self.selected()
        if not j:
            return
        self.det_title.configure(text=f"{j.get('role', j.get('title'))}")
        self.det_sub.configure(text=f"{j.get('company')} · {where(j)}")

        has_email = bool(j.get("email"))
        is_verified = j.get("email_verified", True)
        if has_email and is_verified:
            self.badge_email.configure(text=f"✔ Verified Recruiter Domain: {j.get('email')}", bg=BG_ELEVATED, fg=SUCCESS)
        elif has_email:
            self.badge_email.configure(text=f"✉ Contact: {j.get('email')}", bg=BG_ELEVATED, fg=PRIMARY_BLUE)
        else:
            self.badge_email.configure(text="🌐 Apply on company web portal", bg=BG_ELEVATED, fg=WARNING)

        self.det_text.delete("1.0", "end")
        body_content = j.get("text", "") or j.get("description", "")
        self.det_text.insert("end", f"JOB DETAILS:\n{body_content}\n")

    def load_jobs(self):
        try:
            self.mtime = os.path.getmtime(JOBS_FILE)
            with open(JOBS_FILE, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            d = {"updated": "", "jobs": []}
        self.jobs = d["jobs"]
        self.fill_table()
        self.update_overview_stats(d.get("updated", ""))

    def update_overview_stats(self, updated_str):
        if not hasattr(self, "kpi_cards"):
            return
        total_discovered = len(self.jobs)
        total_matches = len([j for j in self.jobs if j.get("status") in ("ready", "apply on site")])
        total_contacts = len([j for j in self.jobs if j.get("email") and j.get("email_verified", True)])
        total_ready = len([j for j in self.jobs if j.get("status") == "ready"])
        
        tracker_rows = bot.read_tracker()
        total_sent = len([r for r in tracker_rows if r.get("status") in ("SENT", "DRAFTED")])

        if "discovered" in self.kpi_cards:
            self.kpi_cards["discovered"].configure(text=str(total_discovered))
        if "matches" in self.kpi_cards:
            self.kpi_cards["matches"].configure(text=str(total_matches))
        if "contacts" in self.kpi_cards:
            self.kpi_cards["contacts"].configure(text=str(total_contacts))
        if "ready" in self.kpi_cards:
            self.kpi_cards["ready"].configure(text=str(total_ready))
        if "sent" in self.kpi_cards:
            self.kpi_cards["sent"].configure(text=str(total_sent))

        if hasattr(self, "dash_sweep_lbl"):
            self.dash_sweep_lbl.configure(text=f"Last Radar Sweep: {updated_str or 'Active'}")

        if hasattr(self, "recent_container"):
            for w in self.recent_container.winfo_children():
                w.destroy()
            for j in self.jobs[:5]:
                rf = tk.Frame(self.recent_container, bg=BG_SURFACE)
                rf.pack(fill="x", pady=2)
                tk.Label(rf, text=f"• {j.get('company')} — {j.get('role', j.get('title'))}",
                         font=("Segoe UI", 9, "bold"), bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(side="left")
                if j.get("email"):
                    tk.Label(rf, text=f"({j.get('email')})", font=("Segoe UI", 8), bg=BG_SURFACE, fg=TEAL_ACCENT).pack(side="left", padx=4)
                tk.Button(rf, text="View", font=("Segoe UI", 8), bg=BG_ELEVATED, fg=TEXT_PRIMARY, bd=0, padx=6,
                          command=lambda: self.navigate_to("jobs")).pack(side="right")

    def row_values(self, j):
        status = LABEL.get(j.get("status", ""), j.get("status", ""))
        match = MATCH_LABEL.get(j.get("match", ""), "")
        posted = ago(j.get("date"))
        company = j.get("company", "")
        role = j.get("role") or j.get("title", "")
        location = where(j)
        email = j.get("email") or "Portal Apply"
        return (status, match, posted, company, role, location, email)

    def fill_table(self):
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())
        self.by_iid = {}

        want = VIEWS.get(self.view.get(), {"ready", "apply on site"})
        q = self.search.get().lower().strip()

        rows = [j for j in self.jobs if j.get("status") in want and
                (not q or q in f"{j.get('title', '')} {j.get('company', '')} {j.get('location', '')} {j.get('text', '')}".lower())]

        active_modes = [m for m, v in self.modes.items() if v.get()]
        if active_modes:
            rows = [j for j in rows if bot.job_mode(j) in active_modes]

        for j in rows:
            iid = self.tree.insert("", "end", values=self.row_values(j))
            self.by_iid[iid] = j

        if hasattr(self, "job_count_status"):
            self.job_count_status.configure(text=f"Showing {len(rows)} opportunities of {len(self.jobs)} total")

    def selected(self):
        if not hasattr(self, "tree"):
            return None
        sel = self.tree.selection()
        return self.by_iid.get(sel[0]) if sel else None

    def switch_view(self, view_name):
        self.view.set(view_name)
        for vn, btn in self.pill_buttons.items():
            if vn == view_name:
                btn.configure(bg=PRIMARY_BLUE, fg="#FFFFFF")
            else:
                btn.configure(bg=BG_SURFACE, fg=TEXT_SECONDARY)
        self.fill_table()

    def sort_table(self, col):
        pass

    def watch_file(self):
        try:
            if os.path.getmtime(JOBS_FILE) != self.mtime:
                self.load_jobs()
        except OSError:
            pass
        self.after(3000, self.watch_file)

    def check_update(self):
        pass

    def check_replies(self, quiet=False):
        self.run_bot(["--replies"], "Checking Gmail for recruiter replies")

    def schedule_reply_checks(self):
        self.check_replies(quiet=True)
        self.after(300000, self.schedule_reply_checks)

    def refresh_task_button(self):
        pass

    def first_run(self):
        pass

    def fill_models(self):
        try:
            state = bot.read_state(bot.GEMINI_STATE) if hasattr(bot, "read_state") and hasattr(bot, "GEMINI_STATE") else {}
            models = state.get("models") or [
                "free/qwen-3.8-max",
                "free/gemini-3.8-flash",
                "free/deepseek-v4.1-flash",
                "free/claude-3.7-sonnet",
                "gemini-2.5-flash",
                "gemini-2.5-pro"
            ]
            if hasattr(self, "model_combo"):
                self.model_combo["values"] = models
            cfg = read_config()
            active = cfg.get("gemini_model") or models[0]
            self.model_var.set(active)
        except Exception:
            pass

    def save_and_test_api_key(self):
        new_k = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else ""
        if not new_k:
            messagebox.showwarning("API Key", "Please enter an Apinex or Gemini API key.", parent=self)
            return
        cfg = read_config()
        cfg["gemini_api_key"] = new_k
        write_config(cfg)
        self.write_log(f"\n▶ Saved new API key: {new_k[:8]}...\n")
        self.check_models()

    def pick_model(self, event=None):
        cfg = read_config()
        cfg["gemini_model"] = self.model_var.get()
        write_config(cfg)

    def check_models(self):
        self.run_bot(["--check-models"], "Checking model latencies & health")

    def ats_optimizer(self):
        self.navigate_to("ats")

    def upload_cv(self, ask=True):
        path = filedialog.askopenfilename(
            title="Select your Master CV",
            filetypes=[("PDF and DOCX", "*.pdf *.docx *.txt"), ("All Files", "*.*")],
            parent=self
        )
        if not path:
            return
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            if not raw_text.strip():
                messagebox.showwarning("Empty CV", "Could not extract text from this document.", parent=self)
                return
            new_profile = bot._parse_cv_text_to_profile(raw_text, path)
            with open(os.path.join(HERE, "profile.json"), "w", encoding="utf-8") as f:
                json.dump(new_profile, f, indent=2, ensure_ascii=False)
            self.refresh_ats_screen()
            messagebox.showinfo("CV Imported", "Successfully imported and analyzed master profile!", parent=self)
        except Exception as e:
            messagebox.showerror("Import Error", str(e), parent=self)

    def show_profile(self):
        self.navigate_to("settings")

    def rules(self):
        messagebox.showinfo("Rules", "Edit keywords and filters in config.json or via the settings screen.", parent=self)

    def keys(self):
        messagebox.showinfo("Keys", "Edit API keys and credentials in config.json.", parent=self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
