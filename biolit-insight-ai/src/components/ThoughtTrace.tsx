import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2, Terminal, Clock } from "lucide-react";

export interface TraceEntry {
  id: string;
  time: string;
  label: string;
  detail?: string;
  status: "running" | "done";
  stepNumber: number;
}

interface ThoughtTraceProps {
  traces: TraceEntry[];
  isLoading: boolean;
  sessionId: string | null;
}

const ThoughtTrace = ({ traces, isLoading, sessionId }: ThoughtTraceProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [traces]);

  const doneCount = traces.filter((t) => t.status === "done").length;

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ background: "rgba(6,10,22,0.8)" }}>

      {/* Header */}
      <div className="px-4 py-3 border-b border-white/[0.06] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest">
            Thought Trace
          </span>
        </div>
        {traces.length > 0 && (
          <span className="text-[10px] font-mono text-slate-600">
            {doneCount}/{traces.length}
          </span>
        )}
      </div>

      {/* Session ID */}
      {sessionId && (
        <div className="px-4 py-2 border-b border-white/[0.04] shrink-0">
          <span className="text-[10px] font-mono text-slate-600">
            session:{" "}
            <span className="text-indigo-400">{sessionId.slice(-12)}</span>
          </span>
        </div>
      )}

      {/* Trace entries */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 space-y-1 font-mono"
      >
        <AnimatePresence initial={false}>
          {traces.length === 0 && !isLoading ? (
            <div className="flex flex-col items-center justify-center h-32 gap-2">
              <Clock className="w-5 h-5 text-slate-700" />
              <p className="text-[11px] text-slate-600 font-mono">Awaiting session…</p>
            </div>
          ) : (
            traces.map((entry) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
                className={`group rounded-md px-2.5 py-2 border transition-colors ${
                  entry.status === "running"
                    ? "bg-indigo-500/10 border-indigo-500/20"
                    : "bg-white/[0.03] border-white/[0.06]"
                }`}
              >
                {/* Top row: time + status icon */}
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-slate-600">{entry.time}</span>
                  {entry.status === "done" ? (
                    <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                  ) : (
                    <Loader2 className="w-3 h-3 text-indigo-400 animate-spin shrink-0" />
                  )}
                </div>

                {/* Step label */}
                <p className={`text-[11px] leading-snug ${
                  entry.status === "running"
                    ? "text-indigo-300 font-semibold"
                    : "text-slate-500"
                }`}>
                  <span className="text-slate-700 mr-1.5 select-none">
                    {String(entry.stepNumber).padStart(2, "0")}
                  </span>
                  {entry.label}
                </p>

                {/* Optional detail */}
                {entry.detail && (
                  <p className="text-[10px] text-slate-600 mt-0.5 pl-5">
                    → {entry.detail}
                  </p>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {/* Live cursor when streaming */}
        {isLoading && traces.length > 0 && (
          <div className="flex items-center gap-1.5 px-2.5 py-1.5">
            <span className="text-[10px] font-mono text-slate-600">›</span>
            <motion.span
              className="inline-block w-1.5 h-3.5 bg-indigo-400 rounded-sm"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.9, repeat: Infinity }}
            />
          </div>
        )}
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2.5 border-t border-white/[0.06] shrink-0">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono text-slate-600">
            {isLoading ? (
              <span className="text-indigo-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse inline-block" />
                processing
              </span>
            ) : traces.length > 0 ? (
              <span className="text-emerald-500">complete</span>
            ) : (
              "idle"
            )}
          </span>
          {traces.length > 0 && (
            <span className="text-[10px] font-mono text-slate-600">
              {doneCount} done
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ThoughtTrace;
