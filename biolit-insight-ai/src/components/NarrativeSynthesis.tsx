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
    desc: "Controlled clinical trials demonstrate significant therapeutic efficacy with a manageable adverse event profile.",
    border: "border-l-[#EAAA00]",
    bg: "bg-[#FDF6E4]",
    badge: "bg-[#3A0F34] text-[#FAF8F5] border-[#240720]",
    iconClass: "text-[#EAAA00]",
  },
  negative: {
    icon: AlertCircle,
    label: "Non-Supportive Evidence",
    desc: "Aggregated trials do not corroborate superior clinical efficacy or reveal critical safety endpoints.",
    border: "border-l-rose-500",
    bg: "bg-rose-50/60",
    badge: "bg-rose-100 text-rose-800 border-rose-300",
    iconClass: "text-rose-600",
  },
  neutral: {
    icon: HelpCircle,
    label: "Inconclusive Findings",
    desc: "Mixed or contradictory findings across trials — supplementary high-powered RCTs recommended.",
    border: "border-l-[#B8AEA3]",
    bg: "bg-[#FAF8F5]",
    badge: "bg-[#EFF3F6] text-[#211B20] border-[#DDE3E8]",
    iconClass: "text-[#6B5F69]",
  },
};

const NarrativeSynthesis = ({ data }: NarrativeSynthesisProps) => {
  const [showEmailModal, setShowEmailModal] = useState(false);
  const cfg = conclusionConfig[data.conclusion] || conclusionConfig.neutral;
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Header Bar */}
      <div className="flex items-center justify-between gap-4 border-b border-[#DDE3E8] pb-2">
        <div className="flex items-center gap-2">
          <p className="text-[11px] font-mono font-bold tracking-widest text-[#211B20] uppercase">
            Systematic Narrative Synthesis
          </p>
          <span className="text-[10px] font-mono text-[#B8AEA3]">
            GRADE EVALUATED
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button className="btn-editorial-secondary flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-heading font-medium">
            <Download className="w-3.5 h-3.5 text-[#B8AEA3]" />
            <span>PDF</span>
          </button>
          <button
            onClick={() => setShowEmailModal(true)}
            className="btn-editorial-primary flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-heading font-semibold"
          >
            <Mail className="w-3.5 h-3.5 text-[#EAAA00]" />
            <span>Email Report</span>
          </button>
        </div>
      </div>

      {/* Synthesis Content Card */}
      <div className="editorial-card rounded-2xl p-6 sm:p-7 space-y-4 bg-white border border-[#DDE3E8]">
        {data.synthesis.split("\n\n").map((paragraph, idx) => {
          if (paragraph.startsWith("## ")) {
            return (
              <h2 key={idx} className="text-base sm:text-lg font-bold text-[#211B20] font-heading mt-6 mb-2 pb-2 border-b border-[#DDE3E8] tracking-tight">
                {paragraph.replace(/^#+\s*/, "")}
              </h2>
            );
          }
          if (paragraph.startsWith("### ")) {
            return (
              <h3 key={idx} className="text-sm font-bold text-[#3A0F34] font-heading mt-4 mb-1">
                {paragraph.replace(/^#+\s*/, "")}
              </h3>
            );
          }
          if (paragraph.startsWith("-")) {
            return (
              <ul key={idx} className="space-y-2 my-2">
                {paragraph.split("\n").filter((l) => l.trim()).map((item, i) => (
                  <li key={i} className="flex gap-2.5 text-xs sm:text-sm text-[#3B333A] leading-relaxed">
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-[#EAAA00] flex-shrink-0" />
                    <span>{item.replace(/^-\s*/, "")}</span>
                  </li>
                ))}
              </ul>
            );
          }
          return (
            <p key={idx} className="text-xs sm:text-sm text-[#3B333A] leading-relaxed">
              {paragraph}
            </p>
          );
        })}

        {/* Clinical Verdict Panel */}
        <div className={`border-l-4 ${cfg.border} ${cfg.bg} rounded-r-xl p-4 sm:p-5 flex items-start gap-3.5 mt-6 border border-[#DDE3E8] border-l-4`}>
          <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${cfg.iconClass}`} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-mono font-bold tracking-widest text-[#211B20] uppercase">
                {cfg.label}
              </p>
              <span className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded border ${cfg.badge}`}>
                {data.conclusion.toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-[#6B5F69] leading-relaxed">
              {cfg.desc}
            </p>
          </div>
        </div>
      </div>

      <EmailModal open={showEmailModal} onOpenChange={setShowEmailModal} />
    </motion.div>
  );
};

export default NarrativeSynthesis;
