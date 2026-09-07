import { motion } from "framer-motion";
import ArticleCard from "./ArticleCard";
import EvidenceTable from "./EvidenceTable";
import NarrativeSynthesis from "./NarrativeSynthesis";
import ProgressSteps from "./ProgressSteps";
import MarkdownRenderer from "./MarkdownRenderer";
import { FlaskConical, User } from "lucide-react";

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
      className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"} py-1`}
    >
      {!isUser && (
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm shadow-indigo-200">
          <FlaskConical className="w-3.5 h-3.5 text-white" />
        </div>
      )}

      <div className={`flex flex-col gap-1 ${isUser ? "items-end max-w-[75%]" : "flex-1 min-w-0"}`}>
        <span className="text-[11px] text-slate-400 font-medium px-1 tracking-wide">
          {isUser ? `You · ${timestamp}` : `Research Assistant · ${timestamp}`}
        </span>

        {isUser ? (
          <div className="bg-gradient-to-br from-indigo-500 to-violet-600 text-white px-4 py-3 rounded-xl rounded-tr-sm shadow-sm shadow-indigo-200">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{displayContent}</p>
          </div>
        ) : (
          <div className="w-full space-y-4">
            {displayContent === "progress" && message.data?.steps && (
              <ProgressSteps steps={message.data.steps} />
            )}
            {displayContent === "articles" && message.data?.articles && (
              <div className="space-y-3">
                <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase px-1">
                  Source Articles ({message.data.articles.length})
                </p>
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
              <div className="bubble-agent rounded-xl rounded-tl-sm px-5 py-4">
                <MarkdownRenderer content={displayContent} />
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center flex-shrink-0 mt-0.5">
          <User className="w-3.5 h-3.5 text-slate-500" />
        </div>
      )}
    </motion.div>
  );
};

export default ChatMessage;
