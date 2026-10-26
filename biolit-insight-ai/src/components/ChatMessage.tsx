import { motion } from "framer-motion";
import ArticleCard from "./ArticleCard";
import EvidenceTable from "./EvidenceTable";
import NarrativeSynthesis from "./NarrativeSynthesis";
import ProgressSteps from "./ProgressSteps";
import MarkdownRenderer from "./MarkdownRenderer";
import { Microscope, User } from "lucide-react";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
  data?: any;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.type === "user";
  const displayContent =
    typeof message.content === "object"
      ? JSON.stringify(message.content)
      : message.content;
  const timestamp = message.timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex gap-3.5 ${isUser ? "justify-end" : "justify-start"} py-2`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-[#3A0F34] border border-[#240720] flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <Microscope className="w-4 h-4 text-[#EAAA00]" />
        </div>
      )}

      <div className={`flex flex-col gap-1.5 ${isUser ? "items-end max-w-[80%]" : "flex-1 min-w-0"}`}>
        <div className="flex items-center gap-2 px-1 text-[11px] font-mono text-[#B8AEA3]">
          <span className="font-semibold text-[#3A0F34]">
            {isUser ? "Clinician Inquiry" : "Medpedia Synthesis"}
          </span>
          <span>·</span>
          <span>{timestamp}</span>
        </div>

        {isUser ? (
          <div className="bg-[#3A0F34] text-[#FAF8F5] px-5 py-3.5 rounded-2xl rounded-tr-sm border border-[#240720] shadow-sm">
            <p className="text-sm font-heading leading-relaxed whitespace-pre-wrap">{displayContent}</p>
          </div>
        ) : (
          <div className="w-full space-y-4">
            {displayContent === "progress" && message.data?.steps && (
              <ProgressSteps steps={message.data.steps} />
            )}
            {displayContent === "articles" && message.data?.articles && (
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-[#DDE3E8] pb-1.5">
                  <p className="text-[10px] font-mono font-bold tracking-widest text-[#B8AEA3] uppercase">
                    ISOLATED CITATIONS ({message.data.articles.length})
                  </p>
                  <span className="text-[10px] font-mono text-[#6B5F69]">
                    PRIMARY SOURCES · PMC / MEDLINE
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-3">
                  {message.data.articles.map((article: any, idx: number) => (
                    <ArticleCard key={idx} article={article} />
                  ))}
                </div>
              </div>
            )}
            {displayContent === "evidence-table" && message.data && (
              <EvidenceTable data={message.data} />
            )}
            {displayContent === "synthesis" && message.data && (
              <NarrativeSynthesis data={message.data} />
            )}
            {!["progress", "articles", "evidence-table", "synthesis"].includes(displayContent) && (
              <div className="editorial-card rounded-2xl rounded-tl-sm px-6 py-5 border border-[#DDE3E8]">
                <MarkdownRenderer content={displayContent} />
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-xl border border-[#DDE3E8] bg-[#FAF8F5] flex items-center justify-center flex-shrink-0 mt-1">
          <User className="w-4 h-4 text-[#3A0F34]" />
        </div>
      )}
    </motion.div>
  );
};

export default ChatMessage;
