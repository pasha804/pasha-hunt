"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "motion/react";
import AmbientCanvas from "../components/AmbientCanvas";

export default function PashaHuntLaunch() {
  // Workflow Tab State
  const [activeWorkflowTab, setActiveWorkflowTab] = useState<"discover" | "analyze" | "tailor" | "track">("discover");

  // Interactive ATS Studio State
  const [atsRole, setAtsRole] = useState<"python" | "fullstack" | "aiml">("python");
  const [rawBullet, setRawBullet] = useState<string>("Worked on Python backend APIs and fixed database performance bugs.");
  const [optimizedBullet, setOptimizedBullet] = useState<string>(
    "Architected and deployed asynchronous Python/FastAPI microservices, reducing database query latency by 42% across 1.2M daily transactions."
  );
  const [isOptimized, setIsOptimized] = useState<boolean>(true);
  const [copiedBullet, setCopiedBullet] = useState<boolean>(false);
  const [atsScore, setAtsScore] = useState<number>(96);

  // Live Stream Filter State
  const [streamFilter, setStreamFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Demo Modal State
  const [demoOpen, setDemoOpen] = useState<boolean>(false);

  // FAQ Accordion State
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  // Contact Form State
  const [contactForm, setContactForm] = useState({ name: "", email: "", inquiry: "", honey: "" });
  const [contactStatus, setContactStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [contactRef, setContactRef] = useState<string | null>(null);

  // Handle Preset Role Selection in ATS Studio
  const handleSelectPreset = (role: "python" | "fullstack" | "aiml") => {
    setAtsRole(role);
    setIsOptimized(false);
    if (role === "python") {
      setRawBullet("Responsible for writing Python scripts and managing Redis cache.");
      setOptimizedBullet(
        "Engineered distributed Redis caching layers for high-throughput Python services, accelerating response times by 38% under peak load."
      );
      setAtsScore(68);
    } else if (role === "fullstack") {
      setRawBullet("Built React frontend features and helped design Node.js endpoints.");
      setOptimizedBullet(
        "Spearheaded end-to-end full stack architecture using Next.js and Node microservices, driving a 2.4x uplift in user onboarding conversion."
      );
      setAtsScore(72);
    } else {
      setRawBullet("Trained machine learning models and evaluated accuracy on test sets.");
      setOptimizedBullet(
        "Fine-tuned transformer models using PyTorch and quantization techniques, achieving 94.6% F1 accuracy while cutting inference compute costs by 30%."
      );
      setAtsScore(65);
    }
  };

  const handleRunOptimizer = () => {
    setIsOptimized(true);
    setAtsScore(96);
  };

  const handleCopyBullet = () => {
    navigator.clipboard.writeText(optimizedBullet);
    setCopiedBullet(true);
    setTimeout(() => setCopiedBullet(false), 2000);
  };

  // Job Stream Sample Data
  const jobStreamData = [
    {
      id: "j1",
      title: "Senior Python Developer",
      company: "Google",
      location: "Remote • Worldwide",
      category: "python",
      salary: "$160k - $210k",
      match: "96% Match",
      logo: "G",
      logoColor: "from-blue-500 to-red-500",
      email: "tech-recruiting@google.com",
      tags: ["Python", "Distributed Systems", "FastAPI", "GCP"],
    },
    {
      id: "j2",
      title: "Full Stack Engineer (React / Next.js)",
      company: "Meta",
      location: "Remote • USA",
      category: "fullstack",
      salary: "$175k - $230k",
      match: "94% Match",
      logo: "M",
      logoColor: "from-blue-600 to-indigo-600",
      email: "careers@meta.com",
      tags: ["React", "GraphQL", "Next.js", "Python"],
    },
    {
      id: "j3",
      title: "Cloud Software Engineer",
      company: "Microsoft",
      location: "Hybrid • USA",
      category: "fullstack",
      salary: "$150k - $195k",
      match: "92% Match",
      logo: "⊞",
      logoColor: "from-cyan-500 to-blue-500",
      email: "talent@microsoft.com",
      tags: ["Azure", "C#", "Python", "Kubernetes"],
    },
    {
      id: "j4",
      title: "Full Stack Developer (React / Python)",
      company: "Systems Limited",
      location: "Lahore, Pakistan (Onsite - Seepz)",
      category: "pakistan",
      salary: "PKR 350k - 550k",
      match: "96% Match",
      logo: "S",
      logoColor: "from-emerald-500 to-teal-600",
      email: "careers@systemsltd.com",
      tags: ["FastAPI", "React", "PostgreSQL", "Docker"],
    },
    {
      id: "j5",
      title: "Senior Python Software Engineer",
      company: "Arbisoft",
      location: "Lahore, Pakistan (Canal Road)",
      category: "pakistan",
      salary: "PKR 400k - 650k",
      match: "93% Match",
      logo: "A",
      logoColor: "from-orange-500 to-amber-600",
      email: "jobs@arbisoft.com",
      tags: ["Django", "AWS", "Celery", "FastAPI"],
    },
    {
      id: "j6",
      title: "AI & ML Inference Engineer",
      company: "Tether.io",
      location: "Remote • Worldwide",
      category: "python",
      salary: "$140k - $190k",
      match: "95% Match",
      logo: "T",
      logoColor: "from-emerald-400 to-teal-500",
      email: "hiring@tether.to",
      tags: ["PyTorch", "vLLM", "Docker", "Python"],
    },
  ];

  const filteredJobs = useMemo(() => {
    return jobStreamData.filter((job) => {
      const matchesFilter =
        streamFilter === "all" ||
        (streamFilter === "python" && job.category === "python") ||
        (streamFilter === "fullstack" && job.category === "fullstack") ||
        (streamFilter === "pakistan" && job.category === "pakistan");
      const matchesSearch =
        !searchQuery ||
        job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesFilter && matchesSearch;
    });
  }, [streamFilter, searchQuery]);

  // Handle Contact Submit
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

  // FAQ Content
  const faqs = [
    {
      q: "How does Pasha Hunt 2.0 differ from generic job boards?",
      a: "Generic job boards flood you with repetitive listings and force you into ATS black holes. Pasha Hunt operates as an autonomous desktop career intelligence workstation that continuously sweeps 18 radar feeds, deduplicates postings, scores your profile with Google XYZ criteria, and establishes direct verified SMTP handshake connections with engineering hiring managers.",
    },
    {
      q: "What is the Google XYZ Impact Formula?",
      a: "Originated by Google leadership, the XYZ formula benchmarks top 2% resume performance: 'Accomplished [X], as measured by [Y], by doing [Z]'. Pasha Hunt's integrated engine rewrites passive descriptions into quantified, executive-grade statements that pass Workday, Greenhouse, and Lever filters with 90%+ scores.",
    },
    {
      q: "Is my CV and personal data stored on the cloud?",
      a: "No. Pasha Hunt is architected local-first. Your profile, resume bullets, scraped opportunities, and application history reside strictly on your local device in encrypted SQLite databases. Zero telemetry or user profile exfiltration.",
    },
    {
      q: "How does the direct Recruiter Socket MX protocol work?",
      a: "Instead of routing your application through third-party recruiters or clogged web forms, Pasha Hunt validates the corporate MX records of employer domains and connects directly to verified recruiting inboxes with SPF/DKIM-compliant headers.",
    },
    {
      q: "What are the requirements for the Windows Desktop Workstation?",
      a: "Pasha Hunt 2.0 runs natively on Windows 10/11 x64. It requires no heavy runtimes or cloud subscriptions and consumes less than 120MB of RAM during full 18-feed radar sweeps.",
    },
  ];

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
            <a href="#product" className="hover:text-white transition-colors">
              Product
            </a>
            <a href="#superpowers" className="hover:text-white transition-colors">
              Superpowers
            </a>
            <a href="#workflow" className="hover:text-white transition-colors">
              Workflow
            </a>
            <a href="#ats-studio" className="hover:text-white transition-colors">
              ATS Studio
            </a>
            <a href="#live-stream" className="hover:text-white transition-colors">
              Radar Stream
            </a>
            <a href="#pipeline" className="hover:text-white transition-colors">
              Pipeline
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
                onClick={() => setDemoOpen(true)}
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
                <span className="text-[#FF6B00] text-sm">⚡</span>
                <span>Intelligent Job Discovery</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#FF6B00] text-sm">🧠</span>
                <span>AI-Powered CV Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#FF6B00] text-sm">📊</span>
                <span>Application Intelligence</span>
              </div>
            </div>
          </div>

          {/* Right Column: Picture 3 Exact 3D Tilted Showcase & Radiant Amber Sun Orb */}
          <div className="lg:col-span-7 relative flex items-center justify-center">
            {/* The Giant Radiant Sunset Orb */}
            <div
              className="absolute -top-12 md:-top-20 left-1/2 -translate-x-1/2 w-[340px] h-[340px] sm:w-[460px] sm:h-[460px] md:w-[540px] md:h-[540px] rounded-full pointer-events-none z-0"
              style={{
                background:
                  "radial-gradient(circle at center, #FF6B00 0%, #F2AA4C 35%, rgba(255,107,0,0.3) 65%, transparent 80%)",
                filter: "blur(40px)",
                opacity: 0.75,
              }}
            />

            {/* Radiant Core Sun Rim Light */}
            <div
              className="absolute -top-8 left-1/2 -translate-x-1/2 w-[280px] h-[280px] sm:w-[380px] sm:h-[380px] rounded-full pointer-events-none z-0"
              style={{
                background: "radial-gradient(circle at center, #FFA14A 0%, #FF6B00 60%, transparent 100%)",
                filter: "blur(18px)",
                opacity: 0.85,
              }}
            />

            {/* 3D Tilted Laptop Hardware Frame */}
            <div
              className="relative z-10 w-full max-w-[620px] rounded-2xl bg-[#0F141A] border-2 border-[#2B3542] shadow-[0_30px_90px_rgba(0,0,0,0.9),0_0_60px_rgba(255,107,0,0.35)] overflow-hidden"
              style={{
                transform: "perspective(1200px) rotateY(-7deg) rotateX(4deg) scale(0.98)",
                transformStyle: "preserve-3d",
              }}
            >
              {/* Laptop Header Bar */}
              <div className="bg-[#141A22] px-4 py-2.5 border-b border-[#242D38] flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
                </div>
                <div className="text-[10px] font-mono text-[#8E98A4] flex items-center gap-2">
                  <span className="text-[#FF6B00]">⚡</span>
                  <span>pasha-hunt-workstation.app</span>
                </div>
                <div className="text-[10px] font-mono text-[#22C55E]">● Connected</div>
              </div>

              {/* Inside Laptop: Picture 2 Dashboard Clone Preview */}
              <div className="p-4 bg-[#0B0E11] space-y-4">
                {/* Hero Greeting Box */}
                <div className="p-4 rounded-xl bg-[#12161A] border border-[#252C34] flex items-center justify-between">
                  <div>
                    <div className="text-xs font-extrabold text-white">Welcome back, Muhammad!</div>
                    <div className="text-[10px] text-[#8E98A4] mt-0.5">Your career journey is on track 🚀</div>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#181D22] border border-[#FF6B00]/30">
                    <div className="w-7 h-7 rounded-full border-2 border-[#FF6B00] flex items-center justify-center text-[10px] font-bold text-white">
                      92%
                    </div>
                    <div>
                      <div className="text-[9px] font-bold text-white">Career Score</div>
                      <div className="text-[8px] text-[#22C55E]">✓ Top Fit</div>
                    </div>
                  </div>
                </div>

                {/* 4 Mini Stat Cards */}
                <div className="grid grid-cols-4 gap-2">
                  <div className="p-2.5 rounded-lg bg-[#12161A] border border-[#252C34]">
                    <div className="text-[9px] text-[#8E98A4]">Total Jobs</div>
                    <div className="text-sm font-black text-white">5,435</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#12161A] border border-[#252C34]">
                    <div className="text-[9px] text-[#8E98A4]">Applied</div>
                    <div className="text-sm font-black text-[#22C55E]">8</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#12161A] border border-[#252C34]">
                    <div className="text-[9px] text-[#8E98A4]">Shortlisted</div>
                    <div className="text-sm font-black text-[#F2AA4C]">5</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#12161A] border border-[#252C34]">
                    <div className="text-[9px] text-[#8E98A4]">Interviews</div>
                    <div className="text-sm font-black text-[#38BDF8]">2</div>
                  </div>
                </div>

                {/* Top Opportunities Row */}
                <div className="p-3 rounded-xl bg-[#12161A] border border-[#252C34] space-y-2">
                  <div className="flex items-center justify-between text-[10px] font-bold text-white">
                    <span className="flex items-center gap-1.5">
                      <span className="text-[#FF6B00]">🔥</span> Top Job Matches
                    </span>
                    <span className="text-[#FF6B00] text-[9px]">Live Radar Stream</span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#0B0E11] border border-[#1E252D]">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded bg-blue-600 flex items-center justify-center text-[10px] font-bold text-white">
                        G
                      </div>
                      <div>
                        <div className="text-[10px] font-bold text-white">Senior Python Developer</div>
                        <div className="text-[8px] text-[#8E98A4]">Google • Remote Worldwide</div>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                      96% Match
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded-lg bg-[#0B0E11] border border-[#1E252D]">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded bg-indigo-600 flex items-center justify-center text-[10px] font-bold text-white">
                        M
                      </div>
                      <div>
                        <div className="text-[10px] font-bold text-white">Full Stack Developer</div>
                        <div className="text-[8px] text-[#8E98A4]">Meta • Remote USA</div>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                      94% Match
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Picture 3 Notification Badge */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8, type: "spring" }}
              className="absolute -top-4 -right-4 sm:top-6 sm:-right-6 z-20 px-4 py-3 rounded-xl bg-[#181D22]/95 border border-[#FF6B00]/40 shadow-2xl shadow-black/80 backdrop-blur-md flex items-center gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-[#FF6B00]/20 text-[#FF6B00] flex items-center justify-center text-sm font-bold">
                💼
              </div>
              <div>
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <span>New Job Match</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
                </div>
                <div className="text-[10px] text-[#8E98A4]">3 new opportunities for you!</div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 2: WORKFLOW (Picture 3 Lower Fold)
      ========================================================================= */}
      <section id="workflow" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto">
          {/* Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/30 text-[10px] font-mono text-[#F2AA4C] mb-4">
            <span className="text-[#FF6B00]">★</span>
            <span className="font-bold tracking-wider uppercase">SMARTER CAREER. BRIGHTER FUTURE.</span>
          </div>

          {/* Heading */}
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            One Workspace. <br />
            <span className="bg-gradient-to-r from-white via-[#F7F3EA] to-[#8E98A4] bg-clip-text text-transparent">
              A Smarter Career Workflow.
            </span>
          </h2>

          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] max-w-xl mx-auto leading-relaxed">
            From job discovery to application tracking — Pasha Hunt brings everything together in one powerful platform.
          </p>

          {/* Workflow Tabs */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-2 sm:gap-8 border-b border-[#1E252D] pb-3 text-sm font-semibold">
            {[
              { id: "discover", label: "Discover Jobs" },
              { id: "analyze", label: "Analyze CV" },
              { id: "tailor", label: "Tailor Applications" },
              { id: "track", label: "Track Progress" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveWorkflowTab(tab.id as any)}
                className={`pb-3 px-3 transition-colors relative cursor-pointer ${
                  activeWorkflowTab === tab.id ? "text-white" : "text-[#8E98A4] hover:text-[#F7F3EA]"
                }`}
              >
                <span>{tab.label}</span>
                {activeWorkflowTab === tab.id && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF6B00]"
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Workflow Showcase Screen Preview */}
        <div className="mt-12 max-w-5xl mx-auto">
          <div className="rounded-2xl bg-[#12161A] border border-[#252C34] p-6 sm:p-8 shadow-2xl relative overflow-hidden">
            <AnimatePresence mode="wait">
              {activeWorkflowTab === "discover" && (
                <motion.div
                  key="discover"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.35 }}
                  className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center"
                >
                  <div className="md:col-span-6 space-y-4 text-left">
                    <span className="text-xs font-mono uppercase text-[#FF6B00] font-bold tracking-wider">
                      RADAR DISCOVERY STAGE
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                      18 Autonomous Feeds Sweeping 5,400+ Opportunities
                    </h3>
                    <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed">
                      Continuous real-time ingestion from RemoteOK, WeWorkRemotely, Pakistan Tech, Himalayas, Jobicy,
                      and HackerNews. Duplicate postings are automatically culled, and roles matching your stack are
                      ranked instantly.
                    </p>
                    <div className="pt-2 flex items-center gap-4 text-xs font-mono text-[#22C55E]">
                      <span>✓ 5,435 Indexed Roles</span>
                      <span>✓ Zero Web Ads</span>
                      <span>✓ Direct URLs</span>
                    </div>
                  </div>

                  <div className="md:col-span-6 bg-[#0B0E11] p-5 rounded-xl border border-[#252C34] space-y-3">
                    <div className="flex items-center justify-between text-xs font-bold text-white border-b border-[#1E252D] pb-2">
                      <span>Live Radar Stream</span>
                      <span className="text-[#22C55E] flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#22C55E] animate-ping" /> Real-time
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#252C34] flex items-center justify-between">
                      <div>
                        <div className="text-xs font-bold text-white">Systems Limited • Full Stack Developer</div>
                        <div className="text-[10px] text-[#8E98A4]">Lahore, Pakistan • React / Python / FastAPI</div>
                      </div>
                      <span className="px-2 py-1 rounded text-[10px] font-bold bg-[#22C55E]/15 text-[#22C55E]">96%</span>
                    </div>
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#252C34] flex items-center justify-between">
                      <div>
                        <div className="text-xs font-bold text-white">Google • Senior Python Developer</div>
                        <div className="text-[10px] text-[#8E98A4]">Remote Worldwide • Distributed Systems</div>
                      </div>
                      <span className="px-2 py-1 rounded text-[10px] font-bold bg-[#22C55E]/15 text-[#22C55E]">96%</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeWorkflowTab === "analyze" && (
                <motion.div
                  key="analyze"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.35 }}
                  className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center"
                >
                  <div className="md:col-span-6 space-y-4 text-left">
                    <span className="text-xs font-mono uppercase text-[#22C55E] font-bold tracking-wider">
                      ATS INTELLIGENCE STAGE
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                      Deep 5-Pillar Compatibility & Ranking
                    </h3>
                    <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed">
                      Evaluates your profile against real enterprise screening algorithms: Contact completeness,
                      summary impact, quantifiable experience metrics, skills taxonomy, and credential verification.
                    </p>
                    <div className="pt-2 flex items-center gap-4 text-xs font-mono text-[#F2AA4C]">
                      <span>✓ Workday Compatible</span>
                      <span>✓ Greenhouse Verified</span>
                      <span>✓ Lever Compliant</span>
                    </div>
                  </div>

                  <div className="md:col-span-6 bg-[#0B0E11] p-6 rounded-xl border border-[#252C34] flex items-center justify-around">
                    <div className="text-center">
                      <div className="w-24 h-24 rounded-full border-4 border-[#22C55E] flex flex-col items-center justify-center mx-auto shadow-lg shadow-[#22C55E]/20">
                        <span className="text-2xl font-black text-white">92%</span>
                        <span className="text-[8px] text-[#22C55E] font-bold uppercase">ATS Pass</span>
                      </div>
                      <div className="mt-3 text-xs font-bold text-white">Elite (Top 2% ATS Ready)</div>
                    </div>
                    <div className="space-y-2 text-xs font-medium text-[#8E98A4]">
                      <div className="flex items-center gap-2">
                        <span className="text-[#22C55E]">✓</span> Contact & Socials: 15/15
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[#22C55E]">✓</span> Executive Summary: 15/15
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[#22C55E]">✓</span> Google XYZ Bullets: 35/35
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[#22C55E]">✓</span> Skills Taxonomy: 20/20
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeWorkflowTab === "tailor" && (
                <motion.div
                  key="tailor"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.35 }}
                  className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center"
                >
                  <div className="md:col-span-6 space-y-4 text-left">
                    <span className="text-xs font-mono uppercase text-[#F2AA4C] font-bold tracking-wider">
                      GOOGLE XYZ TAILORING
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                      Transform Weak Descriptions Into Hard Metrics
                    </h3>
                    <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed">
                      Replaces passive job duty lists with Google&apos;s formula: &quot;Accomplished [X] measured by [Y]
                      by doing [Z]&quot;. Instantly elevates your credibility for Staff and Senior engineering roles.
                    </p>
                    <div className="pt-2 flex items-center gap-4 text-xs font-mono text-[#FF6B00]">
                      <span>✓ Action Verb Anchored</span>
                      <span>✓ Scale Quantified</span>
                      <span>✓ Zero Fluff</span>
                    </div>
                  </div>

                  <div className="md:col-span-6 bg-[#0B0E11] p-5 rounded-xl border border-[#252C34] space-y-3">
                    <div className="text-[10px] font-mono uppercase text-[#EF4444] font-bold">Before (Generic Description):</div>
                    <div className="p-3 rounded-lg bg-[#181D22] border border-[#252C34] text-xs text-[#8E98A4] line-through">
                      Worked on backend Python APIs and fixed database performance bugs.
                    </div>
                    <div className="text-[10px] font-mono uppercase text-[#22C55E] font-bold">After (Google XYZ Executive Standard):</div>
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#22C55E]/40 text-xs text-white font-medium">
                      Architected and deployed asynchronous Python/FastAPI microservices, reducing database query latency by 42% across 1.2M daily transactions.
                    </div>
                  </div>
                </motion.div>
              )}

              {activeWorkflowTab === "track" && (
                <motion.div
                  key="track"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.35 }}
                  className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center"
                >
                  <div className="md:col-span-6 space-y-4 text-left">
                    <span className="text-xs font-mono uppercase text-[#38BDF8] font-bold tracking-wider">
                      COMMAND TRACKER
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                      Track Every Transmission & Interview
                    </h3>
                    <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed">
                      Automated lifecycle tracking from initial recruiter outreach to stage rounds and signed offers.
                      Direct integration with local SQLite for zero-leak privacy.
                    </p>
                    <div className="pt-2 flex items-center gap-4 text-xs font-mono text-[#38BDF8]">
                      <span>✓ 8 Applications Active</span>
                      <span>✓ 2 Interviews Scheduled</span>
                    </div>
                  </div>

                  <div className="md:col-span-6 bg-[#0B0E11] p-5 rounded-xl border border-[#252C34] grid grid-cols-3 gap-3 text-center">
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#252C34]">
                      <div className="text-xl font-black text-white">8</div>
                      <div className="text-[10px] text-[#8E98A4] mt-1">Dispatched</div>
                    </div>
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#252C34]">
                      <div className="text-xl font-black text-[#F2AA4C]">5</div>
                      <div className="text-[10px] text-[#8E98A4] mt-1">Shortlisted</div>
                    </div>
                    <div className="p-3 rounded-lg bg-[#12161A] border border-[#22C55E]/40">
                      <div className="text-xl font-black text-[#22C55E]">2</div>
                      <div className="text-[10px] text-[#22C55E] mt-1 font-bold">Interviews</div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 3: 3D BENTO GRID (Core Superpowers - Syvex / Picture 3 3D Tech Cards)
      ========================================================================= */}
      <section id="superpowers" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/40 text-[10px] font-mono text-[#F2AA4C] mb-4">
            <span className="text-[#FF6B00]">★</span>
            <span className="font-bold tracking-wider uppercase">CORE INTELLIGENCE PILLARS</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            Engineered for Candidates Who <br />
            <span className="bg-gradient-to-r from-[#FF6B00] via-[#FF8533] to-[#F2AA4C] bg-clip-text text-transparent">
              Refuse to Settle.
            </span>
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] leading-relaxed">
            Four proprietary architectural breakthroughs that give you an unfair competitive advantage.
          </p>
        </div>

        {/* 3D Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 max-w-6xl mx-auto">
          {/* Card 1: 18 Autonomous Job Radars (Span 7 cols) */}
          <motion.div
            whileHover={{ y: -4, rotateX: 1, rotateY: -1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="md:col-span-7 rounded-2xl bg-[#12161A] border border-[#252C34] hover:border-[#FF6B00]/50 p-8 shadow-xl transition-all relative overflow-hidden group"
            style={{ transformStyle: "preserve-3d" }}
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-radial from-[#FF6B00]/15 to-transparent blur-3xl pointer-events-none" />
            <div className="flex items-center justify-between mb-6">
              <span className="text-[11px] font-mono uppercase text-[#FF6B00] font-bold tracking-widest">
                01 • RADAR INGESTION
              </span>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30">
                18 FEEDS ACTIVE
              </span>
            </div>

            <h3 className="text-2xl font-bold text-white tracking-tight mb-3">
              18 Autonomous Job Radars
            </h3>
            <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed max-w-lg mb-6">
              Sweeps global, remote, and regional tech boards every 15 minutes. Automatically bypasses sponsored job
              clutter and deduplicates postings with AST-based similarity scoring.
            </p>

            <div className="grid grid-cols-3 gap-3 text-left">
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-white">5,435</div>
                <div className="text-[10px] text-[#8E98A4]">Indexed Roles</div>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-[#22C55E]">&lt;50ms</div>
                <div className="text-[10px] text-[#8E98A4]">Query Speed</div>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-[#F2AA4C]">100%</div>
                <div className="text-[10px] text-[#8E98A4]">Clean Deduplication</div>
              </div>
            </div>
          </motion.div>

          {/* Card 2: Google XYZ Impact Engine (Span 5 cols) */}
          <motion.div
            whileHover={{ y: -4, rotateX: 1, rotateY: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="md:col-span-5 rounded-2xl bg-[#12161A] border border-[#252C34] hover:border-[#F2AA4C]/50 p-8 shadow-xl transition-all relative overflow-hidden group"
            style={{ transformStyle: "preserve-3d" }}
          >
            <div className="flex items-center justify-between mb-6">
              <span className="text-[11px] font-mono uppercase text-[#F2AA4C] font-bold tracking-widest">
                02 • CV OPTIMIZATION
              </span>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                +42% CALLBACKS
              </span>
            </div>

            <h3 className="text-2xl font-bold text-white tracking-tight mb-3">
              Google XYZ Impact Engine
            </h3>
            <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed mb-6">
              Applies Google&apos;s executive hiring formula to every sentence in your resume. Elevates passive duties
              into measurable financial, latency, and scale achievements.
            </p>

            <div className="p-3.5 rounded-xl bg-[#0B0E11] border border-[#1E252D] text-xs font-mono text-[#F2AA4C]">
              &ldquo;Accomplished [X] measured by [Y] doing [Z]&rdquo;
            </div>
          </motion.div>

          {/* Card 3: Socket MX Recruiter Protocol (Span 5 cols) */}
          <motion.div
            whileHover={{ y: -4, rotateX: 1, rotateY: -1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="md:col-span-5 rounded-2xl bg-[#12161A] border border-[#252C34] hover:border-[#38BDF8]/50 p-8 shadow-xl transition-all relative overflow-hidden group"
            style={{ transformStyle: "preserve-3d" }}
          >
            <div className="flex items-center justify-between mb-6">
              <span className="text-[11px] font-mono uppercase text-[#38BDF8] font-bold tracking-widest">
                03 • DIRECT DELIVERY
              </span>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/30">
                99.4% INBOX
              </span>
            </div>

            <h3 className="text-2xl font-bold text-white tracking-tight mb-3">
              Socket MX Protocol
            </h3>
            <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed mb-6">
              Bypasses third-party headhunters and automated portal filters. Direct SMTP handshake verification with
              corporate mailboxes ensures deliverability to hiring managers.
            </p>

            <div className="p-3.5 rounded-xl bg-[#0B0E11] border border-[#1E252D] flex items-center justify-between text-xs font-mono">
              <span className="text-white">recruiting@enterprise.com</span>
              <span className="text-[#22C55E]">✓ MX Verified</span>
            </div>
          </motion.div>

          {/* Card 4: Local-First Privacy Vault (Span 7 cols) */}
          <motion.div
            whileHover={{ y: -4, rotateX: 1, rotateY: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="md:col-span-7 rounded-2xl bg-[#12161A] border border-[#252C34] hover:border-[#22C55E]/50 p-8 shadow-xl transition-all relative overflow-hidden group"
            style={{ transformStyle: "preserve-3d" }}
          >
            <div className="flex items-center justify-between mb-6">
              <span className="text-[11px] font-mono uppercase text-[#22C55E] font-bold tracking-widest">
                04 • SECURITY & PRIVACY
              </span>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                100% LOCAL-FIRST
              </span>
            </div>

            <h3 className="text-2xl font-bold text-white tracking-tight mb-3">
              Encrypted Local-First Vault
            </h3>
            <p className="text-xs sm:text-sm text-[#8E98A4] leading-relaxed max-w-lg mb-6">
              Zero cloud tracking. Your CV, past salaries, contact details, and applications remain safely stored on your
              local machine in encrypted SQLite tables.
            </p>

            <div className="grid grid-cols-3 gap-3 text-left">
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-[#22C55E]">0 Bytes</div>
                <div className="text-[10px] text-[#8E98A4]">Data Exfiltrated</div>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-white">AES-256</div>
                <div className="text-[10px] text-[#8E98A4]">Local Security</div>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0E11] border border-[#1E252D]">
                <div className="text-base font-extrabold text-[#F2AA4C]">On-Device</div>
                <div className="text-[10px] text-[#8E98A4]">SQLite Engine</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 4: LIVE INTERACTIVE ATS RESUME STUDIO & GOOGLE XYZ PLAYGROUND
      ========================================================================= */}
      <section id="ats-studio" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#22C55E]/40 text-[10px] font-mono text-[#22C55E] mb-4">
            <span className="text-[#22C55E]">★</span>
            <span className="font-bold tracking-wider uppercase">INTERACTIVE ATS BENCHMARK STUDIO</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            Benchmark & Optimize Your CV <br />
            <span className="bg-gradient-to-r from-white via-[#F7F3EA] to-[#22C55E] bg-clip-text text-transparent">
              In Real Time.
            </span>
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] leading-relaxed">
            Experience firsthand how Pasha Hunt transforms descriptive duties into high-impact Google XYZ statements.
          </p>
        </div>

        {/* Interactive Studio Container */}
        <div className="max-w-4xl mx-auto rounded-2xl bg-[#12161A] border border-[#252C34] p-6 sm:p-10 shadow-2xl relative">
          {/* Preset Role Selector */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#1E252D] pb-6 mb-8">
            <div className="text-xs font-mono text-[#8E98A4] uppercase font-bold">Choose Benchmark Profile:</div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleSelectPreset("python")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  atsRole === "python" ? "bg-[#FF6B00] text-black" : "bg-[#0B0E11] text-[#8E98A4] hover:text-white"
                }`}
              >
                Python Backend
              </button>
              <button
                onClick={() => handleSelectPreset("fullstack")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  atsRole === "fullstack" ? "bg-[#FF6B00] text-black" : "bg-[#0B0E11] text-[#8E98A4] hover:text-white"
                }`}
              >
                Full Stack Engineer
              </button>
              <button
                onClick={() => handleSelectPreset("aiml")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  atsRole === "aiml" ? "bg-[#FF6B00] text-black" : "bg-[#0B0E11] text-[#8E98A4] hover:text-white"
                }`}
              >
                AI & ML Specialist
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            {/* Left: Input Textarea & Button */}
            <div className="md:col-span-7 space-y-4">
              <label className="block text-xs font-mono uppercase text-[#8E98A4] font-bold">
                Original Bullet Point (Input):
              </label>
              <textarea
                value={rawBullet}
                onChange={(e) => {
                  setRawBullet(e.target.value);
                  setIsOptimized(false);
                }}
                rows={3}
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-xl p-3.5 text-xs text-white font-mono focus:outline-none focus:border-[#FF6B00] resize-none"
              />

              <div className="flex items-center gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleRunOptimizer}
                  className="px-6 py-3 rounded-xl text-xs font-bold bg-[#FF6B00] text-black hover:bg-[#FF7A1A] transition-all shadow-lg shadow-[#FF6B00]/25 flex items-center gap-2 cursor-pointer"
                >
                  <span>⚡ Optimize with Google XYZ</span>
                </motion.button>

                {isOptimized && (
                  <span className="text-xs font-mono text-[#22C55E] flex items-center gap-1">
                    <span>✓</span> Verified XYZ Format
                  </span>
                )}
              </div>

              {/* Transformed Output */}
              <div className="mt-6 pt-4 border-t border-[#1E252D]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono uppercase text-[#22C55E] font-bold">
                    Optimized Google XYZ Statement:
                  </span>
                  <button
                    onClick={handleCopyBullet}
                    className="text-[11px] font-mono text-[#F2AA4C] hover:text-white transition-colors cursor-pointer"
                  >
                    {copiedBullet ? "✓ Copied to Clipboard" : "Copy Bullet"}
                  </button>
                </div>
                <div className="p-4 rounded-xl bg-[#0B0E11] border border-[#22C55E]/40 text-xs sm:text-sm text-white font-medium leading-relaxed">
                  {optimizedBullet}
                </div>
              </div>
            </div>

            {/* Right: Real-time ATS Score Ring & Verification Breakdown */}
            <div className="md:col-span-5 bg-[#0B0E11] p-6 rounded-xl border border-[#252C34] text-center space-y-4">
              <div className="text-xs font-mono uppercase text-[#8E98A4] font-bold">ATS Compatibility Score</div>

              <div className="relative w-32 h-32 mx-auto flex items-center justify-center">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="42" stroke="#1E252D" strokeWidth="8" fill="none" />
                  <motion.circle
                    cx="50"
                    cy="50"
                    r="42"
                    stroke={atsScore >= 90 ? "#22C55E" : "#F2AA4C"}
                    strokeWidth="8"
                    strokeDasharray="264"
                    strokeDashoffset={264 - (264 * atsScore) / 100}
                    strokeLinecap="round"
                    fill="none"
                    transition={{ duration: 0.8, type: "spring" }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-black text-white">{atsScore}%</span>
                  <span className="text-[9px] font-mono text-[#8E98A4]">Score</span>
                </div>
              </div>

              <div className="text-xs font-bold text-white">
                {atsScore >= 90 ? "Elite (Top 2% ATS Ready)" : "Qualified (Average ATS Pass)"}
              </div>

              <div className="space-y-2 text-[11px] text-[#8E98A4] text-left pt-2 border-t border-[#1E252D]">
                <div className="flex items-center justify-between">
                  <span>Action Verb Strength:</span>
                  <span className="text-[#22C55E] font-bold">98% High</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Quantified Scale Metrics:</span>
                  <span className="text-[#22C55E] font-bold">100% Present</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Keyword Density Match:</span>
                  <span className="text-[#22C55E] font-bold">94% High</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 5: 18-RADAR LIVE OPPORTUNITY STREAM
      ========================================================================= */}
      <section id="live-stream" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/40 text-[10px] font-mono text-[#F2AA4C] mb-4">
            <span className="text-[#FF6B00]">★</span>
            <span className="font-bold tracking-wider uppercase">LIVE RADAR STREAM</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            5,435 Opportunities Synchronized <br />
            <span className="bg-gradient-to-r from-[#FF6B00] via-[#FF8533] to-[#F2AA4C] bg-clip-text text-transparent">
              Across 18 Radar Feeds.
            </span>
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] leading-relaxed">
            Real opportunities filtered, deduplicated, and matched directly to your tech stack.
          </p>
        </div>

        {/* Filter Pills & Search Bar */}
        <div className="max-w-5xl mx-auto flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {[
              { id: "all", label: "All Roles (5,435)" },
              { id: "python", label: "Python / AI" },
              { id: "fullstack", label: "Full Stack" },
              { id: "pakistan", label: "Pakistan Tech" },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setStreamFilter(f.id)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  streamFilter === f.id ? "bg-[#FF6B00] text-black" : "bg-[#12161A] text-[#8E98A4] hover:text-white"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div className="w-full sm:w-64">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search title, company, skills..."
              className="w-full bg-[#12161A] border border-[#252C34] rounded-xl px-3.5 py-2 text-xs text-white placeholder-[#5C6572] focus:outline-none focus:border-[#FF6B00]"
            />
          </div>
        </div>

        {/* Job Stream Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {filteredJobs.map((job) => (
            <motion.div
              key={job.id}
              whileHover={{ y: -4 }}
              transition={{ type: "spring", stiffness: 350, damping: 25 }}
              className="p-6 rounded-2xl bg-[#12161A] border border-[#252C34] hover:border-[#FF6B00]/40 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`w-9 h-9 rounded-xl bg-gradient-to-br ${job.logoColor} flex items-center justify-center font-black text-white text-base shadow-md`}
                  >
                    {job.logo}
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                    {job.match}
                  </span>
                </div>

                <h4 className="text-base font-bold text-white tracking-tight">{job.title}</h4>
                <div className="text-xs text-[#8E98A4] mt-1">
                  {job.company} • {job.location}
                </div>

                <div className="mt-4 flex flex-wrap gap-1.5">
                  {job.tags.map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 rounded text-[9px] font-mono bg-[#0B0E11] text-[#8E98A4] border border-[#1E252D]"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-[#1E252D] flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-white">{job.salary}</span>
                <a
                  href="#transmission"
                  className="font-bold text-[#FF6B00] hover:text-[#FF8533] flex items-center gap-1 transition-colors"
                >
                  <span>Apply Now</span>
                  <span>→</span>
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 6: 7-STAGE APPLICATION PIPELINE VISUALIZER
      ========================================================================= */}
      <section id="pipeline" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#38BDF8]/40 text-[10px] font-mono text-[#38BDF8] mb-4">
            <span className="text-[#38BDF8]">★</span>
            <span className="font-bold tracking-wider uppercase">APPLICATION COMMAND CENTER</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            From Cold Discovery to <br />
            <span className="bg-gradient-to-r from-white via-[#F7F3EA] to-[#38BDF8] bg-clip-text text-transparent">
              Signed Offer.
            </span>
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#8E98A4] leading-relaxed">
            The 7-stage automated career pipeline orchestrated end-to-end on your local desktop.
          </p>
        </div>

        {/* 7 Horizontal Pipeline Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 max-w-6xl mx-auto">
          {[
            { step: "01", title: "Discovered", desc: "18 Feeds Swept", metric: "5,435", color: "border-[#FF6B00]" },
            { step: "02", title: "AI Analyzed", desc: "Compatibility Filter", metric: "92%", color: "border-[#F2AA4C]" },
            { step: "03", title: "XYZ Tailored", desc: "Executive Bullets", metric: "11/11", color: "border-[#22C55E]" },
            { step: "04", title: "Recruiter MX", desc: "Direct Socket Verified", metric: "99.4%", color: "border-[#38BDF8]" },
            { step: "05", title: "Dispatched", desc: "Direct Email Outbox", metric: "8 Sent", color: "border-purple-500" },
            { step: "06", title: "Interviews", desc: "Calendar Scheduled", metric: "2 Confirmed", color: "border-pink-500" },
            { step: "07", title: "Offer Secured", desc: "Milestone Achieved", metric: "Top 2%", color: "border-emerald-400" },
          ].map((st) => (
            <div
              key={st.step}
              className={`p-4 rounded-xl bg-[#12161A] border-t-2 ${st.color} border-[#252C34] text-left space-y-2`}
            >
              <div className="text-[10px] font-mono text-[#8E98A4] font-bold">{st.step}</div>
              <div className="text-sm font-bold text-white">{st.title}</div>
              <div className="text-[10px] text-[#8E98A4]">{st.desc}</div>
              <div className="pt-2 text-xs font-mono font-bold text-[#FF6B00]">{st.metric}</div>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 7: INTERACTIVE FAQ ACCORDION
      ========================================================================= */}
      <section id="faq" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181D22] border border-[#FF6B00]/40 text-[10px] font-mono text-[#F2AA4C] mb-4">
            <span className="text-[#FF6B00]">★</span>
            <span className="font-bold tracking-wider uppercase">FREQUENTLY ASKED QUESTIONS</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
            Everything You Need to Know <br />
            <span className="bg-gradient-to-r from-white via-[#F7F3EA] to-[#8E98A4] bg-clip-text text-transparent">
              About Pasha Hunt 2.0.
            </span>
          </h2>
        </div>

        {/* Accordion Container */}
        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-[#12161A] border border-[#252C34] overflow-hidden transition-all"
            >
              <button
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                className="w-full p-5 text-left flex items-center justify-between text-sm sm:text-base font-bold text-white hover:text-[#FF6B00] transition-colors cursor-pointer"
              >
                <span>{faq.q}</span>
                <span className="text-[#FF6B00] text-lg font-mono">{openFaq === idx ? "−" : "+"}</span>
              </button>

              <AnimatePresence>
                {openFaq === idx && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="px-5 pb-5 text-xs sm:text-sm text-[#8E98A4] leading-relaxed border-t border-[#1E252D] pt-3"
                  >
                    {faq.a}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 8: HIGH-END 3D GLASS CTA & TRANSMISSION CONSOLE
      ========================================================================= */}
      <section id="transmission" className="relative z-10 py-28 px-6 max-w-7xl mx-auto border-t border-[#1E252D] scroll-mt-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start max-w-5xl mx-auto">
          {/* Download Box */}
          <div className="p-8 rounded-2xl bg-[#12161A] border border-[#252C34] shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-[#FF6B00]/10 rounded-full blur-3xl pointer-events-none" />
            <span className="text-[11px] font-mono uppercase text-[#FF6B00] font-bold tracking-widest block mb-2">
              WINDOWS DESKTOP WORKSTATION
            </span>
            <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight">Download Pasha Hunt 2.0</h3>
            <p className="text-xs sm:text-sm text-[#8E98A4] mt-2 leading-relaxed">
              Standalone Windows x64 Workstation. Zero cloud latency, 100% local SQLite privacy, and native 18-feed
              autonomous scraper sweeps.
            </p>

            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              href="https://github.com/pasha804/pasha-hunt/releases/latest"
              className="mt-8 w-full py-4 rounded-xl text-sm font-bold bg-[#FF6B00] text-black hover:bg-[#FF7A1A] transition-all shadow-xl shadow-[#FF6B00]/30 flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Download for Windows (v2.0)</span>
              <span>↓</span>
            </motion.a>

            <div className="mt-4 flex items-center justify-between text-[11px] font-mono text-[#8E98A4]">
              <span>x64 Standalone Executable</span>
              <span>v2.0 APINEX Edition</span>
            </div>
          </div>

          {/* Contact Box */}
          <div className="p-8 rounded-2xl bg-[#12161A] border border-[#252C34] shadow-2xl">
            <span className="text-[11px] font-mono uppercase text-[#FF6B00] font-bold tracking-widest block mb-2">
              COMMERCIAL INQUIRIES
            </span>
            <h3 className="text-2xl font-bold text-white tracking-tight">Direct Transmission</h3>
            <p className="text-xs text-[#8E98A4] mt-1">Direct message to Muhammad Mubashar (Founder & Architect).</p>

            <form onSubmit={handleContactSubmit} className="mt-6 space-y-3">
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
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-3 text-xs text-white font-mono focus:outline-none focus:border-[#FF6B00]"
              />
              <input
                type="email"
                required
                value={contactForm.email}
                onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                placeholder="Your work email"
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-3 text-xs text-white font-mono focus:outline-none focus:border-[#FF6B00]"
              />
              <textarea
                required
                rows={3}
                value={contactForm.inquiry}
                onChange={(e) => setContactForm({ ...contactForm, inquiry: e.target.value })}
                placeholder="Inquiry, partnership proposal or feedback..."
                className="w-full bg-[#0B0E11] border border-[#252C34] rounded-lg p-3 text-xs text-white font-mono resize-none focus:outline-none focus:border-[#FF6B00]"
              />
              <button
                type="submit"
                disabled={contactStatus === "submitting"}
                className="w-full py-3 rounded-lg text-xs font-bold bg-[#181D22] border border-[#303844] text-white hover:border-[#FF6B00] hover:text-[#FF6B00] transition-all cursor-pointer"
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
        <div className="mt-20 pt-8 border-t border-[#1E252D] flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-[#8E98A4]">
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

      {/* Demo Modal */}
      <AnimatePresence>
        {demoOpen && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6"
            onClick={() => setDemoOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-3xl bg-[#12161A] border border-[#252C34] rounded-2xl p-6 shadow-2xl relative"
            >
              <div className="flex items-center justify-between pb-4 border-b border-[#252C34]">
                <h3 className="text-lg font-bold text-white">Pasha Hunt 2.0 — Live Workstation Walkthrough</h3>
                <button onClick={() => setDemoOpen(false)} className="text-[#8E98A4] hover:text-white text-lg">
                  ✕
                </button>
              </div>
              <div className="mt-4 aspect-video bg-[#0B0E11] rounded-xl flex items-center justify-center border border-[#1E252D] text-center p-6">
                <div>
                  <div className="w-12 h-12 rounded-full bg-[#FF6B00]/20 text-[#FF6B00] flex items-center justify-center mx-auto text-xl mb-3">
                    ▶
                  </div>
                  <div className="text-sm font-bold text-white">Interactive Product Demonstration</div>
                  <div className="text-xs text-[#8E98A4] mt-1 max-w-sm">
                    Running live on your local machine with PySide6 & embedded local IPC server at 127.0.0.1:58241.
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
