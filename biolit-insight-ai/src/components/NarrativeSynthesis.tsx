import { motion } from "framer-motion";
import { Download, Mail, CheckCircle2, AlertCircle, HelpCircle } from "lucide-react";
import { useState } from "react";
import EmailModal from "./EmailModal";

interface NarrativeSynthesisProps {
  data: {
    synthesis: string;
    conclusion: "positive" | "negative" | "neutral";
  };
}

const conclusionConfig = {
  positive: {
    icon: CheckCircle2,
    label: "Supportive Evidence",
    desc: "Evidence supports clinical efficacy with an acceptable safety profile.",
    border: "border-l-emerald-500",
    bg: "bg-emerald-50",
    badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
    iconClass: "text-emerald-600",
  },
  negative: {
    icon: AlertCircle,
    label: "Non-Supportive Evidence",
    desc: "Current evidence does not support widespread clinical adoption.",
    border: "border-l-red-500",
    bg: "bg-red-50",
    badge: "bg-red-50 text-red-700 border-red-200",
    iconClass: "text-red-500",
  },
  neutral: {
    icon: HelpCircle,
    label: "Inconclusive Findings",
    desc: "Mixed findings — further research is needed to establish clinical utility.",
    border: "border-l-slate-400",
    bg: "bg-slate-50",
    badge: "bg-slate-100 text-slate-600 border-slate-200",
    iconClass: "text-slate-500",
  },
};

const NarrativeSynthesis = ({ data }: NarrativeSynthesisProps) => {
  const [showEmailModal, setShowEmailModal] = useState(false);
  const cfg = conclusionConfig[data.conclusion];
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase">
          Narrative Synthesis
        </p>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-[11px] text-slate-500 hover:text-slate-700 hover:border-slate-300 hover:bg-slate-50 transition-all">
            <Download className="w-3 h-3" />
            PDF
          </button>
          <button
            onClick={() => setShowEmailModal(true)}
            className="btn-primary flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px]"
          >
            <Mail className="w-3 h-3" />
            Email Report
          </button>
        </div>
      </div>

      {/* Synthesis body */}
      <div className="bg-white border border-slate-200 rounded-xl px-5 py-5 space-y-3 shadow-sm">
        {data.synthesis.split("\n\n").map((paragraph, idx) => {
          if (paragraph.startsWith("## ")) {
            return (
              <h2 key={idx} className="text-base font-bold text-slate-800 mt-5 mb-2 pb-2 border-b border-slate-200 tracking-tight">
                {paragraph.replace(/^#+\s*/, "")}
              </h2>
            );
          }
          if (paragraph.startsWith("### ")) {
            return (
              <h3 key={idx} className="text-sm font-semibold text-slate-700 mt-3 mb-1">
                {paragraph.replace(/^#+\s*/, "")}
              </h3>
            );
          }
          if (paragraph.startsWith("-")) {
            return (
              <ul key={idx} className="space-y-1.5 my-1">
                {paragraph.split("\n").filter((l) => l.trim()).map((item, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-600">
                    <span className="mt-2 w-1 h-1 rounded-full bg-indigo-400 flex-shrink-0" />
                    {item.replace(/^-\s*/, "")}
                  </li>
                ))}
              </ul>
            );
          }
          return (
            <p key={idx} className="text-sm text-slate-600 leading-relaxed">
              {paragraph}
            </p>
          );
        })}

        {/* Verdict */}
        <div className={`border-l-4 ${cfg.border} ${cfg.bg} rounded-r-lg pl-4 py-3 flex items-start gap-3 mt-4`}>
          <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${cfg.iconClass}`} />
          <div>
            <p className="text-xs font-bold tracking-widest text-slate-700 uppercase mb-0.5">{cfg.label}</p>
            <p className="text-xs text-slate-500">{cfg.desc}</p>
          </div>
          <span className={`ml-auto flex-shrink-0 text-[10px] font-bold px-2 py-0.5 rounded border ${cfg.badge}`}>
            {data.conclusion.charAt(0).toUpperCase() + data.conclusion.slice(1)}
          </span>
        </div>
      </div>

      <EmailModal open={showEmailModal} onOpenChange={setShowEmailModal} />
    </motion.div>
  );
};

export default NarrativeSynthesis;
