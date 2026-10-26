import { motion } from "framer-motion";
import { Loader2, Check } from "lucide-react";

interface ProgressStepsProps {
  steps: string[];
}

const ProgressSteps = ({ steps }: ProgressStepsProps) => {
  return (
    <div className="editorial-card-ivory rounded-2xl p-4 sm:p-5 space-y-2.5 border border-[#DDE3E8]">
      <div className="flex items-center justify-between border-b border-[#DDE3E8] pb-2 mb-3">
        <p className="text-[10px] font-mono font-bold tracking-widest text-[#3A0F34] uppercase">
          AGENT REASONING PIPELINE
        </p>
        <span className="text-[10px] font-mono text-[#B8AEA3]">
          LANGGRAPH ORCHESTRATION
        </span>
      </div>

      {steps.map((step, idx) => {
        const isActive = idx === steps.length - 1;
        const isDone = idx < steps.length - 1;
        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.08 }}
            className="flex items-center gap-3 text-xs"
          >
            {isDone ? (
              <div className="w-4 h-4 rounded-full bg-[#3A0F34] flex items-center justify-center flex-shrink-0">
                <Check className="w-2.5 h-2.5 text-[#EAAA00]" />
              </div>
            ) : isActive ? (
              <Loader2 className="w-4 h-4 text-[#EAAA00] animate-spin flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-[#DDE3E8] bg-[#FAF8F5] flex-shrink-0" />
            )}
            <span className={
              isDone
                ? "text-[#6B5F69]"
                : isActive
                ? "text-[#211B20] font-semibold"
                : "text-[#B8AEA3]"
            }>
              {step}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
};

export default ProgressSteps;
