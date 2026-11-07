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

# ---------- 5-Color Luxury Theme (User Selected Palette) ----------
# 1. Indigo: #540D6E (Deep Royal Violet)
# 2. Watermelon: #EE4266 (Vibrant Coral Red)
# 3. Golden Pollen: #FFD23F (Warm Vivid Gold)
# 4. Turquoise: #3BCEAC (Electric Mint Aqua)
# 5. Jungle Green: #0EAD69 (Cyber Emerald)
INDIGO = "#540D6E"
WATERMELON = "#EE4266"
GOLD = "#FFD23F"
TURQUOISE = "#3BCEAC"
JUNGLE = "#0EAD69"

GRADIENT = [(10, 7, 20), (22, 13, 38), (35, 18, 56), (18, 11, 32)]  # Deep obsidian infused with Indigo
PERIOD = 2400   # pixels along the diagonal before the colours repeat
BAND = 6        # width of one colour band
GAP, PAD, RADIUS = 14, 10, 14  # space between cards, card padding, corner radius
FROST, SMOKE = 0.15, 0.80       # subtle dark glass tinting
WHITE, NIGHT = (255, 255, 255), (10, 7, 20)
INK, MUTED, LIGHT_INK, LIGHT_MUTED = "#F8FAFC", "#A79BBF", "#F8FAFC", "#A79BBF"
SURFACE, LINE, ACCENT, CONSOLE, DIALOG = "#130D24", "#2E1C4E", TURQUOISE, "#07040D", "#0A0714"


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
        face = mix(under, (7, 4, 13), 0.85) if self.dark else mix(under, (20, 13, 36), 0.80)
        if face == self.face:
            return
        self.face, bg = face, hexcolor(face)
        outline_col = hexcolor(mix(face, (84, 13, 110), 0.35 if not self.dark else 0.15))
        self.canvas.itemconfigure(self.shape, fill=bg, outline=outline_col)
        todo = [self]
        while todo:
            w = todo.pop()
            todo += w.winfo_children()
            if getattr(w, "solid", False):
                continue
            if isinstance(w, tk.Checkbutton):
                w.configure(bg=bg, activebackground=bg, fg="#F8FAFC", activeforeground=TURQUOISE, selectcolor="#0A0714")
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
        caption_color = ctypes.c_int(0x00240D13)  # BGR for #130D24 (Deep Indigo Surface)
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


