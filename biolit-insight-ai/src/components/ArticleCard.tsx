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
      ? "bg-[#3A0F34] text-[#FAF8F5] border-[#240720]"
      : article.relevance >= 60
      ? "bg-[#FDF6E4] text-[#7A5800] border-[#EAAA00]"
      : "bg-[#FAF8F5] text-[#6B5F69] border-[#DDE3E8]";

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 350, damping: 25 }}
      className="editorial-card rounded-2xl p-4 sm:p-5 border border-[#DDE3E8] bg-white"
    >
      <div className="flex items-start justify-between gap-4 mb-2.5">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[10px] font-mono font-bold tracking-widest text-[#B8AEA3] uppercase">
              {article.journal}
            </span>
            <span className="text-[#DDE3E8]">·</span>
            <span className="text-[10px] font-mono text-[#6B5F69]">
              PEER-REVIEWED
            </span>
          </div>
          <h4 className="text-sm sm:text-base font-bold text-[#211B20] font-heading leading-snug">
            {article.title}
          </h4>
        </div>

        <div className="flex flex-col items-end flex-shrink-0">
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${relevanceBadge}`}>
            {article.relevance}% MATCH
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4 text-xs text-[#6B5F69] mb-3.5">
        <span className="flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-[#B8AEA3]" />
          <span className="truncate max-w-[240px]">{article.authors}</span>
        </span>
        <span className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-[#B8AEA3]" />
          <span>{article.year}</span>
        </span>
        {article.doi && (
          <span className="font-mono text-[11px] text-[#B8AEA3] truncate max-w-[180px]">
            DOI: {article.doi}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-[#DDE3E8]">
        <div className="flex items-center gap-3">
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmcid}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs font-heading font-semibold text-[#3A0F34] hover:text-[#EAAA00] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#EAAA00]" />
            <span>PubMed Citation</span>
          </a>
          <span className="text-[#DDE3E8]">|</span>
          <a
            href={`https://doi.org/${article.doi}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-[#6B5F69] hover:text-[#211B20] transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5 text-[#B8AEA3]" />
            <span>Full-Text Access</span>
          </a>
        </div>

        <span className="text-[10px] font-mono text-[#B8AEA3]">
          PMID: {article.pmcid}
        </span>
      </div>
    </motion.div>
  );
};

export default ArticleCard;
