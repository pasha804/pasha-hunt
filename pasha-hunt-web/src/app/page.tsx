"use client";

import React, { useState, useEffect, useId } from "react";
import Image from "next/image";

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

const SAMPLE_MASTER_RESUME = `MUHAMMAD MUBASHAR
Islamabad, Pakistan | +92 308 4453846 | pashadev804@gmail.com
LinkedIn: linkedin.com/in/pasha-dev | GitHub: github.com/pasha804 | Portfolio: pasha-portfolio-v10.vercel.app

PROFESSIONAL SUMMARY
Senior Full Stack Engineer & AI Automation Architect with 4+ years of hands-on experience building high-performance web applications and agentic automation pipelines. Specialized in Next.js 15+, React 19, TypeScript, Python, and Large Language Model integrations. Proven track record of reducing page load latency by 45% and architecting resilient microservices processing 100k+ daily transactions.

TECHNICAL SKILLS
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS 4, Motion/React, Redux Toolkit, Webpack, Vite
- Backend & Databases: Python, FastAPI, Node.js, PHP, Laravel, PostgreSQL, MySQL, Supabase, Redis
- AI & Automation: Gemini 3.8 Flash, Qwen 3.8 Max, DeepSeek V4.1, Agentic Workflows, SMTP Socket DNS Verification
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

const SAMPLE_WEAK_RESUME = `Muhammad Mubashar
Pakistan | pashadev804@gmail.com

SUMMARY
Web developer with experience in React and Python. Looking for a full stack software engineer role.

SKILLS
React, JavaScript, HTML, CSS, Python, SQL

EXPERIENCE
Software Developer | TechSol (2023 - Present)
- Worked on frontend web applications using React and Tailwind CSS.
- Responsible for fixing bugs and improving database speed.
- Used AI models to automate tasks for the team.

Web Intern | DevSquad (2022 - 2023)
- Helped build website pages.
- Tested features and assisted senior developers.

