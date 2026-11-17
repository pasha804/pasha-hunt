"""Build a tailored CV PDF from profile.json plus a small tailoring file.

Usage: python -I cv.py <tailor.json> <out.pdf>
       python -I cv.py --letter <letter.json> <out.pdf>

The tailoring file can only pick, reorder and emphasise facts that already
exist in profile.json. The free text is "summary" and the reworded bullets,
which bot.py checks against profile.json before they get here.

tailor.json fields (all optional):
  title         headline under the name
  summary       2-4 sentences, facts from profile.json only
  skills_first  skills to list first inside their categories
  bullets       {"<experience id>": [bullet indexes in the order to show]}
  rewrites      {"<experience id>": {"<bullet index>": "same bullet, reworded for the job"}}
  projects      [project ids to include, in order]

letter.json fields: company, role, text (paragraphs separated by blank lines)
"""
import datetime as dt
import html
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

FROZEN = getattr(sys, "frozen", False)  # the installed JobHunter.exe keeps your files in %APPDATA%\Job Hunter
HERE = os.environ.get("JOBHUNTER_HOME") or (
    os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "Job Hunter") if FROZEN
    else os.path.dirname(os.path.abspath(__file__)))
# Edge comes with Windows; Chrome is the fallback when Edge is missing or broken (e.g. a half-installed update).
BROWSERS = [os.path.join(os.environ.get(v, ""), path)
            for path in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe")
            for v in ("ProgramFiles(x86)", "ProgramFiles", "LocalAppData")]
BROWSERS = [p for p in dict.fromkeys(BROWSERS) if os.path.exists(p)]

CSS = """
@page { size: A4; margin: 12mm 15mm; }
@media print {
  body { background: #fff !important; padding: 0 !important; margin: 0 !important; }
  .page-container { box-shadow: none !important; margin: 0 !important; padding: 0 !important; width: 100% !important; max-width: 100% !important; }
  .page-badge { display: none !important; }
}
@media screen {
  body {
    background: #0B0F14;
    padding: 24px 12px;
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .page-container {
    background: #FFFFFF;
    width: 210mm;
    max-width: 95%;
    min-height: 297mm;
    margin: 0 auto 24px auto;
    padding: 16mm 20mm;
    box-shadow: 0 10px 35px rgba(0,0,0,0.4);
    border-radius: 6px;
    box-sizing: border-box;
    color: #1a1a1a;
  }
  .page-badge {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8pt;
    color: #64748B;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px dashed #CBD5E1;
    font-family: monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}
body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif; font-size: 10pt; color: #1a1a1a; line-height: 1.4; }
h1 { font-size: 20pt; margin: 0; color: #070A0E; font-weight: 800; }
.title { color: #0f766e; font-weight: 700; font-size: 11pt; margin: 2px 0 4px; }
.contact { font-size: 9pt; color: #444; }
h2 { font-size: 9.5pt; letter-spacing: 1.5px; color: #0f766e; border-bottom: 1.5px solid #0f766e; padding-bottom: 2px; margin: 12px 0 6px; text-transform: uppercase; font-weight: 700; }
.role { display: flex; justify-content: space-between; margin-top: 8px; page-break-inside: avoid; }
.role .dates { color: #555; font-size: 8.5pt; white-space: nowrap; }
.note { color: #555; font-size: 8.5pt; }
ul { margin: 2px 0 0 0; padding-left: 16px; }
li { margin: 2px 0; }
table { border-collapse: collapse; width: 100%; }
td { vertical-align: top; padding: 2px 10px 2px 0; font-size: 9.5pt; }
td.k { font-weight: 700; white-space: nowrap; color: #334155; width: 170px; }
.letter { font-size: 10.5pt; line-height: 1.55; margin-top: 16px; }
.letter p { margin: 0 0 10px; }
.meta { margin-top: 14px; color: #444; }
"""


def esc(s):
    return html.escape(s, quote=False)


def header(profile, title):
    c = profile.get("contact") or {}
    return [f"<h1>{esc(profile['name'])}</h1>", f"<div class='title'>{esc(title)}</div>",
            "<div class='contact'>" + " · ".join(esc(c[k]) for k in
                ("phone", "email", "linkedin", "github", "portfolio") if c.get(k)) + "</div>"]


