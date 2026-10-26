import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AgenticHero from "@/components/AgenticHero";
import {
  Search, ArrowRight, Database, BrainCircuit, FileBarChart2,
  Shield, Zap, Mail
} from "lucide-react";

const exampleQueries = [
  "Immunotherapy trials for glioblastoma 2023–2024",
  "SGLT2i vs GLP-1 efficacy in heart failure",
  "JAK inhibitors safety in rheumatoid arthritis",
  "mRNA vaccine efficacy in elderly populations",
];

const stats = [
  { value: "35.2M+", label: "Indexed Records", detail: "MEDLINE, PubMed Central & PMC" },
  { value: "< 14s",   label: "Synthesis Latency", detail: "Multi-agent literature orchestration" },
  { value: "GRADE",  label: "Certainty Standard", detail: "Objective evidence quality assessment" },
  { value: "100%",   label: "Audited Citations", detail: "Direct DOI and PMCID verifiable backlinks" },
];

const capabilities = [
  {
    num: "01",
    icon: Database,
    title: "Live PubMed Central Retrieval",
    desc: "Autonomous retrieval pipeline querying 35M+ peer-reviewed citations across MEDLINE and PMC for randomized controlled trials and meta-analyses.",
    tag: "PMC ARCHIVE",
  },
  {
    num: "02",
    icon: BrainCircuit,
    title: "Multi-Agent Synthesis Engine",
    desc: "Specialized reasoning agents coordinate search parameter formulation, exclusion filtering, and comparative evidence synthesis.",
    tag: "LANGGRAPH AGENTS",
  },
  {
    num: "03",
    icon: Shield,
    title: "GRADE Certainty Grading",
    desc: "Evaluates risk of bias, inconsistency, indirectness, and imprecision following standardized GRADE clinical methodology.",
    tag: "QUALITY AUDIT",
  },
  {
    num: "04",
    icon: FileBarChart2,
    title: "Structured Evidence Matrices",
    desc: "Compiles study designs, sample sizes (n), primary clinical endpoints, effect sizes, and documented limitations into comparative tables.",
    tag: "PICO FRAMEWORK",
  },
  {
    num: "05",
    icon: Mail,
    title: "Archival Delivery & Export",
    desc: "Transmit comprehensive research syntheses directly to clinical colleagues via formatted PDF reports and spreadsheet matrices.",
    tag: "DISPATCH READY",
  },
  {
    num: "06",
    icon: Zap,
    title: "Transparent Reasoning Stream",
    desc: "Inspect intermediate search queries, isolated publication counts, and reasoning milestones token-by-token in real time.",
    tag: "AUDITABLE AI",
  },
];

const steps = [
  {
    num: "01",
    title: "Formulate Clinical Query",
    desc: "Pose your question using natural clinical terminology or PICO frameworks. The engine parses therapeutic drug classes and target patient populations.",
  },
  {
    num: "02",
    title: "Autonomous Systematic Extraction",
    desc: "Agents isolate pertinent trials, extract statistical endpoints, filter confounding biases, and grade certainty using GRADE protocols.",
  },
  {
    num: "03",
    title: "Receive Structured Synthesis",
    desc: "A verified synthesis with full narrative analysis, structured evidence tables, and definitive clinical takeaways is compiled instantly.",
  },
];

