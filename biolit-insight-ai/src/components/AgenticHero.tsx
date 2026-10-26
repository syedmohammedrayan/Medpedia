import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, Database, BrainCircuit, FileBarChart2, Check } from "lucide-react";

const steps = [
  {
    icon: Search,
    label: "Querying PubMed Archive",
    doneDetail: "47 peer-reviewed publications isolated",
    stepNum: "01",
  },
  {
    icon: Database,
    label: "Extracting Clinical Evidence",
    doneDetail: "3 RCTs · 4 meta-analyses · 2 systematic reviews",
    stepNum: "02",
  },
  {
    icon: BrainCircuit,
    label: "Grading Evidence Quality",
    doneDetail: "GRADE criteria applied — High certainty",
    stepNum: "03",
  },
  {
    icon: FileBarChart2,
    label: "Structuring Synthesis Matrix",
    doneDetail: "PICO matrix compiled & citable",
    stepNum: "04",
  },
];

const streamLines = [
  "query: semaglutide cardiovascular outcomes type-2 diabetes meta-analysis",
  "matched: STEP-1 trial (Wilding et al. NEJM 2021) — n=1,961 patients",
  "isolated: HbA1c delta −1.8% (95% CI −2.0 to −1.6), p < 0.001",
  "assessed: GRADE certainty Level A, low risk of bias detected",
  "synthesizing: structured evidence report compiled for clinical review",
];

export default function AgenticHero() {
  const [phase, setPhase] = useState(0);
  const [streamIdx, setStreamIdx] = useState(0);

  useEffect(() => {
    const delay = phase >= steps.length ? 2600 : 1900;
    const t = setTimeout(() => setPhase(p => (p >= steps.length ? 0 : p + 1)), delay);
    return () => clearTimeout(t);
  }, [phase]);

  useEffect(() => {
    const t = setInterval(() => setStreamIdx(i => (i + 1) % streamLines.length), 2400);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-[#FFFFFF] rounded-2xl border border-[#DDE3E8] shadow-sm overflow-hidden">

        {/* ── Editorial Header Bar ── */}
        <div className="flex items-center justify-between px-5 py-3.5 bg-[#FAF8F5] border-b border-[#DDE3E8]">
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#EAAA00] animate-pulse" />
            <span className="text-[11px] font-mono font-semibold tracking-wider text-[#211B20] uppercase">
              Pipeline Monitor
            </span>
            <span className="text-[11px] text-[#B8AEA3] font-serif italic hidden sm:inline">
              Autonomous reasoning trace
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-[#6B5F69]">
              SYS: <span className="text-[#3A0F34] font-bold">ONLINE</span>
            </span>
            {phase >= steps.length && (
              <motion.span
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-[#FDF6E4] text-[#C58E00] border border-[#EAAA00]"
              >
                COMPLETED
              </motion.span>
            )}
          </div>
        </div>

        {/* ── Steps List ── */}
        <div className="px-5 py-4 space-y-3.5">
          {steps.map((step, i) => {
            const isDone = phase > i;
            const isActive = phase === i;
            const isPending = phase < i;

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: isPending ? 0.35 : 1, x: 0 }}
                transition={{ delay: i * 0.08, duration: 0.3 }}
                className="flex items-center gap-3.5"
              >
                {/* Step indicator */}
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-all text-xs font-mono font-bold ${
                    isDone
                      ? "bg-[#3A0F34] text-[#EAAA00]"
                      : isActive
                      ? "border border-[#3A0F34] bg-[#FAF8F5] text-[#3A0F34]"
                      : "border border-[#DDE3E8] bg-[#FAF8F5] text-[#B8AEA3]"
                  }`}
                >
                  {isDone ? (
                    <Check className="w-3.5 h-3.5 text-[#EAAA00]" />
                  ) : (
                    <span>{step.stepNum}</span>
                  )}
                </div>

                {/* Progress & Label */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-xs font-heading font-medium tracking-tight ${
                      isDone ? "text-[#211B20]" : isActive ? "text-[#3A0F34] font-bold" : "text-[#B8AEA3]"
                    }`}>
                      {step.label}
                    </span>
                    <span className={`text-[10px] font-mono truncate max-w-[220px] ${
                      isDone ? "text-[#6B5F69]" : isActive ? "text-[#EAAA00] font-semibold animate-pulse" : "text-[#DDE3E8]"
                    }`}>
                      {isDone ? step.doneDetail : isActive ? "Evaluating records…" : "Queued"}
                    </span>
                  </div>

                  {/* Hairline progress bar */}
                  <div className="h-1 bg-[#EFF3F6] rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        isDone ? "bg-[#3A0F34]" : isActive ? "bg-[#EAAA00]" : "bg-transparent"
                      }`}
                      initial={{ width: "0%" }}
                      animate={{
                        width: isDone ? "100%" : isActive ? "65%" : "0%",
                      }}
                      transition={{ duration: isDone ? 0.35 : 1.4, ease: "easeOut" }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* ── Monospaced Terminal Output ── */}
        <div className="px-5 py-3 border-t border-[#DDE3E8] bg-[#FAF8F5] flex items-center gap-2">
          <span className="text-[#EAAA00] font-mono text-xs font-bold select-none">›</span>
          <motion.p
            key={streamIdx}
            initial={{ opacity: 0, y: 3 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="text-[11px] text-[#6B5F69] font-mono truncate flex-1"
          >
            {streamLines[streamIdx]}
          </motion.p>
          <span className="text-[10px] font-mono text-[#B8AEA3] hidden sm:inline">LIVE STREAM</span>
        </div>

      </div>
    </div>
  );
}
