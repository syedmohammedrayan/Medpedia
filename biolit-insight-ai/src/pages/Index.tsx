import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AgenticHero from "@/components/AgenticHero";
import {
  Search, ArrowRight, Database, BrainCircuit, FileBarChart2,
  Shield, Zap, Mail, Stethoscope, CheckCircle2,
} from "lucide-react";

const exampleQueries = [
  "Immunotherapy trials for glioblastoma 2023–2024",
  "SGLT2i vs GLP-1 efficacy in heart failure",
  "JAK inhibitors safety in rheumatoid arthritis",
  "mRNA vaccine efficacy in elderly populations",
];

const features = [
  {
    color: "indigo",
    icon: Database,
    badge: "35M+ Articles",
    title: "Live PubMed Search",
    desc: "Real-time access to 35M+ peer-reviewed articles from PubMed Central and MEDLINE databases.",
  },
  {
    color: "violet",
    icon: BrainCircuit,
    badge: "Multi-Agent AI",
    title: "Agentic Synthesis",
    desc: "Multi-step AI pipeline that retrieves, ranks, and synthesizes clinical evidence automatically.",
  },
  {
    color: "cyan",
    icon: FileBarChart2,
    badge: "Structured Data",
    title: "Evidence Tables",
    desc: "Structured evidence matrices with effect sizes, p-values, and study limitations — exportable.",
  },
  {
    color: "emerald",
    icon: Shield,
    badge: "GRADE System",
    title: "Quality Grading",
    desc: "Automatic evidence quality assessment following GRADE methodology standards.",
  },
  {
    color: "rose",
    icon: Mail,
    badge: "PDF + Email",
    title: "Report Delivery",
    desc: "Export your synthesis as a formatted PDF report or receive it directly to your email.",
  },
  {
    color: "amber",
    icon: Zap,
    badge: "Real-time",
    title: "Streaming Results",
    desc: "Watch the AI agent work live — results stream token-by-token as analysis runs.",
  },
];

const stats = [
  { color: "indigo", icon: Database, value: "35M+", label: "PubMed Articles", sub: "MEDLINE + PMC" },
  { color: "violet", icon: BrainCircuit, value: "AI", label: "Agentic Pipeline", sub: "Multi-step reasoning" },
  { color: "emerald", icon: CheckCircle2, value: "GRADE", label: "Evidence Quality", sub: "Systematic grading" },
  { color: "cyan", icon: Zap, value: "Live", label: "Streaming Results", sub: "Real-time output" },
];

const steps = [
  {
    color: "indigo",
    num: "01",
    icon: Search,
    title: "Enter Your Clinical Question",
    desc: "Type any clinical or biomedical research question. Our system understands complex medical terminology and PICO frameworks.",
  },
  {
    color: "violet",
    num: "02",
    icon: BrainCircuit,
    title: "AI Searches & Analyzes",
    desc: "The agent searches PubMed, extracts key data, grades evidence quality, and identifies patterns across studies.",
  },
  {
    color: "emerald",
    num: "03",
    icon: FileBarChart2,
    title: "Receive Structured Report",
    desc: "Get a comprehensive synthesis with evidence tables, narrative analysis, and a clinical verdict — ready to cite.",
  },
];

const colorMap: Record<string, {
  feat: string; iconBg: string; icon: string; badge: string;
  stepBg: string; title: string; num: string;
}> = {
  indigo:  { feat: "feat-indigo",  iconBg: "bg-indigo-100",  icon: "text-indigo-600",  badge: "bg-indigo-100 text-indigo-700 border-indigo-300",  stepBg: "bg-indigo-50 border-indigo-200",  title: "text-indigo-800",  num: "text-indigo-300" },
  violet:  { feat: "feat-violet",  iconBg: "bg-violet-100",  icon: "text-violet-600",  badge: "bg-violet-100 text-violet-700 border-violet-300",  stepBg: "bg-violet-50 border-violet-200",  title: "text-violet-800",  num: "text-violet-300" },
  cyan:    { feat: "feat-cyan",    iconBg: "bg-cyan-100",    icon: "text-cyan-600",    badge: "bg-cyan-100 text-cyan-700 border-cyan-300",    stepBg: "bg-cyan-50 border-cyan-200",    title: "text-cyan-800",    num: "text-cyan-300" },
  emerald: { feat: "feat-emerald", iconBg: "bg-emerald-100", icon: "text-emerald-600", badge: "bg-emerald-100 text-emerald-700 border-emerald-300", stepBg: "bg-emerald-50 border-emerald-200", title: "text-emerald-800", num: "text-emerald-300" },
  rose:    { feat: "feat-rose",    iconBg: "bg-rose-100",    icon: "text-rose-600",    badge: "bg-rose-100 text-rose-700 border-rose-300",    stepBg: "bg-rose-50 border-rose-200",    title: "text-rose-800",    num: "text-rose-300" },
  amber:   { feat: "feat-amber",   iconBg: "bg-amber-100",   icon: "text-amber-600",   badge: "bg-amber-100 text-amber-700 border-amber-300",   stepBg: "bg-amber-50 border-amber-200",   title: "text-amber-800",   num: "text-amber-300" },
};