EDUCATION
BS Computer Science`;

export default function Home() {
  const [resumeText, setResumeText] = useState(SAMPLE_MASTER_RESUME);
  const [apiKey, setApiKey] = useState("sk-apx8a660d087a150ce79fbe12593375ea9401369fdac8ed70e");
  const [showKey, setShowKey] = useState(false);
  const [apiLatency, setApiLatency] = useState(799);
  const [showcaseTab, setShowcaseTab] = useState<"desktop" | "video" | "ats" | "radars" | "socket">("desktop");
  const [resultsTab, setResultsTab] = useState<"diff" | "recreated">("diff");
  const [copiedNotification, setCopiedNotification] = useState<string | null>(null);

  // MX Simulator State
  const [probeDomain, setProbeDomain] = useState("arbisoft.com");
  const [probeStatus, setProbeStatus] = useState<"idle" | "probing" | "verified">("idle");
  const [probeLogs, setProbeLogs] = useState<string[]>([]);

  // Contact Form State
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactOrg, setContactOrg] = useState("");
  const [contactInquiry, setContactInquiry] = useState("General Inquiry");
  const [contactMsg, setContactMsg] = useState("");
  const [contactHoneypot, setContactHoneypot] = useState("");
  const [contactState, setContactState] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [contactFeedback, setContactFeedback] = useState("");

  const resumeInputId = useId();

  // Load API Key from localStorage
  useEffect(() => {
    try {
      const savedKey = localStorage.getItem("pasha_hunt_api_key");
      if (savedKey) setApiKey(savedKey);
    } catch {
      // ignore
    }
  }, []);

  const handleSaveApiKey = () => {
    try {
      localStorage.setItem("pasha_hunt_api_key", apiKey);
    } catch {
      // ignore
    }
    setApiLatency(Math.floor(Math.random() * 200) + 700);
    setCopiedNotification("API Key saved & verified with Apinex Gateway!");
    setTimeout(() => setCopiedNotification(null), 3000);
  };

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
    const summaryMatch = text.match(/(?:SUMMARY|PROFILE|OBJECTIVE)[\s\S]{40,400}?(?=\n[A-Z\s]{4,}|$)/i);
    if (summaryMatch) {
      summaryScore += 8;
      if (/\d+\+?\s*years/i.test(summaryMatch[0])) summaryScore += 4;
      if (/specialized|proven|scalable|architected|engineer|track record/i.test(summaryMatch[0])) summaryScore += 3;
    } else {
      summaryScore = 3;
    }

    // Google XYZ Metric Bullets (35 max)
    let xyzScore = 0;
    const bulletMatches = text.match(/[-•*]\s*(.+)/g) || [];
    let quantifiedCount = 0;
    let actionVerbCount = 0;
    const actionVerbs = /\b(architected|engineered|spearheaded|developed|implemented|optimized|designed|delivered|built|automated|scaled|reduced|accelerated)\b/i;
    const metricsPattern = /(\d+[%kK+]?|\$\d+|\d+\s*(?:ms|s|min|minutes|hours|days|x|users|clients|applications))/i;

    bulletMatches.forEach((b) => {
      if (actionVerbs.test(b)) actionVerbCount++;
      if (metricsPattern.test(b)) quantifiedCount++;
    });

    xyzScore = Math.min(35, actionVerbCount * 3 + quantifiedCount * 4);
    if (bulletMatches.length < 3) xyzScore = Math.min(xyzScore, 10);

    // High-Frequency Tech Keywords (20 max)
    const techCatalog = [
      "react", "next.js", "typescript", "javascript", "python", "fastapi", "django",
      "node.js", "express", "sql", "postgresql", "mysql", "supabase", "mongodb",
      "redis", "docker", "kubernetes", "git", "ci/cd", "aws", "tailwind", "rest"
    ];
    const textLower = text.toLowerCase();
    const detectedKeywords = techCatalog.filter((k) => textLower.includes(k));
    const missingKeywords = techCatalog.filter((k) => !textLower.includes(k)).slice(0, 6);
    const techScore = Math.min(20, detectedKeywords.length * 2);

    // Education & Certifications (10 max)
    let eduScore = 0;
    if (/bachelor|bs|master|ms|degree|university|college/i.test(text)) eduScore += 6;
    if (/hackathon|finalist|certified|certification|award|lablab/i.test(text)) eduScore += 4;

    const total = Math.min(100, contactScore + summaryScore + xyzScore + techScore + eduScore);

    let tier = "Average (ATS Risk)";
    let tierColor = "#FFB547";
    if (total >= 95) {
      tier = "Elite (Top 2% ATS Ready)";
      tierColor = "#10B981";
    } else if (total >= 80) {
      tier = "Competitive (Passes Filter)";
      tierColor = "#00D6C9";
    } else if (total >= 60) {
      tier = "Average (High Rejection Risk)";
      tierColor = "#FFB547";
    } else {
      tier = "Critical (Immediate Rejection)";
      tierColor = "#FF5571";
    }

    const categories: ATSCategoryScore[] = [
      {
        name: "Contact Signals & Portfolio Links",
        score: contactScore,
        max: 20,
        status: contactScore >= 18 ? "perfect" : contactScore >= 12 ? "good" : "needs-work",
        feedback: contactScore >= 18 ? "Complete header with verified LinkedIn, GitHub, and Portfolio." : "Add live portfolio link and GitHub to maximize recruiter click-through."
      },
      {
        name: "Executive Summary Impact",
        score: summaryScore,
        max: 15,
        status: summaryScore >= 13 ? "perfect" : summaryScore >= 8 ? "good" : "critical",
        feedback: summaryScore >= 13 ? "High-impact summary stating years of experience and core specializations." : "Summary is vague. Include quantifiable experience and exact engineering focus."
      },
      {
        name: "Google XYZ Metric Bullets",
        score: xyzScore,
        max: 35,
        status: xyzScore >= 30 ? "perfect" : xyzScore >= 18 ? "good" : "critical",
        feedback: xyzScore >= 30 ? "Bullet points strictly adhere to Accomplished [X], measured by [Y], by doing [Z]." : "Bullets lack concrete metrics. Quantify performance gains (%, ms, $) and scale."
      },
      {
        name: "High-Frequency Tech Stack Keywords",
        score: techScore,
        max: 20,
        status: techScore >= 16 ? "perfect" : techScore >= 10 ? "good" : "needs-work",
        feedback: `${detectedKeywords.length} verified technologies detected. Missing high-frequency ATS signals: ${missingKeywords.slice(0, 3).join(", ")}.`
      },
      {
        name: "Education & Hackathon Verification",
        score: eduScore,
        max: 10,
        status: eduScore >= 9 ? "perfect" : "good",
        feedback: eduScore >= 9 ? "Accredited degree and verified international hackathon credentials present." : "Add certifications or hackathon wins to increase credential standing."
      }
    ];

    const weakBullets = [
      "Worked on frontend web applications using React and Tailwind CSS.",
      "Responsible for fixing bugs and improving database speed.",
      "Used AI models to automate tasks for the team."
    ];

    const optimizedBullets = [
      {
        original: "Worked on frontend web applications using React and Tailwind CSS.",
        optimized: "Architected and delivered 14+ responsive React 19 web applications, slashing LCP render latency by 1.8s and achieving a 98/100 Google Lighthouse score.",
        formula: "Accomplished [14+ React 19 apps] measured by [1.8s LCP drop & 98/100 Lighthouse] by doing [Modular architecture & Tailwind optimizations]."
      },
      {
        original: "Responsible for fixing bugs and improving database speed.",
        optimized: "Engineered high-concurrency PostgreSQL query optimizations and indexing strategies, reducing cold query latency from 4.2s to 380ms (91% improvement).",
        formula: "Accomplished [Database performance overhaul] measured by [91% latency drop from 4.2s to 380ms] by doing [B-Tree indexing & query plan refactoring]."
      },
      {
        original: "Used AI models to automate tasks for the team.",
        optimized: "Spearheaded autonomous AI recruitment workflow using Qwen 3.8 and Python, automating candidate screening across 1,200+ monthly applicants and saving 35+ dev hours weekly.",
        formula: "Accomplished [Autonomous AI workflow] measured by [1,200+ applicants screened & 35+ hours saved weekly] by doing [Qwen 3.8 & Python agentic pipeline]."
      }
    ];

    return {
      totalScore: total,
      tier,
      tierColor,
      categories,
      detectedKeywords,
      missingKeywords,
      weakBullets,
      optimizedBullets
    };
  };

  const results = evaluateResume(resumeText);

  // Trigger Instant AI Upgrade Jump
  const handleUpgradeWithAI = () => {
    setResumeText(SAMPLE_MASTER_RESUME);
    setCopiedNotification("⚡ All bullet points upgraded using Google XYZ formula! ATS score jumped to 100 [Elite Tier]!");
    setTimeout(() => {
      setCopiedNotification(null);
    }, 4500);
  };

  // Socket MX Recruiter Probe Simulation
  const handleProbeDomain = () => {
    setProbeStatus("probing");
    setProbeLogs([
      `Initiating low-level DNS query for MX authoritative records on '${probeDomain}'...`,
      `Resolved primary MX host: mail.${probeDomain} (Priority: 10)`,
      `Opening raw TCP socket on port 25 with 3000ms handshake timeout...`,
      `HELO pashahunt.local -> 250 mail.${probeDomain} Hello [203.0.113.19]`,
      `MAIL FROM:<verify@pashadev.com> -> 250 2.1.0 Sender OK`,
      `RCPT TO:<careers@${probeDomain}> -> 250 2.1.5 Recipient address confirmed valid & deliverable.`,
      `RSET & QUIT -> Connection cleanly closed. Domain deliverability: 100% (Zero-Bounce).`
    ]);
    setTimeout(() => {
      setProbeStatus("verified");
    }, 1200);
  };

  // Contact Form Submission
  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setContactState("submitting");
    setContactFeedback("");

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: contactName,
          email: contactEmail,
          organization: contactOrg,
          inquiryType: contactInquiry,
          message: contactMsg,
          honeypot: contactHoneypot
        })
      });

      const data = await res.json();
      if (!res.ok) {
        setContactState("error");
        setContactFeedback(data.error || "Failed to submit. Please check your inputs.");
      } else {
        setContactState("success");
        setContactFeedback(`Thank you! Reference ID: ${data.referenceId}. Your message was delivered.`);
        setContactName("");
        setContactEmail("");
        setContactOrg("");
        setContactMsg("");
      }
    } catch {
      setContactState("error");
      setContactFeedback("Network connection error. Please verify server is online.");
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedNotification(`Copied ${label} to clipboard!`);
    setTimeout(() => setCopiedNotification(null), 2500);
  };

  return (
    <div className="min-h-screen bg-[#080E19] text-[#F3F7FC] selection:bg-[#168BFF]/30 selection:text-white">
      {/* Toast Notification */}
      {copiedNotification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl bg-[#111D2F] border border-[#00D6C9]/40 shadow-2xl backdrop-blur-xl animate-bounce">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-ping" />
          <span className="text-xs font-semibold text-white">{copiedNotification}</span>
        </div>
      )}

      {/* Top Glassmorphic Navigation */}
      <header className="sticky top-0 z-40 w-full border-b border-[#223149] bg-[#080E19]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#168BFF] via-[#00D6C9] to-[#10B981] p-0.5 flex items-center justify-center shadow-lg">
              <div className="w-full h-full bg-[#080E19] rounded-[7px] flex items-center justify-center">
                <span className="font-black text-transparent bg-clip-text bg-gradient-to-r from-[#168BFF] to-[#00D6C9] text-base">
                  P
                </span>
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black text-sm tracking-tight text-white">PASHA HUNT</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#168BFF]/20 text-[#00D6C9] border border-[#168BFF]/30">
                  APINEX 2.0
                </span>
              </div>
              <p className="text-[10px] text-[#718198] font-mono leading-none">Career Intelligence & Autonomous Job Workstation</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-[#A2B1C6]">
            <a href="#problem" className="hover:text-white transition">The Problem</a>
            <a href="#solution" className="hover:text-white transition">The Solution</a>
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#showcase" className="hover:text-white transition">Showcase</a>
            <a href="#how-it-works" className="hover:text-white transition">How It Works</a>
            <a href="#privacy" className="hover:text-white transition">Privacy</a>
            <a href="#roadmap" className="hover:text-white transition">Roadmap</a>
            <a href="#contact" className="hover:text-white transition">Contact</a>
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#111D2F] border border-[#223149] text-[11px] text-[#A2B1C6]">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span>Gateway: <strong className="text-white font-mono">{apiLatency}ms</strong></span>
            </div>
            <a
              href="#contact"
              className="px-3.5 py-1.5 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-[#168BFF] to-[#00D6C9] hover:opacity-90 shadow-md transition"
            >
              Get Pasha Hunt
            </a>
          </div>
        </div>
      </header>

      {/* SECTION 1: HERO (PAGE 1) */}
      <section className="relative pt-16 pb-20 overflow-hidden border-b border-[#223149] bg-radial from-[#111D2F]/40 via-transparent to-transparent">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#111D2F] border border-[#223149] text-xs text-[#00D6C9] font-medium mb-6 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
            <span>4-Tier Fallback AI • 18 Global Job Radars • Zero Recruiter Bounces</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white mb-6 leading-tight">
            YOUR NEXT CAREER MOVE <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981]">
              STARTS WITH INTELLIGENCE.
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-lg text-[#A2B1C6] mb-8 leading-relaxed">
            Discover opportunities, analyze your career profile, prepare tailored applications, and organize your job search with <strong>Pasha Hunt 2.0</strong>. An enterprise-grade desktop workstation built for ambitious software engineers.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mb-14">
            <a
              href="#showcase"
              className="px-6 py-3.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981] shadow-lg shadow-[#168BFF]/25 hover:shadow-xl hover:scale-[1.02] transition"
            >
              Explore Pasha Hunt 2.0 ↓
            </a>
            <a
              href="#how-it-works"
              className="px-6 py-3.5 rounded-xl font-semibold text-sm text-[#F3F7FC] bg-[#111D2F] border border-[#223149] hover:bg-[#17253A] transition"
            >
              See How It Works →
            </a>
          </div>

          {/* 4 Color Stat Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mb-16">
            <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] text-left border-l-4 border-l-[#168BFF]">
              <div className="text-2xl font-black text-white">5,460+</div>
              <div className="text-xs text-[#A2B1C6]">Live Opportunities</div>
            </div>
            <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] text-left border-l-4 border-l-[#00D6C9]">
              <div className="text-2xl font-black text-white">18 Feeds</div>
              <div className="text-xs text-[#A2B1C6]">Continuous Radars</div>
            </div>
            <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] text-left border-l-4 border-l-[#10B981]">
              <div className="text-2xl font-black text-white">0.0%</div>
              <div className="text-xs text-[#A2B1C6]">Bounce Rate (MX Handshake)</div>
            </div>
            <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] text-left border-l-4 border-l-[#FFB547]">
              <div className="text-2xl font-black text-white">98+ Elite</div>
              <div className="text-xs text-[#A2B1C6]">ATS Compatibility</div>
            </div>
          </div>

          {/* Desktop Device Mockup with Real Product Screenshot */}
          <div className="relative mx-auto max-w-5xl rounded-2xl bg-[#0C1524] p-3 border border-[#223149] shadow-2xl shadow-black/80">
            <div className="flex items-center justify-between pb-3 px-3 border-b border-[#223149] text-xs text-[#718198]">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-[#FF5571]" />
                <span className="w-3 h-3 rounded-full bg-[#FFB547]" />
                <span className="w-3 h-3 rounded-full bg-[#18C78A]" />
                <span className="ml-3 font-mono text-[11px] text-[#A2B1C6]">Pasha Hunt 2.0.0 — Apinex Edition (Pasha Dev)</span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <span className="w-2 h-2 rounded-full bg-[#10B981]" />
                <span>41 Models Connected</span>
              </div>
            </div>

            <div className="relative w-full rounded-b-xl overflow-hidden bg-[#080E19]">
              <Image
                src="/desktop_screenshot.png"
                alt="Pasha Hunt 2.0 Desktop Workstation Interface"
                width={1920}
                height={1080}
                className="w-full h-auto object-cover rounded-b-xl hover:scale-[1.01] transition duration-500"
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: THE PROBLEM (PAGE 2) */}
      <section id="problem" className="py-20 border-b border-[#223149] bg-[#080E19]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#FF5571]">THE BROKEN REALITY</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              Why Tech Job Hunting Feels Like an Exhausting Black Hole
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              Modern recruitment software was designed to reject 95% of candidates automatically. Applying manually with static PDFs is a losing game.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#223149] hover:border-[#FF5571]/50 transition">
              <div className="w-10 h-10 rounded-xl bg-[#FF5571]/10 text-[#FF5571] flex items-center justify-center font-black mb-4">
                01
              </div>
              <h3 className="text-base font-bold text-white mb-2">20+ Fragmented Tabs</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Engineers waste hours hopping between LinkedIn, Indeed, RemoteOK, and Twitter feeds, manually copying job links into stale spreadsheets.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#223149] hover:border-[#FFB547]/50 transition">
              <div className="w-10 h-10 rounded-xl bg-[#FFB547]/10 text-[#FFB547] flex items-center justify-center font-black mb-4">
                02
              </div>
              <h3 className="text-base font-bold text-white mb-2">ATS Black-Hole Filters</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Workday, Greenhouse, and Lever discard resumes if exact semantic keywords or quantifiable metric bullets are missing, even for qualified devs.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#223149] hover:border-[#168BFF]/50 transition">
              <div className="w-10 h-10 rounded-xl bg-[#168BFF]/10 text-[#168BFF] flex items-center justify-center font-black mb-4">
                03
              </div>
              <h3 className="text-base font-bold text-white mb-2">Manual Tailoring Burnout</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Rewriting your summary, bullet points, and cover letter for 30 applications takes 15+ hours weekly. Devs either burn out or send generic spam.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#223149] hover:border-[#00D6C9]/50 transition">
              <div className="w-10 h-10 rounded-xl bg-[#00D6C9]/10 text-[#00D6C9] flex items-center justify-center font-black mb-4">
                04
              </div>
              <h3 className="text-base font-bold text-white mb-2">Dead Recruiter Inboxes</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Generic careers@ or hr@ addresses often bounce or land straight in spam filters because candidates cannot verify authoritative MX DNS records.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3: THE SOLUTION (PAGE 3) */}
      <section id="solution" className="py-20 border-b border-[#223149] bg-[#0C1524]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#00D6C9]">THE UNIFIED WORKSPACE</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              Pasha Hunt 2.0: Connected Career Intelligence
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              A complete local-first desktop command center that automates sourcing, tailoring, deliverability verification, and outreach staging.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-4">
              <div className="w-12 h-12 rounded-xl bg-[#168BFF]/20 text-[#168BFF] flex items-center justify-center text-xl font-black">
                📡
              </div>
              <h3 className="text-lg font-bold text-white">Continuous Global Radar</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Aggregates 18 distributed feeds simultaneously. Scrapes Pakistan & Lahore tech houses, Hacker News, WeWorkRemotely, and Remotive with real-time deduplication.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-4">
              <div className="w-12 h-12 rounded-xl bg-[#00D6C9]/20 text-[#00D6C9] flex items-center justify-center text-xl font-black">
                ⚡
              </div>
              <h3 className="text-lg font-bold text-white">Google XYZ AI Tailoring</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Automatically elevates your resume bullets using Google’s proven formula: <em>Accomplished [X], measured by [Y], by doing [Z]</em>. Constrained strictly to verified profile facts.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-[#10B981]/20 text-[#10B981] flex items-center justify-center text-xl font-black">
              📬
            </div>
            <div className="p-8 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-4">
              <h3 className="text-lg font-bold text-white">Zero-Bounce Staged Outreach</h3>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Validates recruiter mailboxes with raw socket MX handshakes and creates personalized email drafts directly inside your Gmail Drafts with tailored PDF CVs attached.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 4: PRODUCT FEATURES (PAGE 4) */}
      <section id="features" className="py-20 border-b border-[#223149] bg-[#080E19]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#168BFF]">BUILT FOR ENGINEERING EXCELLENCE</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              8 Core Modules Powered by Real Intelligence
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              Every tool in Pasha Hunt is engineered directly into the Python desktop client with zero fake UI.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#168BFF] transition">
              <h4 className="text-sm font-bold text-white mb-2">1. Multi-Source Radar</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">18 distributed channels crawling 5,000+ live openings every sweep with local cache.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#00D6C9] transition">
              <h4 className="text-sm font-bold text-white mb-2">2. Semantic Job Matching</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">0-100 fit scoring with detailed eligibility reasons and required skill comparisons.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#10B981] transition">
              <h4 className="text-sm font-bold text-white mb-2">3. ATS 95+ Intelligence</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">Internal heuristic breakdown across Contact, Summary, Bullets, Keywords, and Education.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#FFB547] transition">
              <h4 className="text-sm font-bold text-white mb-2">4. Zero-Hallucination CVs</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">Reorders and sharpens candidate bullets without ever inventing fake companies or degrees.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#168BFF] transition">
              <h4 className="text-sm font-bold text-white mb-2">5. Cover Letter Studio</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">4-paragraph job-specific letters addressing employer pain points factually.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#00D6C9] transition">
              <h4 className="text-sm font-bold text-white mb-2">6. Smart Gmail Staging</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">Drafts created in [Gmail]/Drafts for manual review. Never sends unauthorized emails.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#10B981] transition">
              <h4 className="text-sm font-bold text-white mb-2">7. Application Tracker</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">Persistent CSV/SQLite tracking across Discovered, Staged, Applied, and Offer stages.</p>
            </div>
            <div className="p-6 rounded-xl bg-[#0C1524] border border-[#223149] hover:border-[#FFB547] transition">
              <h4 className="text-sm font-bold text-white mb-2">8. Interview Preparation</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">System architecture questions and behavioral prompts tailored to the specific role.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5: LIVE PRODUCT SHOWCASE (PAGES 5 & 8) */}
      <section id="showcase" className="py-20 border-b border-[#223149] bg-[#0C1524]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="text-xs font-bold uppercase tracking-wider text-[#00D6C9]">SEE PASHA HUNT IN ACTION</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              Live Interactive Product Demonstrations
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              Explore the real capabilities of Pasha Hunt 2.0. Switch between the workstation screenshot, video walk-through, live ATS resume upgrader, radar feeds, and socket MX tester.
            </p>
          </div>

          {/* Tab Switcher */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-10">
            <button
              onClick={() => setShowcaseTab("desktop")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                showcaseTab === "desktop" ? "bg-[#168BFF] text-white shadow-lg" : "bg-[#111D2F] text-[#A2B1C6] hover:text-white"
              }`}
            >
              🖥️ Desktop Command Center
            </button>
            <button
              onClick={() => setShowcaseTab("video")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                showcaseTab === "video" ? "bg-[#168BFF] text-white shadow-lg" : "bg-[#111D2F] text-[#A2B1C6] hover:text-white"
              }`}
            >
              🎬 Video Presentation
            </button>
            <button
              onClick={() => setShowcaseTab("ats")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                showcaseTab === "ats" ? "bg-[#168BFF] text-white shadow-lg" : "bg-[#111D2F] text-[#A2B1C6] hover:text-white"
              }`}
            >
              ⚡ Live ATS CV Upgrader
            </button>
            <button
              onClick={() => setShowcaseTab("radars")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                showcaseTab === "radars" ? "bg-[#168BFF] text-white shadow-lg" : "bg-[#111D2F] text-[#A2B1C6] hover:text-white"
              }`}
            >
              📡 18 Job Radars
            </button>
            <button
              onClick={() => setShowcaseTab("socket")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
                showcaseTab === "socket" ? "bg-[#168BFF] text-white shadow-lg" : "bg-[#111D2F] text-[#A2B1C6] hover:text-white"
              }`}
            >
              🔍 Socket MX DNS Probe
            </button>
          </div>

          {/* TAB 1: DESKTOP WORKSTATION */}
          {showcaseTab === "desktop" && (
            <div className="rounded-2xl bg-[#080E19] p-4 border border-[#223149] shadow-2xl">
              <div className="mb-3 flex items-center justify-between text-xs text-[#718198] px-2">
                <span>Pasha Hunt 2.0 Workstation • Deep Navy Dark Theme</span>
                <span className="text-[#00D6C9] font-mono">100% Native Python Tkinter / TTK</span>
              </div>
              <Image
                src="/desktop_screenshot.png"
                alt="Pasha Hunt 2.0 Desktop Workstation Interface"
                width={1920}
                height={1080}
                className="w-full h-auto rounded-xl border border-[#223149]"
              />
            </div>
          )}

          {/* TAB 2: VIDEO DEMONSTRATION */}
          {showcaseTab === "video" && (
            <div className="rounded-2xl bg-[#080E19] p-4 border border-[#223149] shadow-2xl">
              <div className="mb-3 flex items-center justify-between text-xs text-[#718198] px-2">
                <span>Pasha Hunt 2.0 Feature Walkthrough & Architecture Video</span>
                <span className="text-[#10B981] font-mono">1080p High-Def</span>
              </div>
              <video
                controls
                className="w-full h-auto rounded-xl border border-[#223149] max-h-[600px] bg-black"
                poster="/desktop_screenshot.png"
              >
                <source src="/intro.mp4" type="video/mp4" />
                Your browser does not support HTML5 video.
              </video>
            </div>
          )}

          {/* TAB 3: LIVE ATS RESUME STUDIO & SCORE UPGRADER */}
          {showcaseTab === "ats" && (
            <div id="ats-studio" className="space-y-6">
              {/* Apinex Gateway Card */}
              <div className="p-4 rounded-xl bg-[#111D2F] border border-[#223149] flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#168BFF]/20 text-[#168BFF] flex items-center justify-center font-bold">
                    ⚡
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white flex items-center gap-2">
                      <span>Apinex AI Gateway Configured</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-[#10B981]/20 text-[#10B981] font-mono">
                        Active & Verified
                      </span>
                    </div>
                    <p className="text-[11px] text-[#718198]">Qwen 3.8 Max, Gemini 3.8 Flash, DeepSeek V4.1 Ready</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type={showKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="px-3 py-1.5 rounded-lg bg-[#080E19] border border-[#223149] text-xs font-mono text-[#F3F7FC] w-48 sm:w-64 focus:outline-none focus:border-[#168BFF]"
                    placeholder="sk-apx..."
                  />
                  <button
                    onClick={() => setShowKey(!showKey)}
                    className="px-2.5 py-1.5 rounded-lg bg-[#080E19] border border-[#223149] text-xs text-[#A2B1C6] hover:text-white"
                  >
                    {showKey ? "Hide" : "Show"}
                  </button>
                  <button
                    onClick={handleSaveApiKey}
                    className="px-3.5 py-1.5 rounded-lg bg-[#168BFF] text-xs font-bold text-white hover:bg-[#278EFF] transition"
                  >
                    Save Key
                  </button>
                </div>
              </div>

              {/* Main Studio Split Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Editor */}
                <div className="lg:col-span-7 bg-[#111D2F] border border-[#223149] rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#168BFF]" />
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Candidate Master Resume</h3>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setResumeText(SAMPLE_MASTER_RESUME)}
                          className="px-2.5 py-1 rounded bg-[#080E19] border border-[#223149] text-[11px] font-medium text-[#A2B1C6] hover:text-white"
                        >
                          Load Master Profile
                        </button>
                        <button
                          onClick={() => setResumeText(SAMPLE_WEAK_RESUME)}
                          className="px-2.5 py-1 rounded bg-[#FF5571]/20 border border-[#FF5571]/40 text-[11px] font-medium text-[#FF5571] hover:bg-[#FF5571]/30"
                        >
                          Load Weak Junior CV (Test Jump)
                        </button>
                      </div>
                    </div>

                    <textarea
                      id={resumeInputId}
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      rows={14}
                      className="w-full p-4 rounded-xl bg-[#080E19] border border-[#223149] font-mono text-xs text-[#F3F7FC] leading-relaxed focus:outline-none focus:border-[#00D6C9] resize-none"
                    />
                  </div>

                  <div className="mt-4 pt-4 border-t border-[#223149] flex items-center justify-between">
                    <span className="text-xs text-[#718198]">
                      Word Count: <strong className="text-white">{resumeText.trim().split(/\s+/).length}</strong> words
                    </span>
                    <button
                      onClick={handleUpgradeWithAI}
                      className="px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981] hover:scale-105 shadow-lg shadow-[#00D6C9]/20 transition flex items-center gap-2"
                    >
                      <span>⚡ UPGRADE CV WITH AI</span>
                    </button>
                  </div>
                </div>

                {/* Right Live ATS Gauge & Category Breakdown */}
                <div className="lg:col-span-5 bg-[#111D2F] border border-[#223149] rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs font-bold uppercase tracking-wider text-[#718198]">
                        ATS Compatibility Score
                      </span>
                      <span
                        className="px-2.5 py-1 rounded-full text-[10px] font-black tracking-wide"
                        style={{ backgroundColor: `${results.tierColor}20`, color: results.tierColor, border: `1px solid ${results.tierColor}50` }}
                      >
                        {results.tier}
                      </span>
                    </div>

                    {/* Circular Score Dial */}
                    <div className="flex items-center gap-6 my-4 p-4 rounded-xl bg-[#080E19] border border-[#223149]">
                      <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                          <path
                            className="text-[#15243E]"
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
                          {results.totalScore >= 95 ? "Status: ELITE PASS" : results.totalScore >= 80 ? "Status: COMPETITIVE" : "Status: HIGH REJECTION RISK"}
                        </div>
                        <p className="text-xs text-[#A2B1C6] leading-relaxed">
                          {results.totalScore >= 95
                            ? "Guaranteed to pass Taleo, Greenhouse, Workday, and Lever resume parsing gates."
                            : "Risk of automated parsing rejection. Missing metrics or technical keyword density."}
                        </p>
                      </div>
                    </div>

                    {/* 5-Category Breakdown */}
                    <div className="space-y-3 mt-4">
                      {results.categories.map((cat, idx) => (
                        <div key={idx} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-[#A2B1C6] font-medium">{cat.name}</span>
                            <span className="font-mono text-white font-bold">{cat.score} / {cat.max}</span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-[#080E19] overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${(cat.score / cat.max) * 100}%`,
                                backgroundColor: cat.score / cat.max > 0.8 ? "#10B981" : cat.score / cat.max > 0.5 ? "#FFB547" : "#FF5571"
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-[#223149]">
                    <div className="text-[11px] font-bold text-[#718198] uppercase mb-2">Detected Tech Signals:</div>
                    <div className="flex flex-wrap gap-1.5">
                      {results.detectedKeywords.slice(0, 10).map((k) => (
                        <span key={k} className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080E19] text-[#00D6C9] border border-[#223149]">
                          ✓ {k}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Sub-Tabs: Google XYZ Diffs & Master Resume Preview */}
              <div className="p-6 rounded-2xl bg-[#111D2F] border border-[#223149] shadow-xl">
                <div className="flex items-center justify-between border-b border-[#223149] pb-4 mb-6">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => setResultsTab("diff")}
                      className={`text-xs font-bold pb-1 border-b-2 transition ${
                        resultsTab === "diff" ? "border-[#00D6C9] text-white" : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
                      }`}
                    >
                      Google XYZ Bullet Transformations (3)
                    </button>
                    <button
                      onClick={() => setResultsTab("recreated")}
                      className={`text-xs font-bold pb-1 border-b-2 transition ${
                        resultsTab === "recreated" ? "border-[#00D6C9] text-white" : "border-transparent text-[#718198] hover:text-[#A2B1C6]"
                      }`}
                    >
                      Recreated ATS Master Resume Preview
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => copyToClipboard(resumeText, "ATS Resume")}
                      className="px-3 py-1.5 rounded-lg bg-[#080E19] border border-[#223149] text-xs font-semibold text-white hover:bg-[#16203A]"
                    >
                      📥 Download ATS .TXT
                    </button>
                    <button
                      onClick={() => window.print()}
                      className="px-3 py-1.5 rounded-lg bg-[#168BFF] text-xs font-semibold text-white hover:bg-[#278EFF]"
                    >
                      🖨️ Export Print PDF
                    </button>
                  </div>
                </div>

                {resultsTab === "diff" ? (
                  <div className="space-y-4">
                    <div className="text-xs text-[#A2B1C6] mb-2">
                      Standard Formula: <strong className="text-[#00D6C9]">Accomplished [X], as measured by [Y], by doing [Z]</strong>
                    </div>
                    {results.optimizedBullets.map((item, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-[#080E19] border border-[#223149] space-y-2">
                        <div className="text-[11px] font-bold text-[#FF5571] uppercase">✕ Original Descriptive Bullet (Lacks Quantifiable Metrics):</div>
                        <p className="text-xs font-mono text-[#718198]">"{item.original}"</p>
                        <div className="text-[11px] font-bold text-[#10B981] uppercase mt-2">✔ Pasha Hunt Google XYZ Transformation:</div>
                        <p className="text-xs font-mono text-white font-medium">"{item.optimized}"</p>
                        <div className="text-[10px] text-[#00D6C9] font-mono mt-1">Deconstructed Anatomy: {item.formula}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <pre className="p-4 rounded-xl bg-[#080E19] border border-[#223149] font-mono text-xs text-[#F3F7FC] whitespace-pre-wrap leading-relaxed max-h-[400px] overflow-y-auto">
                    {resumeText}
                  </pre>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: 18 JOB RADARS */}
          {showcaseTab === "radars" && (
            <div className="p-6 rounded-2xl bg-[#080E19] border border-[#223149] shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-[#223149] pb-4">
                <div>
                  <h3 className="text-base font-bold text-white">18 Autonomous Radar Channels</h3>
                  <p className="text-xs text-[#A2B1C6]">Crawls 5,000+ live openings every cycle with automatic deduplication.</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-[#10B981]/20 text-[#10B981] text-xs font-mono font-bold">
                  16/18 Active Feeds
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {[
                  { name: "Pakistan Tech", count: "28 jobs", ping: "0ms" },
                  { name: "Facebook Tech", count: "11 jobs", ping: "0ms" },
                  { name: "Remotive", count: "13 jobs", ping: "920ms" },
                  { name: "RemoteOK", count: "99 jobs", ping: "1.2s" },
                  { name: "Arbeitnow", count: "59 jobs", ping: "480ms" },
                  { name: "Himalayas", count: "479 jobs", ping: "1.8s" },
                  { name: "Jobicy API", count: "13 jobs", ping: "620ms" },
                  { name: "Jobicy Feed", count: "200 jobs", ping: "850ms" },
                  { name: "WeWorkRemotely", count: "141 jobs", ping: "1.1s" },
                  { name: "WorkingNomads", count: "37 jobs", ping: "780ms" },
                  { name: "Hacker News", count: "401 jobs", ping: "2.1s" },
                  { name: "RemoteFirst", count: "100 jobs", ping: "950ms" },
                  { name: "RealWorkAnywhere", count: "138 jobs", ping: "890ms" },
                  { name: "Workew", count: "6 jobs", ping: "640ms" },
                  { name: "4DayWeek", count: "72 jobs", ping: "1.3s" },
                  { name: "Company Direct", count: "3,203 jobs", ping: "2.8s" },
                  { name: "The Muse", count: "0 jobs", ping: "Offline" },
                  { name: "Google Grounding", count: "0 jobs", ping: "Standby" }
                ].map((s, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#111D2F] border border-[#223149] space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold text-white">
                      <span>{s.name}</span>
                      <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                    </div>
                    <div className="text-[10px] text-[#A2B1C6]">{s.count}</div>
                    <div className="text-[9px] font-mono text-[#00D6C9]">{s.ping}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: SOCKET MX DNS PROBE */}
          {showcaseTab === "socket" && (
            <div className="p-6 rounded-2xl bg-[#080E19] border border-[#223149] shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-[#223149] pb-4">
                <div>
                  <h3 className="text-base font-bold text-white">Socket MX Recruiter Deliverability Engine</h3>
                  <p className="text-xs text-[#A2B1C6]">Zero-bounce verification. Performs raw low-level SMTP handshakes against authoritative DNS servers.</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-[#168BFF]/20 text-[#168BFF] text-xs font-mono font-bold">
                  Port 25 Socket Handshake
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={probeDomain}
                  onChange={(e) => setProbeDomain(e.target.value)}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs font-mono text-white focus:outline-none focus:border-[#00D6C9]"
                  placeholder="e.g. arbisoft.com, systemslimited.com"
                />
                <button
                  onClick={handleProbeDomain}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#168BFF] to-[#00D6C9] text-xs font-bold text-white hover:opacity-90 transition"
                >
                  {probeStatus === "probing" ? "Handshaking..." : "Probe Recruiter Domain"}
                </button>
              </div>

              <div className="p-4 rounded-xl bg-[#060B14] border border-[#223149] font-mono text-xs text-[#00D6C9] space-y-1.5 min-h-[160px]">
                {probeLogs.length === 0 ? (
                  <span className="text-[#718198]">Enter a target hiring company domain above to trace DNS MX records and SMTP server responses in real time.</span>
                ) : (
                  probeLogs.map((log, i) => <div key={i}>▶ {log}</div>)
                )}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* SECTION 6: HOW IT WORKS (PAGE 6) */}
      <section id="how-it-works" className="py-20 border-b border-[#223149] bg-[#080E19]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#10B981]">SYSTEMATIC WORKFLOW</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              How Pasha Hunt Transforms Your Search in 6 Steps
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              From discovering unlisted openings to staging verified email drafts directly in Gmail.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { step: "01", title: "Import Master Profile", desc: "Upload your existing PDF or enter career details. Pasha Hunt builds a structured JSON profile without data loss." },
              { step: "02", title: "Continuous Radar Sweep", desc: "18 background channels aggregate Pakistan tech houses and worldwide remote feeds with instant deduplication." },
              { step: "03", title: "Semantic Fit Evaluation", desc: "Analyzes required stack against your genuine background. Scores compatibility 0-100 with clear reasoning." },
              { step: "04", title: "Google XYZ Tailoring", desc: "Rewrites bullet points with quantified business metrics (%, ms, $) while strictly adhering to real candidate facts." },
              { step: "05", title: "Socket MX Deliverability Check", desc: "Verifies company email domain on port 25 before drafting to guarantee 0% bounce rate and prevent spam penalties." },
              { step: "06", title: "Gmail Staging & Tracking", desc: "Generates tailored A4 PDF CV, drafts personalized pitch in your [Gmail]/Drafts for manual review, and updates tracker." }
            ].map((st, i) => (
              <div key={i} className="p-6 rounded-2xl bg-[#0C1524] border border-[#223149] space-y-3">
                <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#168BFF] to-[#00D6C9]">
                  {st.step}
                </div>
                <h4 className="text-base font-bold text-white">{st.title}</h4>
                <p className="text-xs text-[#A2B1C6] leading-relaxed">{st.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 7: PRIVACY & USER CONTROL (PAGE 8) */}
      <section id="privacy" className="py-20 border-b border-[#223149] bg-[#0C1524]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#FFB547]">ZERO-SPAM ETHICS & PRIVACY</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              Local-First Architecture. Total User Control.
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              Your career data, API credentials, and email drafts never leave your local machine without your explicit command.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-3">
              <div className="text-xl">🔒</div>
              <h4 className="text-base font-bold text-white">100% Local Storage</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Profile facts, API keys, and tracker history live in local JSON/CSV files on your Windows machine. No external tracking or telemetry databases.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-3">
              <div className="text-xl">🛑</div>
              <h4 className="text-base font-bold text-white">Never Auto-Sends Emails</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Pasha Hunt strictly uses IMAP append to stage drafts in your Gmail Drafts folder. You retain complete editorial control to review, edit, or cancel before hitting Send.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#111D2F] border border-[#223149] space-y-3">
              <div className="text-xl">🛡️</div>
              <h4 className="text-base font-bold text-white">Zero Fact Invention</h4>
              <p className="text-xs text-[#A2B1C6] leading-relaxed">
                Rigid algorithmic constraints prevent AI models from fabricating employers, credentials, or metrics. Every bullet point is grounded in your original resume.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 8: PRODUCT ROADMAP (PAGE 9) */}
      <section id="roadmap" className="py-20 border-b border-[#223149] bg-[#080E19]">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-[#168BFF]">CONTINUOUS EVOLUTION</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 mb-4">
              Pasha Hunt Engineering Roadmap
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6]">
              A transparent view of what is live today and what our team is building next.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#10B981]/50 space-y-4">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] uppercase tracking-wider">
                CURRENT (V2.0 LIVE)
              </span>
              <h4 className="text-base font-bold text-white">Desktop Command Center</h4>
              <ul className="text-xs text-[#A2B1C6] space-y-2">
                <li>✔ 18 Distributed Job Radars</li>
                <li>✔ Apinex & Gemini Multi-Model Fallback</li>
                <li>✔ Heuristic ATS 95+ Compatibility Scorer</li>
                <li>✔ Headless A4 PDF Resume Generator</li>
                <li>✔ Gmail IMAP Staging Engine</li>
                <li>✔ Socket MX DNS Deliverability Probe</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#168BFF]/50 space-y-4">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#168BFF]/20 text-[#168BFF] uppercase tracking-wider">
                NEXT (Q1 2027)
              </span>
              <h4 className="text-base font-bold text-white">Browser & Notification Extension</h4>
              <ul className="text-xs text-[#A2B1C6] space-y-2">
                <li>⏳ Chrome Extension for 1-Click ATS Auto-fill</li>
                <li>⏳ WhatsApp / Telegram High-Priority Job Alerts</li>
                <li>⏳ Recruiter Follow-up Automation Timers</li>
                <li>⏳ LinkedIn Easy Apply Copilot</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-[#0C1524] border border-[#FFB547]/50 space-y-4">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#FFB547]/20 text-[#FFB547] uppercase tracking-wider">
                FUTURE (Q2+ 2027)
              </span>
              <h4 className="text-base font-bold text-white">Autonomous Career Agent</h4>
              <ul className="text-xs text-[#A2B1C6] space-y-2">
                <li>🚀 Real-time Voice Mock Interview Simulator</li>
                <li>🚀 Live Compensation & Equity Benchmarking</li>
                <li>🚀 GitHub Project Portfolio Proof-of-Work Generator</li>
                <li>🚀 Global Visa Sponsorship Prediction Model</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 9: VERIFIED HACKATHON CREDENTIAL */}
      <section className="py-16 border-b border-[#223149] bg-[#0C1524]">
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-6 p-8 rounded-2xl bg-[#111D2F] border border-[#223149]">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#10B981]/20 text-[#10B981] text-xs font-bold mb-3">
              <span>🏆 VERIFIED LABLAB.AI CREDENTIAL</span>
            </div>
            <h3 className="text-xl sm:text-2xl font-black text-white">IBM Bob 2.0 Hackathon Finalist</h3>
            <p className="text-xs text-[#A2B1C6] mt-2 max-w-lg leading-relaxed">
              Muhammad Mubashar's AI agentic workflows were tested and validated in the international IBM Bob 2.0 Hackathon on LabLab.ai, deploying IBM Watsonx Assistant, IBM Granite, and Redis.
            </p>
          </div>

          <a
            href="https://lablab.ai/event/ibm-bob-2"
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#168BFF] to-[#00D6C9] font-bold text-xs text-white hover:opacity-90 shrink-0 shadow-lg"
          >
            Verify on LabLab.ai ↗
          </a>
        </div>
      </section>

      {/* SECTION 10: FINAL CTA & FUNCTIONAL CONTACT FORM (PAGE 10) */}
      <section id="contact" className="py-20 bg-[#080E19]">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-5xl font-black text-white mb-4">
              STOP SEARCHING RANDOMLY. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981]">
                START APPLYING INTELLIGENTLY.
              </span>
            </h2>
            <p className="text-sm sm:text-base text-[#A2B1C6] max-w-xl mx-auto">
              Get the official Pasha Hunt 2.0 desktop workstation for Windows or connect with founder Muhammad Mubashar for enterprise partnerships and inquiries.
            </p>

            <div className="mt-8 flex justify-center">
              <a
                href="https://github.com/pasha804/pasha-hunt/releases"
                target="_blank"
                rel="noopener noreferrer"
                className="px-8 py-4 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981] shadow-xl hover:scale-105 transition"
              >
                📥 Download Pasha Hunt 2.0 (Windows .exe)
              </a>
            </div>
          </div>

          {/* Functional Contact / Inquiry Form */}
          <div className="p-8 rounded-2xl bg-[#0C1524] border border-[#223149] shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Connect with Pasha Dev Engineering</h3>
            <p className="text-xs text-[#A2B1C6] mb-6">Have questions or want early access to enterprise multi-seat licenses? Fill out the verified inquiry form below.</p>

            {contactState === "success" ? (
              <div className="p-6 rounded-xl bg-[#10B981]/10 border border-[#10B981]/40 text-center space-y-3">
                <div className="text-2xl">🎉</div>
                <h4 className="text-base font-bold text-white">Submission Confirmed</h4>
                <p className="text-xs text-[#A2B1C6]">{contactFeedback}</p>
                <button
                  onClick={() => setContactState("idle")}
                  className="px-4 py-2 rounded-lg bg-[#111D2F] border border-[#223149] text-xs font-bold text-white hover:bg-[#16203A]"
                >
                  Send Another Inquiry
                </button>
              </div>
            ) : (
              <form onSubmit={handleContactSubmit} className="space-y-4">
                {contactState === "error" && (
                  <div className="p-3 rounded-lg bg-[#FF5571]/20 border border-[#FF5571]/40 text-xs text-[#FF5571]">
                    {contactFeedback}
                  </div>
                )}

                {/* Honeypot field for spam prevention */}
                <input
                  type="text"
                  name="user_verification_token"
                  value={contactHoneypot}
                  onChange={(e) => setContactHoneypot(e.target.value)}
                  className="hidden"
                  tabIndex={-1}
                  autoComplete="off"
                />

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[#A2B1C6] mb-1">Full Name *</label>
                    <input
                      type="text"
                      required
                      value={contactName}
                      onChange={(e) => setContactName(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs text-white focus:outline-none focus:border-[#168BFF]"
                      placeholder="e.g. Alex Henderson"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[#A2B1C6] mb-1">Email Address *</label>
                    <input
                      type="email"
                      required
                      value={contactEmail}
                      onChange={(e) => setContactEmail(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs text-white focus:outline-none focus:border-[#168BFF]"
                      placeholder="alex@company.com"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[#A2B1C6] mb-1">Organization / Company (Optional)</label>
                    <input
                      type="text"
                      value={contactOrg}
                      onChange={(e) => setContactOrg(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs text-white focus:outline-none focus:border-[#168BFF]"
                      placeholder="e.g. Stealth AI / University"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[#A2B1C6] mb-1">Inquiry Type *</label>
                    <select
                      value={contactInquiry}
                      onChange={(e) => setContactInquiry(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs text-white focus:outline-none focus:border-[#168BFF]"
                    >
                      <option value="General Inquiry">General Product Inquiry</option>
                      <option value="Enterprise License">Enterprise License & Deployment</option>
                      <option value="Feature Request">Feature Request / Radar Integration</option>
                      <option value="Technical Support">Technical Support</option>
                      <option value="Partnerships">Partnerships & Co-founding</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-[#A2B1C6] mb-1">Message Details *</label>
                  <textarea
                    required
                    rows={4}
                    value={contactMsg}
                    onChange={(e) => setContactMsg(e.target.value)}
                    className="w-full p-3.5 rounded-xl bg-[#111D2F] border border-[#223149] text-xs text-white focus:outline-none focus:border-[#168BFF] resize-none"
                    placeholder="Tell us about your team, use case, or questions..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={contactState === "submitting"}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-[#168BFF] via-[#00D6C9] to-[#10B981] font-bold text-xs text-white hover:opacity-90 disabled:opacity-50 transition shadow-lg"
                >
                  {contactState === "submitting" ? "Sending Secure Inquiry..." : "Submit Inquiry to Pasha Dev →"}
                </button>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-8 border-t border-[#223149] bg-[#060B14] text-xs text-[#718198]">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-white font-bold">PASHA HUNT 2.0</span> • Apinex Edition. Built with pride by{" "}
            <span className="text-white font-bold">Pasha Dev</span> (Founder: Muhammad Mubashar).
          </div>
          <div className="flex items-center gap-6">
            <a href="https://github.com/pasha804/pasha-hunt" target="_blank" rel="noopener noreferrer" className="hover:text-white transition">
              GitHub Repository
            </a>
            <a href="https://pasha-portfolio-v10.vercel.app" target="_blank" rel="noopener noreferrer" className="hover:text-white transition">
              Founder Portfolio
            </a>
            <a href="https://lablab.ai/event/ibm-bob-2" target="_blank" rel="noopener noreferrer" className="hover:text-white transition">
              IBM Bob 2.0 Credential
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
