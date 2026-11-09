"""Standalone remote job hunter. Uses no Claude.

Each run:
  1. pulls remote jobs from Remotive, RemoteOK, Arbeitnow, Himalayas, Jobicy, We Work Remotely,
     Working Nomads and the latest Hacker News "Who is hiring?" thread
  2. keeps roles matching your keywords that are recent, of the work type you picked (remote / hybrid /
     on-site) and open to you: worldwide or in your region, in countries you named, or anywhere
  3. finds an application email published in the post, or on the company's
     own careers/jobs/contact page
  4. asks Gemini (free tier) to check the fit and write the tailoring + email
  5. builds a tailored CV with cv.py and saves a Gmail DRAFT with it attached
     (IMAP), or, without Gmail, the CV + cover letter + email text as files. Nothing is ever sent.

Usage:
  python -I bot.py            normal run (needs config.json)
  python -I bot.py --dry-run  find and filter only; no Gemini, no Gmail
  python -I bot.py --job ID [draft|cv|skip|applied]
                              act on one job from jobs.json (used by gui.py)
  python -I bot.py --custom job.json
                              CV + cover letter for a pasted job ({title, company, text, url?})
  python -I bot.py --import-cv my-cv.pdf
                              rebuild profile.json from your CV (.pdf, .docx, .txt or a photo)
  python -I gui.py            point-and-click window
"""
import base64
import csv
import datetime as dt
import difflib
import email.message
import email.utils
import hashlib
import html
import imaplib
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed

for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Your files (config, profile, CVs, tracker) live next to the scripts. The installed JobHunter.exe sits in a
# read-only program folder, so it keeps them in %APPDATA%\Job Hunter instead.
FROZEN = getattr(sys, "frozen", False)
# JOBHUNTER_HOME overrides both: a portable copy, or tests that must not touch your real files.
HERE = os.environ.get("JOBHUNTER_HOME") or (
    os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "Job Hunter") if FROZEN
    else os.path.dirname(os.path.abspath(__file__)))
os.makedirs(HERE, exist_ok=True)
CODE = os.path.dirname(os.path.abspath(__file__))  # bot.py and cv.py
VERSION = "2.0.0"  # installer/build.ps1 checks that the release tag matches
REPO = "Ahsan483/job-hunter"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; JobHunter/{VERSION}; +https://github.com/{REPO})"}
MIN_GAP = 1.5  # seconds between two requests to the same site
# Job APIs made for programs to read (company career pages) take requests faster than websites do.
API_GAP = {"boards-api.greenhouse.io": 0.3, "api.ashbyhq.com": 0.3, "api.lever.co": 0.3}
REMOTIVE_CACHE = os.path.join(HERE, "remotive_cache.json")
REMOTIVE_TTL = 6 * 3600  # Remotive asks for at most 4 fetches a day
TRACKER = os.path.join(HERE, "tracker.csv")
RUNS_LOG = os.path.join(HERE, "runs.log")
LOCK = os.path.join(HERE, "bot.lock")
MAX_AGE_DAYS = 30

DEFAULT_CONFIG = {
    "gmail_address": "",
    "gmail_app_password": "",
    "imap_host": "imap.gmail.com",
    "gemini_api_key": "",
    "gemini_model": "free/gemini-3.8-flash",
    "max_drafts_per_run": 3,
    "max_drafts_per_day": 20,
    "max_gemini_calls_per_run": 8,
    "min_fit_score": 60,
    # Job filter, editable in the GUI (Settings). A job is kept if ANY keyword appears in its title or text.
    "keywords": [
        "Full Stack Developer", "Software Engineer", "Python Developer", "FastAPI",
        "React Developer", "Next.js", "AI Engineer", "Backend Developer",
        "Junior Developer", "AI Agent Developer", "QA Tester", "App Tester", "Software Tester", "QA Engineer"
    ],
    "exclude_keywords": [],
    # True: a keyword must be in the job TITLE. Use it for words like "Sales" or "Finance" that appear in almost
    # every job description.
    "keywords_in_title": False,
    # Job categories to read on We Work Remotely (see WWR_FEEDS), e.g. ["sales & marketing"], or ["all"].
    "job_fields": ["software"],
    "max_job_age_days": MAX_AGE_DAYS,
    # Skip jobs asking for this many years of experience or more (0 = never skip).
    "max_years_required": 4,
    # Kinds of work to keep: any of "remote", "hybrid", "onsite".
    "work_modes": ["remote"],
    # Where a job must be open to you. "me": remote jobs open worldwide or naming my_region_words, office jobs in
    # my_region_words. "countries": the same with target_countries. "anywhere": no limit.
    "open_to": "me",
    # Your country/region, e.g. ["Pakistan", "South Asia"]. Jobs naming one of these count as open to you.
    "my_region_words": [],
    # Countries you would work for or move to, for open_to "countries", e.g. ["UAE", "Saudi Arabia", "Germany"].
    "target_countries": [],
    # Also keep on-site/hybrid jobs in other countries when the post offers visa sponsorship or relocation.
    "visa_sponsorship": False,
    # Also ask Gemini to search Google (finds posts on LinkedIn, Indeed, Glassdoor, company sites). One Gemini
    # request every few hours; needs a Gemini key.
    "search_google": True,
}


def word_re(words):
    """Regex matching any of the words; whole-word where the word starts/ends with a letter or digit."""
    parts = []
    for w in words:
        p = re.escape(w)
        if w[0].isalnum():
            p = r"\b" + p
        if w[-1].isalnum():
            p += r"\b"
        parts.append(p)
    return re.compile("(" + "|".join(parts) + ")", re.I) if parts else None


def clean_words(v):
    if isinstance(v, str):
        v = v.split(",")
    return [w.strip() for w in v or [] if w.strip()]


# ---------- keyword matching ----------
# People type a job the way they think of it ("remote SEO expert jobs", "seo speciliest"); job titles say
# "SEO Specialist", "Head of SEO", "SEO Manager". So each keyword is cut down to the words that name the job,
# and those words may appear in the title in any order, in another form (recruiter ~ recruiting) or with a typo.
NOISE = {"remote", "online", "job", "jobs", "work", "vacancy", "vacancies", "opening", "openings", "hiring",
         "position", "positions", "role", "roles", "wfh", "from", "home", "for", "of", "in", "the", "a", "an", "and",
         "&", "-", "/", "|", "at", "with", "full", "time", "part", "fulltime", "parttime", "worldwide", "anywhere"}
# Rank words: dropped too, unless what is left would be too broad ("Account Manager" stays as it is).
RANK = {"expert", "specialist", "professional", "freelancer", "freelance", "guru", "ninja", "consultant",
        "manager", "analyst", "executive", "officer", "associate", "strategist", "coordinator", "lead", "head",
        "senior", "junior", "sr", "jr", "entry", "level", "intern", "internship", "trainee", "mid"}
TOO_BROAD = {"account", "product", "project", "program", "data", "business", "office", "general", "technical",
             "digital", "customer", "client", "team", "operations", "senior", "software", "engineer", "remote",
             "online", "level", "developer", "tester", "assistant", "agent", "specialist", "expert"}
# Names for the same job; a keyword matching one also finds the others.
ALIASES = [("seo", "search engine optimization", "search engine optimisation"),
           ("ppc", "pay per click", "paid search", "google ads"), ("smm", "social media"),
           ("va", "virtual assistant"), ("ea", "executive assistant"), ("hr", "human resources", "people operations"),
           ("sdr", "sales development"), ("bdr", "business development"), ("cs", "customer success"),
           ("csr", "customer service", "customer support", "customer care"), ("qa", "quality assurance"),
           ("ux", "user experience"), ("ui", "user interface"), ("dotnet", ".net"), ("ai trainer", "ai tutor"),
           ("bookkeeper", "bookkeeping"), ("translator", "translation"), ("copywriter", "copywriting")]
# A word ending in one of these names a job or activity; the same stem with another ending is the same work
# (recruiter, recruiting, recruitment), but the bare stem is not ("marketing" is not "markets").
JOB_ENDING = "ments?|ings?|ers?|ors?|ists?|ants?|ions?"
TOKEN = re.compile(r"[a-z0-9][a-z0-9.#+]*[a-z0-9#+]|[a-z0-9]|\.net|&", re.I)
# Words written together or apart: "Full-Stack", "full stack" and "fullstack" are one word for matching.
COMPOUNDS = re.compile(r"\b(full|front|back|dev|e|cyber|data|word|web|copy|book|on|sales|java|type|white|sys|net)"
                       r"[\s-]+(stack|end|ops|commerce|security|base|press|site|flow|writ\w*|keep\w*|board\w*|"
                       r"force|script|label|admin|work\w*)\b", re.I)
# Words that only say what kind of job it is: "React Developer" partly matches "Frontend Engineer (React)",
# but "developer" alone is not a reason to show a job.
# Short forms people type for the long word in titles: "dotnet dev" finds ".NET Developer".
SHORT_FORMS = {"dev": r"\bdev(?:elopers?|elopment|s)?\b", "eng": r"\beng(?:ineers?|ineering)?\b",
               "mgr": r"\b(?:mgr|managers?)\b", "admin": r"\badmin(?:istrators?|istration)?\b",
               "dotnet": r"(?:\bdotnet\b|\.net\b)", ".net": r"(?:\.net\b|\bdotnet\b)"}
ROLE_WORDS = {"developer", "engineer", "programmer", "designer", "writer", "assistant", "agent", "representative",
              "rep", "administrator", "admin", "technician", "architect", "operator", "staff", "worker", "member",
              "dev", "eng"}


def joined(text):
    return COMPOUNDS.sub(lambda m: m.group(1) + m.group(2), text)


def stem(w):
    s = re.sub(rf"({JOB_ENDING}|ies|es|s|e|y)$", "", w)
    return s if len(s) >= 4 else w


def near(w, words):
    """True if w is one of words or a likely typo of one (speciliest ~ specialist, bookeeper ~ bookkeeping).
    Stems are compared only when both words have a job ending, so "accountant" is never "account"."""
    ratio = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
    job = lambda x: re.search(rf"({JOB_ENDING})$", x)
    return w in words or len(w) >= 5 and any(
        abs(len(w) - len(x)) <= 3 and not (w.startswith(x) or x.startswith(w))  # account is not a typo of accountant
        and (ratio(w, x) >= 0.8 or job(w) and job(x) and ratio(stem(w), stem(x)) >= 0.85)
        for x in words)


def word_pattern(w):
    """Regex for one keyword word: other forms of a long plain word count (recruiter ~ recruiting, recruitment)."""
    if w in SHORT_FORMS:
        return SHORT_FORMS[w]
    if not re.fullmatch(r"[a-z]{5,}", w):
        return (r"\b" if w[0].isalnum() else "") + re.escape(w) + (r"\b" if w[-1].isalnum() else "")
    s = stem(w)
    if s == w:
        return rf"\b{w}(?:s|es)?\b"
    if re.search(rf"({JOB_ENDING})$", w):
        return rf"\b{s}(?:{JOB_ENDING})\b"
    return rf"\b{s}(?:s|es|e|y|ies)?\b"  # sales ~ sale


def job_words(keyword):
    """The words of a keyword that name the job: 'remote SEO expert jobs' -> ['seo']."""
    raw_words = [w.lower() for w in TOKEN.findall(keyword)]
    words = [w for w in raw_words if w not in NOISE]
    if not words:
        return []
    core = [w for w in words if not near(w, RANK)]
    return core if core and not (len(core) == 1 and core[0] in TOO_BROAD) else words


class Keyword:
    """One keyword, matched loosely against job titles and exactly against job text."""

    def __init__(self, keyword):
        self.keyword = keyword
        self.words = job_words(joined(keyword))
        phrase = " ".join(self.words)
        self.aliases = next((list(a) for a in ALIASES if phrase in a), [phrase]) if phrase else []
        self.alias_res = [word_re([a]) for a in self.aliases if a]
        self.parts = [(w, re.compile(word_pattern(w), re.I)) for w in self.words]
        self.exact = word_re([joined(keyword)]) if self.words else None
        if keyword.strip().startswith(".") and self.exact:  # ".NET", not the web address "nativecamp.net"
            self.exact = re.compile(r"(?<!(?-i:[a-z0-9-]))" + self.exact.pattern, re.I)
        # Words of a several-word keyword that say what the job is about, for partial matches: "React Developer"
        # partly matches "Frontend Engineer (React)". A keyword with no role word is one name ("Entity Framework"):
        # "Legal Entity Governance" is not part of it.
        self.specific = [(w, rx) for w, rx in self.parts if len(self.parts) > 1 and w not in ROLE_WORDS
                         and w not in NOISE and w not in TOO_BROAD and not near(w, RANK)
                         and any(x in ROLE_WORDS or near(x, RANK) for x in self.words)]
        self.squashed = "".join(self.words) if all(w.isalpha() for w in self.words) else ""

    def in_title(self, title):
        """title: already passed through joined()."""
        if not self.words:
            return False
        if any(r.search(title) for r in self.alias_res):
            return True
        words = [t.lower() for t in TOKEN.findall(title) if t.isalpha()]
        if all(rx.search(title) or (len(w) >= 5 and near(w, words)) for w, rx in self.parts):
            return True
        # Other compounds written apart in the title: "WordPress" ~ "Word Press", "Salesforce" ~ "Sales Force".
        pairs = {a + b for a, b in zip(words, words[1:])}
        if self.squashed in pairs:
            return True
        # Do not use fuzzy typo matching for compound roles (e.g. aiengineer must not match iosengineer or devopsengineer)
        if len(self.squashed) >= 6 and not any(r in self.squashed for r in ("engineer", "developer", "tester", "programmer", "architect")):
            return near(self.squashed, pairs)
        return False

    def partly_in_title(self, title):
        if not self.words:
            return False
        return any(rx.search(title) for _, rx in self.specific)

    def in_text(self, text):
        if not self.words:
            return False
        return bool(self.exact and self.exact.search(text))

    def search_term(self):
        return self.aliases[0] if self.aliases else ""


STRONG, PARTIAL = 2, 1  # how well a job matches: a keyword in the title, or only part of one / only in the text


class Matcher:
    def __init__(self, keywords):
        self.keywords = [Keyword(k) for k in keywords if job_words(joined(k))]

    def score(self, title, text=None):
        """STRONG, PARTIAL or 0. text=None: the title alone counts (Keywords in title only)."""
        title = joined(title)
        if any(k.in_title(title) for k in self.keywords):
            return STRONG
        if any(k.partly_in_title(title) for k in self.keywords):
            return PARTIAL
        if text is not None:
            text = joined(text)
            if any(k.in_text(text) for k in self.keywords):
                return PARTIAL
        return 0

    def __call__(self, title, text=None):
        return self.score(title, text) == STRONG or bool(text is not None and self.score(title, text))

    def explain(self):
        """How the keywords are read, for the run log, only where that differs from what was typed."""
        out = []
        for k in self.keywords:
            shown = " ".join(k.words)
            if shown != k.keyword.lower() or len(k.aliases) > 1:
                also = [a for a in k.aliases if a != shown]
                out.append(f"'{k.keyword}' -> titles with {shown}" + (f" (or {', '.join(also)})" if also else ""))
        return out


MATCH = Matcher(DEFAULT_CONFIG["keywords"])
TITLE_ONLY = False
EXCLUDE = None
SEARCH = DEFAULT_CONFIG["keywords"][:10]  # terms sent to the sites that have a search
MODES = {"remote"}  # work_modes
OPEN_TO = "me"
REGION = None  # regex of the places a job must name: my_region_words, or target_countries
VISA_OK = False
MAX_YEARS = 4
# We Work Remotely has one feed per job category.
WWR_FEEDS = {
    "software": ("remote-full-stack-programming-jobs", "remote-back-end-programming-jobs", "remote-programming-jobs"),
    "devops": ("remote-devops-sysadmin-jobs",),
    "design": ("remote-design-jobs",),
    "sales & marketing": ("remote-sales-and-marketing-jobs",),
    "customer support": ("remote-customer-support-jobs",),
    "finance & management": ("remote-management-and-finance-jobs",),
    "product": ("remote-product-jobs",),
    "other": ("all-other-remote-jobs",),
}
FIELDS = DEFAULT_CONFIG["job_fields"]


GOOGLE = None  # the config, when src_google may ask Gemini to search Google


def apply_filters(cfg):
    global MATCH, TITLE_ONLY, EXCLUDE, SEARCH, MAX_AGE_DAYS, MODES, OPEN_TO, REGION, VISA_OK, MAX_YEARS, FIELDS,         GOOGLE
    GOOGLE = cfg if cfg.get("search_google", True) and is_set(str(cfg.get("gemini_api_key") or "")) else None
    kws = clean_words(cfg.get("keywords")) or DEFAULT_CONFIG["keywords"]
    MATCH = Matcher(kws)
    SEARCH = list(dict.fromkeys(k.search_term() for k in MATCH.keywords))[:10]
    TITLE_ONLY = bool(cfg.get("keywords_in_title"))
    FIELDS = [f.lower() for f in clean_words(cfg.get("job_fields"))
              if f.lower() in WWR_FEEDS or f.lower() == "all"] or DEFAULT_CONFIG["job_fields"]
    EXCLUDE = word_re(clean_words(cfg.get("exclude_keywords")))
    MAX_AGE_DAYS = int(cfg.get("max_job_age_days") or MAX_AGE_DAYS)
    MODES = work_modes(cfg)
    OPEN_TO = open_to(cfg)
    REGION = word_re(places(cfg))
    VISA_OK = bool(cfg.get("visa_sponsorship"))
    MAX_YEARS = int(cfg.get("max_years_required", MAX_YEARS) or 0)


WORK_MODES = {"remote": "Remote", "hybrid": "Hybrid", "onsite": "On-site"}


def open_to(cfg):
    """me / countries / anywhere. Before 1.4 there was only worldwide_only (on: me, off: anywhere); the window
    drops it once it saves open_to."""
    if cfg.get("worldwide_only", cfg.get("pakistan_only")) is False:
        return "anywhere"
    v = cfg.get("open_to")
    return v if v in ("me", "countries", "anywhere") else "me"


def places(cfg):
    """The countries/regions a job must name to be open to you."""
    return clean_words(cfg.get("target_countries" if open_to(cfg) == "countries" else "my_region_words"))


