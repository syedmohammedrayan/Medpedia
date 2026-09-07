import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, Database, BrainCircuit, FileBarChart2, CheckCircle2 } from "lucide-react";

const steps = [
  {
    icon: Search,
    label: "Searching PubMed",
    doneDetail: "47 publications found",
    iconBg: "bg-indigo-100", iconColor: "text-indigo-600",
    bar: "bg-indigo-500", check: "text-indigo-500",
  },
  {
    icon: Database,
    label: "Extracting Evidence",
    doneDetail: "3 RCTs · 4 meta-analyses · 2 reviews",
    iconBg: "bg-violet-100", iconColor: "text-violet-600",
    bar: "bg-violet-500", check: "text-violet-500",
  },
  {
    icon: BrainCircuit,
    label: "Grading Quality",
    doneDetail: "GRADE A/B evidence confirmed",
    iconBg: "bg-sky-100", iconColor: "text-sky-600",
    bar: "bg-sky-500", check: "text-sky-500",
  },
  {
    icon: FileBarChart2,
    label: "Synthesizing Report",
    doneDetail: "Evidence matrix complete",
    iconBg: "bg-emerald-100", iconColor: "text-emerald-600",
    bar: "bg-emerald-500", check: "text-emerald-500",
  },
];

const streamLines = [
  "Querying: semaglutide efficacy type 2 diabetes meta-analysis...",
  "Found: Wilding et al. 2021 — STEP-1 trial, n=1,961 patients...",
  "Extracting: HbA1c reduction −1.8% (95% CI −2.0 to −1.6)...",
  "Grading: High-quality RCT evidence, low risk of bias...",
  "Synthesis: Strong evidence for glycaemic benefit. Preparing report...",
];

export default function AgenticHero() {
  const [phase, setPhase] = useState(0);
  const [streamIdx, setStreamIdx] = useState(0);

  useEffect(() => {
    const delay = phase >= steps.length ? 2200 : 1700;
    const t = setTimeout(() => setPhase(p => (p >= steps.length ? 0 : p + 1)), delay);
    return () => clearTimeout(t);
  }, [phase]);

  useEffect(() => {
    const t = setInterval(() => setStreamIdx(i => (i + 1) % streamLines.length), 2200);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-md overflow-hidden">

        {/* Title bar */}
        <div className="flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-slate-50 to-indigo-50/60 border-b border-slate-100">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-400" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-indigo-500" />
            </span>
            Medical Research Assistant · Agent running
          </div>
          {phase >= steps.length && (
            <motion.span
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-700 border border-emerald-200"
            >
              ✓ Complete
            </motion.span>
          )}
        </div>

        {/* Steps */}
        <div className="px-5 py-4 space-y-3.5">
          {steps.map((step, i) => {
            const isDone = phase > i;
            const isActive = phase === i;
            const isPending = phase < i;

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: isPending ? 0.30 : 1, x: 0 }}
                transition={{ delay: i * 0.08, duration: 0.3 }}
                className="flex items-center gap-3"
              >
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors ${isDone ? step.iconBg : isActive ? step.iconBg : "bg-slate-100"}`}>
                  {isDone
                    ? <CheckCircle2 className={`w-3.5 h-3.5 ${step.check}`} />
                    : <step.icon className={`w-3.5 h-3.5 ${isActive ? step.iconColor : "text-slate-300"}`} />
                  }
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-xs font-semibold ${isDone ? "text-slate-700" : isActive ? "text-slate-800" : "text-slate-300"}`}>
                      {step.label}
                    </span>
                    <span className={`text-[10px] font-medium truncate max-w-[180px] ${isDone ? "text-slate-400" : isActive ? "text-slate-400 animate-pulse" : "text-slate-200"}`}>
                      {isDone ? step.doneDetail : isActive ? "Processing…" : "—"}
                    </span>
                  </div>
                  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full ${step.bar} rounded-full`}
                      initial={{ width: "0%" }}
                      animate={{
                        width: isDone ? "100%" : isActive ? "60%" : "0%",
                      }}
                      transition={{ duration: isDone ? 0.3 : 1.5, ease: "easeOut" }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Live log */}
        <div className="px-5 py-2.5 border-t border-slate-100 bg-slate-50/60 min-h-[36px] flex items-center">
          <motion.p
            key={streamIdx}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="text-[11px] text-slate-400 font-mono truncate"
          >
            <span className="text-indigo-400 mr-1">›</span>
            {streamLines[streamIdx]}
          </motion.p>
        </div>
      </div>
    </div>
  );
}
