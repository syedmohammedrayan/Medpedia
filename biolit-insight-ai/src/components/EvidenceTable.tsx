import { motion } from "framer-motion";
import { ExternalLink, TableIcon } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface EvidenceTableProps {
  data: {
    columns: string[];
    rows: any[];
  };
}

const EvidenceTable = ({ data }: EvidenceTableProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      <div className="flex items-center gap-2">
        <TableIcon className="w-3.5 h-3.5 text-indigo-500" />
        <p className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">
          Evidence Matrix
        </p>
        <span className="text-[10px] text-slate-400 ml-1">
          ({data.rows.length} {data.rows.length === 1 ? "study" : "studies"})
        </span>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-slate-100 hover:bg-transparent bg-slate-50">
                {data.columns.map((col, idx) => (
                  <TableHead
                    key={idx}
                    className="text-[10px] font-bold tracking-widest text-slate-500 uppercase whitespace-nowrap h-10"
                  >
                    {col}
                  </TableHead>
                ))}
                <TableHead className="text-[10px] font-bold tracking-widest text-slate-500 uppercase h-10 w-10">
                  Ref
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.rows.map((row, idx) => (
                <motion.tr
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.06 }}
                  className="border-b border-slate-100 hover:bg-indigo-50/40 transition-colors last:border-0"
                >
                  <TableCell className="text-sm font-semibold text-slate-800 py-3 whitespace-nowrap font-mono">
                    {row.study}
                  </TableCell>
                  <TableCell className="text-xs text-slate-500 py-3">{row.design}</TableCell>
                  <TableCell className="text-xs font-mono text-slate-700 py-3 text-center">{row.n}</TableCell>
                  <TableCell className="text-xs text-slate-500 py-3 max-w-[180px]">{row.outcome}</TableCell>
                  <TableCell className="text-xs font-semibold py-3">
                    <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono whitespace-nowrap">
                      {row.effect}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs font-mono text-slate-500 py-3 whitespace-nowrap">
                    {row.pvalue}
                  </TableCell>
                  <TableCell className="text-xs text-slate-500 italic py-3 max-w-[160px]">
                    {row.limitations}
                  </TableCell>
                  <TableCell className="py-3">
                    {row.link && (
                      <a
                        href={row.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-7 h-7 rounded-md border border-indigo-200 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                        aria-label="Open source"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </motion.div>
  );
};

export default EvidenceTable;