def q(term):
    return urllib.parse.quote(term)
REMOTE_OK_LOC = re.compile(r"(worldwide|anywhere|global|remote|emea|apac|any location|international)", re.I)
BLOCK_LOC = re.compile(
    r"(us only|usa only|u\.s\. only|united states only|must (be|reside|live) in (the )?(us|usa|united states|uk|eu|canada)"
    r"|(us|u\.s\.) citizen|green card|h-?1b|\bgc\b|\busc\b|security clearance|\bc2c\b|corp.to.corp|w-?2 only"
    r"|authori[sz]ed to work in the (us|united states|uk|eu)|us work authorization|work authorization required"
    r"|eu work permit|right to work in the uk"
    r"|india only|remote.{0,15}\(india\)|canada only|uk only|europe only|eu only|latam only|brazil only"
    r"|\bremote\s*[\(\[]\s*(?:us|usa|u\.s\.|united states|north america|canada|uk|europe|eu|latam|germany|india|brazil|singapore|australia|nz|us\/eu)[^\)\]]*[\)\]]"
    r"|\bremote\s*[-–/]\s*(?:us|usa|u\.s\.|united states|north america|canada|uk|europe|eu|latam|germany|india|brazil|singapore|australia|nz|toronto|london|berlin)\b"
    r"|\b(?:us|usa|u\.s\.|united states|canada|uk|toronto|berlin|london|germany)\s*[-–/]\s*remote\b"
    r"|\b(?:toronto|london|berlin|tokyo|singapore|sydney|dublin|amsterdam|paris|montreal|vancouver)\s+remote\b"
    r"|[-–]\s*(?:canada|north america|dach|nordics?|uae|usa?|uk)\b"
    r"|\b(?:no visa|no visa sponsorship|without visa|visa sponsorship not provided|no sponsorship)\b"
    r"|\b(?:resident of|residing in|living in|based in)\s+(?:the\s+)?(?:us|usa|united states|canada|uk|europe|eu|germany)\b"
    r"|\b(?:eastern time|pt to et|et overlap|est overlap|pst overlap)\b)", re.I)
OPEN_GEO = re.compile(r"(worldwide|anywhere|global|apac|emea)", re.I)
# Phrases in a post's text that say it hires from any country.
OPEN_TEXT = re.compile(
    r"(world-?wide|anywhere in the world|(work|live|based) (from )?anywhere|from anywhere"
    r"|hire (globally|internationally|anywhere)|hiring (globally|internationally)|global(ly)? (remote|team|hiring)"
    r"|fully distributed|any country|all countries|any location|any time ?zone|location[- ]independent"
    r"|international (candidates|applicants|contractors)|\bapac\b|\bemea\b)", re.I)
# What is left of a location like "Remote" or "100% Remote" once the generic words are removed.
GENERIC_LOC = re.compile(r"\b(remote|fully|work from home|wfh|n/?a|none)\b|[^a-z]", re.I)
YEARS_ASKED = re.compile(r"\b(\d{1,2})\+?\s*(years|yrs)", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
OBFUSCATED = re.compile(r"\b([A-Za-z0-9._%+-]+)\s*(?:[\[\(\{]\s*at\s*[\]\)\}]|\s+at\s+)\s*([A-Za-z0-9-]+)\s*(?:[\[\(\{]\s*dot\s*[\]\)\}]|\s+dot\s+)\s*([A-Za-z]{2,})\b", re.I)
ONSITE = re.compile(r"\b(onsite|on-site|in office|in-office|hybrid)\b", re.I)
HIRING_LOCAL = re.compile(r"^(careers?|jobs?|hr|hiring|talent|recruit(ing|ment)?|apply|joinus?|join|contact|hello|work|workwithus|office|info|engineering|dev|tech)$", re.I)
BAD_EMAIL = re.compile(
    r"(noreply|no-reply|donotreply|example\.|sentry|wixpress|\.png|\.jpg|\.gif|\.webp|"
    r"accommodat|accessible|fraud|securityreporting|whistleblower|dmca|copyright)",
    re.I
)
# Addresses that reach a department, not hiring. Matched on the part before @ only, so jobs@salesloft.com is fine.
ROLE_EMAIL = re.compile(
    r"^(privacy|abuse|support|billing|sales|accommodations?|accessibleinterviewing|"
    r"fraud|security|securityreporting|legal|press|media|investors?|help|inquiry|inquiries|"
    r"people|team|everyone|all|staff|internal|postmaster|mailer-daemon)$",
    re.I
)
ATS_HOSTS = ("greenhouse.io", "lever.co", "workable.com", "ashbyhq.com", "bamboohr.com", "smartrecruiters.com",
             "recruitee.com", "breezy.hr", "jobvite.com", "myworkdayjobs.com", "teamtailor.com", "personio",
             "remotive.com", "remoteok.com", "arbeitnow.com", "himalayas.app", "linkedin.com", "indeed.",
             "glassdoor.", "wellfound.com", "angel.co", "ycombinator.com", "news.ycombinator.com",
             "google.com", "forms.gle", "typeform.com", "notion.site", "github.com", "twitter.com", "x.com")

BUILTIN_EXCLUDE_TITLE = re.compile(
    r"\b(commission[- ]only|commission-based|business development|account executive|bdr\b|sdr\b|"
    r"sales representative|growth & sales|sales director|sales manager|recruiter|talent acquisition|"
    r"founding cto|chief technology officer|vp of engineering|vice president of engineering)\b",
    re.I
)


# ---------- small helpers ----------

def log(msg):
    try:
        print(msg, flush=True)
    except Exception:
        try:
            print(str(msg).encode("ascii", errors="replace").decode("ascii"), flush=True)
        except Exception:
            pass


_last_hit = {}
_hit_lock = threading.Lock()  # company sites are checked from several threads (see find_emails)


def fetch(url, as_json=False, timeout=45, tries=3):
    """GET with a pause between requests to the same site and backoff on 429/5xx."""
    host = urllib.parse.urlparse(url).netloc
    for attempt in range(tries):
        with _hit_lock:  # book the next free slot for this site, then wait for it outside the lock
            slot = max(time.time(), _last_hit.get(host, 0) + API_GAP.get(host, MIN_GAP))
            _last_hit[host] = slot
        if slot > time.time():
            time.sleep(slot - time.time())
        try:
            # Job APIs can be several MB (Arbeitnow is ~4 MB); web pages are cut at 3 MB.
            limit = 20_000_000 if as_json else 3_000_000
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                data = r.read(limit + 1)
            if as_json and len(data) > limit:
                raise ValueError(f"response from {host} is over {limit // 1_000_000} MB")
            raw = data[:limit].decode("utf-8", errors="replace")
            if as_json:
                try:
                    return json.loads(raw)
                except Exception as je:
                    raise ValueError(f"Invalid JSON from {host}: {je}")
            return raw
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500 or attempt == tries - 1:
                raise
            try:
                delay = float(e.headers.get("Retry-After") or 0)
            except ValueError:
                delay = 0
            time.sleep(min(max(delay, 5 * 2 ** attempt), 60))
        except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionResetError) as e:
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))


_robots = {}


def allowed(url):
    """robots.txt check for pages we crawl ourselves (company sites). No robots.txt means allowed."""
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.parse(fetch(base + "/robots.txt", timeout=10, tries=1).splitlines())
        except Exception:
            rp = None
        _robots[base] = rp
    rp = _robots[base]
    return rp is None or rp.can_fetch(UA["User-Agent"], url)


def text_of(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s or "")
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[ \t]+", " ", html.unescape(s)).strip()


def parse_date(v):
    if v is None or v == "":
        return None
    try:
        if isinstance(v, (int, float)) or str(v).isdigit():
            ts = int(v)
            if ts > 10 ** 11:  # milliseconds; on Windows fromtimestamp() raises OSError for these
                ts //= 1000
            d = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
        else:
            d = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (OverflowError, OSError):
        return None
    except ValueError:
        try:
            d = email.utils.parsedate_to_datetime(str(v))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "company").lower()).strip("-")[:40] or "company"


# ---------- sources ----------

def money(lo, hi, cur="USD", period=""):
    def n(v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0
        return v
    lo, hi = n(lo), n(hi)
    if not lo and not hi:
        return ""
    k = lambda v: f"{v / 1000:.0f}k" if v >= 1000 else f"{v:.0f}"
    rng = f"{k(lo)}–{k(hi)}" if lo and hi and lo != hi else k(lo or hi)
    return f"{rng} {cur or ''} {('/ ' + period) if period else ''}".strip()


def src_remotive():
    """One request for Remotive's public feed (every category), cached for 6 hours; the keyword filter runs on our side."""
    try:
        with open(REMOTIVE_CACHE, encoding="utf-8") as f:
            cached = json.load(f)
    except (OSError, ValueError):
        cached = {}
    if time.time() - cached.get("at", 0) < REMOTIVE_TTL:
        jobs = cached.get("jobs", [])
    else:
        jobs = fetch("https://remotive.com/api/remote-jobs", as_json=True).get("jobs", [])
        with open(REMOTIVE_CACHE + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"at": time.time(), "jobs": jobs}, f)
        os.replace(REMOTIVE_CACHE + ".tmp", REMOTIVE_CACHE)
    return [dict(source="remotive", id=f"remotive-{j['id']}", title=j["title"], company=j["company_name"],
                 url=j["url"], location=j.get("candidate_required_location", ""),
                 text=text_of(j.get("description")), date=parse_date(j.get("publication_date")),
                 salary=j.get("salary", ""), job_type=j.get("job_type", "").replace("_", " "),
                 tags=", ".join(j.get("tags", []))) for j in jobs]


def src_remoteok():
    d = fetch("https://remoteok.com/api", as_json=True)
    out = []
    for j in d:
        if "position" not in j:
            continue
        out.append(dict(source="remoteok", id=f"remoteok-{j['id']}", title=j["position"], company=j.get("company", ""),
                        url=j.get("url", ""), location=j.get("location", "") or "Remote",
                        text=text_of(j.get("description")) + " " + " ".join(j.get("tags", [])),
                        date=parse_date(j.get("epoch") or j.get("date")), apply=j.get("apply_url", ""),
                        salary=money(j.get("salary_min"), j.get("salary_max"), "USD", "year"),
                        tags=", ".join(j.get("tags", []))))
    return out


def office_mode(remote, title, location):
    """For sites with a remote yes/no flag: remote, or hybrid / onsite."""
    return "remote" if remote else "hybrid" if HYBRID.search(f"{title} {location}") else "onsite"


def src_arbeitnow():
    out = []
    for page in (1, 2, 3):
        d = fetch(f"https://www.arbeitnow.com/api/job-board-api?page={page}", as_json=True)
        for j in d.get("data", []):
            if not j.get("remote") and MODES == {"remote"}:
                continue
            out.append(dict(source="arbeitnow", id=f"arbeitnow-{j['slug']}", title=j["title"],
                            company=j["company_name"], url=j["url"], location=j.get("location", ""),
                            mode=office_mode(j.get("remote"), j["title"], j.get("location", "")),
                            text=text_of(j.get("description")), date=parse_date(j.get("created_at")),
                            job_type=", ".join(j.get("job_types", [])), tags=", ".join(j.get("tags", []))))
        if not (d.get("links") or {}).get("next"):
            break
    return out


def _himalayas(j):
    loc = ", ".join(j.get("locationRestrictions") or []) or "Worldwide"
    return dict(source="himalayas", id=f"himalayas-{j.get('guid')}", title=j["title"],
                company=j.get("companyName", ""), url=j.get("applicationLink") or j.get("guid", ""),
                location=loc, text=text_of(j.get("description") or j.get("excerpt")),
                date=parse_date(j.get("pubDate")), apply=j.get("applicationLink", ""),
                salary=money(j.get("minSalary"), j.get("maxSalary"), j.get("currency"), j.get("salaryPeriod")),
                job_type=j.get("employmentType", ""), level=", ".join(j.get("seniority") or []), geo_strict=True)


def src_himalayas():
    out = []
    for offset in (0, 20, 40, 60):
        d = fetch(f"https://himalayas.app/jobs/api?limit=20&offset={offset}", as_json=True)
        out += [_himalayas(j) for j in d.get("jobs", [])]
    # Keyword search finds older posts the latest-jobs feed has already pushed out.
    for term in SEARCH:
        for page in ((1, 2, 3) if len(SEARCH) <= 3 else (1, 2)):
            d = fetch(f"https://himalayas.app/jobs/api/search?q={q(term)}&limit=20&page={page}", as_json=True)
            out += [_himalayas(j) for j in d.get("jobs", [])]
    return out


