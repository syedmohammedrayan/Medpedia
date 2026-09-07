import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "@/components/Navbar";
import ChatMessage from "@/components/ChatMessage";
import PremiumLoader from "@/components/PremiumLoader";
import {
  Send, Database, BrainCircuit,
  FileBarChart2, Shield, ChevronRight, Microscope, Scale, ShieldCheck,
} from "lucide-react";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
  data?: any;
}

const API_URL = "http://localhost:8000/research/start";

const exampleQueries = [
  "Immunotherapy trials for glioblastoma 2023–2024",
  "Compare SGLT2i vs GLP-1 efficacy in heart failure",
  "Safety profile of JAK inhibitors in rheumatoid arthritis",
];

const pipelineSteps = [
  { num: "01", icon: Database,      label: "PubMed Search",    desc: "35M+ articles",     cardClass: "border-indigo-100 hover:border-indigo-300 hover:shadow-indigo-100",  iconBg: "bg-indigo-50",  iconColor: "text-indigo-600",  numColor: "text-indigo-400" },
  { num: "02", icon: BrainCircuit,  label: "Extract Evidence", desc: "Full-text analysis", cardClass: "border-violet-100 hover:border-violet-300 hover:shadow-violet-100",   iconBg: "bg-violet-50",  iconColor: "text-violet-600",  numColor: "text-violet-400" },
  { num: "03", icon: Shield,        label: "Grade Quality",    desc: "GRADE standards",    cardClass: "border-cyan-100 hover:border-cyan-300 hover:shadow-cyan-100",         iconBg: "bg-cyan-50",    iconColor: "text-cyan-600",    numColor: "text-cyan-400"   },
  { num: "04", icon: FileBarChart2, label: "Synthesize",       desc: "Structured report",  cardClass: "border-emerald-100 hover:border-emerald-300 hover:shadow-emerald-100", iconBg: "bg-emerald-50", iconColor: "text-emerald-600", numColor: "text-emerald-400" },
];

const queryMeta = [
  { icon: Microscope,  iconBg: "bg-indigo-50",  iconBorder: "border-indigo-200", iconColor: "text-indigo-600",  tagClass: "bg-indigo-50 text-indigo-600 border border-indigo-200",   tagLabel: "Clinical Trial",   hoverCard: "hover:border-indigo-300 hover:shadow-indigo-100/60" },
  { icon: Scale,       iconBg: "bg-violet-50",  iconBorder: "border-violet-200", iconColor: "text-violet-600",  tagClass: "bg-violet-50 text-violet-600 border border-violet-200",   tagLabel: "Drug Comparison",  hoverCard: "hover:border-violet-300 hover:shadow-violet-100/60" },
  { icon: ShieldCheck, iconBg: "bg-emerald-50", iconBorder: "border-emerald-200",iconColor: "text-emerald-600", tagClass: "bg-emerald-50 text-emerald-600 border border-emerald-200", tagLabel: "Safety Profile",   hoverCard: "hover:border-emerald-300 hover:shadow-emerald-100/60" },
];

