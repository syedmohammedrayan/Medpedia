import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const STEPS = [
  "Querying PubMed Central archive…",
  "Retrieving full-text clinical trials…",
  "Extracting statistical endpoints & effect sizes…",
  "Grading study certainty according to GRADE…",
  "Synthesizing comparative evidence findings…",
  "Compiling audit-ready clinical matrix…",
  "Finalizing structured narrative synthesis…",
];

const ECG_PATH =
  "M0,16 L45,16 L50,3 L55,29 L60,8 L65,16 L175,16 L180,3 L185,29 L190,8 L195,16 L320,16";

const PremiumLoader = () => {
  const [stepIdx, setStepIdx] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t = setInterval(
      () => setStepIdx((i) => Math.min(i + 1, STEPS.length - 1)),
      2600,
    );
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.25 }}
      className="flex gap-3.5 py-2"
    >
      {/* ── Avatar Mark ── */}
      <div className="relative flex-shrink-0 mt-1">
        <div className="w-8 h-8 rounded-xl bg-[#3A0F34] border border-[#240720] flex items-center justify-center shadow-sm">
          <span className="w-2 h-2 rounded-full bg-[#EAAA00] animate-ping" />
        </div>
      </div>

      {/* ── Editorial Card ── */}
      <div className="editorial-card rounded-2xl rounded-tl-sm p-4 space-y-3 min-w-[320px] max-w-md border border-[#DDE3E8]">

        {/* Header row */}
        <div className="flex items-center justify-between border-b border-[#DDE3E8] pb-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#EAAA00]" />
            <span className="text-xs font-heading font-bold text-[#211B20] tracking-tight">
              Medpedia Agent Active
            </span>
          </div>
          <span className="text-[11px] font-mono text-[#6B5F69]">
            {mm}:{ss}
          </span>
        </div>

        {/* Current task */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-[#B8AEA3]">
            <span>PHASE {String(stepIdx + 1).padStart(2, "0")} / {String(STEPS.length).padStart(2, "0")}</span>
            <span className="text-[#3A0F34] font-semibold">SYNTHESIZING</span>
          </div>
          <p className="text-xs font-medium text-[#211B20] leading-snug">
            {STEPS[stepIdx]}
          </p>
        </div>

        {/* ECG pulse track in Marigold */}
        <div className="relative h-7 overflow-hidden rounded-lg bg-[#FAF8F5] border border-[#DDE3E8] flex items-center">
          <svg
            className="w-full h-full"
            viewBox="0 0 320 32"
            fill="none"
            preserveAspectRatio="none"
          >
            <path
              d={ECG_PATH}
              stroke="#DDE3E8"
              strokeWidth="1.5"
              fill="none"
            />
            <motion.path
              d={ECG_PATH}
              stroke="#EAAA00"
              strokeWidth="2"
              fill="none"
              strokeDasharray="60 260"
              animate={{ strokeDashoffset: [-320, 0] }}
              transition={{ duration: 1.8, repeat: Infinity, ease: "linear" }}
            />
          </svg>
        </div>

      </div>
    </motion.div>
  );
};

export default PremiumLoader;
