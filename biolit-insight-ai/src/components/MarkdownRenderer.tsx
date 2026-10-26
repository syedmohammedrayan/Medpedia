import { ReactNode } from "react";
import { CheckCircle2, AlertTriangle, Sparkles } from "lucide-react";

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer = ({ content }: MarkdownRendererProps) => {
  if (!content || typeof content !== "string") return null;

  const renderInline = (text: string): ReactNode[] =>
    text.split(/(\*\*.*?\*\*|\[.*?\]\(.*?\))/g).map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**"))
        return <strong key={i} className="font-bold text-[#211B20] font-heading">{part.slice(2, -2)}</strong>;
      const link = part.match(/^\[(.*?)\]\((.*?)\)$/);
      if (link)
        return (
          <a
            key={i}
            href={link[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#3A0F34] font-semibold underline decoration-[#EAAA00] decoration-2 underline-offset-2 hover:text-[#EAAA00] transition-colors"
          >
            {link[1]}
          </a>
        );
      return part;
    });

  const renderTable = (header: string[], rows: string[][], key: string) => (
    <div key={key} className="my-4 bg-white border border-[#DDE3E8] rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-[#DDE3E8] bg-[#FAF8F5]">
              {header.map((h, i) => (
                <th key={i} className="px-4 py-2.5 text-left font-mono font-bold tracking-wider text-[#3A0F34] uppercase whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className="border-b border-[#DDE3E8] hover:bg-[#FAF8F5]/80 transition-colors last:border-0">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-4 py-2.5 text-[#3B333A] leading-relaxed align-top">
                    {renderInline(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const elements: ReactNode[] = [];
  const lines = content.split("\n");
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Table detection
    if (line.includes("|") && line.split("|").length > 2) {
      const header = line.split("|").map((c) => c.trim()).filter(Boolean);
      const rows: string[][] = [];
      i++;
      while (i < lines.length && lines[i].includes("|")) {
        const tl = lines[i].trim();
        if (tl.replace(/[\|:\-\s]/g, "") === "") { i++; continue; }
        const cells = lines[i].split("|").map((c) => c.trim()).filter(Boolean);
        if (cells.length > 0) rows.push(cells);
        i++;
      }
      elements.push(renderTable(header, rows, `table-${i}`));
      continue;
    }

    // Section highlights
    const highlights = ["Key Findings", "Consistent Results", "Discrepancies", "Evidence Gaps"];
    const hl = highlights.find((s) => trimmed.startsWith(s));
    if (hl) {
      elements.push(
        <div key={i} className="flex items-center gap-2 mt-6 mb-3 border-b border-[#DDE3E8] pb-1.5">
          <div className="w-6 h-6 rounded-md bg-[#3A0F34] flex items-center justify-center flex-shrink-0">
            {hl === "Key Findings" && <Sparkles className="w-3.5 h-3.5 text-[#EAAA00]" />}
            {hl === "Consistent Results" && <CheckCircle2 className="w-3.5 h-3.5 text-[#EAAA00]" />}
            {(hl === "Discrepancies" || hl === "Evidence Gaps") && <AlertTriangle className="w-3.5 h-3.5 text-[#EAAA00]" />}
          </div>
          <h3 className="text-xs font-mono font-bold tracking-widest text-[#3A0F34] uppercase">{hl}</h3>
        </div>
      );
      i++; continue;
    }

    // Standard markdown
    if (trimmed.startsWith("> ")) {
      elements.push(
        <div key={i} className="my-3 border-l-4 border-[#EAAA00] bg-[#FDF6E4] pl-4 py-2.5 rounded-r-lg border border-[#DDE3E8] border-l-4">
          <p className="text-xs sm:text-sm text-[#3B333A] leading-relaxed">{renderInline(trimmed.replace("> ", ""))}</p>
        </div>
      );
    } else if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="text-sm font-bold text-[#3A0F34] font-heading mt-5 mb-2">
          {renderInline(line.replace("### ", ""))}
        </h3>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={i} className="text-base font-bold text-[#211B20] font-heading mt-6 mb-3 pb-1.5 border-b border-[#DDE3E8]">
          {renderInline(line.replace("## ", ""))}
        </h2>
      );
    } else if (trimmed.startsWith("- ")) {
      elements.push(
        <div key={i} className="flex gap-2.5 my-2">
          <span className="mt-2 w-1.5 h-1.5 rounded-full bg-[#EAAA00] flex-shrink-0" />
          <div className="text-xs sm:text-sm text-[#3B333A] leading-relaxed">
            {renderInline(trimmed.replace("- ", ""))}
          </div>
        </div>
      );
    } else if (trimmed === "---") {
      elements.push(<hr key={i} className="my-5 border-[#DDE3E8]" />);
    } else if (trimmed) {
      elements.push(
        <p key={i} className="text-xs sm:text-sm text-[#3B333A] leading-relaxed mt-2.5">
          {renderInline(line)}
        </p>
      );
    }
    i++;
  }

  return <div className="text-left space-y-0.5">{elements}</div>;
};

export default MarkdownRenderer;
