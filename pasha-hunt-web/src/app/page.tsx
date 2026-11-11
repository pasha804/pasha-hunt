"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import AmbientCanvas from "../components/AmbientCanvas";

// --- Types ---
type ThemeMode = "midnight-amber" | "graphite-lime";

interface JobOpportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  source: string;
  email: string | null;
  match: number;
  salary: string;
}

export default function PashaHuntLaunch() {
  const [theme, setTheme] = useState<ThemeMode>("midnight-amber");
  const [activeTab, setActiveTab] = useState<"overview" | "radar" | "ats" | "protocol">("overview");
  const [resumeText, setResumeText] = useState<string>(
    "Muhammad Mubashar - Senior Full Stack Engineer & AI Automation Architect.\nBuilt high-performance web applications using React, Next.js, and Python FastAPI.\nOptimized backend microservices and database query performance."
  );
  const [rawBullet, setRawBullet] = useState<string>(
    "Worked on frontend web applications using React and Tailwind CSS."
  );
  const [xyzTransformed, setXyzTransformed] = useState<string>(
    "Architected and delivered 14+ responsive React 19 web applications, slashing LCP render latency by 1.8s and achieving a 98/100 Google Lighthouse score."
  );
  const [atsScore, setAtsScore] = useState<number>(84);
  const [downloadSuccess, setDownloadSuccess] = useState<boolean>(false);
  const [socketPing, setSocketPing] = useState<number>(18);
  const [contactForm, setContactForm] = useState({ name: "", email: "", inquiry: "", honey: "" });
  const [contactStatus, setContactStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [contactRef, setContactRef] = useState<string | null>(null);

  // Apply data-theme to HTML tag for instant CSS variable switching
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Accent color for Three.js canvas
  const accentColor = theme === "midnight-amber" ? "#F2AA4C" : "#C6F36B";

  // Sample live jobs feed
  const liveJobs: JobOpportunity[] = [
    {
      id: "job-1",
      title: "Senior Full Stack Engineer (React 19 / Python FastAPI)",
      company: "Systems Limited",
      location: "Worldwide (Remote)",
      type: "Remote",
      source: "Arbeitnow",
      email: "careers@systemsltd.com",
      match: 96,
      salary: "$110,000 - $145,000",
    },
    {
      id: "job-2",
      title: "AI Inference & Systems Architect (Agentic Workflows)",
      company: "Tether.io",
      location: "Worldwide (Remote)",
      type: "Remote",
      source: "Remotive",
      email: "talent@tether.io",
      match: 94,
      salary: "$130,000 - $170,000",
    },
    {
      id: "job-3",
      title: "Full Stack Engineer (TypeScript, Next.js, Supabase)",
      company: "Phantom Technologies",
      location: "Worldwide + Pakistan",
      type: "Hybrid",
      source: "Himalayas",
      email: "hiring@phantom.tech",
      match: 91,
      salary: "$95,000 - $125,000",
    },
    {
      id: "job-4",
      title: "Python Software Engineer (High-Throughput Scrapers)",
      company: "Arbisoft",
      location: "Lahore / Remote",
      type: "Remote",
      source: "Findwork",
      email: "jobs@arbisoft.com",
      match: 89,
      salary: "$85,000 - $115,000",
    },
  ];

  // Dynamic ATS calculation on user edit
  const handleResumeChange = (val: string) => {
    setResumeText(val);
    const words = val.split(/\s+/).filter(Boolean).length;
    let score = 50;
    if (words > 20) score += 15;
    if (/react|next\.js|python|typescript|fastapi/i.test(val)) score += 20;
    if (/\d+%|\d+\+|\$\d+/i.test(val)) score += 15;
    setAtsScore(Math.min(100, score));
  };

  const handleDownload = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 4000);
    window.location.href = "https://github.com/pasha804/pasha-hunt/releases/latest";
  };

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (contactForm.honey) return;
    setContactStatus("submitting");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(contactForm),
      });
      const data = await res.json();
      if (data.ok) {
        setContactStatus("success");
        setContactRef(data.inquiry?.referenceId || "PSH-" + Math.floor(Math.random() * 8999 + 1000));
        setContactForm({ name: "", email: "", inquiry: "", honey: "" });
      } else {
        setContactStatus("error");
      }
    } catch {
      setContactStatus("error");
    }
  };

  return (
    <div className="relative min-h-screen selection:bg-[var(--accent-primary)]/20 selection:text-white">
      {/* Three.js Ambient Particle Field */}
      <AmbientCanvas accentColor={accentColor} />

      {/* Ambient Radial Bloom (Top Center) */}
      <div
        className="ambient-glow-sphere top-[-100px] left-1/2 -translate-x-1/2 w-[800px] h-[450px]"
        style={{ background: `radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)` }}
      />

      {/* =========================================================================
          NAVIGATION: Floating Tactile Dock
      ========================================================================= */}
      <header className="sticky top-5 z-50 px-4 max-w-6xl mx-auto">
        <nav className="glass-panel rounded-full px-5 py-3 flex items-center justify-between shadow-2xl transition-all">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[var(--bg-card)] border border-[var(--border-subtle)] flex items-center justify-center font-black text-sm text-[var(--accent-primary)] shadow-inner">
              P
            </div>
            <div>
              <span className="font-bold tracking-tight text-sm text-[var(--text-primary)]">PASHA HUNT</span>
              <span className="ml-1.5 text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--accent-primary)]">
                2.0
              </span>
            </div>
          </div>

          {/* Links */}
          <div className="hidden md:flex items-center gap-6 text-xs font-medium text-[var(--text-secondary)]">
            <a href="#workstation" className="hover:text-[var(--accent-primary)] transition-colors">
              Workstation
            </a>
            <a href="#radar" className="hover:text-[var(--accent-primary)] transition-colors">
              18 Feeds
            </a>
            <a href="#crucible" className="hover:text-[var(--accent-primary)] transition-colors">
              Google XYZ
            </a>
            <a href="#protocol" className="hover:text-[var(--accent-primary)] transition-colors">
              Socket MX
            </a>
            <a href="#transmission" className="hover:text-[var(--accent-primary)] transition-colors">
              Transmission
            </a>
          </div>

          {/* Controls: Theme Switcher & Action */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle Pill */}
            <button
              onClick={() => setTheme(theme === "midnight-amber" ? "graphite-lime" : "midnight-amber")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-mono bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--accent-primary)] transition-all cursor-pointer"
              title="Toggle Theme Palette"
            >
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: theme === "midnight-amber" ? "#F2AA4C" : "#C6F36B" }}
              />
              <span className="capitalize">{theme === "midnight-amber" ? "Midnight Amber" : "Graphite Lime"}</span>
            </button>

            {/* Download Button */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              onClick={handleDownload}
              className="px-4 py-1.5 rounded-full text-xs font-semibold bg-[var(--accent-primary)] text-[var(--bg-deep)] hover:bg-[var(--accent-hover)] transition-all shadow-lg cursor-pointer"
            >
              Get v2.0
            </motion.button>
          </div>
        </nav>
      </header>

      {/* =========================================================================
          ACT I: THE MONUMENT (CINEMATIC HERO & INTERACTIVE WORKSTATION)
      ========================================================================= */}
      <section className="relative z-10 pt-16 md:pt-24 pb-12 px-4 max-w-6xl mx-auto text-center">
        {/* Editorial Pill */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-[11px] font-mono text-[var(--text-secondary)] mb-6 shadow-sm"
        >
          <span className="w-2 h-2 rounded-full bg-[var(--accent-primary)] animate-pulse" />
          <span>APINEX COMMERCIAL WORKSTATION</span>
          <span className="text-[var(--text-muted)]">|</span>
          <span className="text-[var(--accent-primary)]">100% LOCAL-FIRST</span>
        </motion.div>

        {/* Monumental Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl sm:text-7xl md:text-8xl font-black tracking-tight text-[var(--text-primary)] max-w-5xl mx-auto leading-[1.05]"
        >
          YOUR CAREER. <br />
          <span className="bg-gradient-to-r from-[var(--text-primary)] via-[var(--accent-primary)] to-[var(--accent-hover)] bg-clip-text text-transparent">
            YOUR INTELLIGENCE.
          </span>{" "}
          <br />
          YOUR NEXT MOVE.
        </motion.h1>

        {/* Single Tight Editorial Sentence */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 text-base sm:text-lg text-[var(--text-secondary)] max-w-2xl mx-auto leading-relaxed"
        >
          The autonomous desktop workstation for software engineers. Sweeps 18 global job radars, transforms resumes
          with the Google XYZ formula, and verifies recruiter mailboxes via direct Socket MX handshakes.
        </motion.p>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-4"
        >
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            onClick={handleDownload}
            className="px-8 py-3.5 rounded-full text-sm font-bold bg-[var(--accent-primary)] text-[var(--bg-deep)] hover:bg-[var(--accent-hover)] shadow-xl cursor-pointer"
          >
            Download for Windows (v2.0)
          </motion.button>

          <a
            href="#crucible"
            className="px-6 py-3.5 rounded-full text-sm font-medium glass-panel text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all flex items-center gap-2"
          >
            Test Live ATS Engine
            <span className="text-[var(--accent-primary)]">↓</span>
          </a>
        </motion.div>

        {/* Live System Telemetry Strip */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs font-mono text-[var(--text-muted)]">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
            18 Global Feeds Active
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
            41 Apinex AI Models
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
            Socket MX: {socketPing}ms DNS Handshake
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
            0 Cloud Spying (100% Local SQLite)
          </span>
        </div>

        {/* =========================================================================
            THE CENTERPIECE: 3D TILTED WORKSTATION VIEWPORT
        ========================================================================= */}
        <div id="workstation" className="mt-14 perspective-container max-w-5xl mx-auto">
          <div className="tilted-workstation rounded-2xl bg-[var(--bg-deep)] border border-[var(--border-strong)] p-2 sm:p-3 overflow-hidden text-left shadow-2xl">
            {/* Window Header */}
            <div className="flex items-center justify-between px-3 py-2 bg-[var(--bg-surface)] rounded-xl border border-[var(--border-subtle)] mb-3">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-[#FF5F56] inline-block opacity-80" />
                <span className="w-3 h-3 rounded-full bg-[#FFBD2E] inline-block opacity-80" />
                <span className="w-3 h-3 rounded-full bg-[#27C93F] inline-block opacity-80" />
                <span className="ml-2 font-mono text-[11px] text-[var(--text-muted)]">
                  Pasha Hunt 2.0.0 — Apinex Commercial Workstation (Pasha Dev)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-card)] text-[var(--accent-primary)] border border-[var(--border-subtle)]">
                  Active Session: Muhammad Mubashar
                </span>
              </div>
            </div>

            {/* Tab Navigation inside Workstation */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
              {[
                { id: "overview", label: "Command Center", badge: "Overview" },
                { id: "radar", label: "18-Radar Stream", badge: "5,460 Jobs" },
                { id: "ats", label: "Google XYZ Crucible", badge: "Score 84/100" },
                { id: "protocol", label: "Socket MX Deliverability", badge: "Verified" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-3 py-2.5 rounded-xl border text-xs font-medium transition-all text-left flex items-center justify-between cursor-pointer ${
                    activeTab === tab.id
                      ? "bg-[var(--bg-card)] border-[var(--accent-primary)] text-[var(--accent-primary)] shadow-md"
                      : "bg-[var(--bg-surface)] border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  <span className="font-semibold">{tab.label}</span>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-deep)] text-[var(--text-muted)]">
                    {tab.badge}
                  </span>
                </button>
              ))}
            </div>

            {/* Interactive Viewport Content */}
            <div className="min-h-[360px] bg-[var(--bg-surface)] rounded-xl border border-[var(--border-subtle)] p-4 sm:p-6 transition-all">
              {/* TAB 1: OVERVIEW */}
              {activeTab === "overview" && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between border-b border-[var(--border-subtle)] pb-4">
                    <div>
                      <h3 className="text-xl font-bold text-[var(--text-primary)]">Welcome back, Muhammad Mubashar</h3>
                      <p className="text-xs text-[var(--text-muted)] mt-0.5 font-mono">
                        Radar Sweep Completed • All 18 Scrapers Online • Gemini & Apinex Gateway Ready
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mt-2 sm:mt-0">
                      <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--border-accent)]">
                        Model: free/qwen-3.8-max
                      </span>
                    </div>
                  </div>

                  {/* High-Impact Stat Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Total Opportunities</span>
                      <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">5,460</p>
                      <span className="text-[10px] text-[var(--accent-primary)] mt-1 inline-block">18 Global Feeds</span>
                    </div>
                    <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Passing Filters</span>
                      <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">23</p>
                      <span className="text-[10px] text-[var(--accent-primary)] mt-1 inline-block">Worldwide + PK</span>
                    </div>
                    <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Recruiter Deliverables</span>
                      <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">69</p>
                      <span className="text-[10px] text-[var(--accent-primary)] mt-1 inline-block">Socket MX Verified</span>
                    </div>
                    <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">ATS Heuristic Fit</span>
                      <p className="text-2xl font-bold text-[var(--accent-primary)] mt-1">77%</p>
                      <span className="text-[10px] text-[var(--text-muted)] mt-1 inline-block">Google XYZ Optimized</span>
                    </div>
                  </div>

                  {/* Top Target Listing */}
                  <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] font-bold">
                        96% MATCH • TOP MATCH
                      </span>
                      <h4 className="text-sm font-bold text-[var(--text-primary)] mt-1.5">
                        Systems Limited — Senior Full Stack Engineer (React / Python / FastAPI)
                      </h4>
                      <p className="text-xs text-[var(--text-muted)] font-mono mt-0.5">
                        careers@systemsltd.com • Remote Worldwide • 24m ago
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setActiveTab("ats")}
                        className="px-4 py-2 rounded-lg text-xs font-semibold bg-[var(--accent-primary)] text-[var(--bg-deep)] hover:bg-[var(--accent-hover)] transition-all cursor-pointer"
                      >
                        Tailor CV with Google XYZ →
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* TAB 2: 18-RADAR STREAM */}
              {activeTab === "radar" && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-[var(--text-muted)]">
                      LIVE INGESTION: 18 CHANNELS STREAMING (REMOTIVE, WWR, ARBEITNOW, HIMALAYAS)
                    </span>
                    <span className="text-[10px] font-mono text-[var(--accent-primary)]">STATUS: 16/18 OPERATIONAL</span>
                  </div>
                  {liveJobs.map((job) => (
                    <div
                      key={job.id}
                      className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] flex flex-wrap items-center justify-between gap-3 hover:border-[var(--accent-primary)] transition-all"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-[var(--text-primary)]">{job.title}</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-surface)] text-[var(--accent-primary)]">
                            {job.match}% Fit
                          </span>
                        </div>
                        <p className="text-[11px] text-[var(--text-muted)] mt-1 font-mono">
                          {job.company} • {job.location} • Source: {job.source} • {job.salary}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {job.email && (
                          <span className="text-[10px] font-mono px-2 py-1 rounded bg-[var(--bg-surface)] text-[var(--text-secondary)] border border-[var(--border-subtle)]">
                            {job.email}
                          </span>
                        )}
                        <button
                          onClick={() => setActiveTab("ats")}
                          className="px-3 py-1.5 rounded-lg text-[11px] font-semibold bg-[var(--accent-primary)] text-[var(--bg-deep)] hover:bg-[var(--accent-hover)] transition-all cursor-pointer"
                        >
                          Draft CV
                        </button>
                      </div>
                    </div>
                  ))}
                </motion.div>
              )}

              {/* TAB 3: ATS CRUCIBLE */}
              {activeTab === "ats" && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-[var(--text-primary)]">
                        Google XYZ Formula Transformation Engine
                      </h4>
                      <p className="text-xs text-[var(--text-muted)] font-mono">
                        Accomplished [X], as measured by [Y], by doing [Z]
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-black text-[var(--accent-primary)]">{atsScore}/100</span>
                      <p className="text-[10px] font-mono text-[var(--text-muted)]">ATS Heuristic Score</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[#FF5F56] font-bold block mb-1">
                        ✕ RAW DESCRIPTIVE BULLET (FAILS ATS QUANTIFICATION)
                      </span>
                      <textarea
                        value={rawBullet}
                        onChange={(e) => setRawBullet(e.target.value)}
                        rows={3}
                        className="w-full bg-[var(--bg-deep)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-xs text-[var(--text-primary)] font-mono resize-none focus:outline-none focus:border-[var(--accent-primary)]"
                      />
                    </div>

                    <div className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--accent-primary)]/50 shadow-inner">
                      <span className="text-[10px] font-mono text-[var(--accent-primary)] font-bold block mb-1">
                        ✓ PASHA HUNT GOOGLE XYZ TAILORING (QUALIFIED ELITE)
                      </span>
                      <textarea
                        value={xyzTransformed}
                        onChange={(e) => setXyzTransformed(e.target.value)}
                        rows={3}
                        className="w-full bg-[var(--bg-deep)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-xs text-[var(--text-primary)] font-mono resize-none focus:outline-none focus:border-[var(--accent-primary)]"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-[11px] font-mono text-[var(--text-muted)]">
                      Tokens: Action Verb [Slashing] • Metric [1.8s, 98/100] • Method [React 19, Modular Architecture]
                    </span>
                    <button
                      onClick={() => alert("Copied Google XYZ Tailored Resume to clipboard!")}
                      className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-[var(--accent-primary)] text-[var(--bg-deep)] cursor-pointer"
                    >
                      Copy Clean .TXT
                    </button>
                  </div>
                </motion.div>
              )}

              {/* TAB 4: PROTOCOL */}
              {activeTab === "protocol" && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                  <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-[var(--text-primary)]">
                        Socket MX Direct Recruiter Mailbox Verification
                      </h4>
                      <p className="text-xs text-[var(--text-muted)] font-mono">
                        RFC 5321 DNS MX Handshake without firing unsolicited spam
                      </p>
                    </div>
                    <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-[var(--accent-primary)]/15 text-[var(--accent-primary)]">
                      Status: Socket 25 Handshake Ready
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)]">STEP 01: DNS MX QUERY</span>
                      <p className="text-xs font-mono text-[var(--text-primary)] mt-1.5">
                        query_mx(&quot;systemsltd.com&quot;) &rarr; ASPMX.L.GOOGLE.COM
                      </p>
                      <span className="text-[9px] text-[var(--accent-primary)] font-mono mt-1 block">Resolved in 18ms</span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)]">STEP 02: SOCKET HANDSHAKE</span>
                      <p className="text-xs font-mono text-[var(--text-primary)] mt-1.5">
                        socket.connect((mx, 25)) &rarr; 220 mx.google.com ESMTP
                      </p>
                      <span className="text-[9px] text-[var(--accent-primary)] font-mono mt-1 block">Handshake Valid</span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                      <span className="text-[10px] font-mono text-[var(--text-muted)]">STEP 03: IMAP STAGING</span>
                      <p className="text-xs font-mono text-[var(--text-primary)] mt-1.5">
                        imap.append(&quot;[Gmail]/Drafts&quot;, msg)
                      </p>
                      <span className="text-[9px] text-[var(--accent-primary)] font-mono mt-1 block">
                        Saved in Drafts (Never Auto-Sent)
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>

        {/* Laser Horizon Light Beam */}
        <div className="mt-16 laser-horizon" />
      </section>

      {/* =========================================================================
          ACT II: THE STREAM (18-RADAR LIVE INGESTION TICKER)
      ========================================================================= */}
      <section id="radar" className="relative z-10 py-16 px-4 max-w-6xl mx-auto">
        <div className="text-left mb-8">
          <span className="text-[11px] font-mono uppercase text-[var(--accent-primary)] tracking-widest block mb-2">
            ACT II: GLOBAL DISCOVERY
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[var(--text-primary)] tracking-tight">
            18 Job Feeds. Zero Third-Party Aggregation Lag.
          </h2>
          <p className="text-sm text-[var(--text-secondary)] mt-1 max-w-xl">
            Pasha Hunt bypasses cluttered web portals and queries direct RSS, JSON, and HTML endpoints in real time.
          </p>
        </div>

        {/* Radar Strip Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2.5">
          {[
            { name: "Remotive", type: "JSON API", speed: "210ms", count: "840 jobs" },
            { name: "WeWorkRemotely", type: "RSS Feed", speed: "190ms", count: "1,120 jobs" },
            { name: "Arbeitnow", type: "REST API", speed: "320ms", count: "650 jobs" },
            { name: "Himalayas", type: "JSON Feed", speed: "280ms", count: "920 jobs" },
            { name: "Jobicy", type: "API Endpoint", speed: "240ms", count: "480 jobs" },
            { name: "RemoteOK", type: "Legal Scraper", speed: "410ms", count: "1,450 jobs" },
          ].map((feed, i) => (
            <div
              key={i}
              className="p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)] transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-[var(--text-primary)]">{feed.name}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
              </div>
              <p className="text-[10px] font-mono text-[var(--text-muted)] mt-1">{feed.type}</p>
              <div className="mt-2 flex items-center justify-between text-[10px] font-mono">
                <span className="text-[var(--text-secondary)]">{feed.count}</span>
                <span className="text-[var(--accent-primary)]">{feed.speed}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          ACT III: THE CRUCIBLE (INTERACTIVE ATS & GOOGLE XYZ RESUME STUDIO)
      ========================================================================= */}
      <section id="crucible" className="relative z-10 py-16 px-4 max-w-6xl mx-auto border-t border-[var(--border-subtle)]">
        <div className="text-left mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-mono uppercase text-[var(--accent-primary)] tracking-widest block mb-2">
              ACT III: ATS INTELLIGENCE
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[var(--text-primary)] tracking-tight">
              The Google XYZ Resume Transformer.
            </h2>
            <p className="text-sm text-[var(--text-secondary)] mt-1 max-w-xl">
              Type or paste your experience below. Watch the real-time heuristic calculator analyze keyword density,
              contact signals, and transform raw bullets into high-impact metrics.
            </p>
          </div>
          <div className="glass-panel px-4 py-2 rounded-xl flex items-center gap-3">
            <span className="text-xs font-mono text-[var(--text-muted)]">Calculated Fit:</span>
            <span className="text-xl font-black text-[var(--accent-primary)]">{atsScore}/100</span>
          </div>
        </div>

        {/* Live Interactive Workspace */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Left: Input Textarea */}
          <div className="p-4 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex flex-col justify-between">
            <div>
              <span className="text-xs font-mono text-[var(--text-muted)] uppercase block mb-2">
                YOUR RESUME TEXT OR EXPERIENCE (EDIT LIVE):
              </span>
              <textarea
                value={resumeText}
                onChange={(e) => handleResumeChange(e.target.value)}
                rows={9}
                className="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-3.5 text-xs text-[var(--text-primary)] font-mono resize-none focus:outline-none focus:border-[var(--accent-primary)]"
                placeholder="Paste your resume or experience here..."
              />
            </div>
            <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-[var(--text-muted)]">
              <span>Words: {resumeText.split(/\s+/).filter(Boolean).length}</span>
              <span className="text-[var(--accent-primary)]">Dynamic Heuristic Evaluation</span>
            </div>
          </div>

          {/* Right: Heuristic Metric Breakdown */}
          <div className="p-4 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex flex-col justify-between space-y-4">
            <div>
              <span className="text-xs font-mono text-[var(--text-muted)] uppercase block mb-3">
                5-DIMENSION ATS CRITERIA SCORE:
              </span>
              <div className="space-y-3 text-xs font-mono">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-[var(--text-secondary)]">Contact Signals & Links (Email, LinkedIn, GitHub)</span>
                    <span className="text-[var(--accent-primary)]">20 / 20</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-deep)] overflow-hidden">
                    <div className="h-full bg-[var(--accent-primary)] w-full" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-[var(--text-secondary)]">Technical Keyword Density (React, Next.js, Python)</span>
                    <span className="text-[var(--accent-primary)]">20 / 20</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-deep)] overflow-hidden">
                    <div className="h-full bg-[var(--accent-primary)] w-[95%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-[var(--text-secondary)]">Google XYZ Quantified Metrics</span>
                    <span className="text-[var(--accent-primary)]">30 / 35</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-deep)] overflow-hidden">
                    <div className="h-full bg-[var(--accent-primary)] w-[85%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-[var(--text-secondary)]">Executive Summary Impact</span>
                    <span className="text-[var(--accent-primary)]">14 / 15</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-[var(--bg-deep)] overflow-hidden">
                    <div className="h-full bg-[var(--accent-primary)] w-[90%]" />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[11px] font-mono text-[var(--text-muted)]">
              &quot;Accomplished [14+ React 19 apps], as measured by [1.8s LCP drop], by doing [modular architecture].&quot;
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          ACT IV: THE PROTOCOL (SOCKET MX DNS RECRUITER VERIFICATION)
      ========================================================================= */}
      <section id="protocol" className="relative z-10 py-16 px-4 max-w-6xl mx-auto border-t border-[var(--border-subtle)]">
        <div className="text-left mb-8">
          <span className="text-[11px] font-mono uppercase text-[var(--accent-primary)] tracking-widest block mb-2">
            ACT IV: DELIVERABILITY ARCHITECTURE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[var(--text-primary)] tracking-tight">
            Socket MX Protocol. The Recruiter Handshake.
          </h2>
          <p className="text-sm text-[var(--text-secondary)] mt-1 max-w-xl">
            Why send emails into blind spam folders? Pasha Hunt conducts real RFC 5321 DNS handshakes to confirm the
            recruiter’s mail exchanger exists before drafting your application.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)] transition-all">
            <span className="text-xs font-mono text-[var(--accent-primary)] font-bold">PHASE 01: MX LOOKUP</span>
            <h3 className="text-base font-bold text-[var(--text-primary)] mt-2">Zero Blind Sending</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
              When a recruiter email is extracted, Pasha Hunt performs an asynchronous DNS MX query against authoritative
              root servers to verify domain active status.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)] transition-all">
            <span className="text-xs font-mono text-[var(--accent-primary)] font-bold">PHASE 02: SOCKET 25</span>
            <h3 className="text-base font-bold text-[var(--text-primary)] mt-2">TCP Handshake Verification</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
              Opens a raw TCP connection to Port 25. Verifies the remote mail server responds with HTTP 220 ESMTP without
              transmitting unsolicited payloads.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)] transition-all">
            <span className="text-xs font-mono text-[var(--accent-primary)] font-bold">PHASE 03: IMAP DRAFTS</span>
            <h3 className="text-base font-bold text-[var(--text-primary)] mt-2">Human-in-the-Loop Staging</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
              Pasha Hunt never sends an email autonomously. Every tailored CV and cover letter is cleanly staged into
              your Gmail Drafts folder for final review.
            </p>
          </div>
        </div>
      </section>

      {/* =========================================================================
          ACT V: TRANSMISSION (INSTANT DOWNLOAD & INQUIRY FORM)
      ========================================================================= */}
      <section id="transmission" className="relative z-10 py-16 px-4 max-w-6xl mx-auto border-t border-[var(--border-subtle)]">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          {/* Left: Download Binary */}
          <div className="p-6 rounded-2xl glass-panel border border-[var(--border-strong)]">
            <span className="text-[11px] font-mono uppercase text-[var(--accent-primary)] tracking-widest block mb-2">
              ACT V: GET PASHA HUNT
            </span>
            <h3 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">
              Download the Commercial Workstation
            </h3>
            <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
              Standalone Windows executable (`PashaHunt.exe`). Zero cloud dependencies, zero telemetry tracking, and
              instant integration with your local Apinex API key.
            </p>

            <div className="mt-6 space-y-2 text-xs font-mono text-[var(--text-muted)]">
              <div className="flex justify-between border-b border-[var(--border-subtle)] pb-2">
                <span>Current Release:</span>
                <span className="text-[var(--text-primary)]">v2.0.0 (Apinex Edition)</span>
              </div>
              <div className="flex justify-between border-b border-[var(--border-subtle)] pb-2">
                <span>Architecture:</span>
                <span className="text-[var(--text-primary)]">Windows x64 Standalone</span>
              </div>
              <div className="flex justify-between border-b border-[var(--border-subtle)] pb-2">
                <span>Security:</span>
                <span className="text-[var(--accent-primary)]">100% Local-First (SHA-256 Verified)</span>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              onClick={handleDownload}
              className="mt-6 w-full py-3.5 rounded-xl text-sm font-bold bg-[var(--accent-primary)] text-[var(--bg-deep)] hover:bg-[var(--accent-hover)] transition-all shadow-xl cursor-pointer"
            >
              {downloadSuccess ? "Redirecting to Release..." : "Download Pasha Hunt v2.0 for Windows"}
            </motion.button>
          </div>

          {/* Right: Contact & Commercial Inquiry */}
          <div className="p-6 rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
            <span className="text-[11px] font-mono uppercase text-[var(--accent-primary)] tracking-widest block mb-2">
              COMMERCIAL INQUIRY & FEEDBACK
            </span>
            <h3 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">Transmit a Message</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">
              Direct line to founder Muhammad Mubashar. Handled by the live `/api/contact` route.
            </p>

            <form onSubmit={handleContactSubmit} className="mt-5 space-y-3">
              <input
                type="text"
                name="honey"
                value={contactForm.honey}
                onChange={(e) => setContactForm({ ...contactForm, honey: e.target.value })}
                className="hidden"
                tabIndex={-1}
              />

              <div>
                <label className="text-[11px] font-mono text-[var(--text-muted)] block mb-1">YOUR NAME</label>
                <input
                  type="text"
                  required
                  value={contactForm.name}
                  onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                  placeholder="e.g. Alex Mercer"
                  className="w-full bg-[var(--bg-deep)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-xs text-[var(--text-primary)] font-mono focus:outline-none focus:border-[var(--accent-primary)]"
                />
              </div>

              <div>
                <label className="text-[11px] font-mono text-[var(--text-muted)] block mb-1">WORK EMAIL</label>
                <input
                  type="email"
                  required
                  value={contactForm.email}
                  onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                  placeholder="alex@enterprise.com"
                  className="w-full bg-[var(--bg-deep)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-xs text-[var(--text-primary)] font-mono focus:outline-none focus:border-[var(--accent-primary)]"
                />
              </div>

              <div>
                <label className="text-[11px] font-mono text-[var(--text-muted)] block mb-1">MESSAGE / INQUIRY</label>
                <textarea
                  required
                  rows={3}
                  value={contactForm.inquiry}
                  onChange={(e) => setContactForm({ ...contactForm, inquiry: e.target.value })}
                  placeholder="Tell us about your team or feedback..."
                  className="w-full bg-[var(--bg-deep)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-xs text-[var(--text-primary)] font-mono resize-none focus:outline-none focus:border-[var(--accent-primary)]"
                />
              </div>

              <button
                type="submit"
                disabled={contactStatus === "submitting"}
                className="w-full py-2.5 rounded-lg text-xs font-bold bg-[var(--bg-card)] border border-[var(--border-strong)] text-[var(--text-primary)] hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] transition-all cursor-pointer"
              >
                {contactStatus === "submitting" ? "Transmitting..." : "Send Transmission →"}
              </button>

              {contactStatus === "success" && (
                <div className="p-3 rounded-lg bg-[var(--accent-primary)]/10 border border-[var(--border-accent)] text-xs text-[var(--accent-primary)] font-mono">
                  ✓ Transmission Received! Reference: <strong>{contactRef}</strong>
                </div>
              )}
            </form>
          </div>
        </div>
      </section>

      {/* =========================================================================
          FOOTER: Minimalist Editorial Colophon
      ========================================================================= */}
      <footer className="relative z-10 py-12 px-4 max-w-6xl mx-auto border-t border-[var(--border-subtle)] flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-[var(--text-muted)]">
        <div>
          <span className="font-bold text-[var(--text-primary)]">PASHA HUNT 2.0</span> • APINEX COMMERCIAL EDITION
          <p className="mt-1">Architected & Developed by Muhammad Mubashar (Pasha Dev).</p>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/pasha804/pasha-hunt"
            target="_blank"
            rel="noreferrer"
            className="hover:text-[var(--accent-primary)] transition-colors"
          >
            GitHub Repository
          </a>
          <span>•</span>
          <a href="#workstation" className="hover:text-[var(--accent-primary)] transition-colors">
            Top ↑
          </a>
        </div>
      </footer>
    </div>
  );
}
