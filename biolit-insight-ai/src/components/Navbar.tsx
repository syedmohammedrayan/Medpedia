import { Link, useLocation } from "react-router-dom";
import { ArrowRight, Search, BookOpen, Github } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

/* ─── Compact Editorial Medpedia Logo ──────────────────────────────────────────
   Direct Aubergine lens ring and Marigold ECG signal without bulky containers.
──────────────────────────────────────────────────────────────────────────── */
const EditorialLogo = () => (
  <svg
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="w-5 h-5 flex-shrink-0"
    aria-hidden="true"
  >
    {/* Lens outer ring */}
    <circle cx="12.5" cy="12.5" r="9" stroke="#3A0F34" strokeWidth="2.2" />

    {/* ECG pulse inside lens */}
    <polyline
      points="2,12.5 7,12.5 8.3,6 10.3,19 11.8,9 13,12.5 23,12.5"
      stroke="#EAAA00"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />

    {/* Focal insight accent dot */}
    <circle cx="8.3" cy="6" r="1.5" fill="#EAAA00" />

    {/* Lens handle */}
    <line
      x1="19.2"
      y1="19.2"
      x2="28"
      y2="28"
      stroke="#3A0F34"
      strokeWidth="2.8"
      strokeLinecap="round"
    />
  </svg>
);

