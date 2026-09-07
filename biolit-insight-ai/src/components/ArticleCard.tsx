import { motion } from "framer-motion";
import { ExternalLink, FileText, Calendar, Users } from "lucide-react";

interface Article {
  title: string;
  authors: string;
  journal: string;
  year: number;
  doi: string;
  pmcid: string;
  relevance: number;
}

interface ArticleCardProps {
  article: Article;
}

const ArticleCard = ({ article }: ArticleCardProps) => {
  const relevanceBadge =
    article.relevance >= 80
      ? "text-indigo-700 bg-indigo-50 border-indigo-200"
      : article.relevance >= 60
      ? "text-violet-700 bg-violet-50 border-violet-200"
      : "text-slate-500 bg-slate-50 border-slate-200";

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.005 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className="card-elevated rounded-xl p-4"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase mb-1.5">
            {article.journal}
          </p>
          <h4 className="text-sm font-semibold text-slate-800 leading-snug line-clamp-2">
            {article.title}
          </h4>
        </div>
        <span className={`flex-shrink-0 text-[11px] font-bold px-2 py-0.5 rounded border ${relevanceBadge}`}>
          {article.relevance}%
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mb-3">
        <span className="flex items-center gap-1">
          <Users className="w-3 h-3" />
          <span className="truncate max-w-[200px]">{article.authors}</span>
        </span>
        <span className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          {article.year}
        </span>
        {article.doi && (
          <span className="font-mono text-[10px] truncate max-w-[160px] text-slate-400">{article.doi}</span>
        )}
      </div>

      <div className="flex items-center gap-3 pt-3 border-t border-slate-100">
        <a
          href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmcid}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          <FileText className="w-3.5 h-3.5" />
          PubMed
        </a>
        <span className="text-slate-300">·</span>
        <a
          href={`https://doi.org/${article.doi}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-700 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Full text
        </a>
      </div>
    </motion.div>
  );
};

export default ArticleCard;
