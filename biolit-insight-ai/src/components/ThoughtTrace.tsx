// Renders the progress UI showing which LangGraph node (agent step) is currently active.
// Reacts to node_start and node_end events streaming from the backend.
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
    <div className="flex flex-col h-full overflow-hidden bg-[#FAF8F5] border border-[#DDE3E8] rounded-2xl">

      {/* Header */}
      <div className="px-4 py-3 border-b border-[#DDE3E8] flex items-center justify-between shrink-0 bg-white">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-[#3A0F34]" />
          <span className="text-[10px] font-mono font-bold text-[#3A0F34] uppercase tracking-widest">
            Reasoning Trace
          </span>
        </div>
        {traces.length > 0 && (
          <span className="text-[10px] font-mono text-[#6B5F69]">
            {doneCount}/{traces.length} steps
          </span>
        )}
      </div>

      {/* Session ID */}
      {sessionId && (
        <div className="px-4 py-2 border-b border-[#DDE3E8] shrink-0 bg-[#FAF8F5]">
          <span className="text-[10px] font-mono text-[#B8AEA3]">
            THREAD:{" "}
            <span className="text-[#3A0F34] font-semibold">{sessionId.slice(-12)}</span>
          </span>
        </div>
      )}

      {/* Trace entries */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 space-y-1.5 font-mono"
      >
        <AnimatePresence initial={false}>
          {traces.length === 0 && !isLoading ? (
            <div className="flex flex-col items-center justify-center h-32 gap-2 text-center">
              <Clock className="w-5 h-5 text-[#B8AEA3]" />
              <p className="text-[11px] text-[#6B5F69] font-mono">Awaiting execution thread…</p>
            </div>
          ) : (
            traces.map((entry) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
                className={`group rounded-lg px-3 py-2 border transition-colors ${
                  entry.status === "running"
                    ? "bg-[#FDF6E4] border-[#EAAA00]"
                    : "bg-white border-[#DDE3E8]"
                }`}
              >
                {/* Top row: time + status icon */}
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[10px] text-[#B8AEA3]">{entry.time}</span>
                  {entry.status === "done" ? (
                    <Check className="w-3 h-3 text-[#3A0F34] shrink-0" />
                  ) : (
                    <Loader2 className="w-3 h-3 text-[#EAAA00] animate-spin shrink-0" />
                  )}
                </div>

                {/* Step label */}
                <p className={`text-[11px] leading-snug ${
                  entry.status === "running"
                    ? "text-[#3A0F34] font-semibold"
                    : "text-[#211B20]"
                }`}>
                  <span className="text-[#B8AEA3] mr-1.5 select-none font-bold">
                    {String(entry.stepNumber).padStart(2, "0")}
                  </span>
                  {entry.label}
                </p>

                {/* Optional detail */}
                {entry.detail && (
                  <p className="text-[10px] text-[#6B5F69] mt-0.5 pl-5">
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
            <span className="text-[10px] font-mono text-[#EAAA00]">›</span>
            <motion.span
              className="inline-block w-1.5 h-3.5 bg-[#EAAA00] rounded-sm"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.9, repeat: Infinity }}
            />
          </div>
        )}
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2.5 border-t border-[#DDE3E8] shrink-0 bg-white">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono text-[#6B5F69]">
            {isLoading ? (
              <span className="text-[#3A0F34] flex items-center gap-1.5 font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-[#EAAA00] animate-pulse inline-block" />
                PROCESSING
              </span>
            ) : traces.length > 0 ? (
              <span className="text-[#3A0F34] font-bold">COMPLETED</span>
            ) : (
              "IDLE"
            )}
          </span>
          {traces.length > 0 && (
            <span className="text-[10px] font-mono text-[#6B5F69]">
              {doneCount} finished
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ThoughtTrace;