def page(body):
    return (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Executive ATS Master Document</title>"
        f"<style>{CSS}</style></head>"
        f"<body><div class='page-container'>"
        f"<div class='page-badge'><span>⚡ Verified Executive ATS Standard</span><span>1-Column Chronological Layout</span></div>"
        f"{body}</div></body></html>"
    )


def build(profile, t):
    out = header(profile, t.get("title") or profile.get("default_title", ""))
    summary = t.get("summary") or profile.get("default_summary")
    if summary:
        out += ["<h2>SUMMARY</h2>", f"<div>{esc(summary)}</div>"]
    if profile.get("experience"):  # a student's or career changer's CV may have none
        out.append("<h2>EXPERIENCE</h2>")
    order = t.get("bullets") or {}
    for e in profile.get("experience") or []:
        lines = e.get("bullets") or []
        idx = [int(i) for i in order.get(e.get("id"), range(len(lines))) if str(i).isdigit()]
        reworded = (t.get("rewrites") or {}).get(e.get("id")) or {}
        bullets = [reworded.get(str(i)) or lines[i] for i in idx if i < len(lines)]
        where = ", ".join([f"<b>{esc(e['company'])}</b>"] * bool(e.get("company")) + [esc(e.get("place", ""))] * bool(e.get("place")))
        role_title = e.get("title") or e.get("role") or ""
        out.append(f"<div class='role'><div>{where}" + (f" — {esc(role_title)}" if role_title else "")
                   + f"</div><div class='dates'>{esc(e.get('dates') or e.get('years') or '')}</div></div>")
        if e.get("note"):
            out.append(f"<div class='note'>{esc(e['note'])}</div>")
        if bullets:
            out.append("<ul>" + "".join(f"<li>{esc(b)}</li>" for b in bullets) + "</ul>")
    # Render Projects
    projects = profile.get("projects") or []
    if isinstance(projects, dict):
        projects = list(projects.values())
    if projects:
        proj_items = []
        for p in projects:
            p_name = p.get("name") or p.get("title") or "Key Initiative"
            p_desc = p.get("text") or p.get("description") or ""
            if isinstance(p_desc, list):
                p_desc = " · ".join(p_desc)
            p_tech = p.get("technologies") or p.get("tech") or ""
            if isinstance(p_tech, list):
                p_tech = ", ".join(p_tech)
            tech_str = f" <em>({esc(p_tech)})</em>" if p_tech else ""
            proj_items.append(f"<li><b>{esc(p_name)}</b>{tech_str}: {esc(p_desc)}</li>")
        out.append("<h2>PROJECTS &amp; PORTFOLIO</h2><ul>" + "".join(proj_items) + "</ul>")

    first = [str(s).lower() for s in t.get("skills_first") or []]
    rows = []
    for cat, skills in (profile.get("skills") or {}).items():
        skills = [s.strip() for s in skills.split(",")] if isinstance(skills, str) else [str(s) for s in skills]
        ranked = sorted(skills, key=lambda s: first.index(s.lower()) if s.lower() in first else len(first))
        rows.append(f"<tr><td class='k'>{esc(cat)}</td><td>{esc(', '.join(ranked))}</td></tr>")
    if rows:
        out.append("<h2>SKILLS &amp; TECHNOLOGIES</h2><table>" + "".join(rows) + "</table>")

    # Render Certifications
    certs = profile.get("certifications") or profile.get("certificates") or []
    if certs:
        if isinstance(certs, list):
            cert_items = "".join(f"<li>{esc(str(c))}</li>" for c in certs)
        else:
            cert_items = f"<li>{esc(str(certs))}</li>"
        out.append("<h2>CERTIFICATIONS &amp; CREDENTIALS</h2><ul>" + cert_items + "</ul>")

    # Render Education
    edu = profile.get("education")
    if edu:
        if isinstance(edu, list):
            edu_items = "".join(f"<li><b>{esc(str(e.get('degree', '') if isinstance(e, dict) else e))}</b> — {esc(str(e.get('institution', '')) if isinstance(e, dict) else '')} {esc(str(e.get('year', '') if isinstance(e, dict) else ''))}</li>" for e in edu)
            out.append("<h2>EDUCATION</h2><ul>" + edu_items + "</ul>")
        else:
            out.append(f"<h2>EDUCATION</h2><div><b>{esc(str(edu))}</b></div>")
    return page("".join(out))


