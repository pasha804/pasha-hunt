"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import AmbientCanvas from "../components/AmbientCanvas";

export default function PashaHuntLaunch() {
  const [activeWorkflowTab, setActiveWorkflowTab] = useState<"discover" | "analyze" | "tailor" | "track">("discover");
  const [atsScore, setAtsScore] = useState<number>(95);
  const [demoOpen, setDemoOpen] = useState<boolean>(false);
  const [contactForm, setContactForm] = useState({ name: "", email: "", inquiry: "", honey: "" });
  const [contactStatus, setContactStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [contactRef, setContactRef] = useState<string | null>(null);

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
      if (data.ok || data.success) {
        setContactStatus("success");
        setContactRef(data.referenceId || "PSH-" + Math.floor(Math.random() * 8999 + 1000));
        setContactForm({ name: "", email: "", inquiry: "", honey: "" });
      } else {
        setContactStatus("error");
      }
    } catch {
      setContactStatus("error");
    }
  };

  return (
    <div className="relative min-h-screen bg-[#070A0E] text-[#F7F3EA] selection:bg-[#FF6B00]/25 selection:text-white overflow-x-clip">
      {/* Three.js Ambient Particle Constellation */}
      <AmbientCanvas accentColor="#FF6B00" />

      {/* =========================================================================
          HEADER: Picture 3 Exact Brand Navigation
      ========================================================================= */}
      <header className="sticky top-0 z-50 bg-[#070A0E]/85 backdrop-blur-md border-b border-[#1E252D]/80">
        <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#FF6B00] to-[#F2AA4C] flex items-center justify-center font-black text-black text-xl shadow-lg shadow-[#FF6B00]/20">
              P
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="font-extrabold text-lg text-white tracking-tight">Pasha Hunt</span>
              <span className="text-xs font-mono font-bold text-[#FF6B00]">2.0</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#8E98A4]">
            <a href="#product" className="hover:text-white transition-colors flex items-center gap-1">
              Product <span className="text-[10px] text-[#5C6572]">⌄</span>
            </a>
            <a href="#features" className="hover:text-white transition-colors flex items-center gap-1">
              Features <span className="text-[10px] text-[#5C6572]">⌄</span>
            </a>
            <a href="#workflow" className="hover:text-white transition-colors">
              How It Works
            </a>
            <a href="#technology" className="hover:text-white transition-colors">
              Technology
            </a>
            <a href="#faq" className="hover:text-white transition-colors">
              FAQ
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-5">
            <a href="#transmission" className="text-sm font-semibold text-[#8E98A4] hover:text-white transition-colors">
              Sign In
            </a>
            <motion.a
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              href="https://github.com/pasha804/pasha-hunt/releases/latest"
              className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#FF6B00] text-black hover:bg-[#FF7A1A] transition-all shadow-lg shadow-[#FF6B00]/25 flex items-center gap-1.5 cursor-pointer"
            >
              <span>Explore Pasha Hunt</span>
              <span>→</span>
            </motion.a>
          </div>
        </div>
      </header>

      {/* =========================================================================
          HERO: Picture 3 Exact Layout & Radiant Glowing Orb
      ========================================================================= */}
      <section id="product" className="relative z-10 pt-16 md:pt-24 pb-20 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Typography & CTAs */}
          <div className="lg:col-span-5 text-left">
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/40 text-[11px] font-mono text-[#F2AA4C] mb-6 shadow-sm">
              <span className="text-[#FF6B00]">★</span>
              <span className="font-bold tracking-wider uppercase">AI-POWERED CAREER INTELLIGENCE +</span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-black tracking-tight text-white leading-[1.05]">
              Your Next Move. <br />
              <span className="bg-gradient-to-r from-[#FF6B00] via-[#FF8533] to-[#F2AA4C] bg-clip-text text-transparent">
                Made Intelligent.
              </span>
            </h1>

            {/* Subtitle */}
            <p className="mt-6 text-base sm:text-lg text-[#8E98A4] leading-relaxed max-w-xl">
              Stop chasing opportunities. Start discovering them. Discover relevant jobs, understand your compatibility,
              improve your CV, and organize your applications with one intelligent career command center.
            </p>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <motion.a
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                href="https://github.com/pasha804/pasha-hunt/releases/latest"
                className="px-7 py-3.5 rounded-full text-sm font-bold bg-[#FF6B00] text-black hover:bg-[#FF7A1A] transition-all shadow-xl shadow-[#FF6B00]/30 flex items-center gap-2 cursor-pointer"
              >
                <span>Explore Pasha Hunt</span>
                <span>→</span>
              </motion.a>

              <button
                onClick={() => setDemoOpen(!demoOpen)}
                className="px-6 py-3.5 rounded-full text-sm font-medium bg-[#141920]/80 border border-[#2B3542] text-white hover:border-[#FF6B00] transition-all flex items-center gap-2.5 backdrop-blur-md cursor-pointer"
              >
                <span className="w-5 h-5 rounded-full bg-[#FF6B00]/20 text-[#FF6B00] flex items-center justify-center text-[10px]">
                  ▶
                </span>
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Feature Pills */}
            <div className="mt-10 flex flex-wrap items-center gap-6 text-xs font-semibold text-[#8E98A4]">
              <div className="flex items-center gap-2">
                <span className="text-[#FF6B00]">⚡</span>
                <span className="text-white">Intelligent Job Discovery</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#FF6B00]">🧠</span>
                <span className="text-white">AI-Powered CV Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#FF6B00]">📊</span>
                <span className="text-white">Application Intelligence</span>
              </div>
            </div>
          </div>

          {/* Right Column: 3D Laptop Display with Radiant Glowing Sun Orb */}
          <div className="lg:col-span-7 relative flex items-center justify-center">
            {/* The Giant Glowing Radiant Sun Orb (Picture 3 Signature) */}
            <div
              className="absolute -top-12 -right-8 w-[580px] h-[580px] rounded-full pointer-events-none"
              style={{
                background: "radial-gradient(circle at 50% 50%, rgba(255, 107, 0, 0.85) 0%, rgba(242, 170, 76, 0.4) 35%, rgba(255, 107, 0, 0) 70%)",
                filter: "blur(50px)",
                opacity: 0.85,
              }}
            />

            {/* 3D Laptop Frame */}
            <div className="relative z-10 w-full max-w-2xl transform lg:rotate-y-[-6deg] lg:rotate-x-[6deg] transition-transform duration-500 hover:rotate-0 shadow-2xl">
              <div className="rounded-2xl bg-[#0C0F12] border-2 border-[#2C3540] p-3 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.9)] overflow-hidden">
                {/* Laptop Top Bezel */}
                <div className="flex items-center justify-between px-3 py-1.5 bg-[#141920] rounded-xl border border-[#222A34] mb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
                    <span className="ml-2 font-mono text-[10px] text-[#8E98A4]">Pasha Hunt 2.0 — APINEX Edition</span>
                  </div>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-[#1C232D] text-[#FF6B00]">
                    Muhammad Mubashar
                  </span>
                </div>

                {/* Picture 2 Mini-Dashboard Rendered Directly Inside the Screen */}
                <div className="bg-[#0B0E11] rounded-xl p-3 text-left space-y-3 border border-[#1E252D]">
                  {/* Hero Banner in Mini Display */}
                  <div className="p-3 rounded-xl bg-gradient-to-r from-[#141920] via-[#1E2631] to-[#141920] border border-[#28323E] flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                        Welcome back, Muhammad! 🚀
                      </h4>
                      <p className="text-[10px] text-[#8E98A4] mt-0.5">Your career journey is on track</p>
                      <span className="inline-block mt-1 text-[8px] font-mono text-[#F2AA4C] bg-white/5 px-2 py-0.5 rounded-full">
                        &quot;Dream Big. Apply Smart. Grow Faster.&quot;
                      </span>
                    </div>

                    <div className="flex items-center gap-2 bg-[#181D22] p-2 rounded-lg border border-[#28323E]">
                      <div className="w-9 h-9 rounded-full border-2 border-[#FF6B00] flex items-center justify-center font-bold text-[10px] text-white">
                        92%
                      </div>
                      <div className="text-[9px]">
                        <span className="text-[#22C55E] font-bold block">✓ Excellent</span>
                        <span className="text-[#8E98A4]">Fit for 23 roles</span>
                      </div>
                    </div>
                  </div>

                  {/* 5 Stats Row in Mini Display */}
                  <div className="grid grid-cols-5 gap-1.5 text-center">
                    {[
                      { icon: "💼", num: "24", label: "Total Jobs" },
                      { icon: "✓", num: "8", label: "Applied" },
                      { icon: "🔖", num: "5", label: "Shortlisted" },
                      { icon: "✉", num: "2", label: "Interviews" },
                      { icon: "📊", num: "96%", label: "Match Rate" },
                    ].map((s, i) => (
                      <div key={i} className="p-2 rounded-lg bg-[#141920] border border-[#222A34]">
                        <span className="text-xs block">{s.icon}</span>
                        <p className="text-xs font-bold text-white mt-0.5">{s.num}</p>
                        <span className="text-[8px] text-[#8E98A4] block truncate">{s.label}</span>
                      </div>
                    ))}
                  </div>

                  {/* 3 Middle Cards in Mini Display */}
                  <div className="grid grid-cols-3 gap-2">
                    {/* Top Job Matches */}
                    <div className="p-2.5 rounded-lg bg-[#141920] border border-[#222A34]">
                      <span className="text-[10px] font-bold text-white flex items-center gap-1 mb-1.5">
                        <span className="text-[#FF6B00]">🔥</span> Top Matches
                      </span>
                      <div className="space-y-1.5">
                        <div className="p-1.5 rounded bg-[#181D22] flex items-center justify-between text-[9px]">
                          <span className="font-bold text-white">Google</span>
                          <span className="text-[#22C55E] font-bold">96%</span>
                        </div>
                        <div className="p-1.5 rounded bg-[#181D22] flex items-center justify-between text-[9px]">
                          <span className="font-bold text-white">Meta</span>
                          <span className="text-[#22C55E] font-bold">94%</span>
                        </div>
                      </div>
                    </div>

                    {/* ATS Analysis */}
                    <div className="p-2.5 rounded-lg bg-[#141920] border border-[#222A34] text-center">
                      <span className="text-[10px] font-bold text-white block mb-1">ATS Score</span>
                      <div className="w-10 h-10 mx-auto rounded-full border-2 border-[#22C55E] flex items-center justify-center font-bold text-[10px] text-white">
                        87%
                      </div>
                      <span className="text-[8px] text-[#22C55E] font-bold mt-1 block">5/5 Verified</span>
                    </div>

                    {/* AI Chat Pasha Bot */}
                    <div className="p-2.5 rounded-lg bg-[#141920] border border-[#222A34]">
                      <span className="text-[10px] font-bold text-white flex items-center gap-1 mb-1.5">
                        <span className="text-[#F2AA4C]">🤖</span> Pasha Bot
                      </span>
                      <p className="text-[8px] text-[#8E98A4] leading-tight">
                        &quot;Tailoring CV with Google XYZ metrics for Google application.&quot;
                      </p>
                      <span className="text-[8px] text-[#FF6B00] font-bold mt-2 block">● Ready to Apply</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Frosted Glass Notification Card (Picture 3 Signature) */}
              <motion.div
                initial={{ y: 15, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="absolute -top-5 -right-5 z-20 bg-[#12161D]/90 border border-[#FF6B00]/40 rounded-xl p-3.5 shadow-2xl backdrop-blur-xl flex items-center gap-3.5"
              >
                <div className="w-9 h-9 rounded-lg bg-[#FF6B00]/15 border border-[#FF6B00]/30 flex items-center justify-center text-base">
                  💼
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white tracking-tight">New Job Match</h5>
                  <p className="text-[10px] text-[#8E98A4]">3 new opportunities for you!</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          LOWER FOLD: Picture 3 Second Section (Workflow Showcase)
      ========================================================================= */}
      <section id="workflow" className="relative z-10 py-24 px-6 max-w-7xl mx-auto border-t border-[#1E252D]">
        <div className="text-center max-w-3xl mx-auto mb-14">
          {/* Eyebrow Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/30 text-[11px] font-mono text-[#F2AA4C] mb-4">
            <span className="text-[#FF6B00]">⚡</span>
            <span className="font-bold uppercase tracking-wider">SMARTER CAREER. BRIGHTER FUTURE.</span>
          </div>

          <h2 className="text-4xl sm:text-5xl font-black text-white tracking-tight">
            One Workspace. <br />
            A Smarter Career Workflow.
          </h2>

          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] leading-relaxed">
            From job discovery to application tracking — Pasha Hunt brings everything together in one powerful platform.
          </p>

          {/* Workflow Tabs Strip with Glowing Active Underline (Picture 3 Signature) */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-8 border-b border-[#252E38] pb-4">
            {[
              { id: "discover", label: "Discover Jobs" },
              { id: "analyze", label: "Analyze CV" },
              { id: "tailor", label: "Tailor Applications" },
              { id: "track", label: "Track Progress" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveWorkflowTab(tab.id as any)}
                className={`relative pb-3 text-sm font-semibold transition-all cursor-pointer ${
                  activeWorkflowTab === tab.id ? "text-white" : "text-[#8E98A4] hover:text-white"
                }`}
              >
                <span>{tab.label}</span>
                {activeWorkflowTab === tab.id && (
                  <motion.div
                    layoutId="activeTabUnderline"
                    className="absolute bottom-[-17px] left-0 right-0 h-0.5 bg-[#FF6B00] shadow-[0_0_12px_#FF6B00]"
                  />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Dual Device Displays (Picture 3 Bottom) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch max-w-5xl mx-auto">
          {/* Display Card 1: Job Match Analysis */}
          <div className="rounded-2xl bg-[#12161A] border border-[#252C34] p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
                  <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
                  <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
                </div>
                <span className="text-[10px] font-mono text-[#8E98A4]">Job Match Analysis</span>
              </div>

              <div className="flex flex-col sm:flex-row items-center gap-8">
                {/* 95% Score Gauge */}
                <div className="relative w-28 h-28 flex-shrink-0">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
                    <circle
                      cx="50"
                      cy="50"
                      r="42"
                      fill="none"
                      stroke="#22C55E"
                      strokeWidth="8"
                      strokeDasharray="264"
                      strokeDashoffset="13"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-black text-white">95%</span>
                    <span className="text-[9px] font-bold text-[#22C55E]">Match</span>
                  </div>
                </div>

                {/* Match Signals Checklist */}
                <div className="space-y-2.5 text-xs font-medium text-[#F7F3EA] w-full">
                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#181D22] border border-[#252C34]">
                    <span>Skills Match (React, Python, FastAPI)</span>
                    <span className="text-[#22C55E] font-bold">✓ 100%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#181D22] border border-[#252C34]">
                    <span>Experience Level (4+ Years Senior)</span>
                    <span className="text-[#22C55E] font-bold">✓ 95%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#181D22] border border-[#252C34]">
                    <span>Location (Worldwide Remote)</span>
                    <span className="text-[#22C55E] font-bold">✓ 100%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#181D22] border border-[#252C34]">
                    <span>Benefits & Salary Fit</span>
                    <span className="text-[#22C55E] font-bold">✓ 90%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#252C34] flex items-center justify-between text-xs font-mono text-[#8E98A4]">
              <span>Verified against Workday / Greenhouse</span>
              <span className="text-[#FF6B00]">Elite Candidate Ready</span>
            </div>
          </div>

          {/* Display Card 2: Your CV Analysis Preview */}
          <div className="rounded-2xl bg-[#12161A] border border-[#252C34] p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-white flex items-center gap-2">
                  <span>📄</span> Your CV Analysis
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#FF6B00]/15 text-[#FF6B00]">
                  Google XYZ Formatted
                </span>
              </div>

              <div className="p-4 rounded-xl bg-[#181D22] border border-[#252C34] font-mono text-xs space-y-3 text-[#B7B7AE]">
                <div>
                  <h4 className="text-white font-bold text-xs">MUHAMMAD MUBASHAR</h4>
                  <p className="text-[10px] text-[#8E98A4]">Senior Full Stack Engineer & AI Automation Architect</p>
                </div>

                <div className="p-2.5 rounded bg-[#0B0E11] border border-[#252C34] text-[11px] text-white">
                  <span className="text-[#FF6B00] font-bold block mb-1">✓ GOOGLE XYZ TRANSFORMATION:</span>
                  &quot;Architected and delivered 14+ responsive React 19 web applications, slashing LCP render latency by
                  1.8s and achieving a 98/100 Google Lighthouse score.&quot;
                </div>

                <p className="text-[10px] text-[#8E98A4]">
                  Key Signals: 14+ quantified metrics • 0 fluff verbs • Direct deliverability verified
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#252C34] flex items-center justify-between text-xs font-mono">
              <span className="text-[#8E98A4]">Ready for Staging:</span>
              <a
                href="#transmission"
                className="text-[#FF6B00] hover:text-[#FF8533] font-bold flex items-center gap-1"
              >
                Generate Tailored Cover Letter →
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          TRANSMISSION & FOOTER: Contact Form & Downloads
      ========================================================================= */}
      <section id="transmission" className="relative z-10 py-16 px-6 max-w-7xl mx-auto border-t border-[#1E252D]">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start max-w-5xl mx-auto">
          {/* Download Box */}
          <div className="p-8 rounded-2xl bg-[#12161A] border border-[#252C34]">
            <span className="text-[11px] font-mono uppercase text-[#FF6B00] font-bold tracking-widest block mb-2">
              DESKTOP APPLICATION
            </span>
            <h3 className="text-2xl font-black text-white tracking-tight">Download Pasha Hunt 2.0</h3>
            <p className="text-xs text-[#8E98A4] mt-2 leading-relaxed">
              Standalone Windows x64 Workstation. Zero cloud latency, 100% local SQLite privacy, and native 18-feed
              autonomous scraper sweeps.
            </p>

            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              href="https://github.com/pasha804/pasha-hunt/releases/latest"
              className="mt-6 w-full py-3.5 rounded-xl text-sm font-bold bg-[#FF6B00] text-black hover:bg-[#FF7A1A] transition-all shadow-xl shadow-[#FF6B00]/25 flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Download for Windows (v2.0)</span>
              <span>↓</span>
            </motion.a>
          </div>

          {/* Contact Box */}
          <div className="p-8 rounded-2xl bg-[#12161A] border border-[#252C34]">
            <span className="text-[11px] font-mono uppercase text-[#FF6B00] font-bold tracking-widest block mb-2">
              COMMERCIAL INQUIRIES
            </span>
            <h3 className="text-xl font-bold text-white tracking-tight">Direct Transmission</h3>
            <p className="text-xs text-[#8E98A4] mt-1">Direct message to Muhammad Mubashar.</p>

            <form onSubmit={handleContactSubmit} className="mt-5 space-y-3">
              <input
                type="text"
                name="honey"
                value={contactForm.honey}
                onChange={(e) => setContactForm({ ...contactForm, honey: e.target.value })}
                className="hidden"
                tabIndex={-1}
              />
              <input
                type="text"
                required
                value={contactForm.name}
                onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                placeholder="Your name"
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-2.5 text-xs text-white font-mono focus:outline-none focus:border-[#FF6B00]"
              />
              <input
                type="email"
                required
                value={contactForm.email}
                onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                placeholder="Your work email"
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-2.5 text-xs text-white font-mono focus:outline-none focus:border-[#FF6B00]"
              />
              <textarea
                required
                rows={3}
                value={contactForm.inquiry}
                onChange={(e) => setContactForm({ ...contactForm, inquiry: e.target.value })}
                placeholder="Inquiry or feedback..."
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-2.5 text-xs text-white font-mono resize-none focus:outline-none focus:border-[#FF6B00]"
              />
              <button
                type="submit"
                disabled={contactStatus === "submitting"}
                className="w-full py-2.5 rounded-lg text-xs font-bold bg-[#181D22] border border-[#303844] text-white hover:border-[#FF6B00] hover:text-[#FF6B00] transition-all cursor-pointer"
              >
                {contactStatus === "submitting" ? "Transmitting..." : "Send Transmission →"}
              </button>
              {contactStatus === "success" && (
                <div className="p-3 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/30 text-xs text-[#22C55E] font-mono">
                  ✓ Transmission Received! Reference: <strong>{contactRef}</strong>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-[#1E252D] flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-[#8E98A4]">
          <div>
            <span className="font-bold text-white">PASHA HUNT 2.0</span> • APINEX EDITION
            <p className="mt-1">Architected by Muhammad Mubashar (Pasha Dev).</p>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/pasha804/pasha-hunt"
              target="_blank"
              rel="noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub Repository
            </a>
            <span>•</span>
            <a href="#product" className="hover:text-white transition-colors">
              Top ↑
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
