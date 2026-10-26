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
      {/* Table Header Label */}
      <div className="flex items-center justify-between border-b border-[#DDE3E8] pb-2">
        <div className="flex items-center gap-2">
          <TableIcon className="w-4 h-4 text-[#EAAA00]" />
          <p className="text-[11px] font-mono font-bold tracking-widest text-[#211B20] uppercase">
            Structured Evidence Matrix
          </p>
          <span className="text-[10px] font-mono text-[#B8AEA3]">
            ({data.rows.length} {data.rows.length === 1 ? "study isolated" : "studies isolated"})
          </span>
        </div>
        <span className="text-[10px] font-mono text-[#6B5F69] hidden sm:inline">
          STANDARDIZED PICO METRICS
        </span>
      </div>

      {/* Table Container */}
      <div className="bg-white border border-[#DDE3E8] rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-[#DDE3E8] hover:bg-transparent bg-[#FAF8F5]">
                {data.columns.map((col, idx) => (
                  <TableHead
                    key={idx}
                    className="text-[10px] font-mono font-bold tracking-wider text-[#3A0F34] uppercase whitespace-nowrap h-11 px-4"
                  >
                    {col}
                  </TableHead>
                ))}
                <TableHead className="text-[10px] font-mono font-bold tracking-wider text-[#3A0F34] uppercase h-11 w-12 px-4">
                  REF
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.rows.map((row, idx) => (
                <motion.tr
                  key={idx}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-[#DDE3E8] hover:bg-[#FAF8F5]/80 transition-colors last:border-0"
                >
                  <TableCell className="text-xs font-mono font-bold text-[#211B20] py-3.5 px-4 whitespace-nowrap">
                    {row.study}
                  </TableCell>
                  <TableCell className="text-xs text-[#6B5F69] py-3.5 px-4 whitespace-nowrap">
                    {row.design}
                  </TableCell>
                  <TableCell className="text-xs font-mono font-semibold text-[#3A0F34] py-3.5 px-4 text-center">
                    {row.n}
                  </TableCell>
                  <TableCell className="text-xs text-[#211B20] py-3.5 px-4 max-w-[200px]">
                    {row.outcome}
                  </TableCell>
                  <TableCell className="text-xs py-3.5 px-4 whitespace-nowrap">
                    <span className="px-2.5 py-1 rounded-md bg-[#FAF8F5] text-[#3A0F34] border border-[#DDE3E8] font-mono font-semibold">
                      {row.effect}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs font-mono text-[#6B5F69] py-3.5 px-4 whitespace-nowrap">
                    {row.pvalue}
                  </TableCell>
                  <TableCell className="text-xs text-[#6B5F69] italic py-3.5 px-4 max-w-[180px]">
                    {row.limitations}
                  </TableCell>
                  <TableCell className="py-3.5 px-4">
                    {row.link && (
                      <a
                        href={row.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-7 h-7 rounded-lg border border-[#DDE3E8] bg-[#FAF8F5] text-[#3A0F34] hover:border-[#3A0F34] hover:bg-white transition-all"
                        aria-label="Open source citation"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
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
