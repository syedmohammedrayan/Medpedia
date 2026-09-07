import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const STEPS = [
  { label: "Querying PubMed database",       color: "from-indigo-500 to-indigo-400" },
  { label: "Retrieving full-text articles",  color: "from-indigo-500 to-violet-500" },
  { label: "Extracting clinical evidence",   color: "from-violet-500 to-violet-400" },
  { label: "Grading study quality (GRADE)",  color: "from-violet-500 to-purple-500" },
  { label: "Synthesizing findings",          color: "from-purple-500 to-indigo-500" },
  { label: "Building evidence matrix",       color: "from-indigo-500 to-violet-500" },
  { label: "Preparing your report",          color: "from-violet-500 to-indigo-400" },
];

/* Seamlessly tiling ECG path — starts and ends at y=16 so two copies join invisibly */
const ECG_PATH =
  "M0,16 L45,16 L50,3 L55,29 L60,8 L65,16 L175,16 L180,3 L185,29 L190,8 L195,16 L320,16";

const PremiumLoader = () => {
  const [stepIdx, setStepIdx] = useState(0);
  const [elapsed,  setElapsed]  = useState(0);

  useEffect(() => {
    const t = setInterval(
      () => setStepIdx((i) => Math.min(i + 1, STEPS.length - 1)),
      2800,
    );
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");
  const step = STEPS[stepIdx];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.28 }}
      className="flex gap-3 py-2"
    >
      {/* ── Avatar ──────────────────────────────────────────── */}
      <div className="relative flex-shrink-0 mt-0.5">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center shadow-md"
          style={{
            background: "linear-gradient(145deg,#6366f1,#7c3aed,#6d28d9)",
            boxShadow: "0 2px 8px rgba(99,102,241,0.45)",
          }}
        >
          {/* Logo mark inline */}
          <svg viewBox="0 0 32 32" fill="none" style={{ width: 18, height: 18 }}>
            <defs>
              <clipPath id="loader-lens">
                <circle cx="12.5" cy="12.5" r="8.8" />
              </clipPath>
            </defs>
            <circle cx="12.5" cy="12.5" r="9.2" fill="rgba(255,255,255,0.11)" />
            <circle cx="12.5" cy="12.5" r="9.2" stroke="white" strokeWidth="2.3" />
            <g clipPath="url(#loader-lens)">
              <polyline
                points="2,12.5 7,12.5 8.3,6 10.3,19 11.8,9 13,12.5 23,12.5"
                stroke="white" strokeWidth="2" strokeLinecap="round"
                strokeLinejoin="round" fill="none"
              />
            </g>
            <line x1="19.5" y1="19.5" x2="28" y2="28"
              stroke="white" strokeWidth="3.2" strokeLinecap="round" />
            <circle cx="8.3" cy="6" r="1.5" fill="white" opacity="0.75" />
          </svg>
        </div>

        {/* Pulsing active indicator */}
        <motion.span
          animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-amber-400 border-2 border-white"
        />
      </div>

      {/* ── Main card ───────────────────────────────────────── */}
      <div className="bubble-agent rounded-xl rounded-tl-sm px-4 py-3.5 space-y-3" style={{ minWidth: 292 }}>

        {/* Header row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <motion.span
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
              className="w-1.5 h-1.5 rounded-full bg-indigo-500"
            />
            <span className="text-xs font-bold text-slate-800 tracking-tight">
              Research Assistant
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400 tabular-nums tracking-wide">
            {mm}:{ss}
          </span>
        </div>

        {/* ── Live ECG line ──────────────────────────────────── */}
        <div
          className="relative h-9 overflow-hidden rounded-lg border border-indigo-100/70"
          style={{ background: "linear-gradient(to bottom, #eef2ff 0%, #f8f9ff 100%)" }}
        >
          {/* Scrolling ECG — two seamless copies */}
          <motion.div
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 3.2, repeat: Infinity, ease: "linear" }}
            className="absolute inset-y-0 flex items-center"
            style={{ width: "200%" }}
          >
            {[0, 1].map((k) => (
              <svg
                key={k}
                viewBox="0 0 320 32"
                style={{ width: 320, height: 32, flexShrink: 0 }}
                fill="none"
                preserveAspectRatio="none"
              >
                <defs>
                  <linearGradient id={`ecg-grad-${k}`} x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
                    <stop offset="0%"   stopColor="#6366f1" stopOpacity="0.15" />
                    <stop offset="25%"  stopColor="#6366f1" stopOpacity="1" />
                    <stop offset="65%"  stopColor="#7c3aed" stopOpacity="1" />
                    <stop offset="100%" stopColor="#7c3aed" stopOpacity="0.2" />
                  </linearGradient>
                </defs>
                <path
                  d={ECG_PATH}
                  stroke={`url(#ecg-grad-${k})`}
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ))}
          </motion.div>

          {/* Left / right edge fade masks */}
          <div className="absolute inset-y-0 left-0 w-6 pointer-events-none"
            style={{ background: "linear-gradient(to right, #eef2ff, transparent)" }} />
          <div className="absolute inset-y-0 right-0 w-6 pointer-events-none"
            style={{ background: "linear-gradient(to left, #f8f9ff, transparent)" }} />

          {/* Live pulse dot */}
          <div className="absolute right-2.5 inset-y-0 flex items-center">
            <motion.div
              animate={{ scale: [1, 1.8, 1], opacity: [0.9, 0.3, 0.9] }}
              transition={{ duration: 0.9, repeat: Infinity, ease: "easeInOut" }}
              className="w-1.5 h-1.5 rounded-full bg-emerald-500"
            />
          </div>
        </div>

        {/* ── Current step ───────────────────────────────────── */}
        <div className="flex items-center gap-2.5">
          {/* Spinning ring indicator */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1.6, repeat: Infinity, ease: "linear" }}
            className="flex-shrink-0 w-3.5 h-3.5 rounded-full border-2 border-indigo-500 border-t-transparent"
          />

          <div className="overflow-hidden flex-1" style={{ height: 18 }}>
            <AnimatePresence mode="wait">
              <motion.span
                key={stepIdx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.22 }}
                className="block text-xs text-slate-600 font-semibold whitespace-nowrap"
              >
                {step.label}
              </motion.span>
            </AnimatePresence>
          </div>

          {/* Step counter */}
          <span className="text-[10px] font-bold text-slate-400 flex-shrink-0 tabular-nums">
            {stepIdx + 1}/{STEPS.length}
          </span>
        </div>

        {/* ── Segmented progress bar ─────────────────────────── */}
        <div className="flex gap-[3px]">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1 h-[3px] rounded-full bg-slate-200 overflow-hidden">
              <AnimatePresence>
                {i <= stepIdx && (
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{
                      duration: i === stepIdx ? 2.8 : 0.4,
                      ease: i === stepIdx ? "linear" : "easeOut",
                    }}
                    className={`h-full rounded-full bg-gradient-to-r ${s.color}`}
                  />
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>

      </div>
    </motion.div>
  );
};

export default PremiumLoader;