def build_letter(profile, letter):
    out = header(profile, profile.get("default_title", ""))
    out.append(f"<div class='meta'>{dt.date.today():%d %B %Y}<br>{esc(letter.get('company', ''))}"
               + (f"<br><b>Re: {esc(letter['role'])}</b>" if letter.get("role") else "") + "</div>")
    paras = [p.strip() for p in letter["text"].replace("\r", "").split("\n\n") if p.strip()]
    out.append("<div class='letter'>" + "".join(f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in paras) + "</div>")
    return page("".join(out))


def print_pdf(html_file, out_pdf):
    """Print the page to PDF with the first browser that manages it. Returns the error when none does."""
    error = "Microsoft Edge or Chrome not found. Install it from https://www.microsoft.com/edge"
    out_pdf = os.path.abspath(out_pdf)
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)

    for exe in BROWSERS:
        if not os.path.exists(exe):
            continue
        for flag in ["--headless=new", "--headless"]:
            profile_dir = tempfile.mkdtemp(prefix="pashahunt_pdf_")
            try:
                cmd = [
                    exe, flag, "--disable-gpu", "--no-pdf-header-footer",
                    "--disable-crash-reporter", "--no-first-run", "--no-default-browser-check",
                    "--disable-background-networking", "--disable-sync", "--disable-extensions",
                    f"--user-data-dir={profile_dir}", f"--print-to-pdf={out_pdf}",
                    pathlib.Path(html_file).as_uri()
                ]
                r = subprocess.run(cmd, timeout=30, capture_output=True)
                if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 500:
                    return None
            except (OSError, subprocess.TimeoutExpired) as e:
                error = f"{os.path.basename(exe)} could not make the PDF ({e.__class__.__name__})"
                continue
            finally:
                try:
                    shutil.rmtree(profile_dir, ignore_errors=True)
                except Exception:
                    pass
        if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 500:
            return None
        error = (f"{os.path.basename(exe)} made no PDF. Restart Windows to finish any "
                 "Edge update, or update Edge in edge://settings/help")
    return error


def generate_master_cv(profile_dict=None, out_pdf=None):
    """Programmatic helper to build and compile the ATS Master CV PDF."""
    if profile_dict is None:
        prof_file = os.path.join(HERE, "profile.json")
        if not os.path.exists(prof_file):
            prof_file = os.path.join(os.path.dirname(HERE), "profile.json")
        with open(prof_file, "r", encoding="utf-8-sig") as f:
            profile_dict = json.load(f)
    if out_pdf is None:
        out_pdf = os.path.join(HERE, "active_user_cv.pdf")

    html_content = build(profile_dict, {})
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name
    try:
        err = print_pdf(tmp_path, out_pdf)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "path": out_pdf, "size": os.path.getsize(out_pdf)}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def generate_cover_letter_pdf(profile_dict, company, role, letter_text, out_pdf):
    """Generates an executive-ready Cover Letter PDF matching the ATS Master CV styling."""
    letter_obj = {
        "company": company,
        "role": role,
        "text": letter_text
    }
    html_content = build_letter(profile_dict, letter_obj)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name
    try:
        err = print_pdf(tmp_path, out_pdf)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "path": out_pdf, "size": os.path.getsize(out_pdf)}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    is_letter = sys.argv[1] == "--letter"
    data_path, out_pdf = sys.argv[1 + is_letter], os.path.abspath(sys.argv[2 + is_letter])
    with open(os.path.join(HERE, "profile.json"), encoding="utf-8-sig") as f:
        profile = json.load(f)
    with open(data_path, encoding="utf-8-sig") as f:
        t = json.load(f)
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(build_letter(profile, t) if is_letter else build(profile, t))
        tmp = f.name
    try:
        error = print_pdf(tmp, out_pdf)
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass
    if error:
        sys.exit(error)
    print(out_pdf)

if __name__ == "__main__":
    main()