class App(tk.Tk):
    def __init__(self):
        dpi_aware()
        super().__init__()
        self.title(f"Pasha Hunt {bot.VERSION} (Apinex Edition)")
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
        self.scale = max(1.0, self.winfo_fpixels("1i") / 96)  # 1.5 on a 150% screen: sizes in pixels grow with it
        px = lambda n: round(n * self.scale)
        self.geometry(f"{min(px(1280), self.winfo_screenwidth() - 40)}x{min(px(800), self.winfo_screenheight() - 80)}")
        self.minsize(px(900), px(600))
        self.jobs, self.by_iid, self.mtime = [], {}, 0
        self.proc, self.out, self.stopped = None, queue.Queue(), False
        self.sort_col, self.sort_rev = "Match", False
        self.in_table = False
        self.style_widgets()

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, background=hexcolor(GRADIENT[0]))
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_size = (0, 0)
        self.build_background(self.winfo_screenwidth(), self.winfo_screenheight())
        # Jobs on top, console below, table left, details right: drag the gaps between cards to resize them.
        self.split_x, self.split_y, self.drag, self.body = 0.6, 0.66, None, None
        self.canvas.bind("<Configure>", self.layout)
        self.canvas.bind("<Motion>", self.sash_cursor)
        self.canvas.bind("<ButtonPress-1>", lambda e: setattr(self, "drag", self.sash_at(e.x, e.y)))
        self.canvas.bind("<B1-Motion>", self.sash_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag", None))

        self.build_toolbar()
        self.build_filters()
        self.build_body()
        self.build_log()
        self.load_jobs()
        self.refresh_task_button()
        self.bind_all("<F5>", lambda e: self.find_jobs())
        self.bind_all("<Control-f>", lambda e: (self.search_entry.focus_set(), self.search_entry.select_range(0, "end")))
        self.tree.bind("<Return>", lambda e: self.open_job())
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

    # ---------- look ----------

    def style_widgets(self):
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            tkfont.nametofont(name).configure(family="Segoe UI", size=10)

        # Apply global option database settings BEFORE widgets query them
        for pat in ("*TCombobox*Listbox", "*Combobox*Listbox", "*ComboboxPopdown*Listbox", "*Listbox"):
            self.option_add(f"{pat}.background", "#130D24")
            self.option_add(f"{pat}.foreground", "#F8FAFC")
            self.option_add(f"{pat}.selectBackground", INDIGO)
            self.option_add(f"{pat}.selectForeground", GOLD)
            self.option_add(f"{pat}.highlightBackground", LINE)
            self.option_add(f"{pat}.highlightColor", TURQUOISE)
            self.option_add(f"{pat}.highlightThickness", 1)
            self.option_add(f"{pat}.font", ("Segoe UI", 10))

        self.option_add("*Menu.background", "#130D24")
        self.option_add("*Menu.foreground", "#F8FAFC")
        self.option_add("*Menu.activeBackground", INDIGO)
        self.option_add("*Menu.activeForeground", GOLD)
        self.option_add("*Menu.selectColor", TURQUOISE)
        self.option_add("*Menu.borderWidth", 1)
        self.option_add("*Menu.relief", "solid")

        st = ttk.Style(self)
        st.theme_use("clam")

        # Global base styling & map overrides: strictly eradicate clam's default #eeebe7 white hover
        st.configure(".", background=DIALOG, foreground=INK, bordercolor=LINE, lightcolor="#1C1335",
                     darkcolor="#1C1335", troughcolor="#1C1335", focuscolor=TURQUOISE, fieldbackground="#0E091C",
                     selectbackground=INDIGO, selectforeground=GOLD, arrowcolor=TURQUOISE)
        st.map(".",
               lightcolor=[("disabled", "#130D24"), ("pressed", "#130D24"), ("active", "#2B1A4E"), ("!disabled", "#1C1335")],
               darkcolor=[("disabled", "#130D24"), ("pressed", "#130D24"), ("active", "#2B1A4E"), ("!disabled", "#1C1335")],
               bordercolor=[("disabled", "#130D24"), ("focus", TURQUOISE), ("active", TURQUOISE), ("!disabled", LINE)],
               focuscolor=[("!disabled", TURQUOISE)])

        def button(name, bg, fg, hover, press, off_bg, off_fg, border=None, active_fg=None, **kw):
            st.configure(name, background=bg, foreground=fg, bordercolor=border or bg, lightcolor=bg, darkcolor=bg,
                         relief="flat", focuscolor=bg, **{"padding": (10, 5), **kw})
            states = [("disabled", off_bg), ("pressed", press), ("active", hover)]
            st.map(name, background=states, lightcolor=states, darkcolor=states,
                   focuscolor=[("disabled", off_bg), ("!disabled", hover)],
                   foreground=[("disabled", off_fg), ("active", active_fg or "#FFFFFF")],
                   bordercolor=[("disabled", off_bg), ("focus", TURQUOISE if border else hover),
                                ("active", TURQUOISE if border else hover), ("!disabled", border or bg)])

        # 5-Color Palette Buttons
        # 1. Neutral / Toolbar: Deep Indigo tint
        button("TButton", "#1C1335", "#F8FAFC", "#2B1A4E", "#130D24", "#130D24", "#7E7196", border="#3B2361")

        # 2. Menubutton: Dropdowns with Turquoise arrow
        button("TMenubutton", "#1C1335", "#F8FAFC", "#2B1A4E", "#130D24", "#130D24", "#7E7196", border="#3B2361")
        st.configure("TMenubutton", arrowcolor=TURQUOISE, padding=(10, 5), relief="flat")
        st.map("TMenubutton",
               arrowcolor=[("active", GOLD), ("pressed", WATERMELON), ("!disabled", TURQUOISE)],
               background=[("disabled", "#130D24"), ("pressed", "#130D24"), ("active", "#2B1A4E"), ("!disabled", "#1C1335")],
               lightcolor=[("disabled", "#130D24"), ("pressed", "#130D24"), ("active", "#2B1A4E"), ("!disabled", "#1C1335")],
               darkcolor=[("disabled", "#130D24"), ("pressed", "#130D24"), ("active", "#2B1A4E"), ("!disabled", "#1C1335")],
               foreground=[("disabled", "#7E7196"), ("active", "#FFFFFF"), ("!disabled", "#F8FAFC")],
               bordercolor=[("disabled", "#130D24"), ("active", TURQUOISE), ("focus", TURQUOISE), ("!disabled", "#3B2361")])

        # 3. Active Tabs: Indigo base with Vivid Gold text & Turquoise border
        button("ActiveTab.TButton", INDIGO, GOLD, "#6B128B", "#420A57", "#130D24", "#7E7196", border=TURQUOISE, active_fg=GOLD, font=("Segoe UI", 10, "bold"))
        button("IndigoGold.TButton", INDIGO, GOLD, "#6B128B", "#420A57", "#130D24", "#7E7196", border=GOLD, active_fg=GOLD, font=("Segoe UI", 10, "bold"))

        # 4. Big Primary CTA: Turquoise (#3BCEAC)
        button("Big.TButton", TURQUOISE, "#07040D", "#4DE3C0", "#229074", "#1C1335", "#7E7196",
               active_fg="#07040D", font=("Segoe UI", 10, "bold"), padding=(12, 6))

        # 5. Success Action: Jungle Green (#0EAD69)
        button("Jungle.TButton", JUNGLE, "#FFFFFF", "#12C97B", "#0B8E56", "#1C1335", "#7E7196",
               font=("Segoe UI", 10, "bold"), padding=(12, 6))

        # 6. Stop / Alert: Watermelon (#EE4266)
        button("Stop.TButton", WATERMELON, "#FFFFFF", "#FA567A", "#D02E50", "#1C1335", "#7E7196",
               font=("Segoe UI", 10, "bold"), padding=(10, 5))

        button("Dark.TButton", "#1C1335", "#F8FAFC", "#2B1A4E", "#07040D", "#130D24", "#7E7196")

        for name in ("TEntry", "TSpinbox"):
            st.configure(name, fieldbackground="#0E091C", background="#0E091C", foreground="#F8FAFC", bordercolor=LINE, lightcolor="#0E091C",
                         darkcolor="#0E091C", padding=(6, 3), insertcolor=TURQUOISE)
            st.map(name, bordercolor=[("focus", TURQUOISE), ("active", TURQUOISE)],
                   fieldbackground=[("focus", "#18102E"), ("active", "#18102E")])

        # Combobox: strictly eradicate clam's default #eeebe7 white hover border & background
        st.configure("TCombobox", fieldbackground="#0E091C", background="#1C1335", foreground="#F8FAFC",
                     bordercolor=LINE, lightcolor="#1C1335", darkcolor="#1C1335", padding=(6, 4),
                     insertcolor=TURQUOISE, arrowcolor=TURQUOISE, relief="flat")
        st.map("TCombobox",
               fieldbackground=[("readonly", "focus", "#18102E"),
                                ("readonly", "active", "#18102E"),
                                ("readonly", "#0E091C"),
                                ("active", "#18102E"),
                                ("focus", "#18102E"),
                                ("disabled", "#130D24"),
                                ("!disabled", "#0E091C")],
               background=[("disabled", "#130D24"),
                           ("pressed", "#130D24"),
                           ("active", "#2B1A4E"),
                           ("!disabled", "#1C1335")],
               lightcolor=[("disabled", "#130D24"),
                           ("pressed", "#130D24"),
                           ("active", "#2B1A4E"),
                           ("!disabled", "#1C1335")],
               darkcolor=[("disabled", "#130D24"),
                          ("pressed", "#130D24"),
                          ("active", "#2B1A4E"),
                          ("!disabled", "#1C1335")],
               arrowcolor=[("disabled", "#7E7196"),
                           ("active", GOLD),
                           ("pressed", WATERMELON),
                           ("!disabled", TURQUOISE)],
               bordercolor=[("disabled", "#130D24"),
                            ("focus", TURQUOISE),
                            ("active", TURQUOISE),
                            ("!disabled", LINE)],
               foreground=[("disabled", "#7E7196"),
                           ("active", "#FFFFFF"),
                           ("!disabled", "#F8FAFC")],
               selectbackground=[("readonly", INDIGO), ("active", INDIGO), ("!disabled", INDIGO)],
               selectforeground=[("readonly", GOLD), ("active", GOLD), ("!disabled", GOLD)])

        st.configure("Treeview", background="#0E091C", fieldbackground="#0E091C", foreground="#F8FAFC",
                     rowheight=round(28 * self.scale),
                     bordercolor=LINE, lightcolor="#0E091C", darkcolor="#0E091C")
        st.map("Treeview", background=[("selected", INDIGO)], foreground=[("selected", GOLD)])
        st.configure("Treeview.Heading", background="#1C1335", foreground=TURQUOISE, relief="flat", bordercolor=LINE,
                     lightcolor="#1C1335", darkcolor="#1C1335", font=("Segoe UI", 10, "bold"), padding=(6, 4))
        st.map("Treeview.Heading", background=[("active", "#2B1A4E")], foreground=[("active", GOLD)],
               lightcolor=[("active", "#2B1A4E")], darkcolor=[("active", "#2B1A4E")])
        for orient in ("Vertical", "Horizontal"):
            for prefix, trough, thumb, hover in (("", "#0E091C", "#2A1A47", "#3B2463"),
                                                 ("Dark.", CONSOLE, "#2A1A47", "#3B2463")):
                name = f"{prefix}{orient}.TScrollbar"
                st.configure(name, background=thumb, troughcolor=trough, bordercolor=trough, lightcolor=thumb,
                             darkcolor=thumb, gripcount=0, arrowsize=12)
                st.map(name, background=[("active", hover)], lightcolor=[("active", hover)],
                       darkcolor=[("active", hover)])
        st.configure("Horizontal.TProgressbar", background=TURQUOISE, troughcolor="#1C1335", bordercolor="#1C1335",
                     lightcolor=TURQUOISE, darkcolor=TURQUOISE)

    def build_background(self, w, h):
        """Diagonal colour bands covering a w x h window."""
        self.canvas.delete("bg")
        self.bg_size = (w, h)
        for a in range(0, w + h, BAND):
            self.canvas.create_polygon(a, 0, a + BAND + 1, 0, a + BAND + 1 - h, h, a - h, h, outline="",
                                       fill=hexcolor(gradient_at(a + BAND / 2)), tags="bg")
        self.canvas.tag_lower("bg")

    def tint(self):
        for c in (self.c_head, self.c_filter, self.c_table, self.c_detail, self.c_log):
            c.tint()

    def layout(self, e=None):
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        if W < 100 or H < 100:
            return
        if W > self.bg_size[0] or H > self.bg_size[1]:
            self.build_background(max(W, self.bg_size[0]), max(H, self.bg_size[1]))
        m, step = GAP + PAD, 2 * PAD + GAP
        x, w, y = m, W - 2 * m, m
        for c in (self.c_head, self.c_filter):
            h = c.winfo_reqheight()
            c.place_at(x, y, w, h)
            y += h + step
        avail = max(H - m - y - step, 2)
        self.split_x, self.split_y = min(max(self.split_x, 0.25), 0.8), min(max(self.split_y, 0.15), 0.85)
        top, left = round(avail * self.split_y), round((w - step) * self.split_x)
        self.c_table.place_at(x, y, left, top)
        self.c_detail.place_at(x + left + step, y, w - step - left, top)
        self.c_log.place_at(x, y + top + step, w, avail - top)
        self.body = (x, y, w, avail, step, left, top)
        self.tint()

    def sash_at(self, x, y):
        if not self.body:
            return None
        bx, by, w, avail, step, left, top = self.body
        if by + top <= y <= by + top + step:
            return "y"
        if by <= y <= by + top and bx + left <= x <= bx + left + step:
            return "x"
        return None

    def sash_cursor(self, e):
        if not self.drag:
            cursor = {"y": "sb_v_double_arrow", "x": "sb_h_double_arrow"}.get(self.sash_at(e.x, e.y), "")
            self.canvas.config(cursor=cursor)

    def sash_drag(self, e):
        bx, by, w, avail, step, left, top = self.body
        if self.drag == "y":
            self.split_y = (e.y - by - step / 2) / avail
        elif self.drag == "x":
            self.split_x = (e.x - bx - step / 2) / (w - step)
        else:
            return
        self.layout()

    # ---------- layout ----------

    def build_toolbar(self):
        c = self.c_head = Card(self)
        bar = c.row()
        self.busy_buttons = []

        # Application Logo Badge
        self._brand_logo = None
        if os.path.exists(LOGO_PNG):
            try:
                im = Image.open(LOGO_PNG).resize((32, 32), Image.Resampling.LANCZOS)
                self._brand_logo = ImageTk.PhotoImage(im)
                lbl_logo = tk.Label(bar, image=self._brand_logo, bd=0, highlightthickness=0)
                lbl_logo.pack(side="left", padx=(0, 10))
                Tooltip(lbl_logo, "Pasha Hunt 2.0 (Apinex Edition) — Autonomous AI Career Agent")
            except Exception:
                pass

        b_find = ttk.Button(bar, text="🔍  Find jobs", style="Big.TButton", command=self.find_jobs)
        b_find.pack(side="left", padx=(0, 8))
        Tooltip(b_find, "Search every job site with the filter below (F5). Takes about a minute.")
        self.busy_buttons.append(b_find)

        b_draft = ttk.Button(bar, text="✉  Auto-draft best matches", style="Jungle.TButton", command=self.auto_draft)
        b_draft.pack(side="left", padx=(0, 8))
        Tooltip(b_draft, "Find jobs, tailor CV + email for top matches, and save as Gmail drafts.")
        self.busy_buttons.append(b_draft)

        b_stop = ttk.Button(bar, text="⏹  Stop", style="Stop.TButton", command=self.stop_run)
        b_stop.pack(side="left", padx=(0, 8))
        Tooltip(b_stop, "Stop the run in progress, from this window or from Auto-run.")
        sep = tk.Frame(bar, width=1, bg=LINE)
        sep.solid = True
        sep.pack(side="left", fill="y", padx=8, pady=4)
        self.menu_button(bar, "📁  Open", [
            ("📧  Gmail drafts", self.open_gmail), ("📂  My CVs and cover letters", self.open_cvs),
            ("📊  Tracker (every job handled)", self.open_tracker), ("📜  Run log", self.open_runs),
            None, ("🗂  Job Hunter data folder", lambda: os.startfile(HERE))])
        ttk.Button(bar, text="⚙  Settings", command=self.settings).pack(side="left", padx=(0, 6))
        self.menu_button(bar, "❔  Help", [
            ("🚀  Quick Onboarding Wizard", self.onboarding_wizard),
            ("🎥  Replay Cinematic Intro", self.replay_intro),
            ("Getting started", lambda: (self.tree.selection_set(()), self.show_start())),
            ("User guide", lambda: webbrowser.open(f"https://github.com/{bot.REPO}#readme")),
            ("Check Recruiter Replies", self.check_replies),
            ("Report a problem", lambda: webbrowser.open(f"https://github.com/{bot.REPO}/issues/new/choose")),
            None,
            ("Check for updates", lambda: self.check_update(quiet=False)),
            ("About Pasha Hunt", self.about)])
        self.task_btn = ttk.Button(bar, text="Auto-run: …", command=self.toggle_task)
        self.task_btn.pack(side="right")
        Tooltip(self.task_btn, "Run Auto-draft every 30 minutes in the background while you are signed in to "
                               "Windows. Press again to turn it on or off.")
        self.update_btn = ttk.Button(bar, style="Big.TButton", command=self.update_now)
        Tooltip(self.update_btn, f"You have {bot.VERSION}. One click downloads the new version, installs it and "
                                 "reopens Job Hunter: your keys, profile and CVs are kept.")

        row = c.row(pady=(8, 0))
        c.label(row, "Your CV:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        for text, cmd, busy, tip in [
                ("📤  Upload my CV", self.upload_cv, True,
                 "Gemini reads your CV (PDF, Word, text or a photo) once and builds your profile. Every tailored "
                 "CV is made only from facts in it."),
                ("👤  My profile", self.open_profile, False, "Check or correct your profile (profile.json) in Notepad."),
                ("📝  Tailor CV to a job description…", self.paste_job, True,
                 "Paste any job post (LinkedIn, a company site, …) and get a tailored CV + cover letter for it.")]:
            b = ttk.Button(row, text=text, command=cmd)
            b.pack(side="left", padx=(0, 6))
            Tooltip(b, tip)
            if busy:
                self.busy_buttons.append(b)
        self.profile_lbl = c.label(row, muted=True)
        self.profile_lbl.pack(side="left", padx=(8, 0))
        self.show_profile()

        row = c.row(pady=(8, 0))
        c.label(row, "AI model:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        self.model_var, self.model_of, self.model_mtime = tk.StringVar(), {}, 0
        cb = self.model_cb = ttk.Combobox(row, textvariable=self.model_var, state="readonly", width=70,
                                          postcommand=self.fill_models)
        cb.pack(side="left", padx=(0, 6))
        cb.bind("<<ComboboxSelected>>", lambda e: self.pick_model())
        self.model_btn = ttk.Button(row, text="↻  Check models", command=self.check_models)
        self.model_btn.pack(side="left", padx=(0, 6))
        self.model_lbl = c.label(row, muted=True)
        self.model_lbl.pack(side="left", padx=(8, 0))
        self.fill_models()

    def show_profile(self):
        try:
            with open(PROFILE, encoding="utf-8") as f:
                p = json.load(f)
            self.profile_lbl.config(text=f"Using: {p['name']}  ·  {p['default_title'][:60]}  ·  "
                                         f"{len(p['experience'])} roles  (profile.json)")
        except (OSError, ValueError, KeyError):
            self.profile_lbl.config(text="No profile yet. Press Upload my CV.")

    def model_state(self):
        """gemini_state.json, or an empty state when it belongs to an older key."""
        cfg = read_config()
        state = bot.gemini_state()
        if not has_key(cfg, "gemini_api_key") or state.get("key") != bot.key_id(cfg["gemini_api_key"]):
            return cfg, {}
        return cfg, state

    def fill_models(self):
        """Every model your key can use, with what the bot last saw: working, at its limit and until when."""
        cfg, state = self.model_state()
        key = str(cfg.get("gemini_api_key") or "").strip()

        # For Apinex keys, populate curated free models if state is empty
        if key.startswith("sk-"):
            models = state.get("models", [])
            if not models:
                models = [
                    "free/gemini-3.8-flash", "free/deepseek-v4.1-flash", "free/claude-sonnet-4.6",
                    "free/kimi-k3", "free/gemini-3.1-pro", "free/qwen-3.8-max",
                    "free/minimax-m3.1-flash", "free/glm-5.3-flash", "free/mimo-v2.6-flash", "free/mimo-v2.6-pro"
                ]
                state["models"] = models
                state["key"] = bot.key_id(key)
                state["listed"] = time.time()
                bot.save_gemini_state(state)
            # Sort free models to the very top
            free = [m for m in models if m.startswith("free/")]
            other = [m for m in models if not m.startswith("free/")]
            models = free + other
        else:
            models = sorted(state.get("models", []), key=bot.model_rank)

        current = cfg.get("gemini_model", "free/gemini-3.8-flash" if key.startswith("sk-") else bot.DEFAULT_CONFIG["gemini_model"])
        if current and current not in models:
            models.insert(0, current)
        self.model_of = {AUTO_MODEL: ""}
        usable = 0
        for m in models:
            ok, text = bot.model_status(state, m)
            usable += ok
            self.model_of[f"{'✓' if ok else '⛔'}  {m}   ·   {text}"] = m
        self.model_var.set(next((k for k, m in self.model_of.items() if m == current), AUTO_MODEL))
        self.model_cb.config(values=list(self.model_of))
        if state.get("refused"):
            prov = "Apinex" if key.startswith("sk-") else "Google"
            self.model_lbl.config(text=f"⚠ {prov} refused your key: {state['refused']['message'][:70]}. "
                                       "Check Settings > Accounts.")
        elif not state.get("models") and not key.startswith("sk-"):
            self.model_lbl.config(text="Press Check models to see which models your key can use.")
        else:
            self.model_lbl.config(text=f"{usable} of {len(models)} models usable right now. "
                                       "Others are used when the chosen one is at its limit.")

    def pick_model(self):
        model = self.model_of.get(self.model_var.get(), "")
        cfg, state = self.model_state()
        if model and state.get("blocked", {}).get(model, 0) > dt.datetime.now().timestamp():
            ok, text = bot.model_status(state, model)
            if not messagebox.askyesno("AI model", f"{model}: {text}.\n\nGoogle may still refuse it until then. "
                                       "Try it anyway on the next run?", parent=self):
                self.fill_models()
                return
            if self.proc or lock_owner():
                messagebox.showinfo("AI model", "A run is in progress. Try again when it has finished.", parent=self)
                self.fill_models()
                return
            for k in ("blocked", "why"):
                state.get(k, {}).pop(model, None)
            bot.save_gemini_state(state)
        cfg["gemini_model"] = model
        write_config(cfg)
        self.write_log(f"\nAI model: {model or 'Auto'}"
                       + (" (other free models take over when it is at its limit)\n" if model else "\n"))
        self.fill_models()

    def check_models(self):
        """Ask Google which models this key can use now (the bot also does this once a day)."""
        cfg, state = self.model_state()
        if not has_key(cfg, "gemini_api_key"):
            self.keys()
            return
        if self.proc or lock_owner():
            self.model_lbl.config(text="A run is in progress. Check models when it has finished.")
            return
        self.model_btn.state(["disabled"])
        self.model_lbl.config(text="Asking Apinex …" if str(cfg.get("gemini_api_key") or "").startswith("sk-") else "Asking Google …")

        def work():
            new = {**state, "key": bot.key_id(cfg["gemini_api_key"]), "listed": 0}
            bot.gemini_models(cfg, new)
            self.after(0, done, new)

        def done(new):
            self.model_btn.state(["!disabled"])
            if not new.get("listed"):
                provider = "Apinex" if str(cfg.get("gemini_api_key") or "").startswith("sk-") else "Google"
                self.model_lbl.config(text=f"Could not reach {provider}. Check your internet connection and the key.")
                return
            bot.save_gemini_state(new)
            self.fill_models()

        threading.Thread(target=work, daemon=True).start()

    def build_filters(self):
        # What the bot looks for. Saved in config.json, so scheduled runs use it too.
        cfg = read_config()
        c = self.c_filter = Card(self)
        self.kw = tk.StringVar(value=", ".join(cfg.get("keywords") or DEFAULT_KEYWORDS))
        self.excl = tk.StringVar(value=", ".join(cfg.get("exclude_keywords") or []))
        self.age = tk.StringVar(value=str(cfg.get("max_job_age_days") or bot.MAX_AGE_DAYS))
        modes = bot.work_modes(cfg)
        self.modes = {m: tk.BooleanVar(value=m in modes) for m in bot.WORK_MODES}
        self.open_to = tk.StringVar(value=OPEN_TO_LABEL[bot.open_to(cfg)])
        self.region = tk.StringVar(value=", ".join(bot.clean_words(cfg.get("my_region_words"))))
        self.countries = tk.StringVar(value=", ".join(bot.clean_words(cfg.get("target_countries"))))
        self.visa = tk.BooleanVar(value=bool(cfg.get("visa_sponsorship")))
        self.google = tk.BooleanVar(value=cfg.get("search_google", True))
        self.title_only = tk.BooleanVar(value=bool(cfg.get("keywords_in_title")))
        self.preset = tk.StringVar()
        mine = [k.strip().lower() for k in self.kw.get().split(",")]
        picked = [n for n in cfg.get("job_types") or [] if n in PRESETS] or \
            [n for n, (kws, _, _) in PRESETS.items() if [k.lower() for k in kws] == mine]
        self.types = {n: tk.BooleanVar(value=n in picked) for n in PRESETS}

        top = c.row()
        c.label(top, "Job filter", font=("Segoe UI", 10, "bold")).pack(side="left")
        c.label(top, "Job type:").pack(side="left", padx=(14, 4))
        mb = ttk.Menubutton(top, textvariable=self.preset, width=40)
        menu = tk.Menu(mb, tearoff=False, font=("Segoe UI", 10),
                       bg="#130D24", fg="#F8FAFC", activebackground=INDIGO, activeforeground=GOLD,
                       selectcolor=TURQUOISE, bd=1, relief="solid")
        for n in PRESETS:  # tick several to search them together
            menu.add_checkbutton(label=n, variable=self.types[n], command=self.use_preset)
        mb["menu"] = menu
        mb.pack(side="left", padx=(0, 14))
        Tooltip(mb, "Pick one or more fields. Each fills in the usual job titles for it. Type your own keywords "
                    "below for anything else.")
        w = c.check(top, "Keywords in title only", self.title_only)
        w.pack(side="left", padx=(0, 12))
        Tooltip(w, "A keyword must be in the job title. Turn on for broad words like Sales or Finance that "
                   "appear in almost every job ad.")

        row = c.row(pady=(8, 0))
        c.label(row, "Work type:").pack(side="left", padx=(0, 4))
        tips = {"remote": "Work from home, for a company anywhere.",
                "hybrid": "Some days in the office: the office must be in a place below (or offer a visa).",
                "onsite": "Every day in the office: the office must be in a place below (or offer a visa)."}
        for m, name in bot.WORK_MODES.items():
            self.modes[m].trace_add("write", lambda *a: self.fill_table())
            w = c.check(row, name, self.modes[m])
            w.pack(side="left", padx=(0, 8))
            Tooltip(w, tips[m])
        c.label(row, "Open to:").pack(side="left", padx=(8, 4))
        cb = ttk.Combobox(row, textvariable=self.open_to, values=list(OPEN_TO_LABEL.values()), state="readonly",
                          width=22)
        cb.pack(side="left", padx=(0, 12))
        Tooltip(cb, "Worldwide + my country: remote jobs that hire worldwide or name your country; office jobs in "
                    "your country.\nCountries I pick: the same, for the countries in Countries.\n"
                    "Any country: no limit (remote jobs for the US only too).")
        c.label(row, "My country/region:").pack(side="left", padx=(0, 4))
        w = ttk.Entry(row, textvariable=self.region, width=18)
        w.pack(side="left", padx=(0, 12))
        Tooltip(w, "Where you live. Jobs that name one of these count as open to you, e.g.  Pakistan, South Asia, "
                   "APAC")
        c.label(row, "Countries:").pack(side="left", padx=(0, 4))
        self.countries_entry = ttk.Entry(row, textvariable=self.countries, width=22)
        self.countries_entry.pack(side="left", padx=(0, 12))
        Tooltip(self.countries_entry, "For Open to: Countries I pick. Countries or regions you would work for or "
                                      "move to, e.g.  UAE, Saudi Arabia, Germany, Europe. Remote jobs limited to "
                                      "one of these, and office jobs in them, are kept.")
        w = c.check(row, "Visa / relocation abroad", self.visa)
        w.pack(side="left")
        Tooltip(w, "Also keep hybrid and on-site jobs in other countries when the post offers visa sponsorship or "
                   "relocation help.")
        cb.bind("<<ComboboxSelected>>", lambda e: self.show_open_to())
        self.show_open_to()

        row = c.row(pady=(8, 0))
        c.label(row, "Keywords (any of):").pack(side="left")
        w = ttk.Entry(row, textvariable=self.kw, width=28)
        w.pack(side="left", padx=(4, 12), fill="x", expand=True)
        Tooltip(w, "Comma separated. A job is kept if any keyword matches, e.g.  React, Node.js  or  "
                   "Accountant, Bookkeeper. Small typos are fine.")
        c.label(row, "Exclude in title:").pack(side="left")
        w = ttk.Entry(row, textvariable=self.excl, width=22)
        w.pack(side="left", padx=(4, 12))
        Tooltip(w, "Skip jobs with any of these words in the title, e.g.  Senior, Intern, PHP")
        c.label(row, "Max age (days):").pack(side="left")
        ttk.Spinbox(row, from_=1, to=60, textvariable=self.age, width=4).pack(side="left", padx=(4, 12))
        w = c.check(row, "Search Google too", self.google)
        w.pack(side="left", padx=(0, 12))
        Tooltip(w, "Gemini searches Google for posts on LinkedIn, Indeed, Glassdoor and company sites (one request "
                   "every 4 hours at most). Google only allows this for Gemini keys with billing turned on; on a free "
                   "key Job Hunter notices, says so once and tries again the next day.")
        b = ttk.Button(row, text="🔍  Save & search", style="Big.TButton", command=self.find_jobs)
        b.pack(side="left")
        Tooltip(b, "Save this filter (Auto-run uses it too) and search now.")
        self.busy_buttons.append(b)
        self.show_preset()
        self.kw.trace_add("write", lambda *a: self.show_preset())

    def open_to_key(self):
        return next(k for k, v in OPEN_TO_LABEL.items() if v == self.open_to.get())

    def show_open_to(self):
        self.countries_entry.state(["!disabled"] if self.open_to_key() == "countries" else ["disabled"])

    def picked_types(self):
        """The ticked job types, or [] once the keywords are your own."""
        picked = [n for n, v in self.types.items() if v.get()]
        mine = [w.strip().lower() for w in self.kw.get().split(",") if w.strip()]
        return picked if picked and [k.lower() for k in combine(picked)[0]] == mine else []

    def show_preset(self):
        """Name the ticked job types the keywords come from, or Custom once you have typed your own."""
        picked = self.picked_types()
        self.preset.set(CUSTOM if not picked else picked[0] if len(picked) == 1
                        else f"{picked[0]} + {len(picked) - 1} more")

    def use_preset(self):
        picked = [n for n, v in self.types.items() if v.get()]
        if picked:
            kws, _, title_only = combine(picked)
            self.kw.set(", ".join(kws))
            self.title_only.set(title_only)
        self.show_preset()

    def switch_view(self, view_name):
        self.view.set(view_name)
        self.update_tab_styles(view_name)
        self.fill_table()
        if view_name == "Done, applied or skipped":
            self.check_replies(quiet=True)

    def schedule_reply_checks(self):
        self.check_replies(quiet=True)
        self.after(300000, self.schedule_reply_checks)

    def update_tab_styles(self, current_view=None):
        v = current_view or self.view.get()
        if hasattr(self, "btn_tab_email"):
            self.btn_tab_email.configure(style="ActiveTab.TButton" if v == "Ready to draft (has email)" else "TButton")
        if hasattr(self, "btn_tab_site"):
            self.btn_tab_site.configure(style="ActiveTab.TButton" if v == "Apply on company site" else "TButton")
        if hasattr(self, "btn_tab_tracker"):
            self.btn_tab_tracker.configure(style="ActiveTab.TButton" if v == "Done, applied or skipped" else "TButton")
        if hasattr(self, "btn_tab_all"):
            self.btn_tab_all.configure(style="ActiveTab.TButton" if v == "All matches" else "TButton")

    def check_replies(self, quiet=False):
        cfg = read_config()
        if not bot.has_gmail(cfg):
            if not quiet:
                messagebox.showinfo("Recruiter Tracking", "Connect your Gmail in Settings first to track sent emails and recruiter replies.", parent=self)
            return
        if not quiet:
            self.status_lbl.config(text="Checking Gmail INBOX & Sent Mail for recruiter replies …")
        if hasattr(self, "btn_check_replies"):
            self.btn_check_replies.state(["disabled"])

        def work():
            res = bot.sync_gmail_tracker(cfg)
            self.after(0, done, res)

        def done(res):
            if hasattr(self, "btn_check_replies"):
                self.btn_check_replies.state(["!disabled"])
            if not res.get("checked"):
                if not quiet:
                    self.status_lbl.config(text=f"Tracker sync error: {res.get('reason')}")
                    messagebox.showwarning("Recruiter Tracking", f"Could not check Gmail:\n{res.get('reason')}", parent=self)
                return
            sent = res.get("sent_count", 0)
            replies = res.get("replies", [])
            bounces = res.get("bounces", [])
            msg = f"Gmail Sync: {sent} applications sent."
            if replies:
                msg += f" 🎉 {len(replies)} recruiter replies received!"
                messagebox.showinfo("🎉 Recruiter Reply Received!", "Great news! You have received replies from:\n\n" + "\n".join(f"• {r}" for r in replies), parent=self)
            if bounces:
                msg += f" ⚠️ {len(bounces)} delivery bounced (address rejected)."
                messagebox.showwarning("⚠️ Email Delivery Bounced", "Delivery failed for the following internal/rejected addresses:\n\n" + "\n".join(f"• {b}" for b in bounces) + "\n\nPlease use the '🌐 Apply on Company Site' link in the tracker to submit via their official careers portal.", parent=self)
            if not replies and not bounces:
                msg += " No new replies yet."
            self.status_lbl.config(text=msg)
            if replies or bounces or not quiet:
                self.write_log(f"\n📬 {msg}\n")
            self.fill_table()

        threading.Thread(target=work, daemon=True).start()

    def build_body(self):
        c = self.c_table = Card(self)

        # Prominent Category Filter Tabs
        tabs_row = c.row(pady=(0, 6))
        c.label(tabs_row, "Category:").pack(side="left", padx=(0, 4))
        self.btn_tab_email = ttk.Button(tabs_row, text="✉  Email Direct Apply", command=lambda: self.switch_view("Ready to draft (has email)"))
        self.btn_tab_email.pack(side="left", padx=(0, 4))
        self.btn_tab_site = ttk.Button(tabs_row, text="🌐  Apply on Company Site", command=lambda: self.switch_view("Apply on company site"))
        self.btn_tab_site.pack(side="left", padx=(0, 4))
        self.btn_tab_tracker = ttk.Button(tabs_row, text="📬  Sent & Applied Tracker", command=lambda: self.switch_view("Done, applied or skipped"))
        self.btn_tab_tracker.pack(side="left", padx=(0, 4))
        self.btn_tab_all = ttk.Button(tabs_row, text="📋  All Matches", command=lambda: self.switch_view("All matches"))
        self.btn_tab_all.pack(side="left", padx=(0, 8))

        self.btn_check_replies = ttk.Button(tabs_row, text="🔄 Check Replies", command=self.check_replies)
        self.btn_check_replies.pack(side="left", padx=(4, 0))
        Tooltip(self.btn_check_replies, "Checks your Gmail INBOX and Sent Mail to update application status and detect recruiter replies.")

        row = c.row(pady=(0, 4))
        c.label(row, "Show:").pack(side="left")
        self.view = tk.StringVar(value="All matches")
        cb = ttk.Combobox(row, textvariable=self.view, values=list(VIEWS), state="readonly", width=26)
        cb.pack(side="left", padx=(4, 12))
        cb.bind("<<ComboboxSelected>>", lambda e: self.fill_table())
        c.label(row, "Search in list:").pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.fill_table())
        self.search_entry = ttk.Entry(row, textvariable=self.search, width=24)
        self.search_entry.pack(side="left", padx=(4, 12))
        Tooltip(self.search_entry, "Show only jobs whose title, company, location or text has this (Ctrl+F).")
        info = c.row(pady=(0, 8))
        self.count_lbl = c.label(info, muted=True)
        self.count_lbl.pack(side="left")
        self.updated_lbl = c.label(info, muted=True)
        self.updated_lbl.pack(side="right")

        left = tk.Frame(c)
        left.pack(fill="both", expand=True)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        cols = COLUMNS
        widths = (115, 105, 85, 140, 280, 160, 110)
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, widths):
            sw = round(w * self.scale)
            self.tree.heading(col, text=col, command=lambda col=col: self.sort_by(col))
            self.tree.column(col, width=sw, minwidth=round(w * 0.75 * self.scale), stretch=col in ("Role", "Company", "Location"))
        self.tree.tag_configure("ready", background="#0A2417", foreground=TURQUOISE)
        self.tree.tag_configure("apply on site", background="#1F1038", foreground="#D8B4FE")
        self.tree.tag_configure("done", foreground="#7E7196")
        self.tree.tag_configure("sent", background="#092B1C", foreground=JUNGLE)
        self.tree.tag_configure("reply", background="#382705", foreground=GOLD)
        self.tree.tag_configure("rejected", foreground=WATERMELON)

        sb_y = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb_x = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.show_detail())
        self.tree.bind("<Double-1>", lambda e: self.open_job())

        right = self.c_detail = Card(self)
        acts = right.row(pady=(0, 8))
        buttons = [
            ("b_draft", "✉  Draft email + CV", lambda: self.act("draft"),
             "Gemini writes a tailored CV and an email for this job and saves them as a Gmail draft. Nothing is sent."),
            ("b_cv", "📄  CV + cover letter", lambda: self.act("cv"),
             "A tailored CV and cover letter (PDF) to upload on the company's site. Needs no Gmail."),
            ("b_prep", "🎯  Interview Prep", self.generate_interview_prep,
             "Generate an AI Interview Battle-Pack with custom elevator pitch, top 5 STAR Q&As and smart questions."),
            ("b_pack", "📋  Quick Apply Pack", self.copy_profile_pack,
             "Interactive profile pack with 1-click copy buttons for rapid online form filling."),
            ("b_open", "🌐  Job page", self.open_job, "Open the job post in your browser (Enter)."),
            ("b_files", "📂  My CV for it", self.open_job_files,
             "Open the CV and cover letter already made for this job."),
            ("b_copy", "📋  Copy Email", self.copy_email, "Copy the application email address."),
            ("b_letter", "📋  Cover Letter", self.copy_letter,
             "Copy the cover letter text, to paste into an application form."),
            ("b_applied", "✅  Applied", lambda: self.act("applied"),
             "You applied (on the site or by email): move it to Done and note it in tracker.csv."),
            ("b_skip", "🚫  Skip", lambda: self.act("skip"), "Hide this job. The bot will not draft it."),
        ]
        for i, (name, text, cmd, tip) in enumerate(buttons):
            if name == "b_draft":
                btn_style = "Jungle.TButton"
            elif name == "b_cv":
                btn_style = "Big.TButton"
            elif name == "b_prep":
                btn_style = "IndigoGold.TButton"
            elif name == "b_applied":
                btn_style = "Jungle.TButton"
            elif name == "b_skip":
                btn_style = "Stop.TButton"
            else:
                btn_style = "TButton"
            b = ttk.Button(acts, text=text, command=cmd, style=btn_style)
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
            Tooltip(b, tip)
            setattr(self, name, b)
        for i in range(2):
            acts.columnconfigure(i, weight=1)
        box = tk.Frame(right)
        box.pack(fill="both", expand=True)
        self.detail = tk.Text(box, wrap="word", font=("Segoe UI", 10), padx=12, pady=10, relief="flat",
                              background="#0E091C", foreground="#F8FAFC", highlightthickness=1, highlightbackground=LINE,
                              highlightcolor=TURQUOISE, state="disabled")
        dsb = ttk.Scrollbar(box, orient="vertical", command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.tag_configure("h1", font=("Segoe UI", 14, "bold"), foreground=TURQUOISE, spacing3=4)
        self.detail.tag_configure("h2", font=("Segoe UI", 11), foreground=MUTED, spacing3=8)
        self.detail.tag_configure("key", font=("Segoe UI", 10, "bold"), foreground="#F8FAFC")
        self.detail.tag_configure("link", foreground=TURQUOISE, underline=True)
        self.detail.tag_bind("link", "<Button-1>", lambda e: self.open_job())
        self.detail.tag_bind("link", "<Enter>", lambda e: self.detail.config(cursor="hand2"))
        self.detail.tag_bind("link", "<Leave>", lambda e: self.detail.config(cursor=""))
        self.detail.tag_configure("done", foreground=JUNGLE, font=("Segoe UI", 10, "bold"))
        self.detail.tag_configure("todo", foreground=INK, font=("Segoe UI", 10, "bold"))
        self.detail.tag_configure("muted", foreground=MUTED, lmargin1=26, lmargin2=26, spacing3=8)
        self.detail.tag_configure("warn", foreground=GOLD)
        self.detail.tag_configure("err", foreground=WATERMELON)
        self.detail.pack(side="left", fill="both", expand=True)
        dsb.pack(side="left", fill="y")
        self.set_job_buttons(None)

    def build_log(self):
        c = self.c_log = Card(self, dark=True)
        top = c.row()
        self.status_lbl = c.label(top, "Ready.", font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(side="left")
        ttk.Button(top, text="Clear", style="Dark.TButton", command=self.clear_log).pack(side="right")
        self.bar = ttk.Progressbar(top, mode="indeterminate", length=180)
        body = tk.Frame(c)
        body.pack(fill="both", expand=True, pady=(8, 0))
        self.log = tk.Text(body, height=16, wrap="none", font=LOG_FONT, background=CONSOLE, foreground="#A79BBF",
                           insertbackground="#A79BBF", relief="flat", padx=10, pady=8, spacing1=1,
                           highlightthickness=0, state="disabled")
        ysb = ttk.Scrollbar(body, orient="vertical", command=self.log.yview, style="Dark.Vertical.TScrollbar")
        xsb = ttk.Scrollbar(body, orient="horizontal", command=self.log.xview, style="Dark.Horizontal.TScrollbar")
        self.log.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        bold = LOG_FONT + ("bold",)
        indent = tkfont.Font(self, font=LOG_FONT).measure(" " * REASON_INDENT)
        self.log.tag_configure("head", foreground="#ffffff", font=bold, spacing1=8, spacing3=4)
        self.log.tag_configure("colhead", foreground="#8b949e", font=bold)
        self.log.tag_configure("ready", foreground=TURQUOISE)
        self.log.tag_configure("site", foreground="#D8B4FE")
        self.log.tag_configure("skip", foreground=WATERMELON)
        self.log.tag_configure("reason", foreground="#b1a27a", wrap="word", lmargin1=indent, lmargin2=indent,
                               spacing3=4)
        self.log.tag_configure("good", foreground=JUNGLE, font=bold)
        self.log.tag_configure("err", foreground=WATERMELON)
        self.log.tag_configure("dim", foreground="#8b949e")
        self.log.tag_configure("key", foreground=GOLD, font=bold)
        self.log.tag_configure("summary", foreground=GOLD, font=bold, spacing1=4)

    # ---------- data ----------

    def load_jobs(self):
        try:
            self.mtime = os.path.getmtime(JOBS_FILE)
            with open(JOBS_FILE, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            d = {"updated": "", "jobs": []}
        self.jobs = d["jobs"]
        self.updated_lbl.config(text=f"Last search: {d['updated']}" if d["updated"] else "No search yet. Press Find jobs.")
        self.fill_table()

    def watch_file(self):
        try:
            if os.path.getmtime(JOBS_FILE) != self.mtime:
                self.load_jobs()
        except OSError:
            pass
        try:  # a run just used a model or hit a limit
            if os.path.getmtime(bot.GEMINI_STATE) != self.model_mtime:
                self.model_mtime = os.path.getmtime(bot.GEMINI_STATE)
                self.fill_models()
        except OSError:
            pass
        self.after(3000, self.watch_file)

    def row_values(self, j):
        tr = getattr(self, "tracker_cache", {})
        tr_status = tr.get(j.get("id")) or tr.get(j.get("url")) or tr.get((j.get("email") or "").lower())
        if tr_status:
            if "Reply" in tr_status:
                status = "🎉 Reply Received"
            elif tr_status == "Sent":
                status = "📤 Sent"
            elif tr_status.startswith("draft"):
                status = "✉ Drafted"
            elif tr_status == "applied":
                status = "✅ Applied"
            else:
                status = f"✔ {tr_status}"
        else:
            status = LABEL.get(j["status"], j["status"])
            if j["status"] in ("done", "rejected") and j.get("why"):
                status = f"{status[:1]} {j['why']}"
        company = str(j.get("company") or "").strip()
        company = re.sub(r"\s*\(https?://\S+\)", "", company).strip()
        if company.lower().startswith("seeking"):
            company = company.replace("SEEKING FREELANCER", "").replace("SEEKING WORK", "").strip(" |:-") or "HN Employer"
        role = str(j.get("title") or "").strip()
        if "|" in role:
            parts = [p.strip() for p in role.split("|")]
            ROLE_HINTS = re.compile(r"\b(engineer|developer|dev|architect|cto|lead|programmer|specialist|designer|qa|tester|manager|scientist)\b", re.I)
            matched_roles = [p for p in parts if ROLE_HINTS.search(p) and not p.lower().startswith("seeking")]
            if matched_roles:
                role = matched_roles[0]
            elif len(parts) >= 2 and (parts[0].lower() in company.lower() or company.lower() in parts[0].lower()):
                role = parts[1]
        return (status, MATCH_LABEL.get(j.get("match"), ""), ago(j.get("date")), company, role,
                where(j)[:80], j.get("salary", ""))

    def fill_table(self):
        keep = self.tree.selection()
        keep = self.by_iid.get(keep[0], {}).get("id") if keep else None
        self.tree.delete(*self.tree.get_children())
        self.by_iid = {}

        # Refresh tracker cache
        self.tracker_cache = {}
        for r in bot.read_tracker():
            for k in (r.get("draft_id"), r.get("post_url"), (r.get("email") or "").lower()):
                if k:
                    self.tracker_cache[k] = r.get("status", "")

        want, q = VIEWS[self.view.get()], self.search.get().lower().strip()
        rows = [j for j in self.jobs if j["status"] in want and
                (not q or q in f"{j['title']} {j['company']} {j['location']} {j.get('tags', '')} {j['text']}".lower())]

        # Strict Work Mode Filter
        active_modes = [m for m, v in self.modes.items() if v.get()]
        if active_modes:
            if active_modes == ["remote"]:
                rows = [
                    j for j in rows
                    if bot.job_mode(j) == "remote"
                    and not re.search(
                        r"\b(hybrid|on-?site|in-?office|office-?based|in-?person|days (?:a|per) week in (?:the|our)?\s*office)\b",
                        f"{j.get('title', '')} {j.get('location', '')} {j.get('text', '')[:4000]}",
                        re.I
                    )
                    and (
                        not bot.BLOCK_LOC.search(f"{j.get('title', '')} {j.get('location', '')} {j.get('text', '')[:4000]}")
                        or re.search(r"\b(pakistan|lahore|karachi|islamabad|rawalpindi)\b", f"{j.get('title', '')} {j.get('location', '')}", re.I)
                    )
                ]
            else:
                rows = [j for j in rows if bot.job_mode(j) in active_modes]

        # If keywords_in_title is enabled, strictly require that role/title matches user keywords
        if bot.TITLE_ONLY:
            filtered_by_title = []
            for j in rows:
                t = j.get("title", "")
                if "|" in t:
                    parts = [p.strip() for p in t.split("|")]
                    if len(parts) >= 2 and len(parts[1]) > 3:
                        t = parts[1]
                if bot.MATCH.score(t, None) > 0:
                    filtered_by_title.append(j)
            rows = filtered_by_title

        idx = COLUMNS.index(self.sort_col)
        if self.sort_col in ("Posted", "Match"):  # newest first; for Match, strong matches before partial ones
            rows.sort(key=lambda j: j.get("date") or "", reverse=not self.sort_rev)
            if self.sort_col == "Match":
                rows.sort(key=lambda j: j.get("match") != "strong", reverse=self.sort_rev)
        else:
            rows.sort(key=lambda j: str(self.row_values(j)[idx]).lower(), reverse=self.sort_rev)
        again = None
        for j in rows:
            tr_status = self.tracker_cache.get(j.get("id")) or self.tracker_cache.get(j.get("url")) or self.tracker_cache.get((j.get("email") or "").lower())
            if tr_status and "Reply" in tr_status:
                tag = "reply"
            elif tr_status == "Sent":
                tag = "sent"
            else:
                tag = j["status"]
            iid = self.tree.insert("", "end", values=self.row_values(j), tags=(tag,))
            self.by_iid[iid] = j
            if j["id"] == keep:
                again = iid
        matches = sum(j["status"] in (bot.STATUS_READY, bot.STATUS_SITE) for j in self.jobs)
        if self.jobs and not matches and not rows:
            text = f"No matches in {len(self.jobs)} jobs."
        else:
            text = (f"{len(rows)} shown  ·  {sum(j['status'] == bot.STATUS_READY for j in self.jobs)} with email, "
                    f"{sum(j['status'] == bot.STATUS_SITE for j in self.jobs)} apply on site, "
                    f"{len(self.jobs)} checked")
        if self.jobs and matches < 20:
            text += self.near_misses()
        self.count_lbl.config(text=text, wraplength=round(560 * self.scale), justify="left")
        if again:
            self.tree.selection_set(again)
            self.tree.see(again)
        else:
            self.show_detail()

    def near_misses(self):
        """What loosening the filter would add: jobs that match your keywords but were left out for age or place."""
        near = [j for j in self.jobs if j["status"] == bot.STATUS_REJECTED and j.get("match")]
        old = sum(j["why"] == "too old" for j in near)
        place = sum(j["why"].startswith(("not open", "location/work-auth")) or " outside " in j["why"]
                    for j in near)
        kind = {m: sum(j["why"] == f"{name.lower()} job" for j in near) for m, name in bot.WORK_MODES.items()}
        tips = ([f"{old} more are older than {self.age.get()} days (raise Max age)"] if old else []) + \
               ([f"{place} more are limited to other countries (Open to: Any country, or Countries I pick)"]
                if place else []) + \
               [f"{n} more are {bot.WORK_MODES[m].lower()} (tick {bot.WORK_MODES[m]})" for m, n in kind.items() if n]
        if not tips:
            return "  ·  Try a Job type, more or shorter keywords, or untick Keywords in title only."
        return "  ·  " + "; ".join(tips) + "."

    def sort_by(self, col):
        self.sort_rev = not self.sort_rev if self.sort_col == col else False
        self.sort_col = col
        self.fill_table()

    def selected(self):
        s = self.tree.selection()
        return self.by_iid.get(s[0]) if s else None

    def show_detail(self):
        j = self.selected()
        self.set_job_buttons(j)
        if not j:
            self.show_start()
            return
        t = self.detail
        t.config(state="normal")
        t.delete("1.0", "end")
        t.insert("end", j["title"] + "\n", "h1")
        t.insert("end", f"{j['company']}  ·  {where(j)[:120]}\n", "h2")
        facts = [("Status", LABEL.get(j["status"], j["status"]) + (f"  ({j['why']})" if j.get("why") else "")),
                 ("Posted", (j.get("date") or "")[:10] + (f"  ({ago(j.get('date'))})" if j.get("date") else "")),
                 ("Salary", j.get("salary", "")), ("Type", j.get("job_type", "")), ("Level", j.get("level", "")),
                 ("Match", MATCH_HELP.get(j.get("match"), "")), ("Note", j.get("note", "")),
                 ("Tags", j.get("tags", "")), ("Email", j.get("email", "")),
                 ("Email found on", j.get("email_src", "")), ("Source", j["source"])]
        for k, v in facts:
            if v:
                t.insert("end", f"{k}: ", "key")
                t.insert("end", f"{v}\n")
        t.insert("end", "Link: ", "key")
        t.insert("end", j.get("apply") or j["url"], "link")
        t.insert("end", "\n\n")
        t.insert("end", j["text"])
        t.config(state="disabled")
        t.yview_moveto(0)

    def show_start(self):
        """The getting-started checklist, shown while no job is picked. Each open step is a link that does it."""
        cfg = read_config()
        try:
            with open(PROFILE, encoding="utf-8-sig") as f:
                name = json.load(f).get("name", "")
        except (OSError, ValueError, AttributeError):
            name = ""
        steps = [
            (has_key(cfg, "gemini_api_key"), "Connect Apinex (free)", self.keys,
             "Apinex / Gemini writes your tailored CVs using free models (Gemini 3.8, DeepSeek V4.1, Claude 4.6)."),
            (bool(name), f"Upload your CV{f'  ({name})' if name else ''}", self.upload_cv,
             "Gemini reads it once and builds your profile. Every CV it makes uses only facts from it."),
            (bool(self.jobs), "Find jobs", self.find_jobs,
             "Pick a job type (or type keywords) and your country above, then press Find jobs."),
            (has_key(cfg, "gmail_address") and has_key(cfg, "gmail_app_password"), "Connect Gmail (optional)", self.keys,
             "Saves each application as a Gmail draft for you to check and send. Without it you get the PDFs."),
        ]
        t = self.detail
        t.config(state="normal")
        t.delete("1.0", "end")
        t.insert("end", "Getting Started with Pasha Hunt\n", "h1")
        t.insert("end", "Pick a job on the left to view details. New to Pasha Hunt? Four easy steps:\n", "h2")
        for i, (ok, text, action, note) in enumerate(steps, 1):
            if ok:
                t.insert("end", f"✔  {text}\n", "done")
            else:
                tag = f"step{i}"
                t.tag_configure(tag, foreground=ACCENT, underline=True)
                t.tag_bind(tag, "<Button-1>", lambda e, a=action: a())
                t.tag_bind(tag, "<Enter>", lambda e: t.config(cursor="hand2"))
                t.tag_bind(tag, "<Leave>", lambda e: t.config(cursor=""))
                t.insert("end", f"{i}.  ", "todo")
                t.insert("end", text, ("todo", tag))
                t.insert("end", "\n")
            t.insert("end", note + "\n", "muted")
        t.insert("end", "\nThen, for each job: ", "key")
        t.insert("end", "Draft email + CV when it has an email, or Make CV + cover letter to apply on the company's "
                        "site. Mark as applied when you have sent it. Read every CV and email before you send it.\n")
        t.insert("end", "\nShortcuts: ", "key")
        t.insert("end", "F5 find jobs  ·  Ctrl+F search the list  ·  Enter open the job page  ·  "
                        "hover over a button to see what it does.\n")
        t.config(state="disabled")

    def set_job_buttons(self, j):
        busy = self.proc is not None
        open_ = j is not None and j["status"] in (bot.STATUS_READY, bot.STATUS_SITE)
        cv, letter = job_files(j["id"]) if j else (None, None)
        on = lambda ok: ["!disabled"] if ok else ["disabled"]
        self.b_open.state(on(j))
        self.b_copy.state(on(j and j.get("email")))
        self.b_draft.state(on(open_ and j.get("email") and not busy))
        self.b_cv.state(on(j and j["status"] != bot.STATUS_REJECTED and not busy))
        self.b_prep.state(on(j and not busy))
        self.b_pack.state(on(j))
        self.b_skip.state(on(open_ and not busy))
        self.b_applied.state(on(j and j.get("why") != "applied by you" and not busy))
        self.b_files.state(on(cv))
        self.b_letter.state(on(letter and os.path.exists(letter[:-4] + ".txt")))

    # ---------- running bot.py ----------

    def run_bot(self, args, what):
        if self.proc:
            return
        self.write_log(f"\n▶ {what}\n", "head")
        self.status_lbl.config(text=f"{what} …")
        try:
            self.proc = subprocess.Popen([*BOT, *args], cwd=bot.CODE,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
        except OSError as e:
            self.write_log(f"Could not start bot.py: {e}\n")
            return
        self.bar.pack(side="right", padx=(0, 10))
        self.bar.start(12)
        for b in self.busy_buttons:
            b.state(["disabled"])
        self.set_job_buttons(self.selected())
        threading.Thread(target=self.reader, args=(self.proc,), daemon=True).start()

    def reader(self, proc):
        for line in proc.stdout:
            self.out.put(line)
        proc.wait()
        self.out.put(None)

    def pump(self):
        try:
            while True:
                line = self.out.get_nowait()
                if line is None:
                    self.finished()
                else:
                    self.log_line(line)
        except queue.Empty:
            pass
        self.after(100, self.pump)

    def stop_run(self):
        """Stop this window's run, or the one holding bot.lock (Auto-run, another window), and free the lock."""
        pid = self.proc.pid if self.proc else lock_owner()
        if pid is None:
            if os.path.exists(LOCK):  # left behind by a run that was killed
                os.remove(LOCK)
                self.write_log("\n■ Cleared a leftover lock from a run that had already ended.\n", "head")
            else:
                self.status_lbl.config(text="No run in progress.")
            return
        if messagebox.askyesno("Stop run", "Stop the run that is in progress?\n\n"
                               "Drafts it already made stay in Gmail.", parent=self):
            self.stop_run_now()

    def stop_run_now(self):
        pid = self.proc.pid if self.proc else lock_owner()
        if pid is None:
            return
        self.stopped = self.proc is not None
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                       creationflags=NO_WINDOW, timeout=15)
        try:
            os.remove(LOCK)
        except OSError:
            pass
        self.write_log("\n■ Run stopped.\n", "head")
        self.status_lbl.config(text="Stopped. " + dt.datetime.now().strftime("%H:%M"))

    def finished(self):
        self.proc = None
        self.bar.stop()
        self.bar.pack_forget()
        self.status_lbl.config(text=("Stopped. " if self.stopped else "Done. ") + dt.datetime.now().strftime("%H:%M"))
        self.stopped = False
        for b in self.busy_buttons:
            b.state(["!disabled"])
        self.load_jobs()
        self.show_profile()

    def write_log(self, s, tag=None):
        self.in_table = False
        self.log.config(state="normal")
        self.log.insert("end", s, tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def log_line(self, line):
        """One line of bot.py output, with a column header before each run of job rows."""
        pieces, is_row = pretty(line.rstrip("\n"))
        if is_row and not self.in_table:
            pieces = [(ROW_HEAD, "colhead")] + pieces
        self.log.config(state="normal")
        for text, tag in pieces:
            m = re.search(r"[A-Za-z]:\\.+?\.(?:pdf|txt|json)\b", text)
            if not m:
                self.log.insert("end", text, tag)
                continue
            # Saved files are links: click to open.
            link = f"file{self.log.index('end')}"
            self.log.tag_configure(link, foreground="#79c0ff", underline=True)
            self.log.tag_bind(link, "<Button-1>", lambda e, p=m.group(): os.startfile(p))
            self.log.tag_bind(link, "<Enter>", lambda e: self.log.config(cursor="hand2"))
            self.log.tag_bind(link, "<Leave>", lambda e: self.log.config(cursor=""))
            self.log.insert("end", text[:m.start()], tag)
            self.log.insert("end", m.group(), (tag, link) if tag else link)
            self.log.insert("end", text[m.end():], tag)
        self.log.see("end")
        self.log.config(state="disabled")
        self.in_table = is_row

    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self.in_table = False

    def find_jobs(self):
        if self.save_filter():
            self.search.set("")
            self.run_bot(["--dry-run"], "Searching 16 job sources (takes about a minute)")

    def ready_for(self, gmail=False):
        """True when the keys and profile a Gemini action needs are there; otherwise opens what is missing.
        gmail=True: for a draft. Returns "cv" when Gmail is missing and you chose a CV + cover letter instead."""
        cfg = read_config()
        if not has_key(cfg, "gemini_api_key"):
            messagebox.showinfo("Job Hunter", "First connect Gemini (free): it writes your tailored CVs.", parent=self)
            self.keys()
            return False
        if not os.path.exists(PROFILE):
            if messagebox.askyesno("Job Hunter", "Upload your CV first: every tailored CV is made only from the "
                                                 "facts in it.\n\nUpload it now?", parent=self):
                self.upload_cv(ask=False)
            return False
        if gmail and not (has_key(cfg, "gmail_address") and has_key(cfg, "gmail_app_password")):
            answer = messagebox.askyesnocancel(
                "Gmail is not connected", "A draft needs Gmail.\n\nYes: connect Gmail now.\n"
                                          "No: make the CV + cover letter (PDF) instead, and the email text to "
                                          "send yourself.", parent=self)
            if answer:
                self.keys()
            return "cv" if answer is False else False
        return True

    def auto_draft(self):
        if self.ready_for() and self.save_filter():
            self.search.set("")
            self.run_bot([], "Finding jobs and drafting the best matches")

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

    # ---------- simple actions ----------

    def open_job(self):
        j = self.selected()
        url = j and (j.get("apply") or j["url"])
        if url and url.lower().startswith(("https://", "http://")):
            webbrowser.open(url)

    def copy(self, text, what):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_lbl.config(text=f"Copied {what}.")

    def copy_email(self):
        j = self.selected()
        if j and j.get("email"):
            self.copy(j["email"], j["email"])

    def copy_letter(self):
        j = self.selected()
        letter = j and job_files(j["id"])[1]
        try:
            with open(letter[:-4] + ".txt", encoding="utf-8") as f:
                self.copy(f.read(), "the cover letter")
        except (OSError, TypeError):
            self.status_lbl.config(text="No cover letter for this job yet. Press Make CV + cover letter.")

    def open_job_files(self):
        j = self.selected()
        for path in (job_files(j["id"]) if j else ()):
            if path:
                os.startfile(path)

    def generate_interview_prep(self):
        j = self.selected()
        if not j:
            return
        cfg = read_config()
        if not has_key(cfg, "gemini_api_key"):
            messagebox.showinfo("Interview Prep", "Connect your AI key (Apinex / Gemini) in Settings first to generate interview guides.", parent=self)
            self.keys()
            return
        if not os.path.exists(PROFILE):
            messagebox.showinfo("Interview Prep", "Upload your CV first so the interview guide is customized to your actual background.", parent=self)
            self.upload_cv(ask=False)
            return

        company = j.get("company", "Company")
        role = j.get("role", "Software Engineer")
        self.status_lbl.config(text=f"🎯 Crafting AI Interview Battle-Pack for {company} …")

        def worker():
            try:
                with open(PROFILE, encoding="utf-8") as f:
                    prof = json.load(f)

                job_desc = j.get("summary") or j.get("description") or j.get("role", "")
                prompt = (
                    f"You are an elite Tech Career Coach & Interview Strategist.\n"
                    f"Candidate Profile:\n"
                    f"Name: {prof.get('name')}\n"
                    f"Title: {prof.get('default_title')}\n"
                    f"Top Skills: {', '.join(prof.get('skills', [])[:15])}\n"
                    f"Experience Highlights: {json.dumps(prof.get('experience', [])[:3])}\n\n"
                    f"Target Opportunity:\n"
                    f"Company: {company}\n"
                    f"Role: {role}\n"
                    f"Job Context: {job_desc}\n\n"
                    f"Produce a high-impact, actionable 'Interview Battle-Pack' formatted cleanly in GitHub Markdown with these exact sections:\n"
                    f"# 🎯 Interview Battle-Pack: {role} at {company}\n\n"
                    f"## 1. ⚡ 60-Second Elevator Pitch\n"
                    f"(A razor-sharp introductory pitch answering 'Tell me about yourself', bridging the candidate's exact strengths to {company}'s mission)\n\n"
                    f"## 2. 🧠 Top 5 Anticipated Technical & Behavioral Questions with Winning STAR Answers\n"
                    f"(For each question, provide: Situation, Task, Action, Result grounded in the candidate's actual background)\n\n"
                    f"## 3. 🔥 3 Killer Reverse Questions to Ask the Hiring Manager\n"
                    f"(Thought-provoking questions about system architecture, culture, or roadmap that make the candidate unforgettable)\n\n"
                    f"## 4. 💰 Salary & Compensation Strategy\n"
                    f"(A strategic negotiation bracket and anchoring advice for this role)\n"
                )

                prep_text = None
                key = str(cfg.get("gemini_api_key") or "").strip()
                if key.startswith("sk-"):
                    models = ["free/gemini-3.8-flash", "free/deepseek-v4.1", "free/claude-4.6-sonnet", "free/qwen-3.8-max"]
                    for m in models:
                        payload = {"model": m, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4}
                        req = urllib.request.Request(
                            f"{bot.APINEX_BASE_URL}/chat/completions",
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                            method="POST"
                        )
                        try:
                            with urllib.request.urlopen(req, timeout=35) as r:
                                data = json.loads(r.read().decode("utf-8"))
                                prep_text = data["choices"][0]["message"]["content"]
                                if prep_text:
                                    break
                        except Exception:
                            continue
                else:
                    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                                       "generationConfig": {"temperature": 0.4}}).encode()
                    req = urllib.request.Request(
                        f"{bot.GEMINI_API}/gemini-2.5-flash:generateContent",
                        data=body,
                        headers={"x-goog-api-key": key, "Content-Type": "application/json"}
                    )
                    try:
                        with urllib.request.urlopen(req, timeout=35) as r:
                            data = json.loads(r.read().decode("utf-8"))
                            prep_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    except Exception as e:
                        prep_text = f"# Interview Prep for {company}\n\nCould not reach AI API: {e}"

                if not prep_text:
                    prep_text = f"# Interview Battle-Pack: {role} at {company}\n\nPrepare your core accomplishments and review the job requirements."

                prep_dir = os.path.join(HERE, "cvs", "prep")
                os.makedirs(prep_dir, exist_ok=True)
                clean_comp = re.sub(r'[\\/*?:"<>|]', "", company).replace(" ", "_")
                clean_role = re.sub(r'[\\/*?:"<>|]', "", role).replace(" ", "_")[:30]
                file_path = os.path.join(prep_dir, f"{clean_comp}_{clean_role}_Interview_Prep.md")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(prep_text)

                def on_done():
                    self.status_lbl.config(text=f"✅ Interview Prep Guide saved for {company}!")
                    try:
                        os.startfile(file_path)
                    except Exception:
                        pass
                    self.clipboard_clear()
                    self.clipboard_append(prep_text)
                    messagebox.showinfo(
                        "Interview Prep Ready! 🎯",
                        f"Your tailored Interview Battle-Pack for {company} has been generated and saved to:\n\n"
                        f"{file_path}\n\n"
                        f"The full guide has been opened and copied to your clipboard!",
                        parent=self
                    )

                self.after(0, on_done)
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: (self.status_lbl.config(text="Interview Prep failed."),
                                       messagebox.showerror("Error", f"Could not generate prep guide: {err_msg}", parent=self)))

        threading.Thread(target=worker, daemon=True).start()

    def copy_profile_pack(self):
        j = self.selected()
        try:
            with open(PROFILE, encoding="utf-8") as f:
                p = json.load(f)
        except Exception:
            p = {"name": "Candidate", "default_title": "Software Engineer"}

        comp = j.get("company", "Company") if j else "Target Company"
        role = j.get("role", "Target Role") if j else "Target Role"

        cv_path, letter_path = job_files(j["id"]) if j else (None, None)
        cover_text = ""
        if letter_path and os.path.exists(letter_path[:-4] + ".txt"):
            try:
                with open(letter_path[:-4] + ".txt", encoding="utf-8") as f:
                    cover_text = f.read().strip()
            except Exception:
                cover_text = ""

        name = p.get("name", "")
        title = p.get("default_title", "")
        email = read_config().get("gmail_address", "")
        skills = ", ".join(p.get("skills", [])[:15]) if isinstance(p.get("skills"), list) else ""
        portfolio = p.get("portfolio") or p.get("github") or ""

        pack_text = (
            f"=== CANDIDATE APPLICATION PACK ===\n"
            f"Name: {name}\n"
            f"Role: {title}\n"
            f"Email: {email}\n"
            f"Portfolio/Links: {portfolio}\n"
            f"Skills: {skills}\n\n"
            f"=== TARGET APPLICATION ===\n"
            f"Company: {comp}\n"
            f"Position: {role}\n\n"
        )
        if cover_text:
            pack_text += f"=== TAILORED COVER LETTER ===\n{cover_text}\n"

        self.clipboard_clear()
        self.clipboard_append(pack_text)
        self.status_lbl.config(text="📋 Full Application Profile Pack copied to clipboard!")

        win = tk.Toplevel(self, background=DIALOG)
        win.title(f"Quick Apply Pack — {comp}")
        win.geometry("540x500")
        win.transient(self)
        enable_dark_title_bar(win)

        top_f = tk.Frame(win, bg=DIALOG, padx=12, pady=12)
        top_f.pack(fill="both", expand=True)

        tk.Label(top_f, text=f"📋 Quick Form Paste: {comp}", font=("Segoe UI", 12, "bold"),
                 fg=TURQUOISE, bg=DIALOG).pack(anchor="w", pady=(0, 10))

        fields = [
            ("Full Name", name),
            ("Title", title),
            ("Email", email),
            ("Portfolio / Links", portfolio),
            ("Key Skills", skills),
        ]

        for lbl, val in fields:
            row = tk.Frame(top_f, bg=DIALOG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{lbl}:", font=("Segoe UI", 9, "bold"), width=15, anchor="w",
                     fg=LIGHT_INK, bg=DIALOG).pack(side="left")
            e = ttk.Entry(row)
            e.insert(0, val)
            e.pack(side="left", padx=4, fill="x", expand=True)
            ttk.Button(row, text="Copy", width=6,
                       command=lambda v=val, l=lbl: (self.copy(v, l), self.status_lbl.config(text=f"Copied {l}."))).pack(side="left")

        if cover_text:
            tk.Label(top_f, text="Tailored Cover Letter Preview:", font=("Segoe UI", 9, "bold"),
                     fg=LIGHT_INK, bg=DIALOG).pack(anchor="w", pady=(10, 4))
            tb = tk.Text(top_f, height=7, wrap="word", background="#0E091C", foreground="#F8FAFC",
                         highlightthickness=1, highlightbackground=LINE, relief="flat", padx=6, pady=6)
            tb.insert("1.0", cover_text)
            tb.config(state="disabled")
            tb.pack(fill="both", expand=True, pady=2)
            ttk.Button(top_f, text="📋 Copy Cover Letter", style="Big.TButton",
                       command=lambda: self.copy(cover_text, "Cover Letter")).pack(anchor="w", pady=4)

        b_row = tk.Frame(top_f, bg=DIALOG)
        b_row.pack(fill="x", pady=(10, 0))
        ttk.Button(b_row, text="📋 Copy Entire Profile Pack", style="Jungle.TButton",
                   command=lambda: (self.copy(pack_text, "Entire Profile Pack"), win.destroy())).pack(side="left")
        ttk.Button(b_row, text="Close", command=win.destroy).pack(side="right")

    def menu_button(self, parent, text, items):
        """A toolbar button that opens a menu of (label, command) items; None draws a line."""
        mb = ttk.Menubutton(parent, text=text)
        menu = tk.Menu(mb, tearoff=False, font=("Segoe UI", 10),
                       bg="#130D24", fg="#F8FAFC", activebackground=INDIGO, activeforeground=GOLD,
                       selectcolor=TURQUOISE, bd=1, relief="solid")
        for item in items:
            if item is None:
                menu.add_separator()
            else:
                menu.add_command(label=item[0], command=item[1])
        mb["menu"] = menu
        mb.pack(side="left", padx=(0, 6))
        return mb

    def check_update(self, quiet=True):
        """Show a button when GitHub has a newer release. quiet: say nothing when up to date or offline."""
        def work():
            tag = latest_release()
            self.after(0, done, tag)

        def done(tag):
            if tag and version_tuple(tag) > version_tuple(bot.VERSION):
                self.update_btn.config(text=f"⬆  Update to {tag}")
                self.update_btn.pack(side="right", padx=(0, 8))
                self.new_tag = tag
                if not quiet:
                    self.update_now()
            elif not quiet:
                messagebox.showinfo("Job Hunter", f"You have the latest version ({bot.VERSION})." if tag else
                                    "Could not reach GitHub. Check your internet connection.", parent=self)

        threading.Thread(target=work, daemon=True).start()

    def update_now(self):
        """Download the new installer, run it silently and close: it installs over this copy and reopens Job
        Hunter. Running from source there is no installer, so the download page opens instead."""
        tag = getattr(self, "new_tag", "") or "the new version"
        if not FROZEN:
            if messagebox.askyesno("Job Hunter", f"{tag} is out (you have {bot.VERSION}).\n\nYou run Job Hunter "
                                   "from source: update with  git pull.  Open the download page?", parent=self):
                webbrowser.open(DOWNLOAD_PAGE)
            return
        busy = self.proc or lock_owner()
        if not messagebox.askyesno("Update Job Hunter", f"Update to {tag} now? (you have {bot.VERSION})\n\n"
                                   "Job Hunter downloads it, closes, installs it and opens again in about a minute. "
                                   "Your keys, profile, CVs and tracker are kept."
                                   + ("\n\nThe run in progress will be stopped." if busy else ""), parent=self):
            return
        self.update_btn.state(["disabled"])
        self.status_lbl.config(text="Downloading the update …")

        def progress(pct):
            self.after(0, lambda: self.status_lbl.config(text=f"Downloading the update … {pct}%"))

        def work():
            try:
                path = download_setup(progress)
            except (OSError, ValueError) as e:
                self.after(0, failed, e)
                return
            self.after(0, install, path)

        def failed(e):
            self.update_btn.state(["!disabled"])
            self.status_lbl.config(text="Update failed.")
            if messagebox.askyesno("Update Job Hunter", f"The download failed ({e}).\n\nOpen the download page to "
                                   "get the installer yourself?", parent=self):
                webbrowser.open(DOWNLOAD_PAGE)

        def install(path):
            if self.proc or lock_owner():
                self.stop_run_now()
            # /UPDATE tells the installer to open Job Hunter again when it is done (see JobHunter.iss).
            subprocess.Popen([path, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS",
                              "/NOCANCEL", "/UPDATE"], close_fds=True)
            self.destroy()

        threading.Thread(target=work, daemon=True).start()

    def replay_intro(self):
        if HAS_VIDEO and os.path.exists(INTRO_VIDEO):
            VideoSplash(self, INTRO_VIDEO, None)
        else:
            messagebox.showinfo("Cinematic Intro", "Intro video file not found.", parent=self)

    def about(self):
        messagebox.showinfo("About Pasha Hunt", f"Pasha Hunt {bot.VERSION} (Apinex Edition)\n\n"
                            "Autonomous AI-Powered Remote Job Search & Recruiter Intelligence Suite.\n"
                            "Finds matching remote/global engineering jobs, writes tailored ATS CVs\n"
                            "and cover letters, crafts drafts in Gmail, and tracks recruiter responses.\n\n"
                            f"Your files: {HERE}\n\n{DOWNLOAD_PAGE}\nhttps://github.com/{bot.REPO}", parent=self)

    def open_gmail(self):
        who = read_config().get("gmail_address", "")
        webbrowser.open(f"https://mail.google.com/mail/?authuser={who}#drafts" if who
                        else "https://mail.google.com/mail/#drafts")

    def open_cvs(self):
        os.makedirs(os.path.join(HERE, "cvs"), exist_ok=True)
        os.startfile(os.path.join(HERE, "cvs"))

    def open_file(self, path, missing):
        if os.path.exists(path):
            os.startfile(path)
        else:
            self.status_lbl.config(text=missing)

    def open_tracker(self):
        self.open_file(TRACKER, "No tracker yet: it starts with the first CV, draft or skipped job.")

    def open_profile(self):
        if not os.path.exists(PROFILE):
            if messagebox.askyesno("My profile", "You have no profile yet. Upload your CV to make one?", parent=self):
                self.upload_cv(ask=False)
            return
        subprocess.Popen(["notepad.exe", PROFILE])

    def upload_cv(self, ask=True):
        if not has_key(read_config(), "gemini_api_key"):
            messagebox.showinfo("Upload my CV", "First connect Gemini (free): it reads your CV.", parent=self)
            self.keys()
            return
        path = filedialog.askopenfilename(parent=self, title="Choose your CV", filetypes=[
            ("CV", "*.pdf *.docx *.txt *.md *.png *.jpg *.jpeg *.webp"), ("All files", "*.*")])
        if not path:
            return
        if ask and not messagebox.askokcancel("Upload my CV", "Gemini will read this CV and rebuild profile.json from it.\n\n"
                                      "Every tailored CV, cover letter and email is built only from profile.json. "
                                      "Your current profile is kept as a backup.\n\nContinue?", parent=self):
            return
        self.run_bot(["--import-cv", path], f"Reading your CV: {os.path.basename(path)}")

    def paste_job(self):
        if not self.ready_for():
            return
        win = tk.Toplevel(self, background=DIALOG)
        win.title("Tailor CV to a job description")
        win.transient(self)
        win.geometry("760x620")
        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)
        j = self.selected()
        fields = {}
        for i, (key, label, start) in enumerate([("company", "Company", j["company"] if j else ""),
                                                 ("title", "Job title", j["title"] if j else ""),
                                                 ("url", "Link (optional)", (j.get("apply") or j["url"]) if j else "")]):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="w", pady=3)
            fields[key] = tk.StringVar(value=start)
            ttk.Entry(frm, textvariable=fields[key]).grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=3)
        ttk.Label(frm, text="Paste the full job description:").grid(row=3, column=0, columnspan=2, sticky="w",
                                                                    pady=(10, 3))
        text = tk.Text(frm, wrap="word", font=("Segoe UI", 10), height=18, undo=True, relief="flat", padx=8, pady=6,
                       background=SURFACE, foreground=INK, insertbackground=INK, highlightthickness=1,
                       highlightbackground=LINE, highlightcolor=ACCENT)
        text.grid(row=4, column=0, columnspan=2, sticky="nsew")
        if j:
            text.insert("1.0", j["text"])
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(4, weight=1)

        def go():
            job = {k: v.get().strip() for k, v in fields.items()}
            job["text"] = text.get("1.0", "end").strip()
            if not job["company"] or not job["title"] or len(job["text"]) < 100:
                messagebox.showerror("Tailor CV", "Fill in the company, the job title and the full description.",
                                     parent=win)
                return
            path = os.path.join(HERE, "tailor", "pasted-job.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(job, f, ensure_ascii=False)
            win.destroy()
            self.run_bot(["--custom", path], f"Tailoring your CV + cover letter for {job['company']}")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(btns, text="📄  Make CV + cover letter", style="Big.TButton", command=go).pack(side="right")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right", padx=6)
        win.grab_set()

    def open_runs(self):
        self.open_file(bot.RUNS_LOG, "No run log yet: it starts with the first search.")

    # ---------- scheduled task ----------

    def task_state(self):
        try:
            r = subprocess.run(["schtasks", "/Query", "/TN", TASK, "/FO", "CSV", "/NH"], capture_output=True,
                               text=True, creationflags=NO_WINDOW, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode:
            return None
        return "off" if "Disabled" in r.stdout else "on"

    def refresh_task_button(self):
        s = self.task_state()
        self.task_btn.config(text={"on": "⏱  Auto-run every 30 min: ON", "off": "⏸  Auto-run: OFF",
                                   None: "⏱  Set up auto-run"}[s])

    def toggle_task(self):
        s = self.task_state()
        if s is None:
            if not messagebox.askyesno("Auto-run", "Run Job Hunter every 30 minutes in the background while you "
                                       "are signed in to Windows?\n\nEach run searches, tailors up to "
                                       "'Max drafts per run' CVs and saves Gmail drafts. Nothing is ever sent.\n\n"
                                       "You can turn it off again with this button."):
                return
            cmd = ["schtasks", "/Create", "/TN", TASK, "/SC", "MINUTE", "/MO", "30", "/TR", TASK_RUN, "/F"]
        else:
            cmd = ["schtasks", "/Change", "/TN", TASK, "/DISABLE" if s == "on" else "/ENABLE"]
        r = subprocess.run(cmd, capture_output=True, text=True, creationflags=NO_WINDOW, timeout=15)
        if r.returncode:
            messagebox.showerror("Job Hunter", (r.stderr or r.stdout).strip() or "Could not change the task.")
        self.refresh_task_button()

    # ---------- settings ----------

    def save_filter(self):
        """Write the filter bar to config.json. Returns False (and says why) if it is not valid."""
        words = lambda v: [w.strip() for w in v.get().split(",") if w.strip()]
        if not words(self.kw):
            messagebox.showerror("Job filter", "Type at least one keyword, e.g.  .NET, C#, Accountant, SEO")
            return False
        try:
            age = max(1, int(self.age.get()))
        except ValueError:
            messagebox.showerror("Job filter", "Max age must be a number of days.")
            return False
        modes = [m for m, v in self.modes.items() if v.get()]
        if not modes:
            messagebox.showerror("Job filter", "Tick at least one Work type: Remote, Hybrid or On-site.")
            return False
        where = self.open_to_key()
        if where == "countries" and not words(self.countries):
            messagebox.showerror("Job filter", "Type the countries you want in Countries, e.g.  UAE, Germany, Europe"
                                               "\n\nOr pick another Open to.")
            return False
        if where == "me" and modes != ["remote"] and not words(self.region) and not self.visa.get():
            messagebox.showerror("Job filter", "Type your country in My country/region, e.g.  Pakistan\n\n"
                                               "Hybrid and on-site jobs are kept only if the office is there.")
            return False
        cfg = read_config()
        picked = self.picked_types()
        fields = combine(picked)[1] if picked else ["all"]
        new = dict(keywords=words(self.kw), exclude_keywords=words(self.excl), max_job_age_days=age,
                   work_modes=modes, open_to=where, keywords_in_title=self.title_only.get(), job_fields=fields,
                   job_types=picked, my_region_words=words(self.region), target_countries=words(self.countries),
                   visa_sponsorship=self.visa.get(), search_google=self.google.get())
        if any(cfg.get(k) != v for k, v in new.items()) or "worldwide_only" in cfg or "pakistan_only" in cfg:
            cfg.update(new)
            cfg.pop("pakistan_only", None)
            cfg.pop("worldwide_only", None)
            write_config(cfg)
            self.write_log(f"\nFilter saved: {self.preset.get()} | keywords {', '.join(new['keywords'])}"
                           + (" (in title)" if new["keywords_in_title"] else "")
                           + (f" | exclude {', '.join(new['exclude_keywords'])}" if new["exclude_keywords"] else "")
                           + f" | max age {age} days | {bot.wanted_jobs(new)}\n")
        return True

    def keys(self, first=False):
        """The "Connect your accounts" window: Gmail app password and Gemini key, with how to get each."""
        cfg = read_config()
        win = tk.Toplevel(self, background=DIALOG)
        win.title("Connect your accounts")
        win.transient(self)
        win.resizable(False, False)
        enable_dark_title_bar(win)
        frm = ttk.Frame(win, padding=18)
        frm.pack(fill="both")
        ttk.Label(frm, text="Connect Gmail and Gemini", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frm, wraplength=560, foreground=MUTED, justify="left",
                  text="Job Hunter writes your tailored CVs with Google Gemini (free) and saves each email as a "
                       "draft in your Gmail, ready for you to check and send. It never sends anything itself. "
                       "Gmail is optional: without it you still get the CVs and cover letters.\n\n"
                       f"Your keys stay on this computer, in {CONFIG}").pack(anchor="w", pady=(4, 10))
        vars_, status = {}, {}
        for key, label, secret, steps, links in KEY_FIELDS:
            box = ttk.Frame(frm)
            box.pack(fill="x", pady=(6, 0))
            ttk.Label(box, text=label, font=("Segoe UI", 10, "bold"), width=24).pack(side="left")
            start = cfg.get(key, "")
            vars_[key] = tk.StringVar(value="" if start.startswith("PUT-") else start)
            entry = ttk.Entry(box, textvariable=vars_[key], width=44, show="•" if secret else "")
            entry.pack(side="left", padx=(6, 6))
            if secret:
                ttk.Button(box, text="Show", width=6, command=lambda e=entry: e.config(
                    show="" if e.cget("show") else "•")).pack(side="left")
            status[key] = ttk.Label(frm, text="", wraplength=560, justify="left")
            if steps:
                how = ttk.Frame(frm, padding=(12, 6, 0, 4))
                for i, step in enumerate(steps, 1):
                    ttk.Label(how, text=step if step.startswith("Note:") else f"{i}.  {step}", wraplength=540,
                              justify="left").pack(anchor="w", pady=1)
                links_row = ttk.Frame(how)
                links_row.pack(anchor="w", pady=(4, 0))
                for text, url in links:
                    ttk.Button(links_row, text=f"↗  {text}", command=lambda u=url: webbrowser.open(u)).pack(
                        side="left", padx=(0, 6))
                toggle = ttk.Label(frm, text=f"❔ How do I get a {label}?", foreground=ACCENT,
                                   cursor="hand2", font=("Segoe UI", 9, "underline"))
                toggle.pack(anchor="w", padx=(186, 0), pady=(2, 0))

                def flip(e, how=how, toggle=toggle):
                    if how.winfo_ismapped():
                        how.pack_forget()
                    else:
                        how.pack(after=toggle, fill="x")
                toggle.bind("<Button-1>", flip)
                if first and not vars_[key].get():
                    how.pack(fill="x")
            status[key].pack(anchor="w", padx=(186, 0))

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(16, 0))
        busy = ttk.Label(btns, text="", foreground=MUTED)
        busy.pack(side="left")
        save_btn = ttk.Button(btns, text="Test & save", style="Big.TButton")
        save_btn.pack(side="right")
        ttk.Button(btns, text="Later" if first else "Cancel", command=win.destroy).pack(side="right", padx=6)

        def save(new):
            cfg = read_config()
            cfg.update(new)
            write_config(cfg)
            win.destroy()
            self.status_lbl.config(text="Keys saved.")
            self.after(200, self.check_models)
            if first and not os.path.exists(PROFILE) and messagebox.askyesno(
                    "Job Hunter", "Next, upload your CV (PDF, Word or text). Gemini reads it once and builds your "
                                  "profile, which every tailored CV is made from.\n\nUpload it now?", parent=self):
                self.upload_cv(ask=False)

        def tested(new, errors):
            if not win.winfo_exists():
                return
            save_btn.state(["!disabled"])
            busy.config(text="")
            for key, err in errors.items():
                status[key].config(text=f"✖  {err}" if err else "✔  Works", foreground="#b91c1c" if err else "#15803d")
            if not any(errors.values()) or messagebox.askyesno(
                    "Connect your accounts", "Some keys did not pass the test (see the red notes).\n\n"
                                             "Save them anyway?", parent=win):
                save(new)

        def test():
            new = {k: v.get().strip() for k, v in vars_.items()}
            if not new["gemini_api_key"]:
                messagebox.showerror("Connect your accounts", "Paste your Gemini API key.", parent=win)
                return
            gmail = bool(new["gmail_address"] or new["gmail_app_password"])
            if gmail and ("@" not in new["gmail_address"] or not new["gmail_app_password"]):
                messagebox.showerror("Connect your accounts", "For Gmail drafts fill in both the Gmail address and "
                                     "the app password, or leave both empty.", parent=win)
                return
            save_btn.state(["disabled"])
            busy.config(text="Testing…")
            host = cfg.get("imap_host", "imap.gmail.com")

            def work():
                errors = {"gemini_api_key": test_gemini(new["gemini_api_key"])}
                if gmail:
                    errors["gmail_app_password"] = test_gmail(new["gmail_address"], new["gmail_app_password"], host)
                self.after(0, tested, new, errors)
            threading.Thread(target=work, daemon=True).start()

        save_btn.config(command=test)
        win.grab_set()

    def onboarding_wizard(self, first=False):
        """Interactive, sleek 4-step onboarding wizard for fast setup."""
        cfg = read_config()
        win = tk.Toplevel(self, background="#0A0714")
        win.title("Pasha Hunt 2.0 - Fast Onboarding & Setup")
        win.transient(self)
        win.resizable(False, False)
        enable_dark_title_bar(win)
        
        # Center window
        w_width, w_height = round(700 * self.scale), round(560 * self.scale)
        x = max(0, self.winfo_x() + (self.winfo_width() - w_width) // 2)
        y = max(0, self.winfo_y() + (self.winfo_height() - w_height) // 2)
        win.geometry(f"{w_width}x{w_height}+{x}+{y}")
        
        main_frame = tk.Frame(win, bg="#0A0714", padx=20, pady=16)
        main_frame.pack(fill="both", expand=True)

        # Header with Logo & Title
        hdr = tk.Frame(main_frame, bg="#0A0714")
        hdr.pack(fill="x", pady=(0, 12))
        if os.path.exists(LOGO_PNG):
            try:
                logo_im = Image.open(LOGO_PNG).resize((44, 44), Image.Resampling.LANCZOS)
                self._w_logo = ImageTk.PhotoImage(logo_im)
                tk.Label(hdr, image=self._w_logo, bg="#0A0714").pack(side="left", padx=(0, 12))
            except Exception:
                pass
        t_box = tk.Frame(hdr, bg="#0A0714")
        t_box.pack(side="left", fill="both")
        tk.Label(t_box, text="PASHA HUNT 2.0 (APINEX EDITION)", font=("Segoe UI", 15, "bold"), fg=TURQUOISE, bg="#0A0714").pack(anchor="w")
        tk.Label(t_box, text="Autonomous Remote Job Hunter & Recruiter Reply Tracker", font=("Segoe UI", 10), fg=MUTED, bg="#0A0714").pack(anchor="w")

        # Step indicator tabs bar
        step_bar = tk.Frame(main_frame, bg="#130D24", height=38, relief="flat", highlightthickness=1, highlightbackground=LINE)
        step_bar.pack(fill="x", pady=(0, 16))
        
        step_labels = ["1. Welcome", "2. Apinex AI Key", "3. ATS Master CV", "4. Gmail & Tracker"]
        step_btns = []
        for i, slabel in enumerate(step_labels):
            lbl = tk.Label(step_bar, text=slabel, font=("Segoe UI", 9, "bold"), bg="#130D24", fg=MUTED, padx=12, pady=7)
            lbl.pack(side="left", expand=True, fill="both")
            step_btns.append(lbl)

        # Content Card
        card = tk.Frame(main_frame, bg="#18102E", padx=18, pady=16, relief="flat", highlightthickness=1, highlightbackground=LINE)
        card.pack(fill="both", expand=True)

        # Step Frames container
        step_frames = [tk.Frame(card, bg="#18102E") for _ in range(4)]
        
        # State variables
        v_key = tk.StringVar(value=cfg.get("gemini_api_key", ""))
        v_model = tk.StringVar(value=cfg.get("gemini_model", "free/gemini-3.8-flash"))
        v_gmail = tk.StringVar(value=cfg.get("gmail_address", ""))
        v_app_pass = tk.StringVar(value=cfg.get("gmail_app_password", ""))
        v_cv_status = tk.StringVar()
        
        try:
            with open(PROFILE, encoding="utf-8") as f:
                prof = json.load(f)
            v_cv_status.set(f"✓ Profile Loaded: {prof.get('name', 'Candidate')} ({prof.get('default_title', '')[:40]})")
        except Exception:
            v_cv_status.set("No ATS CV uploaded yet.")

        # --- STEP 1: WELCOME ---
        s1 = step_frames[0]
        tk.Label(s1, text="Welcome to Pasha Hunt 2.0!", font=("Segoe UI", 14, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 4))
        tk.Label(s1, text="The high-performance autonomous engine for remote job seekers.", font=("Segoe UI", 10), fg=MUTED, bg="#18102E").pack(anchor="w", pady=(0, 14))
        
        features = [
            ("🌐 100% Strict Remote Matching", "Searches top remote job boards and eliminates all hybrid/on-site noise."),
            ("🤖 Apinex Multi-Model AI Engine", "Uses 10 free high-speed models (Gemini 3.8 Flash, Qwen 3.8 Max, DeepSeek V4.1) for tailored ATS CVs."),
            ("✉ Direct Recruiter Email Drafting", "Automatically extracts hiring manager emails and creates personalized Gmail drafts."),
            ("📬 Live Recruiter Reply Detection", "Monitors your Gmail inbox via IMAP SSL and alerts you the moment a recruiter responds.")
        ]
        for ftitle, fdesc in features:
            f_box = tk.Frame(s1, bg="#130D24", padx=12, pady=7, highlightthickness=1, highlightbackground=LINE)
            f_box.pack(fill="x", pady=3)
            tk.Label(f_box, text=ftitle, font=("Segoe UI", 9, "bold"), fg=TURQUOISE, bg="#130D24").pack(anchor="w")
            tk.Label(f_box, text=fdesc, font=("Segoe UI", 9), fg=MUTED, bg="#130D24").pack(anchor="w")

        # --- STEP 2: APINEX AI KEY ---
        s2 = step_frames[1]
        tk.Label(s2, text="Step 2: Connect Apinex AI Key", font=("Segoe UI", 14, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 4))
        tk.Label(s2, text="Apinex provides free API access to Gemini 3.8, Qwen 3.8, Claude and DeepSeek without credit cards.", font=("Segoe UI", 9), fg=MUTED, bg="#18102E").pack(anchor="w", pady=(0, 12))

        tk.Label(s2, text="Apinex API Key:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 4))
        e_key = tk.Entry(s2, textvariable=v_key, font=("Consolas", 10), bg="#0E091C", fg="#F8FAFC", insertbackground=TURQUOISE, relief="flat", highlightthickness=1, highlightbackground=LINE)
        e_key.pack(fill="x", ipady=5, pady=(0, 8))

        test_row = tk.Frame(s2, bg="#18102E")
        test_row.pack(fill="x", pady=(0, 10))
        lbl_key_test = tk.Label(test_row, text="", font=("Segoe UI", 9, "bold"), bg="#18102E", fg=JUNGLE)
        
        def run_key_test():
            k = v_key.get().strip()
            if not k:
                lbl_key_test.config(text="Please enter an Apinex API key.", fg=WATERMELON)
                return
            lbl_key_test.config(text="Testing connection to Apinex ...", fg=TURQUOISE)
            def _th():
                err = bot.test_gemini(k)
                if not err:
                    lbl_key_test.config(text="✓ Verified! Connected to Apinex. 10 free models ready.", fg=JUNGLE)
                else:
                    lbl_key_test.config(text=f"Verification: {err[:55]}", fg=GOLD)
            threading.Thread(target=_th, daemon=True).start()

        ttk.Button(test_row, text="⚡ Test Connection & Fetch Models", style="Big.TButton", command=run_key_test).pack(side="left")
        lbl_key_test.pack(side="left", padx=10)

        tk.Label(s2, text="Default AI Model:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(8, 4))
        free_models = [
            "free/gemini-3.8-flash",
            "free/qwen-3.8-max",
            "free/deepseek-v4.1",
            "free/claude-4.6",
            "Auto: best free model that is not at its limit"
        ]
        cb_model = ttk.Combobox(s2, textvariable=v_model, values=free_models, state="readonly")
        cb_model.pack(fill="x", ipady=3)

        # --- STEP 3: ATS MASTER CV ---
        s3 = step_frames[2]
        tk.Label(s3, text="Step 3: Setup ATS Master CV", font=("Segoe UI", 14, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 4))
        tk.Label(s3, text="Pasha Hunt analyzes your CV once and creates tailored ATS resumes for every job opportunity.", font=("Segoe UI", 9), fg=MUTED, bg="#18102E").pack(anchor="w", pady=(0, 12))

        cv_box = tk.Frame(s3, bg="#130D24", padx=14, pady=14, highlightthickness=1, highlightbackground=LINE)
        cv_box.pack(fill="x", pady=(0, 12))
        lbl_cv_det = tk.Label(cv_box, textvariable=v_cv_status, font=("Segoe UI", 10, "bold"), fg=TURQUOISE, bg="#130D24", wraplength=560, justify="left")
        lbl_cv_det.pack(anchor="w")

        def run_upload_cv():
            path = filedialog.askopenfilename(
                title="Select your Master CV",
                filetypes=[("CV files", "*.pdf;*.docx;*.txt"), ("All files", "*.*")],
                parent=win
            )
            if not path:
                return
            v_cv_status.set("Reading and extracting CV profile ...")
            def _th():
                try:
                    text, err = cv.extract_text(path)
                    if err:
                        v_cv_status.set(f"Error reading file: {err}")
                        return
                    prof, perr = cv.build_profile(text)
                    if prof:
                        with open(PROFILE, "w", encoding="utf-8") as f:
                            json.dump(prof, f, indent=2, ensure_ascii=False)
                        v_cv_status.set(f"✓ Loaded: {prof.get('name', 'Candidate')} - {prof.get('default_title', '')[:40]}")
                        self.show_profile()
                    else:
                        v_cv_status.set(f"Profile creation note: {perr}")
                except Exception as e:
                    v_cv_status.set(f"Failed to parse CV: {e}")
            threading.Thread(target=_th, daemon=True).start()

        ttk.Button(s3, text="📄 Upload ATS CV (.pdf / .docx / .txt)", style="Big.TButton", command=run_upload_cv).pack(anchor="w", pady=(4, 6))
        tk.Label(s3, text="Tip: You can re-upload or update your CV at any time from the main toolbar.", font=("Segoe UI", 9), fg=MUTED, bg="#18102E").pack(anchor="w")

        # --- STEP 4: GMAIL & REPLY TRACKER ---
        s4 = step_frames[3]
        tk.Label(s4, text="Step 4: Connect Gmail & Live Tracker", font=("Segoe UI", 14, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 4))
        tk.Label(s4, text="Saves tailored recruiter emails to your Gmail Drafts and automatically monitors replies. (Optional)", font=("Segoe UI", 9), fg=MUTED, bg="#18102E").pack(anchor="w", pady=(0, 12))

        tk.Label(s4, text="Gmail Address:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 3))
        e_gmail = tk.Entry(s4, textvariable=v_gmail, font=("Segoe UI", 10), bg="#0E091C", fg="#F8FAFC", insertbackground=TURQUOISE, relief="flat", highlightthickness=1, highlightbackground=LINE)
        e_gmail.pack(fill="x", ipady=4, pady=(0, 6))

        tk.Label(s4, text="Google 16-Character App Password:", font=("Segoe UI", 10, "bold"), fg="#F8FAFC", bg="#18102E").pack(anchor="w", pady=(0, 3))
        pass_row = tk.Frame(s4, bg="#18102E")
        pass_row.pack(fill="x", pady=(0, 6))
        e_pass = tk.Entry(pass_row, textvariable=v_app_pass, show="•", font=("Segoe UI", 10), bg="#0E091C", fg="#F8FAFC", insertbackground=TURQUOISE, relief="flat", highlightthickness=1, highlightbackground=LINE)
        e_pass.pack(side="left", fill="x", expand=True, ipady=4)
        def toggle_pass():
            e_pass.config(show="" if e_pass.cget("show") else "•")
        ttk.Button(pass_row, text="Show", width=6, command=toggle_pass).pack(side="left", padx=(6, 0))

        tk.Label(s4, text="Generate an App Password at: myaccount.google.com/apppasswords", font=("Segoe UI", 9, "underline"), fg=TURQUOISE, bg="#18102E", cursor="hand2").pack(anchor="w", pady=(0, 8))

        gtest_row = tk.Frame(s4, bg="#18102E")
        gtest_row.pack(fill="x", pady=(0, 8))
        lbl_gtest = tk.Label(gtest_row, text="", font=("Segoe UI", 9, "bold"), bg="#18102E", fg=JUNGLE)
        
        def run_gmail_test():
            gm, pw = v_gmail.get().strip(), v_app_pass.get().strip()
            if not gm or not pw:
                lbl_gtest.config(text="Please enter both Gmail and App Password.", fg=WATERMELON)
                return
            lbl_gtest.config(text="Connecting to Gmail SMTP & IMAP ...", fg=TURQUOISE)
            def _th():
                err = bot.test_gmail(gm, pw)
                if not err:
                    lbl_gtest.config(text="✓ Connected! Drafts & Recruiter Reply tracking active.", fg=JUNGLE)
                else:
                    lbl_gtest.config(text=f"Connection note: {err[:55]}", fg=GOLD)
            threading.Thread(target=_th, daemon=True).start()

        ttk.Button(gtest_row, text="🔄 Test Gmail & IMAP Tracker", style="Big.TButton", command=run_gmail_test).pack(side="left")
        lbl_gtest.pack(side="left", padx=10)

        # --- NAVIGATION & FINISH ---
        cur_step = [0]
        
        nav_row = tk.Frame(main_frame, bg="#0A0714")
        nav_row.pack(fill="x", pady=(14, 0))
        
        btn_back = ttk.Button(nav_row, text="← Back")
        btn_next = ttk.Button(nav_row, text="Next: Connect AI Key →", style="Big.TButton")
        btn_back.pack(side="left")
        btn_next.pack(side="right")

        def show_step(idx):
            cur_step[0] = idx
            for i, f in enumerate(step_frames):
                if i == idx:
                    f.pack(fill="both", expand=True)
                    step_btns[i].configure(bg=TURQUOISE, fg="#0A0714")
                else:
                    f.pack_forget()
                    step_btns[i].configure(bg="#130D24", fg=MUTED)
            
            btn_back.configure(state="normal" if idx > 0 else "disabled")
            if idx == 0:
                btn_next.configure(text="Next: Connect AI Key →", style="Big.TButton")
            elif idx == 1:
                btn_next.configure(text="Next: Setup ATS Resume →", style="Big.TButton")
            elif idx == 2:
                btn_next.configure(text="Next: Connect Gmail →", style="Big.TButton")
            elif idx == 3:
                btn_next.configure(text="🎉 Finish Setup & Start Hunting!", style="Jungle.TButton")

        def on_next():
            if cur_step[0] < 3:
                show_step(cur_step[0] + 1)
            else:
                save_and_finish()

        def on_back():
            if cur_step[0] > 0:
                show_step(cur_step[0] - 1)

        def save_and_finish():
            c = read_config()
            if v_key.get().strip():
                c["gemini_api_key"] = v_key.get().strip()
            if v_model.get().strip():
                c["gemini_model"] = v_model.get().strip()
            if v_gmail.get().strip():
                c["gmail_address"] = v_gmail.get().strip()
            if v_app_pass.get().strip():
                c["gmail_app_password"] = v_app_pass.get().strip()
            c["onboarding_complete"] = True
            write_config(c)
            self.fill_models()
            self.show_profile()
            self.status_lbl.config(text="✓ Setup complete! Pasha Hunt is ready to hunt remote jobs.")
            win.destroy()
            if not self.jobs:
                self.find_jobs()

        btn_back.configure(command=on_back)
        btn_next.configure(command=on_next)
        show_step(0)
        win.grab_set()

    def first_run(self):
        cfg = read_config()
        if not cfg.get("onboarding_complete") or not has_key(cfg, "gemini_api_key"):
            self.onboarding_wizard(first=True)

    def settings(self):
        cfg = read_config()
        win = tk.Toplevel(self, background=DIALOG)
        win.title("Settings")
        win.transient(self)
        win.resizable(False, False)
        enable_dark_title_bar(win)
        frm = ttk.Frame(win, padding=16)
        frm.pack()
        vars_ = {}
        for i, (key, label, lo, hi, note) in enumerate(SETTINGS):
            ttk.Label(frm, text=label, font=("Segoe UI", 10, "bold")).grid(row=2 * i, column=0, sticky="w",
                                                                          pady=(8, 0))
            v = tk.StringVar(value=str(cfg.get(key, bot.DEFAULT_CONFIG[key])))
            ttk.Spinbox(frm, from_=lo, to=hi, textvariable=v, width=8).grid(row=2 * i, column=1, sticky="w",
                                                                            padx=(12, 0), pady=(8, 0))
            ttk.Label(frm, text=note, foreground=MUTED, wraplength=round(380 * self.scale)).grid(
                row=2 * i + 1, column=0, columnspan=2, sticky="w")
            vars_[key] = v

        def save():
            new = read_config()
            for key, label, lo, hi, _ in SETTINGS:
                try:
                    n = int(vars_[key].get().strip())
                except ValueError:
                    n = None
                if n is None or not lo <= n <= hi:
                    messagebox.showerror("Settings", f"{label}: type a whole number from {lo} to {hi}.", parent=win)
                    return
                new[key] = n
            write_config(new)
            win.destroy()
            self.status_lbl.config(text="Settings saved.")

        btns = ttk.Frame(frm)
        btns.grid(row=2 * len(SETTINGS), column=0, columnspan=2, pady=(16, 0), sticky="ew")
        ttk.Button(btns, text="🔑  Gmail & Gemini keys…",
                   command=lambda: (win.destroy(), self.keys())).pack(side="left")
        ttk.Button(btns, text="Save", style="Big.TButton", command=save).pack(side="right")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right", padx=6)
        win.grab_set()


if __name__ == "__main__":
    App().mainloop()