const Index = () => {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) navigate("/search", { state: { query } });
  };

  return (
    <div className="editorial-paper min-h-screen flex flex-col text-[#211B20]">
      <Navbar />

      <main className="flex-1 flex flex-col items-center pt-20 sm:pt-24 pb-24 px-4 sm:px-6">

        {/* ── Reconstructed Typography-Led Hero (No Image, Staggered One After Another) ── */}
        <section className="w-full max-w-6xl mx-auto pt-2 pb-14 sm:pb-20">

          {/* Staggered 3-Line Display Headline ("One After Another" Diagonal Cascade) */}
          <h1 className="hero-title w-full select-none text-left">
            <span className="hero-title__line hero-title__line--one whitespace-nowrap">
              <span className="invisible select-none pointer-events-none hidden sm:inline" aria-hidden="true">intell</span><span className="hero-title__line-one-text">Your intelligent</span>
            </span>

            <span className="hero-title__line hero-title__line--two whitespace-nowrap">
              <span className="invisible select-none pointer-events-none hidden sm:inline" aria-hidden="true">Your intell</span><span className="hero-title__gradient">medical research</span>
            </span>

            <span className="hero-title__line hero-title__line--three whitespace-nowrap">
              <span className="invisible select-none pointer-events-none hidden sm:inline" aria-hidden="true">Your intell</span><span className="invisible select-none pointer-events-none hidden sm:inline" aria-hidden="true">medical res</span><span className="hero-title__line-three-text">assistant</span><span className="hero-title__accent">.</span>
            </span>
          </h1>

          {/* Supporting Description & Broad Query Control positioned beneath headline */}
          <div className="mt-10 sm:mt-14 max-w-3xl mx-auto flex flex-col items-center text-center space-y-6">
            <p className="text-base sm:text-lg text-[#6B5F69] leading-relaxed font-sans max-w-2xl mx-auto text-center">
              Query 35M+ peer-reviewed citations with an autonomous agent pipeline.
              Isolate clinical trials, extract statistical effect sizes, and synthesize evidence using GRADE certainty standards.
            </p>

            {/* Wide, Minimal Research Query Input with Crystal Polish */}
            <div className="space-y-3.5 pt-1 w-full flex flex-col items-center">
              <div className="crystal-input rounded-xl flex items-center px-4 sm:px-5 py-1.5 gap-3 bg-white w-full max-w-2xl shadow-sm mx-auto">
                <Search className="w-4 h-4 text-[#B8AEA3] flex-shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Enter clinical question, therapeutic comparison, or outcome…"
                  className="flex-1 h-13 bg-transparent text-[#211B20] placeholder:text-[#B8AEA3] text-sm sm:text-[15px] outline-none font-sans"
                />
                <button
                  onClick={handleSearch}
                  disabled={!query.trim()}
                  className="crystal-button flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-heading font-semibold uppercase tracking-wider flex-shrink-0"
                >
                  <span>Synthesize</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#EAAA00]" />
                </button>
              </div>

              {/* Compact Suggested Query Outlines */}
              <div className="flex flex-wrap items-center justify-center gap-2 pt-0.5 mx-auto">
                <span className="text-[11px] font-mono uppercase tracking-wider text-[#B8AEA3] mr-1">
                  Inquire:
                </span>
                {exampleQueries.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => { setQuery(q); inputRef.current?.focus(); }}
                    className="text-xs px-3 py-1 rounded border border-[#DDE3E8] bg-[#FAF8F5] text-[#6B5F69] hover:text-[#3A0F34] hover:border-[#3A0F34] hover:bg-white transition-all text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

          </div>

        </section>

        {/* ── Section 01: Live Research-Agent Console ────────── */}
        <section className="w-full max-w-6xl mx-auto mt-16 sm:mt-24">
          <div className="flex items-center justify-between mb-4 border-b border-[#DDE3E8] pb-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono font-bold text-[#3A0F34] tracking-widest uppercase">
                [ SECTION 01 — ORCHESTRATION ]
              </span>
              <span className="text-xs font-mono text-[#B8AEA3] uppercase">
                AUTONOMOUS PIPELINE TRACE
              </span>
            </div>
            <span className="text-[11px] font-mono text-[#6B5F69] hidden sm:inline">
              LANGGRAPH SSE STREAM ENGINE
            </span>
          </div>

          <AgenticHero />
        </section>

        {/* ── 4-Metric Editorial Grid ────────────────────────── */}
        <section className="w-full max-w-6xl mx-auto mt-20 sm:mt-28">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {stats.map((s, idx) => (
              <div
                key={idx}
                className="crystal-card rounded-2xl p-6 sm:p-7 relative overflow-hidden bg-[#FAF8F5] border border-[#DDE3E8] group"
              >
                <div className="text-3xl sm:text-4xl font-extrabold text-[#3A0F34] tracking-tight mb-2 font-heading">
                  {s.value}
                </div>
                <div className="text-xs font-bold text-[#211B20] tracking-wider uppercase mb-1 font-heading">
                  {s.label}
                </div>
                <div className="text-xs text-[#6B5F69] leading-relaxed">
                  {s.detail}
                </div>
                <div className="absolute bottom-0 left-6 right-6 h-[2px] bg-[#EAAA00] scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300" />
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 02: Structural Biology & Capabilities ──── */}
        <section className="w-full max-w-6xl mx-auto mt-24 sm:mt-32">
          <div className="border-t border-[#DDE3E8] pt-12 mb-12">
            <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4">
              <div>
                <p className="text-xs font-mono font-bold tracking-widest text-[#EAAA00] uppercase mb-2">
                  [ SECTION 02 — CAPABILITIES ]
                </p>
                <h2 className="text-clamp-section text-[#211B20]">
                  <span className="block">Architected for</span>
                  <span className="section-gradient-gloss">
                    Evidence Synthesis.
                  </span>
                </h2>
              </div>
              <p className="text-sm text-[#6B5F69] max-w-md leading-relaxed">
                Transforming fragmented medical literature into structured PICO matrices with verified citations and GRADE certainty assessment.
              </p>
            </div>
          </div>

          {/* Cryo-EM Protein Structure Showcase Banner (Below the Fold) */}
          <div className="crystal-card rounded-2xl p-4 sm:p-6 mb-10 bg-white border border-[#DDE3E8]">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              <div className="lg:col-span-7 rounded-xl overflow-hidden aspect-[16/9] border border-[#DDE3E8] bg-[#FAF8F5]">
                <img
                  src="/medical-protein-structure.jpg"
                  alt="High-resolution Cryo-EM structure of kinase protein complex with small molecule inhibitor in marigold"
                  className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                />
              </div>

              <div className="lg:col-span-5 space-y-4 px-2 sm:px-4">
                <span className="text-[10px] font-mono tracking-widest px-2.5 py-1 rounded bg-[#FAF8F5] border border-[#DDE3E8] text-[#3A0F34] font-semibold uppercase">
                  FIG. 02 — STRUCTURAL PHARMACOLOGY
                </span>
                <h3 className="text-2xl sm:text-3xl text-[#211B20] font-editorial italic font-normal tracking-[-0.025em] leading-snug">
                  From Literature Text to Molecular & Clinical Endpoints
                </h3>
                <p className="text-sm text-[#6B5F69] leading-relaxed">
                  Instead of reading dozens of disparate 30-page papers, our multi-agent architecture isolates randomized controlled trials, extracts intervention arms and effect sizes, and evaluates risk of bias automatically.
                </p>
                <div className="pt-2">
                  <button
                    onClick={() => navigate("/search")}
                    className="crystal-button inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-heading font-semibold uppercase tracking-wider"
                  >
                    <span>Launch Research Tool</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#EAAA00]" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 6 Capabilities Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((c, idx) => (
              <div
                key={idx}
                className="crystal-card rounded-2xl p-6 sm:p-7 flex flex-col justify-between hover:border-[#3A0F34] bg-white"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-[#DDE3E8] pb-3">
                    <span className="text-[11px] font-mono text-[#EAAA00] font-bold">
                      {c.num}
                    </span>
                    <span className="text-[9px] font-mono tracking-widest text-[#B8AEA3] uppercase">
                      {c.tag}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-[#211B20] font-heading tracking-tight">
                    {c.title}
                  </h3>

                  <p className="text-xs text-[#6B5F69] leading-relaxed">
                    {c.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 03: 3-Step Systematic Protocol ─────────── */}
        <section className="w-full max-w-6xl mx-auto mt-24 sm:mt-32">
          <div className="border-t border-[#DDE3E8] pt-12 mb-12 text-center">
            <p className="text-xs font-mono font-bold tracking-widest text-[#3A0F34] uppercase mb-2">
              [ SECTION 03 — METHODOLOGY ]
            </p>
            <h2 className="text-clamp-section text-[#211B20]">
              <span className="block">Systematic Protocol in</span>
              <span className="section-gradient-gloss">
                Three Movements.
              </span>
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {steps.map((s, idx) => (
              <div
                key={idx}
                className="crystal-card rounded-2xl p-7 relative border border-[#DDE3E8] bg-[#FAF8F5] space-y-4"
              >
                <div className="text-4xl font-mono font-bold text-[#3A0F34] leading-none">
                  {s.num}.
                </div>
                <h3 className="text-base font-bold text-[#211B20] font-heading tracking-tight">
                  {s.title}
                </h3>
                <p className="text-xs text-[#6B5F69] leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Closing Callout: Ice Silver Surface ───────────── */}
        <section className="w-full max-w-6xl mx-auto mt-24 sm:mt-32">
          <div className="editorial-silver-cta rounded-3xl p-8 sm:p-14 text-center relative overflow-hidden">
            <div className="relative z-10 max-w-2xl mx-auto space-y-6">
              <span className="inline-block text-[10px] font-mono tracking-widest px-3 py-1 rounded bg-[#FAF8F5]/80 border border-[#3A0F34]/[0.16] text-[#3A0F34] uppercase font-semibold">
                CLINICAL LITERATURE DISCOVERY
              </span>

              <h2 className="editorial-cta-headline text-3xl sm:text-5xl lg:text-6xl text-[#3A0F34]">
                <span className="block text-[#3A0F34]">Synthesize literature with</span>
                <span className="editorial-cta-gradient block mt-1.5">
                  journal-ready certainty.
                </span>
              </h2>

              <p className="text-sm sm:text-base text-[#211B20] leading-relaxed max-w-xl mx-auto">
                No subscription required. Query live PubMed Central databases with automated GRADE assessment and exportable clinical matrices.
              </p>

              <div className="pt-2">
                <button
                  onClick={() => navigate("/search")}
                  className="btn-editorial-marigold inline-flex items-center gap-2.5 px-8 py-3.5 rounded-xl text-xs font-heading font-bold uppercase tracking-wider"
                >
                  <span className="text-[#211B20]">Begin Clinical Query</span>
                  <ArrowRight className="w-4 h-4 text-[#3A0F34]" />
                </button>
              </div>
            </div>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
};

export default Index;
