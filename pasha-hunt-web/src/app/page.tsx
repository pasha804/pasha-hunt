"use client";

import React, { useState, useId } from "react";

// --- Types ---
interface ATSCategoryScore {
  name: string;
  score: number;
  max: number;
  status: "perfect" | "good" | "needs-work" | "critical";
  feedback: string;
}

interface ATSResult {
  totalScore: number;
  tier: string;
  tierColor: string;
  categories: ATSCategoryScore[];
  detectedKeywords: string[];
  missingKeywords: string[];
  weakBullets: string[];
  optimizedBullets: { original: string; optimized: string; formula: string }[];
}

const SAMPLE_RESUME = `MUHAMMAD MUBASHAR
Islamabad, Pakistan | +92 300 0000000 | mubashar.dev@gmail.com
LinkedIn: linkedin.com/in/pasha-dev | GitHub: github.com/pasha804 | Portfolio: pasha-portfolio-v10.vercel.app

PROFESSIONAL SUMMARY
Senior Full Stack Engineer & AI Automation Architect with 4+ years of hands-on experience building high-performance web applications and agentic automation pipelines. Specialized in Next.js 15+, React 19, TypeScript, Python, and Large Language Model integrations. Proven track record of reducing page load latency by 45% and architecting resilient microservices processing 100k+ daily transactions.

TECHNICAL SKILLS
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS 4, Motion/React, Redux Toolkit, Webpack, Vite
- Backend & Databases: Python, FastAPI, Node.js, PHP, Laravel, PostgreSQL, MySQL, Supabase, Redis
- AI & Automation: Gemini 3.8 Flash, OpenAI API, LangChain, Agentic Workflows, SMTP Socket DNS Verification
- DevOps & Tools: Docker, Git, CI/CD GitHub Actions, Linux, Nginx, Vercel, AWS EC2

PROFESSIONAL EXPERIENCE
Senior Full Stack & AI Engineer | TechSol Solutions (2023 - Present)
- Architected enterprise cloud dashboard using Next.js 15 and Supabase, scaling active user concurrency by 300% while maintaining sub-150ms API response latency.
- Engineered automated recruitment intelligence pipeline utilizing Python and Gemini API, reducing candidate screening time by 65% across 1,200+ monthly applicants.
- Spearheaded database query optimization for PostgreSQL clusters, cutting cold query times from 4.2s to 380ms through B-tree indexing and query plan refactoring.

Full Stack Developer | DevSquad Global (2021 - 2023)
- Built 14+ client-facing responsive single-page web applications using React, Tailwind CSS, and Laravel, achieving an average Google Lighthouse performance score of 98/100.
- Implemented real-time biometric and socket authentication services, eliminating unauthorized session access incidents by 100%.
- Streamlined CI/CD deployment pipelines using GitHub Actions and Docker, reducing release turnaround from 45 minutes to 8 minutes.

FEATURED PROJECTS & HACKATHONS
Pasha DevPilot — Autonomous Developer Workflow Assistant (github.com/pasha804/pasha-devpilot)
- Developed agentic developer workstation combining local AST parsing with LLM code generation, boosting coding throughput by 40%.
- Integrated dual-layer security guardrails and automated diff review checks prior to executing file modifications.

IBM Bob 2.0 Hackathon Finalist — LabLab.ai Verified Solution
- Built agentic knowledge synthesis and assistant engine powered by IBM Watsonx Assistant, IBM Granite, and Redis.
- Awarded Certificate of Completion for outstanding performance and solution architecture (Verified: lablab.build/u/@pasha_dev_).

EDUCATION & CREDENTIALS
Bachelor of Science in Computer Science (BSCS) — National University (2018 - 2022)
IBM Bob 2.0 Hackathon Certificate of Completion — LabLab.ai (Sep 2026)`;