const Navbar = () => {
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      {/* ── Fixed Editorial Masthead ────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 right-0 z-50 editorial-masthead w-full select-none">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-4">

          {/* ── Left Region: Minimal Menu Toggle + Compact Brand ── */}
          <div className="flex items-center gap-3 sm:gap-4 flex-shrink-0">
            {/* Minimal Two-Line Editorial Menu Icon (as seen in reference top-left) */}
            <button
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={menuOpen ? "Close navigation drawer" : "Open navigation drawer"}
              className="flex flex-col justify-center items-start gap-[4px] w-7 h-7 group p-1 -ml-1 focus:outline-none cursor-pointer"
              title="Editorial Menu"
            >
              <span
                className={`block h-[1.6px] bg-[#211B20] transition-all duration-200 origin-center ${
                  menuOpen ? "w-4 rotate-45 translate-y-[5.6px]" : "w-4 group-hover:w-4.5"
                }`}
              />
              <span
                className={`block h-[1.6px] bg-[#211B20] transition-all duration-200 origin-center ${
                  menuOpen ? "w-4 -rotate-45" : "w-3 group-hover:w-4"
                }`}
              />
            </button>

            {/* Subtle Vertical Grid Separator */}
            <span className="hidden sm:inline-block h-4 w-[1px] bg-[#DDE3E8]" aria-hidden="true" />

            {/* Medpedia Brand Lockup */}
            <Link to="/" className="flex items-center gap-2 group">
              <EditorialLogo />
              <div className="flex items-baseline gap-1.5">
                <span className="font-heading font-extrabold text-[#211B20] text-[15px] sm:text-[16px] tracking-tight group-hover:text-[#3A0F34] transition-colors leading-none">
                  Medpedia
                </span>
                <span className="font-serif italic text-xs text-[#3A0F34] font-medium leading-none">
                  Research
                </span>
                <span className="hidden lg:inline text-[8px] font-mono uppercase tracking-[0.2em] text-[#B8AEA3] font-semibold pl-2 border-l border-[#DDE3E8] leading-none">
                  Clinical Synthesis
                </span>
              </div>
            </Link>
          </div>

          {/* ── Center & Right: Minimal Editorial Navigation Row ── */}
          <nav className="hidden md:flex items-center gap-5 lg:gap-7 flex-shrink-0">
            {/* Home Route */}
            <Link
              to="/"
              className={`text-[11px] font-mono uppercase tracking-[0.2em] transition-colors relative py-1 ${
                pathname === "/"
                  ? "text-[#3A0F34] font-bold"
                  : "text-[#6B5F69] hover:text-[#211B20]"
              }`}
            >
              Home
              {pathname === "/" && (
                <span className="absolute -bottom-1 left-0 right-0 h-[1.5px] bg-[#3A0F34]" />
              )}
            </Link>

            {/* Research Route */}
            <Link
              to="/search"
              className={`text-[11px] font-mono uppercase tracking-[0.2em] transition-colors relative py-1 ${
                pathname === "/search"
                  ? "text-[#3A0F34] font-bold"
                  : "text-[#6B5F69] hover:text-[#211B20]"
              }`}
            >
              Research
              {pathname === "/search" && (
                <span className="absolute -bottom-1 left-0 right-0 h-[1.5px] bg-[#3A0F34]" />
              )}
            </Link>

            {/* Documentation (External PubMed Archive) */}
            <a
              href="https://pubmed.ncbi.nlm.nih.gov/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] font-mono uppercase tracking-[0.2em] text-[#6B5F69] hover:text-[#211B20] transition-colors"
              title="NCBI PubMed Central Documentation & Archive"
            >
              Docs
            </a>

            {/* GitHub Repository */}
            <a
              href="https://github.com/syedmohammedrayan/Medpedia"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] font-mono uppercase tracking-[0.2em] text-[#6B5F69] hover:text-[#211B20] transition-colors"
              title="Source Code on GitHub"
            >
              GitHub
            </a>

            {/* Subtle Divider */}
            <span className="h-3.5 w-[1px] bg-[#DDE3E8]" aria-hidden="true" />

            {/* Publication Availability Indicator */}
            <div className="hidden xl:flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-[#6B5F69]">
              <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#EAAA00] opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#EAAA00]" />
              </span>
              <span className="font-bold text-[#211B20]">35M+</span>
              <span className="text-[#B8AEA3]">Live</span>
            </div>

            {/* Start Research Action (Text-led with Marigold arrow) */}
            <Link
              to="/search"
              className="group inline-flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-[0.2em] font-bold text-[#3A0F34] hover:text-[#211B20] transition-colors"
            >
              <span>Start Research</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#EAAA00] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            {/* Minimal Search Trigger Icon (matches reference top-right search icon) */}
            <Link
              to="/search"
              aria-label="Direct Search"
              className="text-[#211B20] hover:text-[#3A0F34] transition-colors p-1 -mr-1"
              title="Search Literature"
            >
              <Search className="w-4 h-4 stroke-[1.8]" />
            </Link>
          </nav>

          {/* ── Mobile Right Utility Controls ── */}
          <div className="flex md:hidden items-center gap-3">
            <Link
              to="/search"
              className="inline-flex items-center gap-1 text-[11px] font-mono uppercase tracking-wider font-bold text-[#3A0F34]"
            >
              <span>Research</span>
              <ArrowRight className="w-3 h-3 text-[#EAAA00]" />
            </Link>
            <Link
              to="/search"
              aria-label="Search"
              className="text-[#211B20] hover:text-[#3A0F34] p-1"
            >
              <Search className="w-4 h-4" />
            </Link>
          </div>

        </div>

        {/* ── Minimalist Editorial Fold-Out Drawer ───────────────────────── */}
        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
              className="border-t border-[#DDE3E8] bg-[#F4F0E8] overflow-hidden"
            >
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 text-xs font-mono">
                
                {/* Section 1: Navigation */}
                <div>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#B8AEA3] block mb-3 font-semibold">
                    01 / Directory
                  </span>
                  <ul className="space-y-2.5">
                    <li>
                      <Link
                        to="/"
                        onClick={() => setMenuOpen(false)}
                        className={`block text-[11px] uppercase tracking-[0.16em] transition-colors ${
                          pathname === "/" ? "text-[#3A0F34] font-bold" : "text-[#211B20] hover:text-[#3A0F34]"
                        }`}
                      >
                        Home Overview
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/search"
                        onClick={() => setMenuOpen(false)}
                        className={`block text-[11px] uppercase tracking-[0.16em] transition-colors ${
                          pathname === "/search" ? "text-[#3A0F34] font-bold" : "text-[#211B20] hover:text-[#3A0F34]"
                        }`}
                      >
                        Clinical Research Engine
                      </Link>
                    </li>
                  </ul>
                </div>

                {/* Section 2: Repositories */}
                <div>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#B8AEA3] block mb-3 font-semibold">
                    02 / Repositories
                  </span>
                  <ul className="space-y-2.5">
                    <li>
                      <a
                        href="https://pubmed.ncbi.nlm.nih.gov/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-[11px] uppercase tracking-[0.16em] text-[#211B20] hover:text-[#3A0F34] transition-colors"
                      >
                        <BookOpen className="w-3.5 h-3.5 text-[#EAAA00]" />
                        <span>PubMed Central Archive ↗</span>
                      </a>
                    </li>
                    <li>
                      <a
                        href="https://github.com/syedmohammedrayan/Medpedia"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-[11px] uppercase tracking-[0.16em] text-[#211B20] hover:text-[#3A0F34] transition-colors"
                      >
                        <Github className="w-3.5 h-3.5 text-[#3A0F34]" />
                        <span>GitHub Repository ↗</span>
                      </a>
                    </li>
                  </ul>
                </div>

                {/* Section 3: System Status */}
                <div>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#B8AEA3] block mb-3 font-semibold">
                    03 / Architecture
                  </span>
                  <div className="space-y-1.5 text-[#6B5F69]">
                    <div className="flex items-center gap-1.5 text-[#3A0F34] font-bold text-[11px] uppercase tracking-wider">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#EAAA00] animate-pulse" />
                      LangGraph + Gemini 3.5
                    </div>
                    <p className="text-[10px] text-[#B8AEA3] uppercase tracking-wider">
                      35M+ PubMed & PMC Citations
                    </p>
                    <p className="text-[10px] text-[#B8AEA3] uppercase tracking-wider">
                      GRADE Evidence Classification
                    </p>
                  </div>
                </div>

                {/* Section 4: Action */}
                <div className="flex flex-col justify-end">
                  <Link
                    to="/search"
                    onClick={() => setMenuOpen(false)}
                    className="inline-flex items-center justify-between px-4 py-2.5 border border-[#3A0F34] text-[#3A0F34] hover:bg-[#3A0F34] hover:text-[#FAF8F5] transition-colors text-[11px] uppercase tracking-[0.18em] font-semibold"
                  >
                    <span>Launch Research Query</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#EAAA00]" />
                  </Link>
                </div>

              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>
    </>
  );
};

export default Navbar;