const statColorMap: Record<string, { card: string; val: string; label: string; sub: string; icon: string }> = {
  indigo:  { card: "stat-indigo",  val: "text-indigo-700",  label: "text-indigo-600",  sub: "text-indigo-400",  icon: "text-indigo-400" },
  violet:  { card: "stat-violet",  val: "text-violet-700",  label: "text-violet-600",  sub: "text-violet-400",  icon: "text-violet-400" },
  emerald: { card: "stat-emerald", val: "text-emerald-700", label: "text-emerald-600", sub: "text-emerald-400", icon: "text-emerald-400" },
  cyan:    { card: "stat-cyan",    val: "text-cyan-700",    label: "text-cyan-600",    sub: "text-cyan-400",    icon: "text-cyan-400" },
};

const chipColors = [
  "hover:border-indigo-300 hover:text-indigo-700 hover:bg-indigo-50",
  "hover:border-violet-300 hover:text-violet-700 hover:bg-violet-50",
  "hover:border-cyan-300 hover:text-cyan-700 hover:bg-cyan-50",
  "hover:border-emerald-300 hover:text-emerald-700 hover:bg-emerald-50",
];

const Index = () => {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) navigate("/search", { state: { query } });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="hero-premium min-h-screen flex flex-col"
    >
      <Navbar />

      <main className="flex-1 flex flex-col items-center px-6 pt-40 pb-20">
        {/* ── Hero ─────────────────────────────────────────── */}
        <div className="w-full max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="text-center space-y-8"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.92 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.06 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full badge-gradient text-xs font-semibold shadow-sm"
            >
              <span className="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 animate-pulse" />
              AI-Powered Clinical Research Engine
              <span className="px-1.5 py-0.5 rounded-md bg-indigo-500 text-white text-[10px] font-bold">NEW</span>
            </motion.div>

            {/* Headline */}
            <div className="space-y-3">
              <h1 className="text-5xl sm:text-6xl md:text-7xl font-black text-slate-900 leading-[1.04]">
                Your Intelligent
                <br />
                <span className="text-gradient-vivid">Medical Research</span>
                <br />
                <span className="text-slate-800">Assistant</span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
                Ask any clinical question. The AI agent searches PubMed, extracts evidence,
                grades quality, and returns a structured synthesis — in seconds.
              </p>
            </div>

            {/* Search bar */}
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="max-w-2xl mx-auto space-y-4"
            >
              <div className="search-wrap rounded-2xl flex items-center px-4 gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0 shadow-sm shadow-indigo-200">
                  <Search className="w-4 h-4 text-white" />
                </div>
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="e.g. Efficacy of semaglutide in type 2 diabetes meta-analyses"
                  className="flex-1 h-14 bg-transparent text-slate-800 placeholder:text-slate-400 text-[15px] outline-none"
                />
                <button
                  onClick={handleSearch}
                  disabled={!query.trim()}
                  className="btn-primary flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold flex-shrink-0"
                >
                  Search
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              <div className="flex flex-wrap gap-2 justify-center items-center">
                <span className="text-xs text-slate-400 font-medium">Try:</span>
                {exampleQueries.map((q, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => { setQuery(q); inputRef.current?.focus(); }}
                    className={`px-3 py-1.5 text-xs text-slate-600 border border-slate-200 bg-white rounded-lg transition-all shadow-sm font-medium ${chipColors[i]}`}
                  >
                    {q}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* ── Agentic Preview ──────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.30, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="mt-8"
          >
            <AgenticHero />
          </motion.div>

          {/* ── Stat Cards ───────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.38 }}
            className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-14"
          >
            {stats.map(({ color, icon: Icon, value, label, sub }) => (
              <motion.div
                key={label}
                whileHover={{ y: -4, scale: 1.03 }}
                transition={{ type: "spring", stiffness: 280, damping: 22 }}
                className={`stat-card ${statColorMap[color].card} rounded-2xl p-5`}
              >
                <Icon className={`w-6 h-6 ${statColorMap[color].icon} mb-3`} />
                <div className={`text-3xl font-black leading-none mb-1 ${statColorMap[color].val}`}>{value}</div>
                <div className={`text-sm font-semibold leading-tight ${statColorMap[color].label}`}>{label}</div>
                <div className={`text-xs mt-0.5 ${statColorMap[color].sub}`}>{sub}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* ── Feature Cards ─────────────────────────────────── */}
        <div className="w-full max-w-5xl mx-auto mt-28">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <p className="text-xs font-bold tracking-widest text-indigo-500 uppercase mb-3">Capabilities</p>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900">
              Everything You Need for
              <br />
              <span className="text-gradient-pro">Clinical Evidence Synthesis</span>
            </h2>
            <p className="text-slate-500 mt-4 max-w-xl mx-auto text-base leading-relaxed">
              A complete AI research pipeline — from raw PubMed search to structured, citable synthesis.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => {
              const c = colorMap[f.color];
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 22 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.07, duration: 0.5 }}
                  className={`feat-card ${c.feat} rounded-2xl p-6`}
                >
                  <div className={`w-12 h-12 rounded-xl ${c.iconBg} flex items-center justify-center mb-4`}>
                    <f.icon className={`w-6 h-6 ${c.icon}`} />
                  </div>
                  <span className={`inline-block text-[10px] font-bold tracking-wide px-2.5 py-1 rounded-md border ${c.badge} mb-3`}>
                    {f.badge}
                  </span>
                  <h3 className={`text-base font-bold mb-2 ${c.title}`}>{f.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* ── How It Works ──────────────────────────────────── */}
        <div className="w-full max-w-4xl mx-auto mt-28">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <p className="text-xs font-bold tracking-widest text-violet-500 uppercase mb-3">How It Works</p>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900">
              Research in{" "}
              <span className="text-gradient-pro">3 Simple Steps</span>
            </h2>
            <p className="text-slate-500 mt-4 max-w-xl mx-auto text-base leading-relaxed">
              No sign-up required. Just type your question and let the AI do the heavy lifting.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {steps.map((s, i) => {
              const c = colorMap[s.color];
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 22 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.12 }}
                  className={`${c.stepBg} border rounded-2xl p-7 text-center relative overflow-hidden`}
                >
                  <div className={`absolute top-4 right-5 text-7xl font-black ${c.num} leading-none select-none`}>
                    {s.num}
                  </div>
                  <div className={`w-13 h-13 w-12 h-12 rounded-xl ${c.iconBg} flex items-center justify-center mx-auto mb-5 relative z-10`}>
                    <s.icon className={`w-6 h-6 ${c.icon}`} />
                  </div>
                  <h3 className={`text-base font-bold mb-2 relative z-10 ${c.title}`}>{s.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed relative z-10">{s.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* ── CTA Banner ────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="w-full max-w-4xl mx-auto mt-20"
        >
          <div className="cta-gradient rounded-3xl p-12 text-center text-white relative overflow-hidden">
            <div className="absolute inset-0 pointer-events-none" style={{
              background: "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(255,255,255,0.10) 0%, transparent 60%)"
            }} />
            <div className="absolute -bottom-8 -right-8 w-40 h-40 rounded-full bg-white/5" />
            <div className="absolute -top-6 -left-6 w-32 h-32 rounded-full bg-white/5" />
            <div className="relative z-10">
              <div className="w-14 h-14 rounded-2xl bg-white/20 border border-white/30 flex items-center justify-center mx-auto mb-5">
                <Stethoscope className="w-7 h-7 text-white" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-black mb-3">
                Ready to Synthesize Evidence?
              </h2>
              <p className="text-indigo-100 text-base mb-8 max-w-xl mx-auto leading-relaxed">
                Join researchers who use our AI to cut literature review time by 10×.
                Free to use. No sign-up required.
              </p>
              <button
                onClick={() => navigate("/search")}
                className="inline-flex items-center gap-2.5 bg-white text-indigo-700 font-bold px-8 py-4 rounded-2xl text-base shadow-xl hover:shadow-2xl transition-all hover:scale-105 hover:-translate-y-0.5"
              >
                Start Free Research
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>
      </main>

      <Footer />
    </motion.div>
  );
};

export default Index;