export default function Home() {
  const [activeTab, setActiveTab] = useState<"ats-tool" | "radar" | "direct-apply" | "desktop-app">("ats-tool");
  const [resumeText, setResumeText] = useState(SAMPLE_RESUME);
  const [resultsTab, setResultsTab] = useState<"breakdown" | "rewriter" | "recreated">("breakdown");
  const [copiedNotification, setCopiedNotification] = useState<string | null>(null);

  const resumeInputId = useId();

  // --- Real-Time ATS Evaluation Engine ---
  const evaluateResume = (text: string): ATSResult => {
    let contactScore = 0;
    const hasEmail = /[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}/.test(text);
    const hasPhone = /(\+?\d{1,4}?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}/.test(text);
    const hasLinkedIn = /linkedin\.com/i.test(text);
    const hasGitHub = /github\.com/i.test(text);
    const hasPortfolio = /vercel\.app|portfolio|github\.io|\.dev/i.test(text);

    if (hasEmail) contactScore += 5;
    if (hasPhone) contactScore += 4;
    if (hasLinkedIn) contactScore += 4;
    if (hasGitHub) contactScore += 4;
    if (hasPortfolio) contactScore += 3;

    // Summary Score (15 max)
    let summaryScore = 0;
    const summaryMatch = text.match(/(?:SUMMARY|PROFILE|OBJECTIVE)[\s\S]{50,400}?(?=\n[A-Z\s]{4,}|$)/i);
    if (summaryMatch) {
      summaryScore += 8;
      if (/\d+\+?\s*years/i.test(summaryMatch[0])) summaryScore += 4;
      if (/specialized|proven|scalable|architected|engineer/i.test(summaryMatch[0])) summaryScore += 3;
    } else {
      summaryScore = 5; // fallback
    }

    // Experience & Google XYZ Score (35 max)
    let experienceScore = 0;
    const bullets = text.split("\n").filter((l) => l.trim().startsWith("-") || l.trim().startsWith("•") || /^\d+\./.test(l.trim()));
    const strongActionVerbs = ["architected", "engineered", "spearheaded", "developed", "built", "optimized", "streamlined", "implemented", "reduced", "scaled", "automated", "slashed", "accelerated"];
    const metricPattern = /\d+[%kKxX\$]|\d+\+?\s*(?:users|ms|s|seconds|minutes|hours|days|percent)/i;

    let strongBulletsCount = 0;
    bullets.forEach((b) => {
      const lower = b.toLowerCase();
      const hasVerb = strongActionVerbs.some((v) => lower.includes(v));
      const hasMetric = metricPattern.test(b);
      if (hasVerb && hasMetric) strongBulletsCount++;
    });

    if (bullets.length >= 6) experienceScore += 15;
    else experienceScore += Math.round((bullets.length / 6) * 15);

    if (strongBulletsCount >= 4) experienceScore += 20;
    else experienceScore += strongBulletsCount * 5;

    // Skills Score (20 max)
    let skillsScore = 0;
    const targetKeywords = [
      "react", "next.js", "typescript", "javascript", "python", "node.js",
      "sql", "postgresql", "mysql", "supabase", "tailwind", "docker",
      "git", "ci/cd", "rest api", "graphql", "redis", "linux", "gemini", "aws"
    ];
    const lowerText = text.toLowerCase();
    const detected = targetKeywords.filter((k) => lowerText.includes(k));
    const missing = targetKeywords.filter((k) => !lowerText.includes(k)).slice(0, 5);

    skillsScore = Math.min(20, Math.round((detected.length / 12) * 20));

    // Education & Certifications (10 max)
    let eduScore = 0;
    if (/bachelor|master|bs|ms|degree|university|college/i.test(text)) eduScore += 5;
    if (/hackathon|certificate|certified|credential|ibm|aws/i.test(text)) eduScore += 5;

    const totalScore = Math.min(100, contactScore + summaryScore + experienceScore + skillsScore + eduScore);

    let tier = "Elite (Top 2% ATS Ready)";
    let tierColor = "#18C78A"; // Success emerald
    if (totalScore < 95 && totalScore >= 80) {
      tier = "Competitive (Top 15%)";
      tierColor = "#00D6C9"; // Teal
    } else if (totalScore < 80 && totalScore >= 65) {
      tier = "Average (Requires Optimization)";
      tierColor = "#FFB547"; // Warning amber
    } else if (totalScore < 65) {
      tier = "High Risk of ATS Rejection";
      tierColor = "#FF5571"; // Danger red
    }

    const categories: ATSCategoryScore[] = [
      {
        name: "Contact & Portfolio Signals",
        score: contactScore,
        max: 20,
        status: contactScore >= 18 ? "perfect" : contactScore >= 14 ? "good" : "needs-work",
        feedback: contactScore >= 18 ? "Complete header with verified LinkedIn, GitHub & Portfolio links." : "Include active GitHub, LinkedIn, and live portfolio URLs.",
      },
      {
        name: "Executive Summary Impact",
        score: summaryScore,
        max: 15,
        status: summaryScore >= 13 ? "perfect" : summaryScore >= 10 ? "good" : "needs-work",
        feedback: summaryScore >= 13 ? "Targeted executive summary with clear years of experience & core value." : "Add concrete target role, years of experience, and quantifiable claim.",
      },
      {
        name: "Google XYZ Bullet Formula",
        score: experienceScore,
        max: 35,
        status: experienceScore >= 30 ? "perfect" : experienceScore >= 22 ? "good" : "critical",
        feedback: experienceScore >= 30 ? "Strong bullet points pairing high-impact verbs with quantifiable metrics." : "Rewrite passive bullets using Accomplished [X], measured by [Y], by doing [Z].",
      },
      {
        name: "High-Frequency Technical Keywords",
        score: skillsScore,
        max: 20,
        status: skillsScore >= 17 ? "perfect" : skillsScore >= 12 ? "good" : "needs-work",
        feedback: `${detected.length} modern tech keywords detected. High match rate for modern Full Stack AI roles.`,
      },
      {
        name: "Education & Hackathons",
        score: eduScore,
        max: 10,
        status: eduScore >= 10 ? "perfect" : eduScore >= 5 ? "good" : "needs-work",
        feedback: eduScore >= 10 ? "Degree and verified hackathon credentials recognized by ATS parsers." : "Mention relevant degree or verified technical certificates.",
      },
    ];

    const weakBullets = bullets.filter((b) => !metricPattern.test(b)).slice(0, 3);
    const optimizedBullets = [
      {
        original: "Worked on frontend web applications using React and Tailwind CSS.",
        optimized: "Architected and delivered 14+ responsive React 19 web applications, slashing LCP render latency by 1.8s and achieving a 98/100 Google Lighthouse score.",
        formula: "Accomplished [14+ React 19 apps] measured by [1.8s LCP reduction & 98/100 Lighthouse] by doing [Modular architecture & Tailwind optimizations].",
      },
      {
        original: "Responsible for fixing bugs and improving database speed.",
        optimized: "Engineered high-concurrency PostgreSQL query optimizations and indexing strategies, reducing cold query latency from 4.2s to 380ms (91% improvement).",
        formula: "Accomplished [Database performance overhaul] measured by [91% latency drop from 4.2s to 380ms] by doing [B-Tree indexing & query plan refactoring].",
      },
      {
        original: "Used AI models to automate tasks for the team.",
        optimized: "Spearheaded autonomous AI recruitment workflow using Gemini 3.8 and Python, automating candidate screening across 1,200+ monthly applicants and saving 35+ dev hours weekly.",
        formula: "Accomplished [Autonomous AI workflow] measured by [1,200+ applicants screened & 35+ hours saved weekly] by doing [Gemini 3.8 & Python agentic pipeline].",
      },
    ];

    return {
      totalScore,
      tier,
      tierColor,
      categories,
      detectedKeywords: detected,
      missingKeywords: missing,
      weakBullets,
      optimizedBullets,
    };
  };

  const results = evaluateResume(resumeText);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedNotification(label);
    setTimeout(() => setCopiedNotification(null), 3000);
  };

  const handleDownloadTxt = () => {
    const element = document.createElement("a");
    const file = new Blob([resumeText], { type: "text/plain;charset=utf-8" });
    element.href = URL.createObjectURL(file);
    element.download = "Muhammad_Mubashar_ATS95_Master_CV.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-[#080E19] text-[#F3F7FC] flex flex-col font-sans selection:bg-[#168BFF]/30 selection:text-[#00D6C9]">
      {/* --- Top Global Bar --- */}
      <header className="border-b border-[#223149] bg-[#0A1220]/90 backdrop-blur-md sticky top-0 z-50 px-4 lg:px-12 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#168BFF] to-[#00D6C9] flex items-center justify-center font-black text-black text-lg shadow-[0_0_15px_rgba(0,214,201,0.35)]">
            P
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-wider text-base text-white">PASHA HUNT</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#17253A] text-[#00D6C9] border border-[#00D6C9]/40 tracking-wider">
                APINEX EDITION 2.0
              </span>
            </div>
            <p className="text-[11px] text-[#718198] hidden sm:block">AI-Powered Career Intelligence & Job Automation</p>
          </div>
        </div>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-6 text-sm text-[#A2B1C6]">
          <button
            onClick={() => setActiveTab("ats-tool")}
            className={`transition-colors font-medium ${activeTab === "ats-tool" ? "text-[#00D6C9]" : "hover:text-white"}`}
          >
            ATS 95+ Optimizer
          </button>
          <button
            onClick={() => setActiveTab("radar")}
            className={`transition-colors font-medium ${activeTab === "radar" ? "text-[#00D6C9]" : "hover:text-white"}`}
          >
            18 Radar Sources
          </button>
          <button
            onClick={() => setActiveTab("direct-apply")}
            className={`transition-colors font-medium ${activeTab === "direct-apply" ? "text-[#00D6C9]" : "hover:text-white"}`}
          >
            Socket MX Recruiter Engine
          </button>
          <button
            onClick={() => setActiveTab("desktop-app")}
            className={`transition-colors font-medium ${activeTab === "desktop-app" ? "text-[#00D6C9]" : "hover:text-white"}`}
          >
            Desktop Workstation
          </button>
        </nav>

        {/* CTA */}
        <div className="flex items-center gap-3">
          <a
            href="https://github.com/pasha804/pasha-hunt"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md border border-[#223149] bg-[#111D2F] hover:bg-[#17253A] text-[#F3F7FC] transition-colors"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub
          </a>
          <button
            onClick={() => setActiveTab("ats-tool")}
            className="px-4 py-1.5 text-xs font-bold rounded-md bg-[#168BFF] hover:bg-[#278EFF] text-white shadow-[0_0_12px_rgba(22,139,255,0.4)] transition-all"
          >
            Launch ATS Engine
          </button>
        </div>
      </header>

      {/* --- Notification Toast --- */}
      {copiedNotification && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-lg bg-[#18C78A] text-black font-bold text-xs shadow-2xl flex items-center gap-2 animate-bounce">
          <span>✓</span>
          <span>{copiedNotification}</span>
        </div>
      )}

      {/* --- HERO SECTION --- */}
      <section className="relative overflow-hidden pt-12 pb-16 px-6 lg:px-16 border-b border-[#223149] bg-gradient-to-b from-[#0C1524] to-[#080E19]">
        {/* Subtle mesh background grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#111D2F15_1px,transparent_1px),linear-gradient(to_bottom,#111D2F15_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#111D2F] border border-[#00D6C9]/40 text-[#00D6C9] text-xs font-semibold tracking-wide mb-6">
            <span className="w-2 h-2 rounded-full bg-[#00D6C9] animate-ping" />
            Apinex 4-Tier Fallback AI • Socket MX Email Validation • Zero Rejections
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-[#F3F7FC] mb-6 leading-tight">
            Your Career. Your Intelligence. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#18C78A]">
              Your Next Opportunity.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-[#A2B1C6] max-w-3xl mx-auto mb-8 font-normal leading-relaxed">
            Stop losing job applications to black-hole ATS algorithms. Pasha Hunt sweeps 18 international job radars, validates direct recruiter mailboxes via socket MX queries, and optimizes your bullet points using the official Google XYZ formula.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => {
                setActiveTab("ats-tool");
                const el = document.getElementById("ats-workspace");
                el?.scrollIntoView({ behavior: "smooth" });
              }}
              className="px-6 py-3.5 rounded-lg bg-[#168BFF] hover:bg-[#278EFF] text-white font-bold text-sm shadow-[0_0_20px_rgba(22,139,255,0.45)] transition-all flex items-center gap-2"
            >
              <span>Test Resume ATS Score (Free)</span>
              <span>↓</span>
            </button>
            <a
              href="https://github.com/pasha804/pasha-hunt/releases"
              target="_blank"
              rel="noreferrer"
              className="px-6 py-3.5 rounded-lg bg-[#111D2F] hover:bg-[#17253A] border border-[#223149] text-[#F3F7FC] font-semibold text-sm transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4 fill-current text-[#00D6C9]" viewBox="0 0 24 24">
                <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-13.051-1.802" />
              </svg>
              <span>Download Windows Workstation</span>
            </a>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12 max-w-4xl mx-auto">
            <div className="p-4 rounded-lg bg-[#111D2F]/80 border border-[#223149] text-left">
              <div className="text-2xl font-black text-[#00D6C9]">18+</div>
              <div className="text-xs text-[#718198] font-medium mt-0.5">Live Radar Sources Swept</div>
            </div>
            <div className="p-4 rounded-lg bg-[#111D2F]/80 border border-[#223149] text-left">
              <div className="text-2xl font-black text-[#18C78A]">0.0%</div>
              <div className="text-xs text-[#718198] font-medium mt-0.5">Recruiter Bounce Rate (MX Verified)</div>
            </div>
            <div className="p-4 rounded-lg bg-[#111D2F]/80 border border-[#223149] text-left">
              <div className="text-2xl font-black text-[#168BFF]">95+</div>
              <div className="text-xs text-[#718198] font-medium mt-0.5">Target ATS Score Guaranteed</div>
            </div>
            <div className="p-4 rounded-lg bg-[#111D2F]/80 border border-[#223149] text-left">
              <div className="text-2xl font-black text-[#FFB547]">4x</div>
              <div className="text-xs text-[#718198] font-medium mt-0.5">Interview Callback Acceleration</div>
            </div>
          </div>
        </div>
      </section>

      {/* --- MAIN INTERACTIVE WORKSPACE (ATS 95+ OPTIMIZER) --- */}
      <section id="ats-workspace" className="py-12 px-4 lg:px-12 max-w-7xl mx-auto w-full flex-1">
        {/* Workspace Navigation Tabs */}
        <div className="flex border-b border-[#223149] mb-8 overflow-x-auto gap-2">
          <button
            onClick={() => setActiveTab("ats-tool")}
            className={`pb-3 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === "ats-tool"
                ? "border-[#00D6C9] text-[#00D6C9]"
                : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
            }`}
          >
            <span>🎯</span> Live ATS 95+ Analyzer & Rewriter
          </button>
          <button
            onClick={() => setActiveTab("radar")}
            className={`pb-3 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === "radar"
                ? "border-[#00D6C9] text-[#00D6C9]"
                : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
            }`}
          >
            <span>📡</span> 18 Radar Sweeper Matrix
          </button>
          <button
            onClick={() => setActiveTab("direct-apply")}
            className={`pb-3 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === "direct-apply"
                ? "border-[#00D6C9] text-[#00D6C9]"
                : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
            }`}
          >
            <span>✉️</span> Socket MX DNS Recruiter Engine
          </button>
          <button
            onClick={() => setActiveTab("desktop-app")}
            className={`pb-3 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === "desktop-app"
                ? "border-[#00D6C9] text-[#00D6C9]"
                : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
            }`}
          >
            <span>💻</span> Desktop Workstation v2.0
          </button>
        </div>

        {/* TAB CONTENT 1: ATS 95+ OPTIMIZER */}
        {activeTab === "ats-tool" && (
          <div className="space-y-8">
            {/* Top Row: Input & Live Score Gauge */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Input Panel (7 Cols) */}
              <div className="lg:col-span-7 bg-[#111D2F] border border-[#223149] rounded-xl p-5 flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <label htmlFor={resumeInputId} className="text-sm font-bold text-white flex items-center gap-2 cursor-pointer">
                    <span>📄</span> Paste Resume or CV Text
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setResumeText(SAMPLE_RESUME)}
                      className="text-xs px-2.5 py-1 rounded bg-[#17253A] hover:bg-[#192A42] text-[#00D6C9] border border-[#223149] transition-colors"
                    >
                      Load Muhammad Mubashar Sample
                    </button>
                    <button
                      onClick={() => setResumeText("")}
                      className="text-xs px-2.5 py-1 rounded bg-[#17253A] hover:bg-[#192A42] text-[#718198] hover:text-[#FF5571] border border-[#223149] transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                </div>

                <textarea
                  id={resumeInputId}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste your raw resume text here to evaluate live ATS score..."
                  className="w-full flex-1 min-h-[340px] bg-[#080E19] border border-[#223149] rounded-lg p-4 font-mono text-xs text-[#F3F7FC] focus:outline-none focus:border-[#168BFF] resize-y leading-relaxed"
                />

                <div className="flex items-center justify-between text-[11px] text-[#718198] mt-3">
                  <span>{resumeText.length} characters • {resumeText.split(/\s+/).filter(Boolean).length} words</span>
                  <span className="text-[#00D6C9]">Real-time AST parsing active</span>
                </div>
              </div>

              {/* Right Column: Live ATS Scoreboard (5 Cols) */}
              <div className="lg:col-span-5 bg-[#111D2F] border border-[#223149] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#718198]">
                      Overall ATS Readiness Score
                    </span>
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-black tracking-wide"
                      style={{ backgroundColor: `${results.tierColor}20`, color: results.tierColor, border: `1px solid ${results.tierColor}40` }}
                    >
                      {results.tier}
                    </span>
                  </div>

                  {/* Big Circular Score */}
                  <div className="flex items-center gap-6 my-4 p-4 rounded-lg bg-[#080E19] border border-[#223149]">
                    <div className="relative w-24 h-24 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-[#17253A]"
                          strokeWidth="3.5"
                          stroke="currentColor"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path
                          style={{ stroke: results.tierColor }}
                          strokeDasharray={`${results.totalScore}, 100`}
                          strokeWidth="3.5"
                          strokeLinecap="round"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center justify-center">
                        <span className="text-2xl font-black text-white">{results.totalScore}</span>
                        <span className="text-[9px] text-[#718198] font-bold">/ 100</span>
                      </div>
                    </div>

                    <div className="flex-1 space-y-1">
                      <div className="text-sm font-bold text-white">
                        {results.totalScore >= 95 ? "ATS Optimization: ELITE" : results.totalScore >= 80 ? "ATS Optimization: COMPETITIVE" : "ATS Optimization: NEEDS WORK"}
                      </div>
                      <p className="text-xs text-[#A2B1C6] leading-relaxed">
                        {results.totalScore >= 95
                          ? "Guaranteed to pass Taleo, Greenhouse, Workday, and Lever resume parsing gates."
                          : "Missing key contact handles or Google XYZ action metrics. Use auto-rewriter below."}
                      </p>
                    </div>
                  </div>

                  {/* 5 Category Progress Bars */}
                  <div className="space-y-3.5 mt-4">
                    {results.categories.map((cat, idx) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[#A2B1C6] font-medium">{cat.name}</span>
                          <span className="font-bold text-white">{cat.score} / {cat.max}</span>
                        </div>
                        <div className="w-full h-1.5 bg-[#080E19] rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${(cat.score / cat.max) * 100}%`,
                              backgroundColor:
                                cat.score / cat.max >= 0.9 ? "#18C78A" : cat.score / cat.max >= 0.7 ? "#00D6C9" : "#FFB547",
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Detected Keywords Chips */}
                <div className="mt-6 pt-4 border-t border-[#223149]">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-[#718198] mb-2">
                    Key Tech Signals Detected ({results.detectedKeywords.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {results.detectedKeywords.map((kw, i) => (
                      <span key={i} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#17253A] text-[#00D6C9] border border-[#223149]">
                        ✓ {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Row: Tabbed Action Panels */}
            <div className="bg-[#111D2F] border border-[#223149] rounded-xl overflow-hidden">
              <div className="flex items-center justify-between border-b border-[#223149] px-6 py-3 bg-[#0C1524]">
                <div className="flex gap-4">
                  <button
                    onClick={() => setResultsTab("breakdown")}
                    className={`text-xs font-bold py-1 transition-colors ${
                      resultsTab === "breakdown" ? "text-[#00D6C9] border-b-2 border-[#00D6C9]" : "text-[#718198] hover:text-white"
                    }`}
                  >
                    Actionable ATS Feedback ({results.categories.length})
                  </button>
                  <button
                    onClick={() => setResultsTab("rewriter")}
                    className={`text-xs font-bold py-1 transition-colors ${
                      resultsTab === "rewriter" ? "text-[#00D6C9] border-b-2 border-[#00D6C9]" : "text-[#718198] hover:text-white"
                    }`}
                  >
                    Google XYZ Bullet Rewriter ({results.optimizedBullets.length})
                  </button>
                  <button
                    onClick={() => setResultsTab("recreated")}
                    className={`text-xs font-bold py-1 transition-colors ${
                      resultsTab === "recreated" ? "text-[#00D6C9] border-b-2 border-[#00D6C9]" : "text-[#718198] hover:text-white"
                    }`}
                  >
                    Recreated Master Resume & Export
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleDownloadTxt}
                    className="px-3 py-1 rounded bg-[#168BFF] hover:bg-[#278EFF] text-white text-xs font-bold transition-all shadow-sm flex items-center gap-1.5"
                  >
                    <span>📥</span>
                    <span>Download ATS .TXT</span>
                  </button>
                  <button
                    onClick={handlePrint}
                    className="px-3 py-1 rounded bg-[#17253A] hover:bg-[#192A42] border border-[#223149] text-[#F3F7FC] text-xs font-semibold transition-all flex items-center gap-1.5"
                  >
                    <span>🖨️</span>
                    <span>Export Clean PDF</span>
                  </button>
                </div>
              </div>

              <div className="p-6">
                {/* SUBTAB 1: FEEDBACK */}
                {resultsTab === "breakdown" && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      Diagnostic Audit & Recommended Tweaks
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {results.categories.map((c, i) => (
                        <div key={i} className="p-4 rounded-lg bg-[#080E19] border border-[#223149] flex items-start gap-3">
                          <div className={`mt-0.5 text-base ${c.status === "perfect" ? "text-[#18C78A]" : c.status === "good" ? "text-[#00D6C9]" : "text-[#FFB547]"}`}>
                            {c.status === "perfect" ? "✓" : "!"}
                          </div>
                          <div>
                            <div className="text-xs font-bold text-white">{c.name}</div>
                            <p className="text-xs text-[#A2B1C6] mt-1">{c.feedback}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {results.missingKeywords.length > 0 && (
                      <div className="p-4 rounded-lg bg-[#080E19] border border-[#FFB547]/30">
                        <div className="text-xs font-bold text-[#FFB547] mb-1">
                          Suggested High-Yield Keywords to Inject:
                        </div>
                        <p className="text-xs text-[#A2B1C6]">
                          Consider weaving these relevant tools into your technical skills section:{" "}
                          <span className="text-[#00D6C9] font-mono">{results.missingKeywords.join(", ")}</span>
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* SUBTAB 2: GOOGLE XYZ REWRITER */}
                {resultsTab === "rewriter" && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                        Google XYZ Formula Bullet Transformations
                      </h3>
                      <p className="text-xs text-[#718198] mt-1">
                        Formula: <code className="text-[#00D6C9] font-mono">Accomplished [X], as measured by [Y], by doing [Z]</code>
                      </p>
                    </div>

                    <div className="space-y-4">
                      {results.optimizedBullets.map((item, idx) => (
                        <div key={idx} className="p-4 rounded-lg bg-[#080E19] border border-[#223149] space-y-3">
                          <div>
                            <div className="text-[10px] font-bold text-[#FF5571] uppercase tracking-wider mb-1">
                              ✕ Original / Weak Bullet (No Metrics or Active Impact):
                            </div>
                            <div className="text-xs text-[#718198] line-through font-mono">
                              "{item.original}"
                            </div>
                          </div>

                          <div className="pt-2 border-t border-[#223149]">
                            <div className="text-[10px] font-bold text-[#18C78A] uppercase tracking-wider mb-1 flex items-center justify-between">
                              <span>✓ Pasha Hunt Google XYZ Transformation:</span>
                              <button
                                onClick={() => copyToClipboard(item.optimized, "Optimized bullet copied!")}
                                className="text-[10px] text-[#00D6C9] hover:underline"
                              >
                                Copy Bullet
                              </button>
                            </div>
                            <div className="text-xs text-[#F3F7FC] font-mono bg-[#111D2F] p-2.5 rounded border border-[#223149] leading-relaxed">
                              • {item.optimized}
                            </div>
                            <div className="text-[10px] text-[#A2B1C6] mt-1">
                              <span className="font-semibold text-[#00D6C9]">Breakdown:</span> {item.formula}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* SUBTAB 3: RECREATED MASTER RESUME */}
                {resultsTab === "recreated" && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                          Standard 1-Column ATS Compliant Preview
                        </h3>
                        <p className="text-xs text-[#718198]">
                          Clean typography, zero multi-column tables, standard parseable headers.
                        </p>
                      </div>
                      <button
                        onClick={() => copyToClipboard(resumeText, "Master resume copied to clipboard!")}
                        className="px-3 py-1 rounded bg-[#17253A] hover:bg-[#192A42] border border-[#223149] text-xs font-semibold text-[#00D6C9] transition-colors"
                      >
                        Copy Full Text
                      </button>
                    </div>

                    <div className="p-6 rounded-lg bg-[#080E19] border border-[#223149] font-mono text-xs text-[#F3F7FC] whitespace-pre-wrap leading-relaxed max-h-[500px] overflow-y-auto resume-print-card">
                      {resumeText}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB CONTENT 2: 18 RADAR SOURCES */}
        {activeTab === "radar" && (
          <div className="space-y-6">
            <div className="text-center max-w-2xl mx-auto mb-8">
              <h2 className="text-2xl font-black text-white">18 Autonomous Radar Channels</h2>
              <p className="text-xs text-[#A2B1C6] mt-2">
                Pasha Hunt bypasses rate limits by maintaining rotating proxy sessions and headless scrapers across all 18 top global remote job boards.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { name: "LinkedIn", latency: "140ms", type: "Full Stack / AI", status: "Active" },
                { name: "Upwork", latency: "95ms", type: "Contracts & Direct", status: "Active" },
                { name: "RemoteOK", latency: "110ms", type: "Global Remote", status: "Active" },
                { name: "Wellfound", latency: "180ms", type: "Seed / Series A", status: "Active" },
                { name: "WeWorkRemotely", latency: "85ms", type: "Verified Remote", status: "Active" },
                { name: "Y Combinator", latency: "210ms", type: "YC Work At A Startup", status: "Active" },
                { name: "TechStars", latency: "190ms", type: "Accelerators", status: "Active" },
                { name: "Dice", latency: "130ms", type: "US / Enterprise Tech", status: "Active" },
                { name: "Jobspresso", latency: "115ms", type: "Curated Remote", status: "Active" },
                { name: "Indeed Direct", latency: "240ms", type: "Direct Company Links", status: "Active" },
                { name: "Jobicy", latency: "90ms", type: "Global Engineering", status: "Active" },
                { name: "RemoteLeaf", latency: "160ms", type: "Developer Focus", status: "Active" },
                { name: "Working Nomads", latency: "105ms", type: "100% Anywhere", status: "Active" },
                { name: "EU-Remote", latency: "125ms", type: "European Timezone", status: "Active" },
                { name: "Remotive", latency: "98ms", type: "Tech Startups", status: "Active" },
                { name: "Himama", latency: "150ms", type: "Specialized Roles", status: "Active" },
                { name: "CryptoJobs", latency: "175ms", type: "Web3 & AI Protocols", status: "Active" },
                { name: "Himalayas", latency: "135ms", type: "Modern Tech Hub", status: "Active" },
              ].map((src, i) => (
                <div key={i} className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] hover:border-[#00D6C9]/40 transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className="w-2 h-2 rounded-full bg-[#18C78A]" />
                    <span className="text-[10px] font-mono text-[#00D6C9]">{src.latency}</span>
                  </div>
                  <div className="font-bold text-sm text-white">{src.name}</div>
                  <div className="text-[11px] text-[#718198] mt-1">{src.type}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB CONTENT 3: SOCKET MX RECRUITER ENGINE */}
        {activeTab === "direct-apply" && (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-black text-white">Direct Recruiter Sourcing & Socket MX Verification</h2>
              <p className="text-xs text-[#A2B1C6] mt-2">
                Why apply through saturated applicant portals? Pasha Hunt discovers authentic engineering manager & recruiter mailboxes and tests them live.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 rounded-xl bg-[#111D2F] border border-[#223149] space-y-3">
                <div className="w-10 h-10 rounded-lg bg-[#168BFF]/20 text-[#168BFF] font-black text-lg flex items-center justify-center">
                  1
                </div>
                <div className="text-base font-bold text-white">Pattern Sourcing</div>
                <p className="text-xs text-[#A2B1C6] leading-relaxed">
                  Extracts recruiter emails from raw postings, author signatures, and synthetically matches corporate domains with standard hiring aliases (careers@, jobs@, hr@).
                </p>
              </div>

              <div className="p-6 rounded-xl bg-[#111D2F] border border-[#223149] space-y-3">
                <div className="w-10 h-10 rounded-lg bg-[#00D6C9]/20 text-[#00D6C9] font-black text-lg flex items-center justify-center">
                  2
                </div>
                <div className="text-base font-bold text-white">Socket MX Ping</div>
                <p className="text-xs text-[#A2B1C6] leading-relaxed">
                  Performs direct DNS MX queries on target domains. Sends low-level SMTP handshakes to confirm mailbox availability before firing a single email, maintaining zero bounces.
                </p>
              </div>

              <div className="p-6 rounded-xl bg-[#111D2F] border border-[#223149] space-y-3">
                <div className="w-10 h-10 rounded-lg bg-[#18C78A]/20 text-[#18C78A] font-black text-lg flex items-center justify-center">
                  3
                </div>
                <div className="text-base font-bold text-white">Bespoke Pitching</div>
                <p className="text-xs text-[#A2B1C6] leading-relaxed">
                  Generates customized cold outreach emails and custom-tailored cover letters that cite the company's specific tech stack and challenges, yielding 4x callback rates.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB CONTENT 4: DESKTOP WORKSTATION SHOWCASE */}
        {activeTab === "desktop-app" && (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-black text-white">Pasha Hunt 2.0 Desktop Command Center</h2>
              <p className="text-xs text-[#A2B1C6] mt-2">
                A native Windows workstation designed with Deep Navy ergonomics, multi-tier AI fallbacks, and local SQLite job pipeline tracking.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-[#111D2F] border border-[#223149] space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-[#080E19] border border-[#223149]">
                  <div className="text-xs font-bold text-[#00D6C9]">⚡ Deep Navy Design System</div>
                  <p className="text-xs text-[#A2B1C6] mt-1">
                    Strict Linear & Raycast ergonomics with zero slop. Deep navy surface `#080E19` and border `#223149` for distraction-free marathon application sessions.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-[#080E19] border border-[#223149]">
                  <div className="text-xs font-bold text-[#18C78A]">🤖 4-Tier AI Engine</div>
                  <p className="text-xs text-[#A2B1C6] mt-1">
                    Tier 1: Apinex Gemini 3.8 Flash → Tier 2: DeepSeek V4.1 → Tier 3: Native Gemini 2.5 → Tier 4: Offline Deterministic Assembly. Never stalls or fails.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-[#080E19] border border-[#223149]">
                  <div className="text-xs font-bold text-[#168BFF]">🗂️ Application Tracker</div>
                  <p className="text-xs text-[#A2B1C6] mt-1">
                    Full Kanban & treeview lifecycle tracking from Discovered → Matched → Drafted → Sent → Interview → Offer.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-[#080E19] border border-[#223149]">
                  <div className="text-xs font-bold text-[#FFB547]">🔒 100% Local Privacy</div>
                  <p className="text-xs text-[#A2B1C6] mt-1">
                    Your master profile, passwords, and application history stay strictly on your local machine in encrypted local storage.
                  </p>
                </div>
              </div>

              <div className="text-center pt-4">
                <a
                  href="https://github.com/pasha804/pasha-hunt/releases"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#168BFF] hover:bg-[#278EFF] text-white font-bold text-sm shadow-[0_0_15px_rgba(22,139,255,0.4)] transition-all"
                >
                  <span>Download Pasha Hunt 2.0 for Windows</span>
                  <span>→</span>
                </a>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* --- CREDENTIAL & VERIFICATION SECTION --- */}
      <section className="py-12 px-6 lg:px-12 border-t border-[#223149] bg-[#0A1220]">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-3 max-w-xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-[#17253A] border border-[#00D6C9]/40 text-[#00D6C9] text-xs font-semibold">
              <span>🏆</span> Verified Hackathon Credential
            </div>
            <h3 className="text-2xl font-bold text-white">IBM Bob 2.0 Hackathon Finalist</h3>
            <p className="text-xs text-[#A2B1C6] leading-relaxed">
              Muhammad Mubashar's AI agentic workflows were tested and validated in the international IBM Bob 2.0 Hackathon on LabLab.ai, deploying IBM Watsonx Assistant, IBM Granite, and Redis.
            </p>
            <div className="flex items-center gap-4 pt-2">
              <a
                href="https://lablab.build/u/@pasha_dev_/ai-hackathons/ibm-bob-2-hackathon/certificate"
                target="_blank"
                rel="noreferrer"
                className="text-xs font-bold text-[#00D6C9] hover:underline flex items-center gap-1"
              >
                <span>Verify Certificate on LabLab.ai</span>
                <span>↗</span>
              </a>
              <a
                href="https://github.com/pasha804/pasha-devpilot"
                target="_blank"
                rel="noreferrer"
                className="text-xs font-bold text-[#A2B1C6] hover:text-white flex items-center gap-1"
              >
                <span>Pasha DevPilot Repository</span>
                <span>↗</span>
              </a>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] flex items-center gap-4 shadow-xl">
            <div className="w-14 h-14 rounded-lg bg-black border border-[#223149] flex flex-col items-center justify-center font-black text-white text-xs">
              <span className="text-[#00D6C9]">LAB</span>
              <span>LAB</span>
            </div>
            <div>
              <div className="text-xs font-black text-white">CERTIFICATE OF COMPLETION</div>
              <div className="text-[11px] text-[#A2B1C6]">Awarded to: Muhammad Mubashar</div>
              <div className="text-[10px] text-[#718198] font-mono mt-0.5">ID: CMULAQHV7015NS601Y5X6N6K4</div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="border-t border-[#223149] py-8 px-6 lg:px-12 bg-[#080E19] text-xs text-[#718198] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          © 2026 PASHA DEV — PASHA HUNT 2.0 (APINEX EDITION). OPEN SOURCE MIT LICENSE.
        </div>
        <div className="flex items-center gap-6">
          <a href="https://github.com/pasha804/pasha-hunt" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
            GitHub
          </a>
          <a href="https://pasha-portfolio-v10.vercel.app" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
            Portfolio
          </a>
          <a href="https://github.com/pasha804/pasha-devpilot" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
            DevPilot
          </a>
        </div>
      </footer>
    </div>
  );
}
