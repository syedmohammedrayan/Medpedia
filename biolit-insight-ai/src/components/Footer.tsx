import { Link } from "react-router-dom";
import { BookOpen } from "lucide-react";

const Footer = () => (
  <footer className="border-t border-[#DDE3E8] bg-[#FAF8F5] py-12 mt-auto text-[#211B20]">
    <div className="max-w-6xl mx-auto px-4 sm:px-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 pb-8 border-b border-[#DDE3E8]">

        {/* Brand Column */}
        <div className="space-y-2 max-w-sm">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#3A0F34] flex items-center justify-center border border-[#240720]">
              <BookOpen className="w-4 h-4 text-[#EAAA00]" />
            </div>
            <div>
              <p className="font-heading font-extrabold text-[#211B20] text-sm tracking-tight">Medpedia</p>
              <p className="text-[10px] font-mono uppercase tracking-widest text-[#B8AEA3]">Clinical Evidence Synthesis</p>
            </div>
          </div>
          <p className="text-xs text-[#6B5F69] leading-relaxed">
            Autonomous multi-agent research architecture querying 35M+ PubMed publications for evidence extraction and GRADE certainty grading.
          </p>
        </div>

        {/* Navigation & Links */}
        <div className="flex flex-wrap items-center gap-x-8 gap-y-3 text-xs font-heading font-semibold uppercase tracking-wider text-[#6B5F69]">
          <Link to="/" className="hover:text-[#3A0F34] transition-colors">
            Home
          </Link>
          <Link to="/search" className="hover:text-[#3A0F34] transition-colors">
            Research Workspace
          </Link>
          <a
            href="https://pubmed.ncbi.nlm.nih.gov/"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[#3A0F34] transition-colors flex items-center gap-1.5"
          >
            <span>PubMed</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#EAAA00]" />
          </a>
          <a
            href="mailto:medpedia@gmail.com"
            className="hover:text-[#3A0F34] transition-colors lowercase font-mono"
          >
            medpedia@gmail.com
          </a>
        </div>

      </div>

      {/* Bottom Legal & Colophon */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 text-[11px] font-mono text-[#B8AEA3]">
        <div className="flex items-center gap-2">
          <span>VOL. 26 · CLINICAL INTELLIGENCE ARCHIVE</span>
          <span>·</span>
          <span>© 2026 MEDPEDIA</span>
        </div>
        <div>
          <span>NATIONAL LIBRARY OF MEDICINE COMPATIBLE</span>
        </div>
      </div>

    </div>
  </footer>
);

export default Footer;
