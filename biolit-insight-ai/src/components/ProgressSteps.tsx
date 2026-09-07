import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

interface ProgressStepsProps {
  steps: string[];
}

const ProgressSteps = ({ steps }: ProgressStepsProps) => {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2 shadow-sm">
      <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase mb-3">
        Agent Steps
      </p>
      {steps.map((step, idx) => {
        const isActive = idx === steps.length - 1;
        const isDone = idx < steps.length - 1;
        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center gap-3 text-sm"
          >
            {isDone ? (
              <div className="w-4 h-4 rounded-full border border-indigo-200 bg-indigo-50 flex items-center justify-center flex-shrink-0">
                <svg className="w-2.5 h-2.5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            ) : isActive ? (
              <Loader2 className="w-4 h-4 text-indigo-500 animate-spin flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-slate-200 bg-slate-50 flex-shrink-0" />
            )}
            <span className={
              isDone
                ? "text-slate-500"
                : isActive
                ? "text-slate-800 font-medium"
                : "text-slate-400"
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