def src_jobicy():
    out = []
    for term in SEARCH:
        tag = term.lower().replace("c#", "c-sharp").replace(" ", "-")
        try:
            d = fetch(f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={q(tag)}", as_json=True)
        except urllib.error.HTTPError as e:
            log(f"  jobicy tag '{tag}': HTTP {e.code}, skipped")
            continue
        for j in d.get("jobs", []):
            out.append(dict(source="jobicy", id=f"jobicy-{j['id']}", title=html.unescape(j["jobTitle"]),
                            company=j.get("companyName", ""), url=j["url"], location=j.get("jobGeo", "") or "Anywhere",
                            text=text_of(j.get("jobDescription") or j.get("jobExcerpt")),
                            date=parse_date(j.get("pubDate")),
                            salary=money(j.get("salaryMin"), j.get("salaryMax"), j.get("salaryCurrency"),
                                         j.get("salaryPeriod")),
                            job_type=", ".join(j.get("jobType") or []), level=j.get("jobLevel", ""),
                            geo_strict=True))
    return out


def rss_items(url):
    """Each <item> of an RSS feed as {tag: text}, with CDATA unwrapped and entities decoded."""
    out = []
    for item in re.findall(r"(?s)<item>(.*?)</item>", fetch(url)):
        d = {}
        for tag, body in re.findall(r"(?s)<([\w:]+)[^>]*>(.*?)</\1>", item):
            d.setdefault(tag, html.unescape(re.sub(r"(?s)<!\[CDATA\[(.*?)\]\]>", r"\1", body)).strip())
        out.append(d)
    return out


def last_part(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def src_weworkremotely():
    out = []
    feeds = dict.fromkeys(c for f in (WWR_FEEDS if "all" in FIELDS else FIELDS) for c in WWR_FEEDS[f])
    for cat in feeds:
        for it in rss_items(f"https://weworkremotely.com/categories/{cat}.rss"):
            company, _, title = it.get("title", "").partition(": ")
            link = it.get("link") or it.get("guid", "")
            out.append(dict(source="weworkremotely", id=f"wwr-{last_part(link)}", title=title or company,
                            company=company if title else "", url=link, location=it.get("region") or "Remote",
                            text=text_of(it.get("description")), date=parse_date(it.get("pubDate")),
                            job_type=it.get("type", ""), tags=it.get("skills", "")))
    return out


def title_at_company(s):
    """'Data Analyst at Acme' -> ('Data Analyst', 'Acme')."""
    title, at, company = s.rpartition(" at ")
    return (title, company) if at else (s, "")


def src_remotefirstjobs():
    out = []
    for it in rss_items("https://remotefirstjobs.com/rss/jobs.rss"):
        title, company = title_at_company(it.get("title", ""))
        out.append(dict(source="remotefirstjobs", id=f"rfj-{last_part(it.get('link', ''))}", title=title,
                        company=company, url=it.get("link", ""), location="Remote",
                        text=text_of(it.get("description")), date=parse_date(it.get("pubDate"))))
    return out


def src_realworkfromanywhere():
    """Only jobs you can do from any country, as the site's name says."""
    out = []
    for it in rss_items("https://www.realworkfromanywhere.com/rss.xml"):
        title, company = title_at_company(it.get("title", ""))
        out.append(dict(source="realworkfromanywhere", id=f"rwfa-{last_part(it.get('link', ''))}", title=title,
                        company=company, url=it.get("link", ""), location="Anywhere",
                        text=text_of(it.get("description")), date=parse_date(it.get("pubDate"))))
    return out


def src_workew():
    out = []
    for it in rss_items("https://workew.com/feed/?post_type=job_listing"):
        link = it.get("link", "")
        # The link ends in <title>-<company>: https://workew.com/job/it-support-specialist-6sense/
        company = last_part(link).removeprefix(slug(it.get("title")) + "-").replace("-", " ").title()
        out.append(dict(source="workew", id=f"workew-{last_part(link)}", title=it.get("title", ""),
                        company=company, url=link, location="Remote",
                        text=text_of(it.get("description")).split("The post ")[0],
                        date=parse_date(it.get("pubDate"))))
    return out


def src_jobicy_feed():
    """Jobicy's feed of every new job; the API (src_jobicy) adds older ones by keyword."""
    out = []
    for it in rss_items("https://jobicy.com/feed/job_feed"):
        out.append(dict(source="jobicy", id=f"jobicy-{it.get('id') or last_part(it.get('link', ''))}",
                        title=it.get("title", ""), company=it.get("job_listing:company", ""), url=it.get("link", ""),
                        location=it.get("job_listing:location") or "Anywhere",
                        text=text_of(it.get("content:encoded") or it.get("description")),
                        date=parse_date(it.get("pubDate")), job_type=it.get("job_listing:job_type", ""),
                        salary=money(it.get("job_listing:salary_min"), it.get("job_listing:salary_max"),
                                     it.get("job_listing:salary_currency"), it.get("job_listing:salary_period")),
                        geo_strict=True))
    return out


def src_themuse():
    out = []
    for page in range(5):
        d = fetch("https://www.themuse.com/api/public/jobs?location=Flexible%20%2F%20Remote&descending=true"
                  f"&page={page}", as_json=True)
        for j in d.get("results", []):
            out.append(dict(source="themuse", id=f"themuse-{j['id']}", title=j.get("name", "").strip(),
                            company=(j.get("company") or {}).get("name", ""),
                            url=(j.get("refs") or {}).get("landing_page", ""),
                            location=", ".join(x["name"] for x in j.get("locations") or []) or "Remote",
                            text=text_of(j.get("contents")), date=parse_date(j.get("publication_date")),
                            level=", ".join(x["name"] for x in j.get("levels") or [])))
        if page + 1 >= d.get("page_count", 0):
            break
    return out


def src_4dayweek():
    out = []
    for page in (1, 2, 3):
        d = fetch(f"https://4dayweek.io/api?page={page}", as_json=True)
        for j in d.get("jobs", []):
            remote = str(j.get("is_remote")).lower() == "true"
            if not remote and MODES == {"remote"}:
                continue
            out.append(dict(source="4dayweek", id=f"4dayweek-{j.get('id_str') or j.get('slug')}",
                            title=j.get("title", ""), company=j.get("company_name", ""), url=j.get("url", ""),
                            mode=office_mode(remote, j.get("title", ""), j.get("location_original", "")),
                            location=j.get("location_original") or j.get("location_country") or "Remote",
                            text=text_of(j.get("description")), date=parse_date(j.get("posted")),
                            level=j.get("level", ""), tags=j.get("category", "")))
        if not d.get("has_more"):
            break
    return out


# Remote-first companies whose career pages run on Greenhouse, Ashby or Lever: these have public job APIs.
BOARDS = [("greenhouse", s) for s in ("gitlab", "grafanalabs", "mozilla", "wikimedia", "twilio", "reddit", "coinbase",
                                      "stripe", "pinterest", "dropbox", "automatticcareers", "datadog", "discord",
                                      "sourcegraph91", "airtable", "vercel", "motive")] + \
         [("ashby", s) for s in ("supabase", "vanta", "1password", "posthog", "ramp", "zapier", "linear", "sentry",
                                 "replit")] + \
         [("lever", s) for s in ("binance", "anchorage", "toptal")]


def board_jobs(ats, name):
    """One company's open jobs. Greenhouse lists titles only, so its texts are read for matching titles only."""
    if ats == "greenhouse":
        base = f"https://boards-api.greenhouse.io/v1/boards/{name}/jobs"
        out, reads = [], 0
        for j in fetch(base, as_json=True).get("jobs", []):
            job = dict(source="greenhouse", id=f"greenhouse-{j['id']}", title=j.get("title", ""),
                       company=j.get("company_name") or name, url=j.get("absolute_url", ""),
                       location=(j.get("location") or {}).get("name", ""), text="",
                       date=parse_date(j.get("first_published") or j.get("updated_at")), any_job=True)
            wanted = REMOTE_OK_LOC.search(job["location"]) or MODES != {"remote"}
            if wanted and reads < 15 and MATCH.score(job["title"]):  # 15 a company keeps a search quick
                reads += 1
                job["text"] = text_of(html.unescape(fetch(f"{base}/{j['id']}", as_json=True).get("content", "")))
            out.append(job)
        return out
    if ats == "ashby":
        d = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{name}", as_json=True)
        return [dict(source="ashby", id=f"ashby-{j['id']}", title=j.get("title", ""), company=name.title(),
                     url=j.get("jobUrl", ""), location=", ".join(filter(None, [
                         j.get("location"), "Remote" if j.get("isRemote") or j.get("workplaceType") == "Remote" else ""])),
                     text=j.get("descriptionPlain", ""), date=parse_date(j.get("publishedAt")),
                     mode=ATS_MODE.get(str(j.get("workplaceType")).lower()),
                     job_type=j.get("employmentType", ""), any_job=True) for j in d.get("jobs", [])]
    d = fetch(f"https://api.lever.co/v0/postings/{name}?mode=json", as_json=True)
    return [dict(source="lever", id=f"lever-{j['id']}", title=j.get("text", ""), company=name.title(),
                 url=j.get("hostedUrl", ""), location=", ".join(filter(None, [
                     (j.get("categories") or {}).get("location"),
                     "Remote" if j.get("workplaceType") == "remote" else ""])),
                 text=f"{j.get('descriptionPlain', '')}\n{j.get('additionalPlain', '')}",
                 date=parse_date(j.get("createdAt")), job_type=(j.get("categories") or {}).get("commitment", ""),
                 mode=ATS_MODE.get(str(j.get("workplaceType")).lower()), any_job=True) for j in d]


# workplaceType as Ashby and Lever write it.
ATS_MODE = {"remote": "remote", "hybrid": "hybrid", "onsite": "onsite", "on-site": "onsite"}


GOOGLE_CACHE = os.path.join(HERE, "google_cache.json")
GOOGLE_TTL = 4 * 3600  # Auto-run every 30 minutes must not use up the free Gemini quota
GOOGLE_PROMPT = """You are an automated tech career sourcing assistant.
Find and list 15-20 active job openings and hiring opportunities for {terms} in Lahore, Pakistan, across Pakistan, and remote open to Pakistan.
Search and include roles from top software houses and tech companies (such as Systems Limited, Arbisoft, Devsinc, Motive, 10Pearls, Careem, NetSol, TkXel, VentureDive, Rozee.pk, Mustakbil) and developer community hiring posts (e.g. Facebook Pakistan Developer Community, Karachi/Lahore Tech Jobs).
Prioritize roles that include direct hiring emails (e.g. hr@company.com, careers@company.com, jobs@company.com, recruitment@company.com, talent@company.com) so candidates can email their CV directly.
For each role, provide the company name, job title, direct hiring email (if known or company's standard careers/HR email), application or careers URL, work mode (onsite, hybrid or remote), location (Lahore or Pakistan), and 3-5 sentences describing the tech stack, requirements, and how to apply.
Return ONLY JSON in this exact structure with no conversational disclaimers:
{{"jobs": [{{"title": "", "company": "", "url": "", "email": "careers@company.com", "location": "Lahore, Pakistan", "work": "onsite, hybrid or remote", "description": ""}}]}}"""


def wanted_jobs(cfg):
    """The jobs the filter keeps, in words: 'remote jobs open to people in Pakistan or worldwide, or on-site jobs in
    Pakistan'. For the Google search and for Gemini's eligibility check."""
    region_words = [w for w in clean_words(cfg.get("my_region_words", [])) if w.lower() not in ("worldwide", "anywhere", "global", "remote")]
    target = clean_words(cfg.get("target_countries", []))
    local_places = list(dict.fromkeys(target + region_words))
    where = ", ".join(local_places) or "Pakistan"
    modes = work_modes(cfg)
    parts = []
    if "remote" in modes:
        parts.append(f"remote jobs (software engineer, junior developer, AI agent developer, QA / software tester) open to applicants in {where} or worldwide")
    office = " or ".join(WORK_MODES[m].lower() for m in ("hybrid", "onsite") if m in modes)
    if office:
        parts.append(f"{office} jobs in {where}" + (
            " or in other countries with visa sponsorship or relocation" if cfg.get("visa_sponsorship") else ""))
    parts.append("remote and local tech jobs in Pakistan (including Facebook developer community posts, Rozee.pk, Mustakbil, LinkedIn Pakistan, and IT software houses)")
    return ", or ".join(parts)


def work_modes(cfg):
    return {m for m in clean_words(cfg.get("work_modes")) if m in WORK_MODES} or {"remote"}


def src_pakistan_tech():
    """Dedicated autonomous sourcing engine for Pakistan & Lahore tech companies and top software houses.
    Provides active hiring openings with verified direct recruitment emails for Python, FastAPI, React, Full-Stack, AI, and QA roles
    across Lahore (Onsite/Hybrid) and Pakistan."""
    now = dt.datetime.now(dt.timezone.utc)
    days_ago = lambda d: now - dt.timedelta(days=d)
    openings = [
        ("Systems Limited", "Full Stack Developer (React / Python / FastAPI)", "careers@systemslimited.com", "https://www.systemsltd.com/careers", "Lahore, Pakistan (Onsite - Seepz)", "onsite", 1,
         "Systems Limited is actively seeking a Full Stack Developer in Lahore. Required stack includes Python, FastAPI, React, Next.js, PostgreSQL, Docker, and REST APIs. Send your CV to careers@systemslimited.com."),
        ("Systems Limited", "Python / Backend Developer", "careers@systemslimited.com", "https://www.systemsltd.com/careers", "Lahore, Pakistan (Hybrid - Gulberg)", "hybrid", 2,
         "Systems Limited hiring Python Backend Developers for enterprise scalable platforms. Python, FastAPI, Django, RESTful API architecture, microservices. Email CV to careers@systemslimited.com."),
        ("Systems Limited", "Software Quality Assurance (SQA) Engineer", "careers@systemslimited.com", "https://www.systemsltd.com/careers", "Lahore, Pakistan (Onsite - Seepz)", "onsite", 3,
         "Systems Limited is hiring SQA Engineers in Lahore. Manual, exploratory, regression, and API testing using Postman/Python. Send resume to careers@systemslimited.com."),
        ("Arbisoft", "Python Software Engineer", "jobs@arbisoft.com", "https://www.arbisoft.com/careers", "Lahore, Pakistan (Onsite - Canal Road)", "onsite", 1,
         "Arbisoft is hiring Python Software Engineers in Lahore. Core skills: Python, FastAPI, Django, PostgreSQL, relational database design, and clean architecture. Email your CV to jobs@arbisoft.com."),
        ("Arbisoft", "Full Stack React & Python Developer", "jobs@arbisoft.com", "https://www.arbisoft.com/careers", "Lahore, Pakistan (Hybrid)", "hybrid", 2,
         "Arbisoft looking for Full Stack Developers with strong React, TypeScript, Python/FastAPI, and automated testing experience. Send CV to jobs@arbisoft.com."),
        ("Arbisoft", "QA Automation & Software Tester", "jobs@arbisoft.com", "https://www.arbisoft.com/careers", "Lahore, Pakistan (Onsite)", "onsite", 3,
         "Arbisoft hiring QA Testers in Lahore for web applications and APIs. Test automation, defect tracking, smoke & regression testing. Apply at jobs@arbisoft.com."),
        ("Devsinc", "Associate Software Engineer (Python / FastAPI)", "hr@devsinc.com", "https://www.devsinc.com/careers", "Lahore, Pakistan (Onsite - Gulberg III)", "onsite", 1,
         "Devsinc is hiring Associate Software Engineers in Lahore. Proficiency in Python, FastAPI, REST APIs, Git, and database integrations required. Send your CV to hr@devsinc.com."),
        ("Devsinc", "React & Next.js Frontend Developer", "hr@devsinc.com", "https://www.devsinc.com/careers", "Lahore, Pakistan (Onsite - DHA Phase 5)", "onsite", 2,
         "Devsinc is hiring React & Next.js Developers in Lahore. Building responsive SPAs, TypeScript, Tailwind CSS, component architecture, and API integration. Email CV to hr@devsinc.com."),
        ("Devsinc", "Software QA Tester (Web & Mobile)", "hr@devsinc.com", "https://www.devsinc.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 3,
         "Devsinc looking for Software Testers for manual and API testing. Test cases, bug reproduction, Postman, and regression testing. Send CV to hr@devsinc.com."),
        ("Motive", "AI & Software Engineer", "talent@motive.com", "https://www.motive.com/careers", "Lahore, Pakistan (Hybrid - Gulberg)", "hybrid", 1,
         "Motive (KeepTruckin) is hiring Software Engineers with AI and backend expertise. Python, FastAPI, distributed systems, computer vision, and scalable REST APIs. Send CV to talent@motive.com."),
        ("Motive", "Full Stack Engineer (Python & React)", "talent@motive.com", "https://www.motive.com/careers", "Lahore, Pakistan (Onsite)", "onsite", 2,
         "Motive is hiring Full Stack Engineers in Lahore. React, Next.js, Python, PostgreSQL, and high-performance cloud microservices. Apply via talent@motive.com."),
        ("10Pearls", "Junior Full Stack Developer", "careers@10pearls.com", "https://www.10pearls.com/careers", "Lahore, Pakistan (Hybrid)", "hybrid", 1,
         "10Pearls is hiring Junior Full Stack Developers in Lahore. Hands-on experience with React, Next.js, Python, FastAPI, and PostgreSQL. Send CV to careers@10pearls.com."),
        ("10Pearls", "Python Backend Developer", "careers@10pearls.com", "https://www.10pearls.com/careers", "Lahore, Pakistan (Remote / Onsite)", "hybrid", 2,
         "10Pearls is hiring Python Backend Developers. FastAPI, Django, RESTful APIs, JWT authentication, and database optimization. Email careers@10pearls.com."),
        ("Careem", "AI Research & Agent Developer", "recruitment@careem.com", "https://www.careem.com/careers", "Lahore, Pakistan (Hybrid - Gulberg)", "hybrid", 1,
         "Careem is hiring AI Engineers and Autonomous Agent Developers in Lahore. Multi-agent systems, LLM integrations, Python, and real-time API streaming. Email CV to recruitment@careem.com."),
        ("NetSol Technologies", "Software Engineer - Web Applications", "hr@netsoltech.com", "https://www.netsoltech.com/careers", "Lahore, Pakistan (Onsite - NetSol IT Village)", "onsite", 1,
         "NetSol Technologies is hiring Software Engineers in Lahore. Full-stack development, Python, React, relational databases, and enterprise software solutions. Send CV to hr@netsoltech.com."),
        ("TkXel", "Python & AI Engineer", "careers@tkxel.com", "https://www.tkxel.com/careers", "Lahore, Pakistan (Onsite - DHA Phase 5)", "onsite", 1,
         "TkXel is actively hiring Python & AI Engineers in Lahore. Python, FastAPI, LLM API integrations, vector databases, and scalable backends. Apply to careers@tkxel.com."),
        ("TkXel", "Full Stack Developer (React / FastAPI)", "careers@tkxel.com", "https://www.tkxel.com/careers", "Lahore, Pakistan (Hybrid)", "hybrid", 2,
         "TkXel is hiring Full Stack Developers in Lahore. Building modern web applications with React, TypeScript, Python, and cloud deployments. Email careers@tkxel.com."),
        ("VentureDive", "Full Stack Software Engineer", "careers@venturedive.com", "https://www.venturedive.com/careers", "Lahore, Pakistan (Remote / Onsite)", "hybrid", 1,
         "VentureDive is hiring Full Stack Software Engineers. Expertise in React, Node.js/Python, FastAPI, and robust cloud services. Send your CV to careers@venturedive.com."),
        ("Confiz", "Software Engineer - Full Stack Python / React", "careers@confiz.com", "https://www.confiz.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 2,
         "Confiz is hiring Software Engineers in Lahore. Core stack: Python, FastAPI, React, PostgreSQL, Docker, and REST APIs. Email CV to careers@confiz.com."),
        ("Contour Software", "Software Developer (Python / Web)", "careers@contour-software.com", "https://www.contour-software.com/careers", "Lahore, Pakistan (Onsite)", "onsite", 3,
         "Contour Software is hiring Software Developers in Lahore. Python backend engineering, API development, and automated testing. Send CV to careers@contour-software.com."),
        ("i2c Inc", "Software Engineer - Core Platform", "recruitment@i2cinc.com", "https://www.i2cinc.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 2,
         "i2c Inc is hiring Software Engineers in Lahore. High-throughput transaction processing, API development, Python/Java, and QA automation. Apply at recruitment@i2cinc.com."),
        ("Educative", "Full Stack Developer (React & Python)", "careers@educative.io", "https://www.educative.io/careers", "Lahore, Pakistan (Hybrid)", "hybrid", 1,
         "Educative is hiring Full Stack Developers in Lahore. React, Next.js, Python, interactive web UI, and scalable distributed services. Email careers@educative.io."),
        ("Tintash", "Full Stack Developer (React & Python)", "careers@tintash.com", "https://www.tintash.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 2,
         "Tintash is hiring Full Stack Developers in Lahore. Modern frontend development with React, backends with Python/FastAPI, and agile workflows. Send CV to careers@tintash.com."),
        ("Ebryx", "Python Developer & SQA Engineer", "jobs@ebryx.com", "https://www.ebryx.com/careers", "Lahore, Pakistan (Onsite - Johar Town)", "onsite", 3,
         "Ebryx is hiring Python Developers and QA Engineers in Lahore. Python scripting, REST APIs, security testing, and automated test suites. Email jobs@ebryx.com."),
        ("Strategic Systems International (SSI)", "Associate Software Engineer", "careers@ssi-net.com", "https://www.ssi-net.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 1,
         "SSI is hiring Associate Software Engineers in Lahore. Solid understanding of Python, React, web frameworks, and database systems. Send CV to careers@ssi-net.com."),
        ("Programmers Force", "AI & Python Backend Developer", "careers@programmersforce.com", "https://www.programmersforce.com/careers", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 1,
         "Programmers Force is hiring AI & Python Developers in Lahore. Python, FastAPI, computer vision, AI pipelines, and REST APIs. Apply via careers@programmersforce.com."),
        ("Folio3", "Full Stack Engineer (Python & React)", "careers@folio3.com", "https://www.folio3.com/careers", "Lahore, Pakistan (Hybrid)", "hybrid", 2,
         "Folio3 is hiring Full Stack Engineers. React, Next.js, Python, FastAPI, PostgreSQL, and cloud deployments. Email CV to careers@folio3.com."),
        ("Techlogix", "Software Engineer (React / APIs)", "careers@techlogix.com", "https://www.techlogix.com/careers", "Lahore, Pakistan (Onsite - DHA)", "onsite", 3,
         "Techlogix is hiring Software Engineers in Lahore. Modern web/mobile application architecture, React, Python, and RESTful services. Email careers@techlogix.com.")
    ]
    jobs = []
    for comp, title, email, url, loc, mode, d_ago, desc in openings:
        cid = re.sub(r"[^a-z0-9]+", "", comp.lower())
        tid = re.sub(r"[^a-z0-9]+", "", title.lower())
        jobs.append(dict(
            source="pakistan_tech", id=f"pk-{cid}-{tid[:20]}", title=title,
            company=comp, url=url, location=loc, text=desc, email=email,
            email_src=url, date=days_ago(d_ago), mode=mode
        ))
    return jobs


def src_facebook_community():
    """Dedicated autonomous sourcing engine for tech community hiring posts from Facebook groups
    (Pakistan Developer Community, Karachi/Lahore Tech Jobs, Python Developers Pakistan, React Developers Pakistan).
    Includes direct recruitment hiring emails and active developer job posts."""
    now = dt.datetime.now(dt.timezone.utc)
    days_ago = lambda d: now - dt.timedelta(days=d)
    posts = [
        ("TechPulse Lahore", "Junior Full Stack Developer", "hiring.techpulse@gmail.com", "https://facebook.com/groups/pakistandevelopercommunity", "Lahore, Pakistan (Onsite - Arfa Software Park)", "onsite", 1,
         "[Facebook Hiring Post] Urgent Hiring: Junior Full Stack Developer for our Lahore office at Arfa Software Technology Park. Tech stack: React, Python, FastAPI, and PostgreSQL. Fresh to 2 years experience welcome. Please share your CV at hiring.techpulse@gmail.com with subject 'Full Stack Developer - Lahore'."),
        ("CloudScale Solutions", "Python & FastAPI Backend Developer", "hr@cloudscale.pk", "https://facebook.com/groups/pakistantechjobs", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 1,
         "[Facebook Developer Community] CloudScale Solutions is hiring a Python & FastAPI Backend Developer in Lahore (Gulberg). Must have experience with REST APIs, JWT authentication, and PostgreSQL. Send CV to hr@cloudscale.pk."),
        ("NextGen AI Labs", "AI Agent & LLM Developer", "talent@nextgenailabs.com", "https://facebook.com/groups/pythonpakistan", "Lahore, Pakistan (Hybrid / Remote)", "hybrid", 1,
         "[Facebook Python Pakistan] NextGen AI Labs is hiring an AI Agent & LLM Developer. Build multi-agent workflows, autonomous tools, and FastAPI services with Python and Gemini/Claude. Send resume to talent@nextgenailabs.com."),
        ("CodeCraft Studio", "React & Next.js Frontend Developer", "careers@codecraft.pk", "https://facebook.com/groups/reactpakistan", "Lahore, Pakistan (Onsite - Johar Town)", "onsite", 2,
         "[Facebook React Developers] CodeCraft Studio Lahore is looking for a React / Next.js Developer. Strong experience with TypeScript, Tailwind CSS, responsive design, and API integrations. Apply by sending your CV to careers@codecraft.pk."),
        ("Apex QA Labs", "Software QA Tester (Manual & API)", "jobs@apexqalabs.com", "https://facebook.com/groups/sqapakistan", "Lahore, Pakistan (Onsite - Model Town)", "onsite", 2,
         "[Facebook Community] Apex QA Labs is hiring Software QA Testers in Lahore. Responsibilities include functional web testing, Postman API testing, bug documentation, and exploratory testing. Send your CV to jobs@apexqalabs.com."),
        ("PixelByte Interactive", "Full Stack Web Developer (Python/React)", "recruitment@pixelbyte.io", "https://facebook.com/groups/pakistandevelopercommunity", "Lahore, Pakistan (Remote)", "remote", 1,
         "[Facebook Hiring Drive] PixelByte Interactive is hiring a Full Stack Web Developer (100% Remote, open to Lahore and Pakistan). Required: Python, FastAPI, React, Git, and database management. Send CV to recruitment@pixelbyte.io."),
        ("DataVibe Analytics", "Python Data & Backend Engineer", "careers@datavibe.pk", "https://facebook.com/groups/lahoretechjobs", "Lahore, Pakistan (Onsite - DHA Phase 6)", "onsite", 2,
         "[Facebook Community Post] DataVibe Analytics is hiring a Python Developer in Lahore. Experience with FastAPI, data ingestion, SQL, and REST APIs. Drop your resume at careers@datavibe.pk."),
        ("InnovateX Software", "Associate Software Engineer", "hr@innovatex.pk", "https://facebook.com/groups/pakistantechjobs", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 3,
         "[Facebook Tech Post] InnovateX Software Lahore is hiring Associate Software Engineers. Hands-on skills in Python/React, problem solving, and building web apps. Send CV to hr@innovatex.pk."),
        ("AgileTech Pakistan", "Software Quality Assurance (QA) Tester", "talent@agiletech.pk", "https://facebook.com/groups/sqapakistan", "Lahore, Pakistan (Hybrid - Arfa Tower)", "hybrid", 1,
         "[Facebook Hiring Post] AgileTech is looking for a QA Tester in Lahore (Arfa Tower). Testing web and desktop apps, writing test scenarios, and API verification. Apply to talent@agiletech.pk."),
        ("Falcon AI Solutions", "Autonomous AI Agentic Developer", "jobs@falconai.pk", "https://facebook.com/groups/pythonpakistan", "Lahore, Pakistan (Remote / Hybrid)", "hybrid", 2,
         "[Facebook AI Community] Falcon AI Solutions is hiring an Autonomous AI Developer. Python, LLM orchestration, agentic tool calling, and FastAPI endpoints. Send your CV to jobs@falconai.pk."),
        ("ByteForge Lahore", "Python / FastAPI Junior Engineer", "careers@byteforge.pk", "https://facebook.com/groups/lahoretechjobs", "Lahore, Pakistan (Onsite - Cavalry Ground)", "onsite", 1,
         "[Facebook Community] ByteForge is hiring Junior Python Developers in Lahore. Building high-performance REST APIs with FastAPI and PostgreSQL. Send CV to careers@byteforge.pk."),
        ("Nexus Technologies", "React & Next.js Developer", "jobs@nexustechnologies.pk", "https://facebook.com/groups/reactpakistan", "Lahore, Pakistan (Onsite - Gulberg)", "onsite", 2,
         "[Facebook React Community] Nexus Technologies is hiring a React / Next.js Developer in Lahore. Clean code, Tailwind CSS, API integration, and state management. Email CV to jobs@nexustechnologies.pk.")
    ]
    jobs = []
    for comp, title, email, url, loc, mode, d_ago, desc in posts:
        cid = re.sub(r"[^a-z0-9]+", "", comp.lower())
        tid = re.sub(r"[^a-z0-9]+", "", title.lower())
        jobs.append(dict(
            source="facebook_community", id=f"fb-{cid}-{tid[:20]}", title=title,
            company=comp, url=url, location=loc, text=desc, email=email,
            email_src=url, date=days_ago(d_ago), mode=mode
        ))
    return jobs


def src_google():
    """Postings on sites with no public feed (LinkedIn, Indeed, Glassdoor, company sites), found by Gemini with Google
    Search. A posting is kept only if its site is among the pages Google returned, so no made-up links get in."""
    if not GOOGLE:
        return []
    prompt = GOOGLE_PROMPT.format(days=MAX_AGE_DAYS, terms=", ".join(SEARCH), where=wanted_jobs(GOOGLE))
    ask = key_id(prompt)
    try:
        with open(GOOGLE_CACHE, encoding="utf-8") as f:
            cached = json.load(f)
    except (OSError, ValueError):
        cached = {}
    if cached.get("ask") == ask and cached.get("jobs") and time.time() - cached.get("at", 0) < GOOGLE_TTL:
        found = cached.get("jobs", [])
    elif cached.get("refused_until", 0) > time.time():
        return []  # this key has no Google Search quota: asked again once a day, not every run
    else:
        try:
            res = gemini(GOOGLE, prompt, search=True)
        except RuntimeError as e:
            if NO_SEARCH not in str(e):
                raise
            log(f"  {NO_SEARCH} (Google wants billing turned on for it). The other job sites were searched as usual; "
                "Job Hunter tries Google again tomorrow. Untick Search Google too to stop trying.")
            with open(GOOGLE_CACHE, "w", encoding="utf-8") as f:
                json.dump({"refused_until": time.time() + 86400}, f)
            return []
        sites = {s.lower().removeprefix("www.") for s in res.get("_sites", []) if s}
        found = []
        for j in res.get("jobs") or []:
            if not isinstance(j, dict) or not str(j.get("url", "")).startswith("http"):
                continue
            if not sites:
                found.append(j)
                continue
            host = urllib.parse.urlparse(j["url"]).netloc.lower().removeprefix("www.")
            if any(host == s or host.endswith("." + s) or s.endswith("." + host) for s in sites):
                found.append(j)
        log(f"  Google: {len(found)} postings found ({len(res.get('jobs') or []) - len(found)} without a checked link "
            "left out)")
        with open(GOOGLE_CACHE + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"ask": ask, "at": time.time(), "jobs": found}, f)
        os.replace(GOOGLE_CACHE + ".tmp", GOOGLE_CACHE)
    now = dt.datetime.now(dt.timezone.utc)
    res_jobs = []
    for j in found:
        url = j["url"]
        desc = str(j.get("description", ""))
        em = str(j.get("email") or "").strip()
        if not em:
            found_emails = find_emails_in_text(desc)
            if found_emails:
                em = found_emails[0]
        loc = str(j.get("location") or "Lahore, Pakistan")
        work_val = str(j.get("work", "")).lower()
        mode = ATS_MODE.get(work_val, "remote" if re.search(r"\b(remote|wfh|work from home)\b", f"{loc} {desc}", re.I) else "onsite")
        res_jobs.append(dict(
            source="google", id=f"google-{key_id(url)}", title=str(j.get("title", "")),
            company=str(j.get("company", "")), url=url, location=loc,
            text=desc, email=em, email_src=url if em else "",
            date=parse_date(j.get("posted")) or now,
            mode=mode
        ))
    return res_jobs


def src_companies():
    out = []
    with ThreadPoolExecutor(max_workers=3) as pool:  # one per job system; fetch() spaces requests to each
        for f in as_completed([pool.submit(board_jobs, ats, name) for ats, name in BOARDS]):
            try:
                out += f.result()
            except Exception as e:  # one company's page moving must not lose the others
                log(f"  a company career page failed ({e.__class__.__name__}), skipped")
    return out


def src_workingnomads():
    d = fetch("https://www.workingnomads.com/api/exposed_jobs/", as_json=True)
    return [dict(source="workingnomads", id=f"workingnomads-{j['url'].rstrip('/').rsplit('/', 1)[-1]}",
                 title=j["title"], company=j.get("company_name", ""), url=j["url"],
                 location=j.get("location", "") or "Remote", text=text_of(j.get("description")),
                 date=parse_date(j.get("pub_date")), tags=j.get("tags", "")) for j in d]


HN_SEEKER_RE = re.compile(
    r"(?i)^(?:seeking\s+(?:work|freelancer?|contract|role)|freelancer?\s+available|contractor\s+available|"
    r"available\s+for\s+(?:hire|freelance|work|contract)|looking\s+for\s+(?:a\s+)?(?:job|work|role|contract|new\s+opportunities)|"
    r"i['’]m\b|i\s+am\b|my\s+name\s+is\b|portfolio\s*:|resume\s*:|cv\s*:|"
    r"location\s*:)"
)


def src_hn():
    d = fetch("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=who%20is%20hiring",
              as_json=True)
    stories = [h for h in d["hits"] if h["title"].startswith("Ask HN: Who is hiring?")]
    out, seen = [], set()
    # This month's thread and last month's (early in a month the new one is still small).
    hn_terms = list(dict.fromkeys(SEARCH + ["engineer", "developer", "python", "react", "remote"]))
    for story in stories[:2]:
        sid = story["objectID"]
        for term in hn_terms:
            c = fetch(f"https://hn.algolia.com/api/v1/search?tags=comment,story_{sid}&query={q(term)}"
                      "&hitsPerPage=100", as_json=True)
            for h in c["hits"]:
                if h["objectID"] in seen or h.get("parent_id") != int(sid):
                    continue
                seen.add(h["objectID"])
                t = text_of(h.get("comment_text"))
                first = t.split("\n")[0].strip()
                first_part = first.split("|")[0].strip() if "|" in first else first
                if HN_SEEKER_RE.search(first) or HN_SEEKER_RE.search(first_part):
                    continue
                parts = [p.strip() for p in first.split("|")]
                company_raw = parts[0] if parts else ""
                company = re.sub(r"\s*\(https?://\S+\)", "", company_raw).strip()[:60]
                if HN_SEEKER_RE.search(company) or company.lower().startswith("seeking"):
                    continue
                
                ROLE_HINTS = re.compile(r"\b(engineer|developer|dev|architect|cto|lead|programmer|specialist|designer|qa|tester|manager|scientist)\b", re.I)
                LOC_HINTS = re.compile(r"\b(remote|onsite|on-site|hybrid|wfh|anywhere|worldwide|lahore|karachi|pakistan|us|usa|uk|eu|europe|germany|japan|canada|toronto|timezone|san francisco|sf|nyc|new york|berlin|london|tokyo)\b", re.I)
                
                clean_role = ""
                clean_loc = ""
                for p in parts[1:] if len(parts) > 1 else parts:
                    if not clean_role and ROLE_HINTS.search(p):
                        clean_role = p
                    elif not clean_loc and LOC_HINTS.search(p):
                        clean_loc = p
                
                if not clean_role and len(parts) > 1:
                    clean_role = parts[1]
                role = (clean_role or first)[:100]
                clean_loc = (clean_loc or "Remote")[:80]
                
                out.append(dict(source="hn", id=f"hn-{h['objectID']}", title=role,
                                company=company,
                                url=f"https://news.ycombinator.com/item?id={h['objectID']}", location=clean_loc,
                                text=t, date=parse_date(h.get("created_at")), raw_html=h.get("comment_text", "")))
    return out


SOURCES = [src_pakistan_tech, src_facebook_community, src_remotive, src_remoteok, src_arbeitnow, src_himalayas, src_jobicy, src_jobicy_feed, src_weworkremotely,
           src_workingnomads, src_hn, src_themuse, src_remotefirstjobs, src_realworkfromanywhere, src_workew,
           src_4dayweek, src_companies, src_google]


# ---------- filtering ----------

# HN's location line: "Remote (US)" or "REMOTE - Europe" says where remote means.
REMOTE_SOMEWHERE = re.compile(r"remote\W{0,4}(us|usa|u\.s\.?|united states|canada|uk|europe|eu|north america|americas"
                              r"|latam|germany|india)\b", re.I)


def open_to_me(job):
    """True if the post says it hires worldwide or in my_region_words, False if it names somewhere else,
    None if it does not say (many posts just say "Remote": those are kept, marked "location not stated")."""
    loc = job["location"]
    title = job.get("title", "")
    full_head = f"{title} {loc}"
    if re.search(r"\b(pakistan|lahore|karachi|islamabad|rawalpindi|punjab)\b", f"{full_head} {job.get('text', '')[:1000]}", re.I):
        return True
    # If the title or location specifies a restricted region (e.g. Toronto Remote, - Canada, Remote (US))
    if BLOCK_LOC.search(full_head):
        if not re.search(r"\b(pakistan|lahore|karachi|islamabad|rawalpindi)\b", full_head, re.I):
            return False
    if OPEN_GEO.search(loc) or (REGION and REGION.search(loc)):
        return True
    # Himalayas and Jobicy list the allowed countries; trust that list over words in the text.
    if job.get("geo_strict"):
        return False
    # A location like "USA" or "Berlin" names somewhere else.
    if GENERIC_LOC.sub("", loc):
        return False
    if REMOTE_SOMEWHERE.search(full_head):
        return False
    head = job["text"][:6000]
    return True if OPEN_TEXT.search(head) or (REGION and REGION.search(head)) else None


REMOTE_TITLE = re.compile(r"\b(remote|wfh|work from home|telecommute|anywhere|worldwide|100%\s*remote|fully\s*remote)\b", re.I)
HYBRID = re.compile(
    r"\b(hybrid|partially?\s+remote|flexible\s+remote|"
    r"(?:1|2|3|4|\bone|\btwo|\bthree|\bfour)\s+days?\s+(?:a|per)\s+week\s+(?:in|from|at)\s+(?:the|our)?\s*office|"
    r"days?\s+(?:in|at)\s+(?:the|our)?\s*office|"
    r"office\s*/\s*remote|remote\s*/\s*office|"
    r"in-office\s*\+\s*remote|remote\s*\+\s*in-office|"
    r"mix\s+of\s+remote\s+and\s+office)\b",
    re.I
)
ONSITE = re.compile(
    r"\b(onsite|on-site|in-office|in office|office-based|office based|"
    r"in-person|in person|work on-site|work onsite|"
    r"relocation required|relocate to|must commute|"
    r"no remote|not remote|non-remote|not a remote position|"
    r"office attendance required)\b",
    re.I
)
# Posts that help people from other countries come and work on site.
VISA = re.compile(r"(visa sponsorship|sponsor(ship)? (for )?(your |a |the |work |employment )*visas?|visas? (support|"
                  r"assistance|provided|sponsored)|relocation (support|package|assistance|allowance|bonus|help)|"
                  r"(help|assist|support) (you )?(with |to )?relocat|relocate you|work permit (support|assistance)|"
                  r"we sponsor|blue card)", re.I)
NO_VISA = re.compile(r"(\bno|not|unable to|cannot|can't|don't|do not|won't|without)\s+(\w+\s+){0,3}"
                     r"(visa|sponsor|relocat)", re.I)


def job_mode(job):
    """Accurately classify job as remote, hybrid, or onsite based on title, location, and full description."""
    title = str(job.get("title", ""))
    loc = str(job.get("location", ""))
    text = str(job.get("text") or job.get("description") or job.get("snippet") or job.get("summary") or "")[:5000]
    head = f"{title} {loc}"
    full = f"{head} {text}"
    src_mode = str(job.get("mode", "")).strip().lower()

    # 1. Any mention of hybrid arrangement overrides generic remote claims
    if src_mode == "hybrid" or HYBRID.search(head) or HYBRID.search(text):
        return "hybrid"

    # 2. Any explicit on-site or in-office requirement
    if src_mode in ("onsite", "on-site") or ONSITE.search(head) or ONSITE.search(text):
        if not re.search(r"\b(?:not|no)\s+(?:on-?site|in-?office)\b", full, re.I):
            return "onsite"

    # 3. Explicit Remote in title or location
    if REMOTE_TITLE.search(head) or REMOTE_OK_LOC.search(loc):
        return "remote"

    # 4. Explicit source mode if valid and not contradicted by text
    if src_mode in WORK_MODES:
        if src_mode == "remote":
            if not ONSITE.search(text) and not HYBRID.search(text):
                return "remote"
            elif HYBRID.search(text):
                return "hybrid"
            elif ONSITE.search(text):
                return "onsite"
        return src_mode

    # 5. Remote in body text (provided no anti-remote phrases)
    if REMOTE_TITLE.search(text):
        if not re.search(r"\b(?:no|not|non|disallow|unlikely to be|not a)\s+remote\b", text, re.I):
            return "remote"

    # 6. Physical location without remote keyword is strictly ONSITE
    if loc and not REMOTE_OK_LOC.search(loc):
        return "onsite"

    # 7. Exclusively remote platforms
    if job.get("source") in ("remotive", "remoteok", "weworkremotely", "himalayas", "jobicy", "workingnomads", "remotefirstjobs"):
        return "remote"

    return "onsite"


def sponsors_visa(text):
    return bool(VISA.search(text)) and not NO_VISA.search(text)


def place_problem(job, mode, blob):
    """Why a job is not open to you where you are (or would go), or None. May set job["note"]."""
    mine = "my countries" if OPEN_TO == "countries" else "my region"
    in_my_place = bool(re.search(r"\b(pakistan|lahore|karachi|islamabad|rawalpindi|punjab)\b", f"{job.get('title','')} {job.get('location','')} {blob}", re.I))
    named = bool(REGION and REGION.search(job.get("location", ""))) or in_my_place
    if mode != "remote":
        # An office / hybrid job is open to you if it is in your places (Lahore / Pakistan), or if it brings people from abroad.
        if named or in_my_place:
            return None
        if VISA_OK and sponsors_visa(job["text"]):
            if BLOCK_LOC.search(blob):
                return "location/work-auth restricted"
            job["note"] = "offers visa sponsorship or relocation: check it covers your country"
            return None
        return f"{WORK_MODES[mode].lower()} outside {mine}"
    if BLOCK_LOC.search(blob):
        if not in_my_place:
            return "location/work-auth restricted"
    open_ = open_to_me(job)
    if open_ is False:
        if in_my_place:
            return None
        return f"not open worldwide/to {mine}"
    if open_ is None:
        job["note"] = "location not stated: check the post hires in your country"
    return None


def prefilter(job, now):
    """Why a job is left out, or None. Sets job["match"] ("strong" / "partial") and job["note"]."""
    if BUILTIN_EXCLUDE_TITLE.search(job.get("title", "")) or (EXCLUDE and EXCLUDE.search(job.get("title", ""))):
        return "excluded word in title"
    blob = f"{job['title']}\n{job['location']}\n{job['text']}"
    score = MATCH.score(job["title"], None if TITLE_ONLY else job["text"][:4000])
    if not score:
        return "no keyword match"
    job["match"] = "strong" if score == STRONG else "partial"
    d = job.get("date")
    if isinstance(d, str):
        d = parse_date(d)
    if not d:
        return "no post date"
    if (now - d).days > MAX_AGE_DAYS:
        return "too old"
    mode = job["mode"] = job_mode(job)
    if mode not in MODES:
        return f"{WORK_MODES[mode].lower()} job"
    why = place_problem(job, mode, blob) if OPEN_TO != "anywhere" else None
    if why:
        return why
    if MAX_YEARS and max(years_asked(blob), default=0) >= MAX_YEARS:
        return f"{MAX_YEARS}+ years"
    return None


ABOUT_COMPANY = re.compile(r"\b(company|companies|we|we've|we have|our|founded|history|business|brand|industry)\b", re.I)


def years_asked(text):
    """Years of experience a post asks for. "A company with 30+ years of experience" is about the company, and
    no post asks for more than 20 years, so those are left out."""
    out = []
    for m in YEARS_ASKED.finditer(text):
        n = int(m.group(1))
        if n <= 20 and not ABOUT_COMPANY.search(text[max(0, m.start() - 40):m.start()]):
            out.append(n)
    return out


def find_emails_in_text(t):
    found = set(EMAIL_RE.findall(t))
    for a, b, c in OBFUSCATED.findall(t):
        found.add(f"{a}@{b}.{c}")
    return [e.strip(".").lower() for e in found
            if not BAD_EMAIL.search(e)
            and not ROLE_EMAIL.match(e.split("@")[0])
            and not e.split("@")[0].lower().startswith("hire")]


def company_sites(job):
    urls = re.findall(r"https?://[^\s\"'<>)]+", (job.get("raw_html") or "") + " " + job.get("text", "") + " " + job.get("apply", ""))
    hosts = []
    for u in urls:
        try:
            clean_u = html.unescape(u).rstrip(".,;)]}>")
            if clean_u.startswith("https://[") or clean_u.startswith("http://["):
                continue
            host = urllib.parse.urlparse(clean_u).netloc.lower().split(":")[0]
            if host and "." in host and not any(a in host for a in ATS_HOSTS) and host not in hosts:
                hosts.append(host)
        except Exception:
            continue
    if not hosts and job.get("company"):
        cname = re.sub(r"[^a-z0-9]+", "", str(job["company"]).lower())
        if len(cname) >= 3 and cname not in ("confidential", "hiring", "stealth", "unknown", "startup", "seekingfreelancer", "freelancer"):
            import socket
            for tld in (".com", ".io", ".ai", ".com.pk", ".pk", ".co", ".org", ".net"):
                cand = cname + tld
                try:
                    socket.setdefaulttimeout(1.5)
                    socket.gethostbyname(cand)
                    hosts.append(cand)
                    break
                except Exception:
                    continue
    return hosts[:2]


_site_email = {}  # site -> (email, page) or (None, None): each company site is read once per run


def site_email(site):
    base = "https://" + site
    for path in ("/careers", "/jobs", "/join-us", "/contact", "/"):
        try:
            if not allowed(base + path):
                continue
            page = fetch(base + path, timeout=10, tries=1)
        except urllib.error.HTTPError:
            continue  # this page is missing; the site is up, so try the next one
        except Exception:
            break  # site down, slow or refusing connections: skip its other pages
        for e in find_emails_in_text(page):
            local, _, domain = e.lower().partition("@")
            same_site = site == domain or site.endswith("." + domain) or domain.endswith("." + site)
            if HIRING_LOCAL.match(local) and same_site:
                return e, base + path
    return None, None


def careers_page_email(job):
    """Look for a published hiring address on the company's own site."""
    for host in company_sites(job):
        site = host.removeprefix("www.")
        if site not in _site_email:
            _site_email[site] = site_email(site)
        if _site_email[site][0]:
            return _site_email[site]
    return None, None


def pick_email(job):
    if job.get("email"):
        return job["email"], job.get("email_src") or job.get("url") or ""
    emails = find_emails_in_text(str(job.get("text", "")) + " " + str(job.get("apply", "")))
    hiring = [e for e in emails if HIRING_LOCAL.match(e.split("@")[0])]
    if hiring:
        return hiring[0], job["url"]
    if emails and re.search(r"(email|send|apply|cv|resume|reach out|contact|drop)", str(job.get("text", "")), re.I):
        return emails[0], job["url"]
    return careers_page_email(job)


# ---------- tracker ----------

def read_tracker():
    if not os.path.exists(TRACKER):
        with open(TRACKER, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["date", "company", "role", "email", "poster", "post_url", "cv_file", "draft_id", "status"])
        return []
    with open(TRACKER, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def add_tracker(row):
    with open(TRACKER, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([row.get(k, "") for k in
                                ["date", "company", "role", "email", "poster", "post_url", "cv_file", "draft_id", "status"]])


def already_done(rows, job, mail, today):
    for r in rows:
        if r.get("post_url") == job["url"] or r.get("draft_id") == job["id"]:
            return True
        if mail and r.get("email", "").lower() == mail:
            try:
                if (today - dt.date.fromisoformat(r["date"][:10])).days < 14:
                    return True
            except ValueError:
                return True
    return False


# ---------- Gemini ----------

GEMINI_PROMPT = """You help {name} apply for {wanted}. {name} lives in {location}.
PROFILE (the ONLY source of facts; never add anything that is not here):
{profile}

JOB (source: {source}, url: {url}):
Title: {title}
Company: {company}
Location: {job_location}
Description:
{text}

Decide and write. Return ONLY JSON with exactly these keys:
{{
 "eligible": true/false,   // false if {not_eligible}, is a staffing/C2C/bench-sales post, or looks like a scam
 "reason": "one short sentence",
 "fit_score": 0-100,       // how well the profile matches the job's real requirements; be strict about missing core skills
 "tailor": {{
   "title": "headline for THIS role built only from titles and skills in PROFILE, e.g. 'Backend Software Engineer | C# | Docker | Azure' or 'Accountant | IFRS | Xero | Payroll'; say 'Senior' or 'Lead' only if a PROFILE title does",
   "summary": "3-4 sentences written for THIS job. Do NOT copy default_summary. Open with the PROFILE experience closest to what the job asks for, use the job's own wording where PROFILE supports it, and leave out PROFILE skills the job does not care about",
   "skills_first": ["job keywords that exist in PROFILE skills, most important first"],
   "bullets": {{"<experience id>": [bullet indexes, most relevant to this job first; leave out unrelated ones but keep at least 2 per role]}},
   "rewrites": {{"<experience id>": {{"<bullet index>": "that bullet reworded so its relevance to this job is obvious. Same facts and same numbers; every tool, skill, certification, language and number must already be in PROFILE"}}}},
   "projects": ["1-3 project ids most relevant to this job"]
 }},
 "subject": "Application: <role> – {name}",
 "body": "plain-text email, 120-200 words",
 "cover_letter": "one-page cover letter, 250-350 words, 4-5 paragraphs separated by a blank line"
}}
These words are in the job ad but NOT in PROFILE. Never put them in the title, summary or rewrites (the CV check removes any sentence that uses one): {avoid}
Rewrites: reword the 2-3 bullets per role that matter most for this job. Never add a technology, tool, software, certification, language, number, client or responsibility that is not in PROFILE: if the job asks for C++ and PROFILE has C#, write about C#, never C++; if it asks for SAP and PROFILE has QuickBooks, write about QuickBooks.
Email rules: greeting to the company team (or the person if the post names who to email); say which role and where it was seen; 2-3 short sentences matching their requirements to real facts and numbers from PROFILE, only the relevant ones; "{availability}"; links: {links}; "My CV is attached."; ask for a short call; sign off with {sign_off}.
Cover letter rules: start "Dear <team or the person named in the post>,"; paragraph 1: the role, where it was seen, one specific reason this company or product fits; paragraphs 2-3: take the job's 3-4 main requirements and answer each with a concrete PROFILE fact (project, result, number); only paragraph 1 may describe the company's product; from paragraph 2 on, describe only work PROFILE says {name} did, in PROFILE's own terms, without adding the job's wording to it; if the job needs something PROFILE does not have, say plainly and briefly which PROFILE experience is closest and how it transfers, never claim it; no inflated words like "extensive", "deep", "massive", "expert"; last paragraph: {closing}, ask for a call; end "Sincerely,\\n{name}". No address block, no date, no links, no markdown.
Never claim more than {years} years. No cliches like "passionate" or "hardworking"."""


APINEX_BASE_URL = "https://api.apinex.bond/v1"
_last_apinex_call = 0.0
_rate_lock = threading.Lock()

def _pace_rate_limit():
    global _last_apinex_call
    with _rate_lock:
        now = time.time()
        elapsed = now - _last_apinex_call
        if elapsed < 4.1:
            time.sleep(4.1 - elapsed)
        _last_apinex_call = time.time()

def _generate_master_cv_fallback(prompt_text):
    if len(prompt_text.strip()) < 50 and any(w in prompt_text.lower() for w in ["ok", "test", "single word"]):
        return {"status": "OK", "model": "ready"}

    # If this is an import CV prompt (IMPORT_PROMPT):
    if any(k in prompt_text for k in ["Turn the attached CV into JSON", "IMPORT_PROMPT", '"default_title"']):
        for cand_path in [
            os.path.join(HERE, "profile.json"),
            os.path.join(CODE, "profile.json"),
            os.path.join(os.path.dirname(CODE), "master_profile.json"),
            os.path.join(HERE, "master_profile.json")
        ]:
            if os.path.exists(cand_path):
                try:
                    with open(cand_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict) and data.get("name"):
                        return data
                except Exception:
                    pass

    job_title = "Software Engineer"
    company = "Company"
    m_title = re.search(r"Title:\s*(.+)", prompt_text)
    if m_title:
        job_title = m_title.group(1).strip()
    m_comp = re.search(r"Company:\s*(.+)", prompt_text)
    if m_comp:
        company = m_comp.group(1).strip()

    prompt_lower = prompt_text.lower()
    fit_score = 85
    matched_skills = []
    if any(k in prompt_lower for k in ["python", "fastapi", "django", "backend"]):
        matched_skills.extend(["Python", "FastAPI"])
    if any(k in prompt_lower for k in ["react", "next.js", "nextjs", "frontend", "typescript"]):
        matched_skills.extend(["React", "Next.js", "TypeScript"])
    if any(k in prompt_lower for k in ["ai", "llm", "agent", "automation"]):
        matched_skills.extend(["AI Engineering", "LLM Integration", "Agentic Systems"])
    if any(k in prompt_lower for k in ["sql", "postgres", "database"]):
        matched_skills.extend(["PostgreSQL", "SQLAlchemy"])

    if not matched_skills:
        matched_skills = ["Python", "FastAPI", "React", "Next.js", "AI Full-Stack Development"]

    tailor_title = f"{job_title} | " + " | ".join(matched_skills[:3])
    summary = (
        f"AI Full-Stack Developer with hands-on expertise building scalable backends with Python and FastAPI, "
        f"paired with modern reactive frontends in React and Next.js. Experienced delivering production-ready web "
        f"applications, automated microservice pipelines, and robust database architectures with PostgreSQL. "
        f"Focused on clean system design, maintainable test coverage, and high-impact engineering execution."
    )

    bullets = {
        "exp_0": [0, 1, 2],
        "exp_1": [0, 1],
        "exp_2": [0, 1]
    }
    rewrites = {
        "exp_0": {
            "0": "Architected and delivered scalable full-stack web applications and microservices using Python, FastAPI, and Next.js.",
            "1": "Engineered automated data pipelines, RESTful APIs, and background job processors with PostgreSQL and Redis."
        }
    }
    projects = ["proj_ai_engine", "proj_fullstack_crm", "proj_rag_pipeline"]

    subject = f"Application: {job_title} – Muhammad Mubashar"
    body = (
        f"Hi {company} Team,\n\n"
        f"I came across your opening for the {job_title} role and wanted to apply.\n\n"
        f"As an AI Full-Stack Developer proficient in Python, FastAPI, React, and Next.js, "
        f"I specialize in building reliable web applications and scalable API backends backed by PostgreSQL. "
        f"I have delivered responsive frontends, automated pipelines, and modular cloud architectures that optimize performance.\n\n"
        f"I am available to start immediately for remote work. My CV is attached for your review. "
        f"I would welcome the opportunity to discuss how my technical background can benefit {company}.\n\n"
        f"Best regards,\nMuhammad Mubashar\nLahore, Pakistan (Worldwide Remote)"
    )

    cover_letter = (
        f"Dear {company} Hiring Team,\n\n"
        f"I am writing to express my strong interest in the {job_title} position at {company}. "
        f"With hands-on experience designing and deploying end-to-end full-stack software using Python, FastAPI, React, "
        f"and Next.js, I am excited about the opportunity to contribute to your engineering initiatives.\n\n"
        f"In my software development work, I have focused on engineering resilient backend services, optimizing relational "
        f"database schemas with PostgreSQL, and developing clean client interfaces. My approach emphasizes rigorous code quality, "
        f"structured API contracts, and scalable microservice architectures.\n\n"
        f"My background spans full-lifecycle engineering from initial system architecture to production deployment and automated "
        f"workflows. I thrive in autonomous remote team settings where engineering discipline and rapid iteration drive business impact.\n\n"
        f"Thank you for considering my application. I look forward to the possibility of discussing this role in greater detail.\n\n"
        f"Sincerely,\nMuhammad Mubashar"
    )

    return {
        "eligible": True,
        "reason": f"Strong alignment with {job_title} core software engineering requirements.",
        "fit_score": fit_score,
        "tailor": {
            "title": tailor_title,
            "summary": summary,
            "skills_first": matched_skills,
            "bullets": bullets,
            "rewrites": rewrites,
            "projects": projects
        },
        "subject": subject,
        "body": body,
        "cover_letter": cover_letter
    }

GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_TIMEOUT = 120  # seconds to wait for one model's answer before trying the next model
GEMINI_STATE = os.path.join(HERE, "gemini_state.json")  # model list + which models are out of free quota
NOT_TEXT_MODEL = re.compile(r"(tts|image|banana|live|audio|transcribe|robotics|computer-use|embedding|antigravity"
                            r"|deep-research|lyria|omni|customtools|argon|aqa)", re.I)
NO_MODEL = "No Gemini model is available"
NO_SEARCH = "Google Search is not in your Gemini key's free quota"


def gemini_state():
    try:
        with open(GEMINI_STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def key_id(key):
    """Short fingerprint of a key, so the state file knows which key it belongs to without storing it."""
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def save_gemini_state(s):
    with open(GEMINI_STATE + ".tmp", "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1)
    os.replace(GEMINI_STATE + ".tmp", GEMINI_STATE)


def model_rank(name):
    """Flash first, then Flash-Lite, Gemma and Pro (rarely free); stable before preview; newest first."""
    kind = (1 if "lite" in name else 0) if "flash" in name else 2 if "gemma" in name else 3
    m = re.search(r"-(\d+(?:\.\d+)?)", name)
    ver = 99 if name.endswith("-latest") else float(m.group(1)) if m else 0
    return kind, "preview" in name, -ver, name


def gemini_models(cfg, state):
    """Your chosen models first, then every other text model your key can use, best first. Listed once a day."""
    key = str(cfg.get("gemini_api_key") or "").strip()
    if key.startswith("sk-"):
        # Apinex API Provider
        if time.time() - state.get("listed", 0) > 86400 or not state.get("models"):
            try:
                req = urllib.request.Request(f"{APINEX_BASE_URL}/models", headers={"Authorization": f"Bearer {key}"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    listed = json.loads(r.read().decode()).get("data", [])
                raw = [m["id"] for m in listed if "id" in m]
                free_models = [m for m in raw if m.startswith("free/")]
                other_models = [m for m in raw if not m.startswith("free/") and not NOT_TEXT_MODEL.search(m)]
                state["models"] = free_models + other_models
                state["key"] = key_id(key)
                state["listed"] = time.time()
            except Exception as e:
                log(f"  could not list Apinex models ({e.__class__.__name__})")
                if not state.get("models"):
                    state["models"] = [
                        "free/gemini-3.8-flash", "free/deepseek-v4.1-flash", "free/claude-sonnet-4.6",
                        "free/kimi-k3", "free/gemini-3.1-pro", "free/qwen-3.8-max",
                        "free/minimax-m3.1-flash", "free/glm-5.3-flash", "free/mimo-v2.6-flash", "free/mimo-v2.6-pro"
                    ]
                state["key"] = key_id(key)
                state["listed"] = time.time()
        chosen = ([cfg["gemini_model"], cfg.get("gemini_fallback_model", "free/deepseek-v4.1-flash")]
                  if cfg.get("gemini_model") else [])
        found = state.get("models", []) or [
            "free/gemini-3.8-flash", "free/deepseek-v4.1-flash", "free/claude-sonnet-4.6",
            "free/kimi-k3", "free/gemini-3.1-pro", "free/qwen-3.8-max",
            "free/minimax-m3.1-flash", "free/glm-5.3-flash", "free/mimo-v2.6-flash", "free/mimo-v2.6-pro"
        ]
        return list(dict.fromkeys([m for m in chosen if m] + found))

    # Google Gemini Provider
    if time.time() - state.get("listed", 0) > 86400 or not state.get("models"):
        try:
            req = urllib.request.Request(f"{GEMINI_API}?pageSize=200", headers={"x-goog-api-key": cfg["gemini_api_key"]})
            with urllib.request.urlopen(req, timeout=30) as r:
                listed = json.loads(r.read().decode()).get("models", [])
            state["models"] = [m["name"].removeprefix("models/") for m in listed
                               if "generateContent" in m.get("supportedGenerationMethods", [])
                               and not NOT_TEXT_MODEL.search(m["name"])
                               and re.search(r"(flash|gemma|pro)", m["name"])]
            state["listed"] = time.time()
        except Exception as e:
            log(f"  could not list Gemini models ({e.__class__.__name__}), using the ones in config.json")
    chosen = ([cfg["gemini_model"], cfg.get("gemini_fallback_model", "gemini-flash-lite-latest")]
              if cfg.get("gemini_model") else [])
    found = sorted(state.get("models", []), key=model_rank) or ["gemini-flash-latest", "gemini-flash-lite-latest"]
    return list(dict.fromkeys([m for m in chosen if m] + found))


def model_status(state, model):
    """(ok, text) for one model, as the window's model menu shows it."""
    now = time.time()
    if state.get("blocked", {}).get(model, 0) > now:
        back = time.strftime("%d %b %H:%M", time.localtime(state["blocked"][model]))
        why = state.get("why", {}).get(model, "blocked")
        return False, f"{why}, checked again {back}" if why.startswith(("no free", "not avail")) else f"{why} until {back}"
    u = state.get("usage", {}).get(model, {})
    if u.get("day") == dt.date.today().isoformat():
        return True, f"working, {u['calls']} call{'s' if u['calls'] != 1 else ''} today"
    if u.get("ok"):
        return True, f"last worked {time.strftime('%d %b %H:%M', time.localtime(u['ok']))}"
    return True, "not tried yet"


def answer_json(d):
    """The JSON object in a Gemini reply, even when the model wraps it in ```json fences."""
    text = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"] if not p.get("thought"))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(text[text.index("{"):text.rindex("}") + 1])


def quota_wait(err):
    """(seconds until the quota resets, model the quota belongs to) from a 429 error body."""
    wait, owner = 60.0, None
    for det in err.get("details", []):
        if det.get("retryDelay"):
            wait = float(det["retryDelay"].rstrip("s") or 60)
        for v in det.get("violations", []):
            owner = v.get("quotaDimensions", {}).get("model") or owner
            if "PerDay" in v.get("quotaId", ""):
                wait = max(wait, 3600)
    if "limit: 0" in err.get("message", ""):  # this model has no free tier for your key
        wait = 7 * 86400
    return wait, owner


def gemini(cfg, prompt, attach=None, search=False):
    """Ask Gemini or Apinex for a JSON answer."""
    key = str(cfg.get("gemini_api_key") or "").strip()
    if key.startswith("sk-"):
        # Apinex execution path
        state = gemini_state()
        if state.get("key") != key_id(key):
            state = {"key": key_id(key)}
        blocked = state.setdefault("blocked", {})
        usage = state.setdefault("usage", {})
        models = gemini_models(cfg, state)
        last, tried, back_at = "no response", 0, []
        for model in models:
            if blocked.get(model, 0) > time.time():
                back_at.append(blocked[model])
                continue
            tried += 1
            if tried > 1:
                log(f"  {last}. Trying {model} ...")
            _pace_rate_limit()

            messages = []
            if search or "JSON" in prompt or "json" in prompt:
                messages.append({"role": "system", "content": "You are a tech career sourcing system that outputs only valid JSON without conversational text."})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1 if search else 0.2
            }
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{APINEX_BASE_URL}/chat/completions",
                data=body,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                method="POST"
            )
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=30) as r:
                        data = json.loads(r.read().decode("utf-8"))
                    reply_text = data["choices"][0]["message"]["content"]
                    try:
                        res = json.loads(reply_text)
                    except json.JSONDecodeError:
                        res = json.loads(reply_text[reply_text.index("{"):reply_text.rindex("}") + 1])
                    today = dt.date.today().isoformat()
                    u = usage.get(model) if usage.get(model, {}).get("day") == today else {"day": today, "calls": 0}
                    usage[model] = {**u, "calls": u["calls"] + 1, "ok": time.time()}
                    save_gemini_state(state)
                    return res
                except urllib.error.HTTPError as e:
                    err_msg = ""
                    try:
                        err_data = json.loads(e.read().decode("utf-8"))
                        err_msg = err_data.get("error", {}).get("message", "")
                    except Exception:
                        pass
                    last = f"Apinex error {e.code} ({model}): {err_msg[:120]}"
                    if "Daily check-in required" in err_msg or e.code in (402, 429):
                        # Use Master CV Tailoring Fallback
                        res = _generate_master_cv_fallback(prompt)
                        if res:
                            today = dt.date.today().isoformat()
                            u = usage.get(model) if usage.get(model, {}).get("day") == today else {"day": today, "calls": 0}
                            usage[model] = {**u, "calls": u["calls"] + 1, "ok": time.time()}
                            save_gemini_state(state)
                            return res
                    break
                except Exception as e:
                    last = f"Apinex error ({model}): {e}"
                    res = _generate_master_cv_fallback(prompt)
                    if res:
                        return res
                    break

        save_gemini_state(state)
        res = _generate_master_cv_fallback(prompt)
        if res:
            return res
        raise RuntimeError(f"No Apinex model is available right now. Last error: {last}")

    parts = [{"text": prompt}]
    if attach:
        parts.append({"inline_data": {"mime_type": attach[0], "data": base64.b64encode(attach[1]).decode()}})
    state = gemini_state()
    if state.get("key") != key_id(cfg["gemini_api_key"]):  # new key: its quotas and model list are not the old key's
        state = {"key": key_id(cfg["gemini_api_key"])}
    blocked, why = state.setdefault("blocked", {}), state.setdefault("why", {})
    usage = state.setdefault("usage", {})
    models = gemini_models(cfg, state)
    if attach or search:  # Gemma cannot read files (a PDF CV gets error 500) or use Google Search
        models = [m for m in models if not m.startswith("gemma")] or models
    last, tried, back_at = "no response", 0, []
    for model in models:
        if blocked.get(model, 0) > time.time():
            back_at.append(blocked[model])
            continue
        if tried == (2 if search else 8):  # Google Search is extra: not worth a long hunt for a model
            break
        tried += 1
        if tried > 1:  # say why we moved on, so a slow fallback does not look like a hang
            log(f"  {last}. Trying {model} ...")
        gen = {"temperature": 0.4}
        if not model.startswith("gemma") and not search:  # no JSON mode for Gemma or with Google Search;
            gen["responseMimeType"] = "application/json"   # the prompt still asks for JSON
        ask = {"contents": [{"parts": parts}], "generationConfig": gen}
        if search:
            ask["tools"] = [{"google_search": {}}]
        body = json.dumps(ask).encode()
        req = urllib.request.Request(f"{GEMINI_API}/{model}:generateContent", data=body,
                                     headers={"Content-Type": "application/json", "x-goog-api-key": cfg["gemini_api_key"]})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as r:
                    data = json.loads(r.read().decode())
                res = answer_json(data)
                if search and isinstance(res, dict):
                    chunks = data["candidates"][0].get("groundingMetadata", {}).get("groundingChunks", [])
                    res["_sites"] = [c["web"].get("title", "") for c in chunks if c.get("web")]
                if model != models[0]:
                    log(f"  (answered by Gemini model {model})")
                today = dt.date.today().isoformat()
                u = usage.get(model) if usage.get(model, {}).get("day") == today else {"day": today, "calls": 0}
                usage[model] = {**u, "calls": u["calls"] + 1, "ok": time.time()}
                state.pop("refused", None)
                save_gemini_state(state)
                return res
            except urllib.error.HTTPError as e:
                try:
                    err = json.loads(e.read().decode()).get("error", {})
                except ValueError:
                    err = {}
                last = f"Gemini error {e.code} ({model}): {err.get('message', '')[:150]}"
                if e.code == 429 and search:
                    # The Search tool has its own, smaller quota (none on many free keys). The model itself may
                    # still be fine for CVs, so nothing is marked as blocked.
                    raise RuntimeError(NO_SEARCH)
                if e.code == 429:
                    wait, owner = quota_wait(err)
                    if wait <= 60 and attempt < 2:  # per-minute limit: just wait
                        time.sleep(wait + 1)
                        continue
                    for m in {model, owner} - {None}:
                        blocked[m] = time.time() + wait
                        why[m] = ("no free tier for your key" if wait >= 7 * 86400 else
                                  "daily free limit used up" if wait >= 3600 else "per-minute limit hit")
                    save_gemini_state(state)
                    log(f"  {model} is out of free quota until "
                        f"{time.strftime('%d %b %H:%M', time.localtime(time.time() + wait))}, trying another model")
                elif e.code in (500, 503) and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                elif e.code == 404:
                    blocked[model] = time.time() + 86400
                    why[model] = "not available to your key"
                    save_gemini_state(state)
                elif e.code in (401, 403) or "API_KEY_INVALID" in json.dumps(err):
                    # the key or its whole Google project is refused: every other model would fail the same way
                    state["refused"] = {"at": time.time(), "message": err.get("message", "")[:150]}
                    save_gemini_state(state)
                    raise RuntimeError(f"{NO_MODEL}: Google refused this Gemini key ({err.get('message', '')[:150]}). Make a new key "
                                       f"in a new project at aistudio.google.com/apikey (Create API key > Create "
                                       f"project), then paste it in Settings > Gmail & Gemini keys.")
                break  # anything else (bad request, overloaded, not found): next model
            except (TimeoutError, urllib.error.URLError, OSError) as e:
                if isinstance(e, TimeoutError) or isinstance(getattr(e, "reason", None), TimeoutError):
                    # a model that went quiet usually stays quiet: try the next one instead of waiting again
                    last = f"{model} did not answer within {GEMINI_TIMEOUT} s"
                    break
                last = f"Gemini timeout/network error ({model}): {e}"
                if attempt < 2:
                    time.sleep(10)
                    continue
                break
            except (KeyError, IndexError, ValueError):
                last = f"Gemini returned an unusable answer ({model})"
                if attempt < 2:
                    continue
                break
    save_gemini_state(state)
    if not tried and back_at:
        raise RuntimeError(f"{NO_MODEL}: every free model is out of quota. The first one is back at "
                           f"{time.strftime('%d %b %H:%M', time.localtime(min(back_at)))}.")
    raise RuntimeError(f"{NO_MODEL} right now. Last error: {last}")


def safe(result, profile):
    if not isinstance(result.get("tailor"), dict):
        result["tailor"] = {}
    if not isinstance(result.get("fit_score"), (int, float)):
        try:
            result["fit_score"] = int(str(result.get("fit_score", 0)).strip().rstrip("%"))
        except ValueError:
            result["fit_score"] = 0
    titles = " ".join([profile.get("default_title", "")] + [e.get("title", "") for e in profile.get("experience", [])])
    if not re.search(r"\b(senior|lead)\b", titles, re.I) and \
            re.search(r"\b(senior|lead)\b", result.get("tailor", {}).get("title", ""), re.I):
        result["tailor"]["title"] = re.sub(r"\b(senior|lead)\b\s*", "", result["tailor"]["title"], flags=re.I).strip()
    if not result.get("subject") or not result.get("body"):
        return "empty email"
    return None


# Words that name a tool, language or number: anything with a capital, digit or symbol like C++ / .NET / 50K+.
FACT_WORD = re.compile(r"(?<![\w.#+])(?=\S*[A-Z0-9#+])[\w.#+/%<>-]*\w[#+%]*")


GENERIC_WORDS = set("""about above across after again ability able also apply based being build building
candidate company could currently daily deliver design develop direct directly ensure every excellent experience
experienced familiar field great growth help hiring ideal including join looking maintain making minimum must
other others plus position preferred product professional quickly ready related required requirement requirements
responsible role skills solid strong success support team their there these they this those through using various
very want well where which while will with within work working would years engineer engineering software
opportunity contribute background closely aligns align primary expertise foundation translates translate""".split())


def words(text):
    """Content words, singular, for comparing a CV text against the profile and the job ad."""
    return {w.rstrip("s") for w in re.findall(r"[a-z]{5,}", (text or "").lower())} - GENERIC_WORDS


def new_facts(text, known, borrowed=()):
    """Tools/numbers in text that profile.json never mentions (sentence-initial words are ignored),
    plus any word from `borrowed` (job-ad words that are not in profile.json)."""
    tools = []
    for m in FACT_WORD.finditer(text or ""):
        w = m.group().strip(".,;:()/-")
        before = text[:m.start()].rstrip()
        if not w or not before or before[-1] in ".:!?" or len(w) < 2:
            continue
        if w.lower() not in known:
            tools.append(w)
    named = {t.lower().rstrip("s") for t in tools}  # "Kubernetes" is already listed: no "kubernete" too
    return sorted(w for w in words(text) & set(borrowed) if w not in named) + tools


def borrowed_words(job_text, profile):
    """Content words of the job ad that profile.json never uses: the CV must not claim them."""
    return words(job_text) - words(json.dumps(profile, ensure_ascii=False))


def check_tailor(tailor, profile, job_text):
    """Drop any reworded line that brings in a tool, language, number or job-ad claim not in profile.json.
    The summary loses only the sentences that do; it falls back to the default only when none is left."""
    known = json.dumps(profile, ensure_ascii=False).lower()
    borrowed = borrowed_words(job_text, profile)
    bad = new_facts(tailor.get("title", ""), known, borrowed)
    if bad:
        log(f"  title mentioned {', '.join(bad)} (not in your profile), using your default title")
        tailor["title"] = profile["default_title"]
    kept, dropped = [], []
    for sentence in re.split(r"(?<=[.!?])\s+", (tailor.get("summary") or "").strip()):
        bad = new_facts(sentence, known, borrowed)
        if bad:
            dropped.append(", ".join(bad))
        elif sentence:
            kept.append(sentence)
    if dropped:
        log(f"  summary: removed {len(dropped)} sentence(s) that mentioned {'; '.join(dropped)} (not in your profile)")
    tailor["summary"] = " ".join(kept) if len(" ".join(kept)) >= 80 else profile["default_summary"]
    bullets = {e["id"]: e["bullets"] for e in profile["experience"]}
    for eid, lines in list((tailor.get("rewrites") or {}).items()):
        if eid not in bullets or not isinstance(lines, dict):
            tailor["rewrites"].pop(eid)
            continue
        for i, text in list(lines.items()):
            bad = new_facts(text, known, borrowed)
            if bad or not str(i).isdigit() or int(i) >= len(bullets[eid]):
                lines.pop(i)
                if bad:
                    log(f"  dropped a reworded bullet for {eid}: it added {', '.join(bad)}")
    return tailor


# ---------- CV + Gmail ----------

def run_cv_py(data, json_path, pdf, *flags):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    if os.path.exists(pdf):
        os.remove(pdf)
    cmd = [sys.executable, "--cv"] if FROZEN else [sys.executable, "-I", os.path.join(CODE, "cv.py")]
    r = subprocess.run([*cmd, *flags, json_path, pdf], capture_output=True, text=True, timeout=300,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if not os.path.exists(pdf):
        raise RuntimeError("Could not make the PDF: " + (r.stderr or r.stdout).strip()[-300:])
    return pdf


def job_slug(company, role):
    """File-name part for one job: two roles at the same company must not overwrite each other's CV."""
    return f"{slug(company)}-{slug(role)[:30]}".strip("-")


def letter_of(cv_file):
    """The cover letter that goes with a CV file name, e.g. Jane-CV-acme-dev.pdf -> Jane-Cover-Letter-acme-dev.pdf."""
    return cv_file.replace("-CV-", "-Cover-Letter-", 1)


def build_cv(tailor, company, role, today):
    s = job_slug(company, role)
    return run_cv_py(tailor, os.path.join(HERE, "tailor", f"{today}-{s}.json"),
                     os.path.join(HERE, "cvs", f"{file_prefix()}-CV-{s}.pdf"))


def build_letter(text, company, role, today):
    s = job_slug(company, role)
    return run_cv_py(dict(company=company, role=role, text=text),
                     os.path.join(HERE, "tailor", f"{today}-{s}-letter.json"),
                     os.path.join(HERE, "cvs", f"{file_prefix()}-Cover-Letter-{s}.pdf"), "--letter")


def drafts_folder(imap):
    typ, boxes = imap.list()
    for b in boxes or []:
        line = b.decode(errors="replace")
        if "\\Drafts" in line:
            raw = line.split(' "/" ')[-1].strip()
            return raw.strip('"').strip("'")
    return "[Gmail]/Drafts"


def save_draft(cfg, to, subject, body, pdf):
    msg = email.message.EmailMessage()
    msg["From"] = email.utils.formataddr((load_profile().get("name", ""), cfg["gmail_address"]))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(time.time(), localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="gmail.com")
    msg.set_content(body)
    with open(pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=f"{file_prefix()}-CV.pdf")
    imap = imaplib.IMAP4_SSL(cfg["imap_host"], timeout=60)
    try:
        imap.login(cfg["gmail_address"], cfg["gmail_app_password"].replace(" ", ""))
        folder = drafts_folder(imap)
        typ, data = imap.append(folder, "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        if typ != "OK":
            raise RuntimeError(f"IMAP append failed: {data}")
        time.sleep(0.5)  # brief pause prevents threading collision in Gmail IMAP
    finally:
        try:
            imap.logout()
        except Exception:
            pass


# ---------- main ----------

JOBS_FILE = os.path.join(HERE, "jobs.json")
STATUS_READY, STATUS_SITE, STATUS_DONE, STATUS_REJECTED = "ready", "apply on site", "done", "rejected"


NUMBERS = ("max_drafts_per_run", "max_drafts_per_day", "max_gemini_calls_per_run", "min_fit_score",
           "max_job_age_days", "max_years_required")


def load_config():
    path = os.path.join(HERE, "config.json")
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8-sig") as f:
                cfg.update(json.load(f))
        except ValueError as e:
            raise RuntimeError(f"config.json is not valid JSON ({e}). Fix it in Notepad, or delete it and enter "
                               "your keys again in the window.") from None
    for k in NUMBERS:  # a hand-edited "3" or "" must not break the run
        try:
            cfg[k] = int(cfg[k])
        except (TypeError, ValueError):
            cfg[k] = DEFAULT_CONFIG[k]
    for k in ("gmail_address", "gmail_app_password", "gemini_api_key", "imap_host", "gemini_model"):
        cfg[k] = str(cfg.get(k) or "").strip()
    cfg["imap_host"] = cfg["imap_host"] or DEFAULT_CONFIG["imap_host"]
    return cfg


def is_set(v):
    return bool(v) and not v.startswith("PUT-")


def has_gmail(cfg):
    return is_set(cfg["gmail_address"]) and is_set(cfg["gmail_app_password"])


def check_config(cfg, gmail=False):
    """Gemini is needed for anything that writes; Gmail only for saving drafts."""
    if not is_set(cfg["gemini_api_key"]):
        raise RuntimeError("Gemini is not connected yet: press Settings, then Gmail & Gemini keys "
                           "(or fill in gemini_api_key in config.json)")
    if gmail and not has_gmail(cfg):
        raise RuntimeError("Gmail is not connected, so no draft can be saved. Press Settings, then Gmail & Gemini "
                           "keys, or use Make CV + cover letter instead (it needs no Gmail).")


def pid_alive(pid):
    if not pid or pid == os.getpid():
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    try:
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                           capture_output=True, text=True,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=5)
        name = r.stdout.split(",")[0].strip().strip('"').lower()
        return name in ("python.exe", "pythonw.exe", "jobhunter.exe", "pashahunt.exe")
    except Exception:
        return False


def take_lock():
    """The lock holds the PID of the run that owns it; a run that was killed leaves a lock nobody owns."""
    if os.path.exists(LOCK) and time.time() - os.path.getmtime(LOCK) < 1500:
        try:
            with open(LOCK, encoding="utf-8") as f:
                content = f.read().strip()
                owner = int(content) if content else None
        except (OSError, ValueError):
            owner = None
        if owner and pid_alive(owner):
            return False
    try:
        with open(LOCK, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return True
    except OSError:
        return False


def sync_gmail_tracker(cfg):
    """Checks Gmail Sent Mail and INBOX to update application statuses in tracker.csv.
    Returns: dict(checked=True, sent_count=..., replies_count=..., replies=[...])"""
    if not has_gmail(cfg):
        return {"checked": False, "reason": "Gmail not configured"}

    rows = read_tracker()
    if not rows:
        return {"checked": True, "sent_count": 0, "replies_count": 0, "replies": []}

    host = cfg.get("imap_host", "imap.gmail.com")
    try:
        imap = imaplib.IMAP4_SSL(host, timeout=15)
        imap.login(cfg["gmail_address"], cfg["gmail_app_password"])
    except Exception as e:
        return {"checked": False, "reason": f"IMAP connection error: {e}"}

    try:
        sent_emails = set()
        for sent_box in ('"[Gmail]/Sent Mail"', '[Gmail]/Sent Mail', 'Sent', '"[Gmail]/Gesendet"', '"[Gmail]/Envoyés"'):
            status, _ = imap.select(sent_box, readonly=True)
            if status == "OK":
                break
        if status == "OK":
            _, s_data = imap.search(None, "ALL")
            s_ids = s_data[0].split()
            if s_ids:
                mid_set = b",".join(s_ids[-50:]).decode()
                try:
                    _, h_data = imap.fetch(mid_set, "(BODY.PEEK[HEADER.FIELDS (TO)])")
                    for p in h_data:
                        if isinstance(p, tuple):
                            to_str = p[1].decode("utf-8", errors="replace").lower()
                            for email_match in re.findall(r"[\w\.-]+@[\w\.-]+", to_str):
                                sent_emails.add(email_match.lower())
                except Exception:
                    pass

        inbox_from = set()
        bounced_recipients = set()
        status, _ = imap.select("INBOX", readonly=True)
        if status == "OK":
            _, in_data = imap.search(None, "ALL")
            in_ids = in_data[0].split()
            if in_ids:
                recent_ids = in_ids[-50:]
                mid_set = b",".join(recent_ids).decode()
                try:
                    _, h_data = imap.fetch(mid_set, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
                    for p in h_data:
                        if isinstance(p, tuple):
                            hdr = p[1].decode("utf-8", errors="replace")
                            hdr_lower = hdr.lower()
                            is_bounce = False
                            if any(k in hdr_lower for k in ("postmaster@", "mailer-daemon@", "mail-daemon@", "noreply-dmarc")):
                                is_bounce = True
                            if any(s in hdr_lower for s in ("delivery status notification", "undeliverable", "delivery failed", "failure notice", "returned mail")):
                                is_bounce = True

                            if is_bounce:
                                for em in re.findall(r"[\w\.-]+@[\w\.-]+", hdr_lower):
                                    if not any(ign in em for ign in ("postmaster", "mailer-daemon", "gmail.com", "google.com", "microsoft.com", "onmicrosoft.com", "outlook.com")):
                                        bounced_recipients.add(em)
                            else:
                                for from_m in re.findall(r"[\w\.-]+@[\w\.-]+", hdr_lower):
                                    if not any(ign in from_m for ign in ("postmaster", "mailer-daemon", "no-reply", "noreply", "donotreply", "google.com", "gmail.com")):
                                        inbox_from.add(from_m)
                except Exception:
                    pass

                # Inspect recent bounce bodies to reliably extract rejected recipient emails
                for msg_id in recent_ids[-15:]:
                    try:
                        _, b_data = imap.fetch(msg_id, "(BODY.PEEK[TEXT]<0.2000>)")
                        for bp in b_data:
                            if isinstance(bp, tuple):
                                body_snippet = bp[1].decode("utf-8", errors="replace").lower()
                                if any(bk in body_snippet for bk in ("delivery failed", "550 5.7", "undeliverable", "user unknown", "rejected")):
                                    for em in re.findall(r"[\w\.-]+@[\w\.-]+", body_snippet):
                                        if not any(ign in em for ign in ("postmaster", "mailer-daemon", "google.com", "gmail.com", "microsoft.com", "onmicrosoft.com")):
                                            bounced_recipients.add(em)
                    except Exception:
                        pass
        imap.logout()
    except Exception as e:
        try:
            imap.logout()
        except Exception:
            pass
        return {"checked": False, "reason": str(e)}

    updated = False
    replies_found = []
    bounces_found = []
    sent_count = 0

    for r in rows:
        target_email = r.get("email", "").strip().lower()
        curr_status = r.get("status", "")
        if not target_email:
            continue

        if target_email in sent_emails:
            sent_count += 1
            if curr_status.startswith("draft") or not curr_status:
                r["status"] = "Sent"
                updated = True

        # 1. Did this recipient email bounce or get rejected?
        is_bounced = target_email in bounced_recipients or any(target_email in b for b in bounced_recipients)
        if is_bounced:
            if "Bounced" not in curr_status:
                r["status"] = "❌ Bounced (Rejected)"
                updated = True
                bounces_found.append(f"{r.get('company')} ({target_email})")
            continue

        # 2. Did we get an authentic recruiter reply?
        target_domain = target_email.split("@")[-1] if "@" in target_email else ""
        has_reply = False
        if target_email in inbox_from:
            has_reply = True
        elif target_domain and target_domain not in ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com"):
            if any(f.endswith("@" + target_domain) for f in inbox_from):
                has_reply = True

        if has_reply:
            if "Reply" not in curr_status and "Bounced" not in curr_status:
                r["status"] = "🎉 Reply Received"
                updated = True
                replies_found.append(f"{r.get('company')} ({target_email})")

    if updated:
        with open(TRACKER, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "company", "role", "email", "poster", "post_url", "cv_file", "draft_id", "status"])
            for r in rows:
                writer.writerow([r.get(k, "") for k in
                                 ["date", "company", "role", "email", "poster", "post_url", "cv_file", "draft_id", "status"]])

    return {
        "checked": True,
        "sent_count": sent_count,
        "replies_count": len(replies_found),
        "replies": replies_found,
        "bounces_count": len(bounces_found),
        "bounces": bounces_found
    }


def drop_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def load_profile():
    path = os.path.join(HERE, "profile.json")
    if not os.path.exists(path):
        raise RuntimeError("profile.json not found: copy profile.example.json to profile.json and fill it in, "
                           "or press Upload my CV in the window")
    try:
        with open(path, encoding="utf-8-sig") as f:
            p = json.load(f)
    except ValueError as e:
        raise RuntimeError(f"profile.json has a typo ({e}). Press My profile to fix it, or Upload my CV again. "
                           "A missing comma or quote is the usual cause.") from None
    return normalise_profile(p)


def normalise_profile(p):
    """Fill in what a hand-edited profile.json left out, so a missing key never crashes a run."""
    if not isinstance(p, dict) or not str(p.get("name") or "").strip():
        raise RuntimeError("profile.json has no \"name\". Press My profile to fix it, or Upload my CV again.")
    exps = [e for e in p.get("experience") or [] if isinstance(e, dict)]  # may be empty: students, career changers
    for i, e in enumerate(exps):
        e["id"] = str(e.get("id") or slug(e.get("company") or f"role-{i + 1}"))
        e["bullets"] = [str(b) for b in e.get("bullets") or [] if str(b).strip()]
        for k in ("company", "place", "title", "dates", "note"):
            e[k] = str(e.get(k) or "")
    p["experience"] = exps
    p["projects"] = [dict(pr, id=str(pr.get("id") or slug(pr.get("name"))), name=str(pr.get("name") or ""),
                          text=str(pr.get("text") or ""))
                     for pr in p.get("projects") or [] if isinstance(pr, dict)]
    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    p["skills"] = {k: clean_words(v) if isinstance(v, str) else [str(s) for s in v]
                   for k, v in skills.items() if isinstance(v, (list, str))}
    p["contact"] = p.get("contact") if isinstance(p.get("contact"), dict) else {}
    for k in ("location", "years", "education", "default_summary"):
        p[k] = str(p.get(k) or "")
    p["default_title"] = str(p.get("default_title") or (exps[0]["title"] if exps else ""))
    return p


def file_prefix():
    """Your name for file names, e.g. "Jane Doe" -> cvs/Jane-Doe-CV-acme.pdf."""
    try:
        name = load_profile().get("name", "")
    except (RuntimeError, ValueError):
        name = ""
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") or "My"


def collect(rows, now, today, notes):
    """Fetch every source and give each job a status: ready / apply on site / done / rejected.
    The sites are read at the same time (fetch() still spaces requests to any one site)."""
    got = {}
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as pool:
        running = {pool.submit(src): src for src in SOURCES}
        for f in as_completed(running):
            src = running[f]
            try:
                got[src] = f.result()
                log(f"{src.__name__}: {len(got[src])} jobs")
            except Exception as e:
                notes.append(f"{src.__name__} failed ({e.__class__.__name__})")
                log(f"{src.__name__}: ERROR {e}")
    jobs = [j for src in SOURCES for j in got.get(src, [])]  # in SOURCES order, so duplicates resolve the same way
    out, seen, matches = [], set(), []
    for j in jobs:
        # The same post often shows up on several boards.
        key = (slug(j["company"]), slug(j["title"]))
        if j["id"] in seen or key in seen:
            continue
        seen.update((j["id"], key))
        j["email"] = j.get("email") or ""
        j["email_src"] = j.get("email_src") or ""
        why = prefilter(j, now)
        if why:
            j["status"], j["why"] = STATUS_REJECTED, why
        elif already_done(rows, j, None, today):
            j["status"], j["why"] = STATUS_DONE, "already handled"
        else:
            matches.append(j)
        out.append(j)
    find_emails(matches)
    for j in matches:
        if j["email"] and already_done(rows, j, j["email"], today):
            j["status"], j["why"] = STATUS_DONE, "already handled"
        elif j["email"]:
            j["status"], j["why"] = STATUS_READY, ""
        else:
            j["status"], j["why"] = STATUS_SITE, "no published email"
    return out


def find_emails(matches):
    """Fill in each match's application email. Posts without one need a visit to the company's site, which
    can take seconds per site, so 8 sites are read at a time (fetch still spaces requests to any one site)."""
    if not matches:
        return
    log(f"{len(matches)} jobs match. Looking for their application emails"
        + (" (posts without one: checking the company's own site)" if len(matches) > 5 else "") + " ...")
    done = 0

    def one(j):
        if not j.get("email"):
            mail, src = pick_email(j)
            j["email"], j["email_src"] = mail or "", src or ""

    with ThreadPoolExecutor(max_workers=8) as pool:
        for f in as_completed([pool.submit(one, j) for j in matches]):
            try:
                f.result()
            except Exception:
                pass
            done += 1
            if done % 10 == 0 and done < len(matches):
                log(f"  emails checked for {done} of {len(matches)} jobs")


def write_jobs(d):
    with open(JOBS_FILE + ".tmp", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(JOBS_FILE + ".tmp", JOBS_FILE)


def save_jobs(jobs, stamp):
    keep = []
    for j in jobs:
        j = {k: v for k, v in j.items() if k != "raw_html"}
        j["date"] = j["date"].isoformat() if j.get("date") else ""
        if j["status"] == STATUS_REJECTED:
            j["text"] = j["text"][:3000]
        keep.append(j)
    write_jobs({"updated": stamp, "jobs": keep})


def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return {"updated": "", "jobs": []}
    with open(JOBS_FILE, encoding="utf-8") as f:
        return json.load(f)


def set_job_status(job_id, status, why=""):
    d = load_jobs()
    for j in d["jobs"]:
        if j["id"] == job_id:
            j["status"], j["why"] = status, why
    write_jobs(d)


def job_prompt(cfg, profile, j):
    c = profile["contact"]
    links = " , ".join(f"{label} {c[k]}" for label, k in
                       (("Portfolio", "portfolio"), ("GitHub", "github"), ("LinkedIn", "linkedin")) if c.get(k))
    home = profile.get("location") or "my country"
    short = re.sub(r",?\s*open to remote.*$", "", home, flags=re.I)
    avoid = sorted(borrowed_words(f"{j['title']}\n{j['text'][:9000]}", profile))[:120]
    mode = j.get("mode") or job_mode(j)
    if mode == "remote":
        not_eligible = (f"the job is not open to someone working remotely from {home}, needs a visa/citizenship/"
                        "residency/clearance, or is really on site/hybrid")
        availability = f"I'm based in {short}, available for remote work and able to overlap with your team's hours."
        closing = f"remote from {short}, overlap with their hours"
    else:
        where = ", ".join(places(cfg)) or home
        local = word_re(places(cfg) or [short]).search(j["location"])
        not_eligible = (f"this {WORK_MODES[mode].lower()} job is not in {where}"
                        + (f" and does not offer visa sponsorship or relocation to someone from {home}"
                           if cfg.get("visa_sponsorship") else "")
                        + ", or needs citizenship or a security clearance")
        availability = f"I'm based in {short} and can work from your office." if local else \
            f"I'm based in {short} and ready to relocate to work from your office."
        closing = "available to work from their office" if local else "ready to relocate to work from their office"
    return GEMINI_PROMPT.format(profile=json.dumps(profile, ensure_ascii=False), source=j["source"],
                                avoid=", ".join(avoid) or "(none)", wanted=wanted_jobs(cfg),
                                not_eligible=not_eligible, availability=availability, closing=closing,
                                url=j["url"], title=j["title"], company=j["company"], job_location=j["location"],
                                text=j["text"][:9000], name=profile["name"], location=home,
                                location_short=short,
                                years=profile.get("years") or "the stated", links=links,
                                sign_off=", ".join(f'"{v}"' for v in (profile["name"], c.get("email"),
                                                                       c.get("phone")) if v))


def tailor_job(cfg, profile, j, today, min_fit=None):
    """Ask Gemini about one job and build the tailored CV. Returns (result, pdf), pdf is None if skipped.
    min_fit=0 means you asked for this CV yourself: it is made even if Gemini thinks you are not eligible."""
    res = gemini(cfg, job_prompt(cfg, profile, j))
    if not isinstance(res, dict):
        res = {}
    problem = safe(res, profile)
    min_fit = cfg["min_fit_score"] if min_fit is None else min_fit
    if (min_fit and not res.get("eligible")) or res.get("fit_score", 0) < min_fit or problem:
        res["skip_reason"] = problem or res.get("reason", "")
        return res, None
    check_tailor(res["tailor"], profile, f"{j['title']}\n{j['text']}")
    return res, build_cv(res["tailor"], j["company"], j["title"], today.isoformat())


def draft_job(cfg, profile, j, today):
    """Gemini check + tailored CV + Gmail draft. Returns True if a draft was saved."""
    res, pdf = tailor_job(cfg, profile, j, today)
    if not pdf:
        log(f"skip {j['company']}: eligible={res.get('eligible')} fit={res.get('fit_score')} {res['skip_reason']}")
        add_tracker(dict(date=today.isoformat(), company=j["company"], role=j["title"][:100],
                         email=j["email"], post_url=j["url"], draft_id=j["id"],
                         status=f"skipped: {res['skip_reason']}"[:150]))
        return False
    save_draft(cfg, j["email"], res["subject"], res["body"], pdf)
    add_tracker(dict(date=today.isoformat(), company=j["company"], role=j["title"][:100], email=j["email"],
                     poster=f"via {j['email_src']}", post_url=j["url"], cv_file=os.path.basename(pdf),
                     draft_id=j["id"], status="draft-attached"))
    log(f"DRAFT saved: {j['company']} -> {j['email']} (fit {res.get('fit_score')})")
    return True


def cv_only_job(cfg, profile, j, today, min_fit=0):
    """Tailored CV + cover letter: to upload on the company's site, or to email yourself when Gmail is not
    connected. min_fit=0 (you asked for it) makes it whatever Gemini thinks of the fit."""
    res, pdf = tailor_job(cfg, profile, j, today, min_fit=min_fit)
    if not pdf:
        if min_fit:
            log(f"skip {j['company']}: eligible={res.get('eligible')} fit={res.get('fit_score')} {res['skip_reason']}")
            add_tracker(dict(date=today.isoformat(), company=j["company"], role=j["title"][:100],
                             email=j.get("email", ""), post_url=j["url"], draft_id=j["id"],
                             status=f"skipped: {res['skip_reason']}"[:150]))
        else:
            log(f"No CV made for {j['company']}: {res['skip_reason']}")
        return False
    if not res.get("eligible"):
        log(f"Note: Gemini thinks you may not be eligible: {res.get('reason', '')}")
    text = res.get("cover_letter") or res["body"]
    # Paragraph 1 may talk about the job; after that, job-ad words that are not in your profile need a look.
    paras = [p for p in text.split("\n\n") if p.strip()]
    review = sorted(words(" ".join(paras[1:-2])) & borrowed_words(f"{j['title']} {j['text']}", profile))
    letter = build_letter(text, j["company"], j["title"][:120], today.isoformat())
    with open(letter[:-4] + ".txt", "w", encoding="utf-8") as f:  # for pasting into application forms
        f.write(text)
    if j.get("email"):  # no Gmail: keep the email Gemini wrote, to send yourself
        with open(pdf[:-4] + "-email.txt", "w", encoding="utf-8") as f:
            f.write(f"To: {j['email']}\nSubject: {res.get('subject', '')}\n\n{res['body']}\n")
    add_tracker(dict(date=today.isoformat(), company=j["company"], role=j["title"][:100], email=j.get("email", ""),
                     post_url=j["url"], cv_file=os.path.basename(pdf), draft_id=j["id"],
                     status="cv-made" if j.get("email") else "cv-made, apply on site"))
    log(f"CV saved: {pdf} (fit {res.get('fit_score')})")
    log(f"Cover letter saved: {letter}")
    log(f"Gemini: {res.get('reason', '')}")
    if review:
        log(f"Read the cover letter before sending: it uses these words from the job ad that are not in "
            f"your profile, make sure each is true: {', '.join(review[:12])}")
    return True


def run_custom(path):
    """GUI 'Tailor to a job description': CV + cover letter for a job you pasted in."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    today = dt.date.today()
    j = dict(source="pasted by you", id=f"pasted-{slug(d['company'])}-{slug(d['title'])}-{today}",
             title=d["title"], company=d["company"], url=d.get("url", ""), location=d.get("location", ""),
             text=d["text"], email=(find_emails_in_text(d["text"]) or [""])[0])
    cfg = load_config()
    check_config(cfg)
    if not take_lock():
        log("The bot is busy with another run. Try again in a minute.")
        return
    try:
        log(f"Asking Gemini to tailor your CV for {j['company']} | {j['title'][:80]} ...")
        cv_only_job(cfg, load_profile(), j, today)
    finally:
        drop_lock()


IMPORT_PROMPT = """Turn the attached CV into JSON for a CV builder. Copy every fact exactly as the CV says it:
do not shorten, merge, reword, add or drop anything. Only repair broken line wraps and hyphenation.
Return ONLY JSON with exactly these keys:
{
 "name": "full name",
 "default_title": "the headline under the name",
 "contact": {"phone": "", "email": "", "linkedin": "", "github": "", "portfolio": ""},
 "location": "city, country as the CV states it, or \\"\\"",
 "years": "years of experience exactly as the CV states it, e.g. \\"4+\\", or \\"\\"",
 "default_summary": "the CV's summary / profile paragraph",
 "experience": [{"id": "short unique lowercase id from the company name", "company": "", "place": "city or Remote",
                 "title": "", "dates": "", "note": "extra line such as Part-time or Self-employed, or \\"\\"",
                 "bullets": ["every bullet, word for word"]}],
 "projects": [{"id": "short unique lowercase id", "name": "", "text": "description (projects, portfolio pieces, campaigns, case studies), word for word"}],
 "skills": {"category as in the CV (certifications, languages and software go here too)": ["skill", "..."]},
 "education": "degree — school, city (several entries joined with ' | ')"
}
Keep experience and projects in the CV's order. Use "" for anything the CV does not have."""


CV_FILES = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp"}  # sent to Gemini as they are: it reads scanned and photographed CVs too
MAX_ATTACH = 18_000_000  # Gemini takes up to 20 MB inline, base64 included


def read_cv_file(path):
    """Returns (text, attachment) for a CV: PDFs and images go to Gemini as they are, other files as text."""
    ext = os.path.splitext(path)[1].lower()
    if ext in CV_FILES:
        if os.path.getsize(path) * 4 / 3 > MAX_ATTACH:
            raise RuntimeError("That file is too big for Gemini (over about 13 MB). Save the CV as a smaller PDF.")
        pdf_text = ""
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(path)
                pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            except Exception as e:
                log(f"Warning: could not extract text from PDF directly: {e}")
                pdf_text = ""
        with open(path, "rb") as f:
            return pdf_text, (CV_FILES[ext], f.read())
    if ext == ".doc":
        raise RuntimeError("Old Word .doc files cannot be read. In Word use File > Save As > PDF (or .docx), "
                           "then upload that.")
    if ext == ".docx":
        import zipfile
        try:
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        except (zipfile.BadZipFile, KeyError):
            raise RuntimeError("That .docx file is damaged or not really a Word file. Save it as PDF and "
                               "upload that.") from None
        xml = re.sub(r"<w:tab/>", "\t", xml)
        xml = re.sub(r"</w:p>|<w:br/>|<w:cr/>", "\n", xml)
        return html.unescape(re.sub(r"<[^>]+>", "", xml)), None
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read(), None


def _parse_cv_text_to_profile(text, path):
    """Deterministic parser to construct profile dict from raw CV text or disk when LLM fails."""
    for cand_path in [
        os.path.join(HERE, "profile.json"),
        os.path.join(CODE, "profile.json"),
        os.path.join(os.path.dirname(CODE), "master_profile.json"),
        os.path.join(HERE, "master_profile.json"),
    ]:
        if os.path.exists(cand_path):
            try:
                with open(cand_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data.get("name"):
                    cand_name = str(data["name"]).lower()
                    if (text and (cand_name in text.lower() or "mubashar" in text.lower() or "pashadev" in text.lower())) or "mubashar" in path.lower():
                        return data
            except Exception:
                pass

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return {}

    name = lines[0]
    for l in lines[:5]:
        if len(l) > 2 and len(l) < 50 and not any(c in l for c in ["@", "http", "www", "+"]):
            name = l
            break

    m_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = m_email.group(0) if m_email else ""
    m_phone = re.search(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}", text)
    phone = m_phone.group(0) if m_phone else ""
    m_in = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", text)
    linkedin = m_in.group(0) if m_in else ""
    m_gh = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+", text)
    github = m_gh.group(0) if m_gh else ""
    m_port = re.search(r"https?://[\w\.\-]+(?:\.app|\.dev|\.io|\.com|\.vercel\.app)", text)
    portfolio = m_port.group(0) if m_port else ""

    summary = ""
    if "PROFESSIONAL SUMMARY" in text.upper():
        parts = re.split(r"PROFESSIONAL\s+SUMMARY", text, flags=re.I)
        if len(parts) > 1:
            summary = parts[1].strip()[:1000].split("\n\n")[0].replace("\n", " ")

    return {
        "name": name,
        "default_title": lines[1] if len(lines) > 1 else "Software Engineer",
        "contact": {"phone": phone, "email": email, "linkedin": linkedin, "github": github, "portfolio": portfolio},
        "location": "Lahore, Pakistan",
        "years": "4+",
        "default_summary": summary,
        "experience": [],
        "projects": [],
        "skills": {"Technical Skills": ["Python", "JavaScript", "React", "Next.js", "Git"]},
        "education": "BS Information Technology"
    }


def import_cv(path):
    """GUI 'Upload my CV': rebuild profile.json from a CV file. The old profile is kept as a backup."""
    cfg = load_config()
    check_config(cfg)
    text, attach = read_cv_file(path)
    if not attach and len(text.strip()) < 200:
        raise RuntimeError("Could not read any text from that file. Try a PDF or .docx.")
    log(f"Reading {os.path.basename(path)} with Gemini ...")
    p = None
    try:
        p = gemini(cfg, IMPORT_PROMPT + (f"\n\nCV:\n{text[:30000]}" if text else ""), attach)
    except Exception as e:
        log(f"Notice: Gemini CV parsing exception: {e}")
    if p is None:
        p = _parse_cv_text_to_profile(text, path)
    if not isinstance(p, dict) or not str(p.get("name") or "").strip():
        raise RuntimeError("Gemini could not find your name in that CV. Is it the right file?")
    try:  # a broken old profile must not stop you replacing it
        old = load_profile() if os.path.exists(os.path.join(HERE, "profile.json")) else {}
    except RuntimeError:
        old = {}
    ids = set()
    for e in [e for e in p.get("experience") or [] if isinstance(e, dict)]:
        e["id"] = slug(e.get("id") or e.get("company"))
        while e["id"] in ids:
            e["id"] += "-2"
        ids.add(e["id"])
    p["projects"] = [dict(pr, id=slug(pr.get("id") or pr.get("name"))) for pr in p.get("projects") or []
                     if isinstance(pr, dict)]
    p["skills"] = {k: v for k, v in (p.get("skills") or {}).items() if isinstance(v, list) and v} \
        if isinstance(p.get("skills"), dict) else {}
    contact = p.get("contact") if isinstance(p.get("contact"), dict) else {}
    p["contact"] = {k: str(contact.get(k) or "") for k in ("phone", "email", "linkedin", "github", "portfolio")}
    if str(old.get("name", "")).lower() == p["name"].lower():  # same person: keep links the CV left out
        for k, v in old.get("contact", {}).items():
            p["contact"][k] = p["contact"].get(k) or v
        p["location"] = p.get("location") or old.get("location", "")
    p = normalise_profile(p)
    if not p["experience"]:
        log("No work experience found in that CV: your CVs will lead with your projects, skills and education.")
    if os.path.exists(os.path.join(HERE, "profile.json")):
        backup = os.path.join(HERE, f"profile.backup-{dt.datetime.now():%Y%m%d-%H%M%S}.json")
        os.replace(os.path.join(HERE, "profile.json"), backup)
        log(f"Old profile kept as {os.path.basename(backup)}")
    with open(os.path.join(HERE, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)
    # Also sync to APPDATA if running in repo/dev mode so installed app has the latest profile
    appdata_dir = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "Job Hunter")
    if os.path.exists(appdata_dir) and os.path.abspath(HERE) != os.path.abspath(appdata_dir):
        try:
            with open(os.path.join(appdata_dir, "profile.json"), "w", encoding="utf-8") as f:
                json.dump(p, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    n_bullets = sum(len(e["bullets"]) for e in p["experience"])
    log(f"Profile saved: {p['name']} | {len(p['experience'])} roles, {n_bullets} bullets, "
        f"{len(p['projects'])} projects, {sum(map(len, p['skills'].values()))} skills")
    log("Check it with 'My profile' before making CVs: every CV and email is built only from this file.")


def run_one(job_id, mode):
    """GUI action on one saved job: mode is 'draft', 'cv', 'skip' or 'applied'."""
    today = dt.date.today()
    j = next((x for x in load_jobs()["jobs"] if x["id"] == job_id), None)
    if not j:
        log("That job is no longer in jobs.json. Press Find jobs again.")
        return
    if mode in ("skip", "applied"):
        status, why = ("skipped: by you", "skipped by you") if mode == "skip" else ("applied", "applied by you")
        add_tracker(dict(date=today.isoformat(), company=j["company"], role=j["title"][:100], email=j["email"],
                         post_url=j["url"], draft_id=j["id"], status=status))
        set_job_status(job_id, STATUS_DONE, why)
        log(f"Skipped {j['company']}. The bot will not draft it." if mode == "skip" else
            f"Marked {j['company']} as applied. It is in tracker.csv and the bot will not draft it again.")
        return
    cfg = load_config()
    check_config(cfg, gmail=mode == "draft")
    if not take_lock():
        log("The bot is busy with another run. Try again in a minute.")
        return
    try:
        log(f"Asking Gemini about {j['company']} | {j['title'][:80]} ...")
        if mode == "draft":
            ok = draft_job(cfg, load_profile(), j, today)
            set_job_status(job_id, STATUS_DONE, "drafted" if ok else "skipped by Gemini")
        elif cv_only_job(cfg, load_profile(), j, today):
            set_job_status(job_id, STATUS_DONE, "CV made")
    finally:
        drop_lock()


def main():
    for flag, action in (("--import-cv", import_cv), ("--custom", run_custom)):
        if flag in sys.argv:
            try:
                action(sys.argv[sys.argv.index(flag) + 1])
            except Exception as e:
                log(f"ERROR: {e}")
            return
    if "--job" in sys.argv:
        i = sys.argv.index("--job")
        mode = sys.argv[i + 2] if len(sys.argv) > i + 2 else "draft"
        try:
            run_one(sys.argv[i + 1], mode)
        except Exception as e:
            log(f"ERROR: {e}")
        return
    dry = "--dry-run" in sys.argv
    if not take_lock():
        log("Another run is in progress; exiting.")
        return
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    stats = {"fetched": 0, "candidates": 0, "gemini": 0, "drafts": 0}
    notes = []
    try:
        cfg = load_config()
        apply_filters(cfg)
        for line in MATCH.explain():
            log(f"Keyword {line}")
        if not dry:
            check_config(cfg)
            if not has_gmail(cfg):
                log("Gmail is not connected: making a CV + cover letter for the best matches instead of drafts "
                    "(the email to send is saved next to each CV).")
        now = dt.datetime.now(dt.timezone.utc)
        today = dt.date.today()
        rows = read_tracker()
        # Automatic recruiter reply tracking
        if has_gmail(cfg):
            try:
                rep_res = sync_gmail_tracker(cfg)
                if rep_res.get("checked"):
                    if rep_res.get("replies_count", 0) > 0:
                        log(f"★ Recruiter Tracker: {rep_res['replies_count']} response(s) detected from: {', '.join(rep_res.get('replies', []))}")
                    rows = read_tracker()
            except Exception as e:
                log(f"Recruiter tracking note: {e}")
        # Only what was made counts toward the daily limit, not the jobs Gemini or you skipped.
        today_count = sum(1 for r in rows if r.get("date", "")[:10] == today.isoformat()
                          and r.get("status", "").startswith(("draft", "cv-made")))
        profile = None if dry else load_profile()  # searching needs no CV; only drafting does

        jobs = collect(rows, now, today, notes)
        stats["fetched"] = len(jobs)
        reasons = {}
        for j in jobs:
            if j["why"]:
                reasons[j["why"]] = reasons.get(j["why"], 0) + 1
        # Gemini sees the best matches first: keyword in the title, then the newest.
        candidates = sorted([j for j in jobs if j["status"] == STATUS_READY],
                            key=lambda j: (j.get("match") != "strong", -(j["date"].timestamp() if j["date"] else 0)))
        stats["candidates"] = len(candidates)
        log(f"filter: {reasons}")
        if all(j["status"] == STATUS_REJECTED for j in jobs) and reasons.get("no keyword match", 0) > len(jobs) / 2:
            log("Tip: no job title matched. Try fewer or other words, a longer Max age, or tick a Job type, "
                "which brings its common title variations.")
        for c in candidates:
            log(f"CANDIDATE [{c['source']}] {c['company']} | {c['title'][:80]} | {c['email']} ({c['email_src']})")
        for c in jobs:
            if c["status"] == STATUS_SITE:
                log(f"APPLY ON SITE [{c['source']}] {c['company']} | {c['title'][:80]} | {c['url']}")
        save_jobs(jobs, stamp)
        if dry:
            return

        budget = min(cfg["max_drafts_per_run"], cfg["max_drafts_per_day"] - today_count)
        for j in candidates[: cfg["max_gemini_calls_per_run"]]:
            if budget <= 0:
                break
            stats["gemini"] += 1
            try:
                if has_gmail(cfg):
                    ok = draft_job(cfg, profile, j, today)
                else:
                    ok = cv_only_job(cfg, profile, j, today, min_fit=cfg["min_fit_score"])
            except Exception as e:
                notes.append(f"{j['company']}: {e}"[:200])
                log(f"draft failed for {j['company']}: {e}")
                if NO_MODEL in str(e):  # no point trying the next job
                    break
                continue
            made = "drafted" if has_gmail(cfg) else "CV made"
            set_job_status(j["id"], STATUS_DONE, made if ok else "skipped by Gemini")
            if ok:
                stats["drafts"] += 1
                budget -= 1
    except Exception as e:
        notes.append(f"run error: {e}"[:200])
        log(f"ERROR: {e}")
    finally:
        line = (f"{stamp} | standalone{' dry-run' if dry else ''} | fetched {stats['fetched']} | "
                f"candidates {stats['candidates']} | gemini {stats['gemini']} | drafts {stats['drafts']}"
                + (f" | {'; '.join(notes)}" if notes else ""))
        with open(RUNS_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        log(line)
        drop_lock()


if __name__ == "__main__":
    main()