const Search = () => {
  const location = useLocation();
  const initialQuery = location.state?.query || "";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sessionRef = useRef<string | null>(null);
  const waitingForEmailRef = useRef(false);
  const processedInitialQuery = useRef(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (initialQuery && !processedInitialQuery.current) {
      setMessages([{ id: Date.now().toString(), type: "user", content: initialQuery, timestamp: new Date() }]);
      processedInitialQuery.current = true;
      sendMessage(initialQuery);
    }
  }, [initialQuery]);

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, isLoading]);

  const sendMessage = async (text: string) => {
    setIsLoading(true);
    if (!sessionRef.current) sessionRef.current = `thread-${Date.now()}`;
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      let url = API_URL;
      let body: any = { query: text, thread_id: sessionRef.current };
      if (waitingForEmailRef.current) {
        url = "http://localhost:8000/research/resume-email";
        body = { email: text, thread_id: sessionRef.current };
        waitingForEmailRef.current = false;
      }
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        while (true) {
          const match = buffer.match(/\r?\n\r?\n/);
          if (!match) break;
          const chunk = buffer.slice(0, match.index!).trim();
          buffer = buffer.slice(match.index! + match[0].length);
          if (!chunk.startsWith("data:")) continue;
          const dataStr = chunk.replace(/^data:\s*/, "");
          if (dataStr === "[DONE]") { setIsLoading(false); break; }
          try { handleServerMessage(JSON.parse(dataStr)); }
          catch (e) { console.error("SSE parse error", e); }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setIsLoading(false);
        setMessages((p) => [...p, {
          id: Date.now().toString(), type: "agent",
          content: `Error: ${err.message || "Failed to connect to the research server."}`,
          timestamp: new Date(),
        }]);
      }
    } finally { setIsLoading(false); }
  };

  const handleServerMessage = (data: any) => {
    if (data.type === "token") {
      setMessages((p) => {
        const last = p[p.length - 1];
        if (last?.type === "agent")
          return [...p.slice(0, -1), { ...last, content: last.content + data.content }];
        return [...p, { id: Date.now().toString(), type: "agent", content: data.content, timestamp: new Date() }];
      });
    } else if (data.type === "node_start" || data.type === "node_end") {
      setMessages((p) => {
        const last = p[p.length - 1];
        if (last?.type === "agent" && last.content && !last.content.endsWith("\n\n"))
          return [...p.slice(0, -1), { ...last, content: last.content + "\n\n" }];
        return p;
      });
    } else if (data.type === "interrupt") {
      waitingForEmailRef.current = true;
      setMessages((p) => [...p, {
        id: Date.now().toString(), type: "agent",
        content: `To deliver your report by email, please provide your address: ${data.query}`,
        timestamp: new Date(),
      }]);
    } else if (data.type === "error") {
      setIsLoading(false);
      setMessages((p) => [...p, {
        id: Date.now().toString(), type: "agent",
        content: `Error: ${data.content}`,
        timestamp: new Date(),
      }]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    setMessages((p) => [...p, { id: Date.now().toString(), type: "user", content: input, timestamp: new Date() }]);
    sendMessage(input);
    setInput("");
  };

  const handleExampleClick = (q: string) => {
    if (isLoading) return;
    setMessages([{ id: Date.now().toString(), type: "user", content: q, timestamp: new Date() }]);
    sendMessage(q);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="h-screen flex flex-col overflow-hidden agent-workspace"
    >
      <Navbar />

      {/* ── Messages ──────────────────────────────────────── */}
      <main ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 pt-24 pb-3 space-y-2">

          {/* ═══ EMPTY STATE ══════════════════════════════ */}
          {messages.length === 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
              className="flex flex-col items-center text-center"
              style={{
                backgroundImage: "radial-gradient(circle, rgba(99,102,241,0.055) 1px, transparent 1px)",
                backgroundSize: "28px 28px",
                borderRadius: "24px",
                padding: "18px 16px 14px",
              }}
            >

              {/* ── Agent Avatar ── */}
              <div className="relative mb-3">
                <div className="absolute inset-0 scale-[2.2] rounded-full bg-gradient-to-br from-indigo-300 to-violet-500 blur-3xl opacity-20" />

                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 22, repeat: Infinity, ease: "linear" }}
                  className="absolute -inset-3 rounded-[36px] border-2 border-dashed border-indigo-200/50"
                />

                <motion.div
                  animate={{ scale: [1, 1.5], opacity: [0.3, 0] }}
                  transition={{ duration: 2.8, repeat: Infinity, ease: "easeOut" }}
                  className="absolute inset-0 rounded-3xl bg-indigo-300/25"
                />

                {/* Orbiting dots — tighter radius to stay compact */}
                {[
                  { delay: 0,   dur: 7,  r: 44, color: "bg-indigo-400",  size: "w-1.5 h-1.5" },
                  { delay: 1.5, dur: 9,  r: 48, color: "bg-violet-400",  size: "w-1 h-1" },
                  { delay: 3,   dur: 11, r: 46, color: "bg-cyan-400",    size: "w-1 h-1" },
                  { delay: 4.5, dur: 8,  r: 42, color: "bg-emerald-400", size: "w-1.5 h-1.5" },
                ].map((dot, i) => (
                  <motion.div
                    key={i}
                    animate={{ rotate: 360 }}
                    transition={{ duration: dot.dur, repeat: Infinity, ease: "linear", delay: dot.delay }}
                    className="absolute inset-0"
                    style={{ transformOrigin: "center" }}
                  >
                    <div
                      className={`absolute ${dot.size} rounded-full ${dot.color} opacity-80`}
                      style={{ top: `calc(50% - ${dot.r}px)`, left: "50%", transform: "translateX(-50%)" }}
                    />
                  </motion.div>
                ))}

                <motion.div
                  animate={{ scale: [1, 1.04, 1] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                  className="relative w-24 h-24 rounded-3xl flex items-center justify-center"
                  style={{
                    background: "linear-gradient(145deg, #6366f1 0%, #7c3aed 55%, #6d28d9 100%)",
                    boxShadow: "0 16px 48px rgba(99,102,241,0.45), 0 6px 16px rgba(124,58,237,0.30), inset 0 2px 0 rgba(255,255,255,0.20), inset 0 -2px 0 rgba(0,0,0,0.14)",
                  }}
                >
                  <svg viewBox="0 0 32 32" fill="none" style={{ width: 56, height: 56 }}>
                    <defs>
                      <clipPath id="avatar-lens-clip">
                        <circle cx="12.5" cy="12.5" r="8.8" />
                      </clipPath>
                    </defs>
                    <circle cx="12.5" cy="12.5" r="9.2" fill="rgba(255,255,255,0.11)" />
                    <circle cx="12.5" cy="12.5" r="9.2" stroke="white" strokeWidth="2.3" />
                    <g clipPath="url(#avatar-lens-clip)">
                      <polyline points="2,12.5  7,12.5  8.3,6  10.3,19  11.8,9  13,12.5  23,12.5"
                        stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    </g>
                    <circle cx="8" cy="7.5" r="2" fill="white" opacity="0.18" />
                    <line x1="19.5" y1="19.5" x2="28" y2="28" stroke="white" strokeWidth="3.2" strokeLinecap="round" />
                    <circle cx="8.3" cy="6" r="1.5" fill="white" opacity="0.7" />
                  </svg>
                </motion.div>

                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, type: "spring", stiffness: 300 }}
                  className="absolute -top-1.5 -right-1.5 w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 border-2 border-white flex items-center justify-center shadow-lg shadow-emerald-200"
                >
                  <span className="text-white text-[10px] font-black tracking-tight">AI</span>
                </motion.div>
              </div>

              {/* ── Headline ── */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="mb-3 space-y-1"
              >
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">
                  Ask.{" "}
                  <span className="text-gradient-vivid">The Agent Answers.</span>
                </h2>
                <p className="text-slate-500 max-w-md mx-auto text-xs leading-relaxed">
                  Enter a clinical question — your AI agent will search{" "}
                  <span className="font-semibold text-slate-700">35M+ PubMed articles</span>,
                  extract evidence, and deliver a structured synthesis in real time.
                </p>
              </motion.div>

              {/* ── Pipeline Steps ── */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.22 }}
                className="w-full max-w-xl mb-3"
              >
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {pipelineSteps.map((step, i) => (
                    <div key={i} className="relative">
                      <motion.div
                        whileHover={{ y: -2 }}
                        transition={{ type: "spring", stiffness: 300, damping: 20 }}
                        className={`bg-white border rounded-xl p-2.5 text-center shadow-sm hover:shadow-md transition-all cursor-default ${step.cardClass}`}
                      >
                        <div className={`w-8 h-8 ${step.iconBg} rounded-lg flex items-center justify-center mx-auto mb-1.5`}>
                          <step.icon className={step.iconColor} style={{ width: 16, height: 16 }} />
                        </div>
                        <div className={`text-[10px] font-black ${step.numColor} mb-0.5 tracking-wide`}>{step.num}</div>
                        <p className="text-[11px] font-bold text-slate-700 leading-tight">{step.label}</p>
                        <p className="text-[10px] text-slate-400">{step.desc}</p>
                      </motion.div>

                      {i < 3 && (
                        <div className="hidden sm:flex absolute -right-1.5 top-1/2 -translate-y-1/2 z-10">
                          <motion.div
                            animate={{ x: [0, 3, 0], opacity: [0.4, 1, 0.4] }}
                            transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.3, ease: "easeInOut" }}
                          >
                            <ChevronRight className="w-3 h-3 text-slate-300" />
                          </motion.div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* ── Example Query Cards — horizontal row ── */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="w-full max-w-2xl"
              >
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2 text-center">
                  Try these research questions
                </p>

                {/* Horizontal row — flex-col on mobile, flex-row on sm+ */}
                <div className="flex flex-col sm:flex-row gap-2">
                  {exampleQueries.map((q, i) => {
                    const meta = queryMeta[i];
                    return (
                      <motion.button
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.35 + i * 0.07 }}
                        whileHover={{ y: -2, scale: 1.02 }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => handleExampleClick(q)}
                        className={`group flex-1 text-left px-3 py-3 bg-white border border-slate-200 rounded-xl transition-all shadow-sm hover:shadow-md ${meta.hoverCard}`}
                      >
                        {/* Icon + tag row */}
                        <div className="flex items-center gap-2 mb-2">
                          <div className={`w-7 h-7 rounded-lg ${meta.iconBg} border ${meta.iconBorder} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                            <meta.icon className={`w-3 h-3 ${meta.iconColor}`} />
                          </div>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${meta.tagClass}`}>
                            {meta.tagLabel}
                          </span>
                          <ChevronRight className="w-3 h-3 text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all ml-auto flex-shrink-0" />
                        </div>
                        {/* Query text */}
                        <p className="text-[11px] font-semibold text-slate-700 leading-snug line-clamp-2 text-left">
                          {q}
                        </p>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>

            </motion.div>
          )}

          {/* Messages */}
          <AnimatePresence mode="popLayout">
            {messages.map((m) => <ChatMessage key={m.id} message={m} />)}
          </AnimatePresence>
          {isLoading && <PremiumLoader />}
        </div>
      </main>

      {/* ── Command Input ──────────────────────────────────── */}
      <div className="flex-shrink-0 bg-white/90 backdrop-blur-md border-t border-slate-200/70 py-4 px-6">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="flex gap-2.5 items-center">
            <div className="flex-1 search-wrap rounded-xl flex items-center px-4 gap-2">
              <span className="text-indigo-400 font-mono text-base font-bold flex-shrink-0 select-none">›</span>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  waitingForEmailRef.current
                    ? "Enter your email address…"
                    : "Ask a clinical research question…"
                }
                className="flex-1 h-11 bg-transparent text-slate-800 placeholder:text-slate-400 text-sm outline-none"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="btn-primary h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <p className="text-[11px] text-slate-400 text-center mt-2">
            AI-generated synthesis · Always verify findings against source publications
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default Search;
