// The main research interface where the user submits clinical queries.
// Communicates with the FastAPI backend and processes real-time Server-Sent Events (SSE).
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

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const API_URL = `${API_BASE}/research/start`;

const exampleQueries = [
  "Immunotherapy trials for glioblastoma 2023–2024",
  "Compare SGLT2i vs GLP-1 efficacy in heart failure",
  "Safety profile of JAK inhibitors in rheumatoid arthritis",
];

const pipelineSteps = [
  { num: "01", icon: Database,      label: "PubMed Search",    desc: "35M+ citations",   tag: "RETRIEVAL" },
  { num: "02", icon: BrainCircuit,  label: "Extract Evidence", desc: "PICO endpoints",   tag: "PARSING" },
  { num: "03", icon: Shield,        label: "Grade Quality",    desc: "GRADE certainty",  tag: "CERTAINTY" },
  { num: "04", icon: FileBarChart2, label: "Synthesize",       desc: "Clinical matrix",  tag: "VERDICT" },
];

const queryMeta = [
  { icon: Microscope,  tagLabel: "Clinical Trial",    spec: "ONCOLOGY" },
  { icon: Scale,       tagLabel: "Comparative Study",  spec: "CARDIOLOGY" },
  { icon: ShieldCheck, tagLabel: "Safety Profile",    spec: "RHEUMATOLOGY" },
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
        url = `${API_BASE}/research/resume-email`;
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
    <div className="h-screen flex flex-col overflow-hidden editorial-paper text-[#211B20]">
      <Navbar />

      {/* ── Messages Container ─────────────────────────────── */}
      <main ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-24 sm:pt-28 pb-4 space-y-4">

          {/* ═══ EMPTY STATE: EDITORIAL MASTHEAD ══════════════ */}
          {messages.length === 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45 }}
              className="flex flex-col items-center text-center py-6 sm:py-10"
            >

              {/* Editorial Icon Mark with Crystal Highlight */}
              <div className="mb-6 relative">
                <div className="w-16 h-16 rounded-2xl bg-[#3A0F34] border border-[#240720] flex items-center justify-center shadow-lg shadow-[#3A0F34]/25 ring-1 ring-white/20">
                  <Microscope className="w-8 h-8 text-[#EAAA00]" />
                </div>
                <div className="absolute -bottom-2 -right-2 px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#DDE3E8] text-[9px] font-mono font-bold text-[#3A0F34] shadow-sm">
                  35M+
                </div>
              </div>

              {/* Title & Description */}
              <div className="max-w-xl mx-auto space-y-2 mb-8">
                <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#B8AEA3] font-semibold">
                  CLINICAL SYNTHESIS WORKSPACE
                </span>
                <h1 className="text-3xl sm:text-5xl text-[#211B20] font-editorial italic font-normal tracking-[-0.028em] leading-tight">
                  Inquire.{" "}
                  <span className="section-gradient-gloss">
                    The Evidence Follows.
                  </span>
                </h1>
                <p className="text-xs sm:text-sm text-[#6B5F69] leading-relaxed max-w-md mx-auto">
                  Type any clinical or pharmacological inquiry. The agent queries MEDLINE and PMC, applies GRADE criteria, and produces an exportable matrix.
                </p>
              </div>

              {/* Pipeline Protocol Badges */}
              <div className="w-full max-w-2xl mb-8">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  {pipelineSteps.map((step, i) => (
                    <div
                      key={i}
                      className="card-ice-silver rounded-xl p-3 text-center"
                    >
                      <div className="text-[10px] font-mono text-[#EAAA00] font-bold mb-1">
                        {step.num} · {step.tag}
                      </div>
                      <p className="text-xs font-bold text-[#211B20] font-heading">{step.label}</p>
                      <p className="text-[10px] text-[#5A4E58] mt-0.5">{step.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Suggested Questions */}
              <div className="w-full max-w-2xl text-left">
                <div className="flex items-center justify-between mb-3 border-b border-[#DDE3E8] pb-1.5">
                  <span className="text-[10px] font-mono font-bold tracking-widest text-[#B8AEA3] uppercase">
                    SUGGESTED CLINICAL INQUIRIES
                  </span>
                  <span className="text-[10px] font-mono text-[#B8AEA3]">
                    SELECT TO EXECUTE
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {exampleQueries.map((q, i) => {
                    const meta = queryMeta[i];
                    return (
                      <button
                        key={i}
                        onClick={() => handleExampleClick(q)}
                        className="card-ice-silver rounded-xl p-3.5 text-left group flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-[#FAF8F5]/90 text-[#3A0F34] border border-[rgba(58,15,52,0.16)] font-semibold uppercase">
                              {meta.tagLabel}
                            </span>
                            <ChevronRight className="w-3.5 h-3.5 text-[#3A0F34]/60 group-hover:text-[#EAAA00] group-hover:translate-x-0.5 transition-all" />
                          </div>
                          <p className="text-xs font-medium text-[#211B20] leading-snug line-clamp-3">
                            {q}
                          </p>
                        </div>
                        <span className="text-[9px] font-mono text-[#5A4E58] mt-3 uppercase tracking-wider font-semibold">
                          {meta.spec}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

            </motion.div>
          )}

          {/* Messages Stream */}
          <AnimatePresence mode="popLayout">
            {messages.map((m) => <ChatMessage key={m.id} message={m} />)}
          </AnimatePresence>
          {isLoading && <PremiumLoader />}
        </div>
      </main>

      {/* ── Editorial Command Input with Crystal Finish ────── */}
      <div className="flex-shrink-0 bg-[#FAF8F5]/90 backdrop-blur-md border-t border-[#DDE3E8] py-3.5 px-4 sm:px-6 shadow-[0_-4px_20px_rgba(58,15,52,0.03)]">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex gap-2.5 items-center">
            <div className="flex-1 crystal-input rounded-xl flex items-center px-4 gap-2.5 bg-white">
              <span className="text-[#EAAA00] font-mono text-base font-bold select-none">›</span>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  waitingForEmailRef.current
                    ? "Enter recipient email address for delivery…"
                    : "Formulate a clinical research question…"
                }
                className="flex-1 h-12 bg-transparent text-[#211B20] placeholder:text-[#B8AEA3] text-sm outline-none font-sans"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="crystal-button h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0"
              title="Submit Inquiry"
            >
              <Send className="w-4 h-4 text-[#FAF8F5]" />
            </button>
          </form>
          <div className="flex items-center justify-between text-[11px] font-mono text-[#B8AEA3] mt-2 px-1">
            <span>MEDLINE & PMC REPOSITORIES</span>
            <span>AI-GENERATED SYNTHESIS · VERIFY AGAINST PRIMARY CITATIONS</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Search;
