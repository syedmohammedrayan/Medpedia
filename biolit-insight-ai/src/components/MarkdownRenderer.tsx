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
        return <strong key={i} className="font-semibold text-slate-800">{part.slice(2, -2)}</strong>;
      const link = part.match(/^\[(.*?)\]\((.*?)\)$/);
      if (link)
        return (
          <a key={i} href={link[2]} target="_blank" rel="noopener noreferrer"
            className="text-indigo-600 hover:text-indigo-700 underline underline-offset-2 transition-colors">
            {link[1]}
          </a>
        );
      return part;
    });

  const renderTable = (header: string[], rows: string[][], key: string) => (
    <div key={key} className="my-4 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {header.map((h, i) => (
                <th key={i} className="px-4 py-2.5 text-left font-bold tracking-widest text-slate-500 uppercase whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className="border-b border-slate-100 hover:bg-indigo-50/40 transition-colors last:border-0">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-4 py-2.5 text-slate-600 leading-relaxed align-top">
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
        <div key={i} className="flex items-center gap-2 mt-6 mb-3">
          <div className="w-6 h-6 rounded-md border border-indigo-200 bg-indigo-50 flex items-center justify-center flex-shrink-0">
            {hl === "Key Findings" && <Sparkles className="w-3 h-3 text-indigo-600" />}
            {hl === "Consistent Results" && <CheckCircle2 className="w-3 h-3 text-indigo-600" />}
            {(hl === "Discrepancies" || hl === "Evidence Gaps") && <AlertTriangle className="w-3 h-3 text-violet-600" />}
          </div>
          <h3 className="text-[11px] font-bold tracking-widest text-slate-500 uppercase">{hl}</h3>
          <div className="flex-1 h-px bg-slate-200" />
        </div>
      );
      i++; continue;
    }

    // Standard markdown
    if (trimmed.startsWith("> ")) {
      elements.push(
        <div key={i} className="my-3 border-l-2 border-violet-400 bg-violet-50 pl-4 py-2 rounded-r-lg">
          <p className="text-sm text-slate-600">{renderInline(trimmed.replace("> ", ""))}</p>
        </div>
      );
    } else if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="text-sm font-semibold text-slate-700 mt-5 mb-2">
          {renderInline(line.replace("### ", ""))}
        </h3>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={i} className="text-base font-bold text-slate-800 mt-6 mb-3 pb-2 border-b border-slate-200">
          {renderInline(line.replace("## ", ""))}
        </h2>
      );
    } else if (trimmed.startsWith("- ")) {
      elements.push(
        <div key={i} className="flex gap-2.5 my-1.5">
          <span className="mt-2 w-1 h-1 rounded-full bg-indigo-400 flex-shrink-0" />
          <div className="text-sm text-slate-600 leading-relaxed">
            {renderInline(trimmed.replace("- ", ""))}
          </div>
        </div>
      );
    } else if (trimmed === "---") {
      elements.push(<hr key={i} className="my-5 border-slate-200" />);
    } else if (trimmed) {
      elements.push(
        <p key={i} className="text-sm text-slate-600 leading-relaxed mt-2">
          {renderInline(line)}
        </p>
      );
    }
    i++;
  }

  return <div className="text-left space-y-0.5">{elements}</div>;
};

export default MarkdownRenderer;
