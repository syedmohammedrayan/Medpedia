import { Link, useLocation } from "react-router-dom";
import { Home, Microscope, ArrowRight, Github, BookOpen } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

const NAV_LINKS = [
  { label: "Home",     path: "/",       icon: Home },
  { label: "Research", path: "/search", icon: Microscope },
];

/* ─── MRA Logo — Magnifying Lens × ECG Pulse ───────────────────────────────
   The lens says "search / research."
   The ECG pulse inside the lens says "medical signal / live analysis."
   Together: one glance → you know this tool searches and analyses medical data.
   This is story-driven iconography — the logo SHOWS what the product does.
──────────────────────────────────────────────────────────────────────────── */
const MRALogo = () => (
  <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: 22, height: 22 }}>
    <defs>
      {/* Clip the ECG line so it never bleeds outside the lens */}
      <clipPath id="mra-lens-clip">
        <circle cx="12.5" cy="12.5" r="8.8" />
      </clipPath>
    </defs>

    {/* ── Lens glass fill (frosted inner glow) ── */}
    <circle cx="12.5" cy="12.5" r="9.2" fill="rgba(255,255,255,0.11)" />

    {/* ── Lens ring ── */}
    <circle cx="12.5" cy="12.5" r="9.2" stroke="white" strokeWidth="2.3" />

    {/* ── ECG / heartbeat pulse clipped inside lens ──
         Flat → sharp spike up → trough → recovery → flat
         This is the universal "medical analysis" signal. ── */}
    <g clipPath="url(#mra-lens-clip)">
      <polyline
        points="2,12.5  7,12.5  8.3,6  10.3,19  11.8,9  13,12.5  23,12.5"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </g>

    {/* ── Glass gleam — top-left highlight (makes it feel like real glass) ── */}
    <circle cx="8" cy="7.5" r="2" fill="white" opacity="0.18" />

    {/* ── Handle — thick rounded stroke at 45° ── */}
    <line x1="19.5" y1="19.5" x2="28" y2="28"
      stroke="white" strokeWidth="3.2" strokeLinecap="round" />

    {/* ── Tiny accent dot where the ECG spike peaks (the "insight" moment) ── */}
    <circle cx="8.3" cy="6" r="1.5" fill="white" opacity="0.7" />
  </svg>
);

const Navbar = () => {
  const { pathname } = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* ── Viewport-wide top accent line ─────────────────── */}
      <div className="fixed top-0 left-0 right-0 z-[60] h-[2px] bg-gradient-to-r from-transparent via-indigo-500/70 to-transparent pointer-events-none" />

      <nav className="fixed top-[2px] left-0 right-0 z-50 px-4 pt-3">
        <div className="max-w-6xl mx-auto navbar-glass rounded-2xl px-5 h-[68px] flex items-center justify-between gap-4">

          {/* ── Brand ──────────────────────────────────────── */}
          <Link to="/" className="flex items-center gap-3 group flex-shrink-0">

            {/* Logo shell */}
            <div className="relative">
              {/* Ambient glow behind the pill */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 blur-[12px] opacity-30 scale-110 group-hover:opacity-55 transition-all duration-300" />
              <motion.div
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.97 }}
                transition={{ type: "spring", stiffness: 380, damping: 22 }}
                className="relative w-11 h-11 rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-400/30"
                style={{
                  background: "linear-gradient(145deg, #6366f1 0%, #7c3aed 55%, #6d28d9 100%)",
                  boxShadow: "0 4px 16px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.22), inset 0 -1px 0 rgba(0,0,0,0.12)",
                }}
              >
                <MRALogo />
              </motion.div>
            </div>

            {/* Text block */}
            <div className="flex flex-col leading-none select-none">
              <div className="flex items-center gap-1.5">
                <span className="font-black text-slate-900 text-[15px] tracking-tight">Medical Research</span>
              </div>
              <div className="flex items-center gap-1.5 mt-[3px]">
                <span
                  className="font-black text-[14px] tracking-tight"
                  style={{
                    background: "linear-gradient(90deg, #6366f1, #7c3aed)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  Assistant
                </span>
                <span className="text-[9px] font-black px-[5px] py-[2px] rounded-md bg-gradient-to-r from-indigo-500 to-violet-600 text-white leading-none tracking-wide shadow-sm">
                  AI
                </span>
              </div>
            </div>
          </Link>

          {/* ── Centre nav tabs (desktop) ───────────────────── */}
          <div className="hidden md:flex items-center bg-slate-100/70 rounded-xl p-1 gap-0.5 flex-shrink-0">
            {NAV_LINKS.map(({ label, path, icon: Icon }) => {
              const active = pathname === path;
              return (
                <Link
                  key={path}
                  to={path}
                  className={`relative flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-colors duration-150 ${
                    active ? "text-indigo-700" : "text-slate-500 hover:text-slate-800"
                  }`}
                >
                  {active && (
                    <motion.div
                      layoutId="nav-pill"
                      className="absolute inset-0 bg-white rounded-lg shadow-sm border border-indigo-100"
                      transition={{ type: "spring", stiffness: 420, damping: 30 }}
                    />
                  )}
                  <Icon
                    className={`relative z-10 transition-colors duration-150 ${
                      active ? "text-indigo-500" : "text-slate-400"
                    }`}
                    style={{ width: 14, height: 14 }}
                  />
                  <span className="relative z-10">{label}</span>
                </Link>
              );
            })}
          </div>

          {/* ── Right actions ───────────────────────────────── */}
          <div className="flex items-center gap-2 flex-shrink-0">

            {/* Live PubMed status — large screens */}
            <div className="hidden lg:flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-slate-200/80 bg-gradient-to-r from-white to-slate-50/80">
              <span className="relative flex h-2 w-2 flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-70" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <div className="flex items-baseline gap-1 text-[11px] leading-none">
                <span className="font-black text-slate-800 text-[13px]">35M+</span>
                <span className="text-slate-400 font-medium">articles</span>
                <span className="mx-0.5 text-slate-300">·</span>
                <span className="font-bold text-emerald-600">Live</span>
              </div>
            </div>

            {/* Compact live pill — medium screens */}
            <div className="hidden md:flex lg:hidden items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-emerald-200 bg-emerald-50">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
              </span>
              <span className="text-[11px] font-bold text-emerald-700">Live</span>
            </div>

            {/* PubMed link */}
            <a
              href="https://pubmed.ncbi.nlm.nih.gov/"
              target="_blank"
              rel="noopener noreferrer"
              title="PubMed Database"
              className="hidden sm:flex w-9 h-9 rounded-xl border border-slate-200 items-center justify-center text-slate-400 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 transition-all duration-200"
            >
              <BookOpen style={{ width: 15, height: 15 }} />
            </a>

            {/* GitHub */}
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              title="GitHub"
              className="hidden sm:flex w-9 h-9 rounded-xl border border-slate-200 items-center justify-center text-slate-400 hover:text-slate-800 hover:border-slate-300 hover:bg-slate-50 transition-all duration-200"
            >
              <Github style={{ width: 15, height: 15 }} />
            </a>

            {/* ── Premium CTA button ── */}
            <Link to="/search" className="group relative hidden sm:flex items-center gap-2 overflow-visible">
              {/* Soft glow halo on hover */}
              <div className="absolute inset-0 rounded-xl bg-indigo-500 blur-lg opacity-0 group-hover:opacity-35 transition-opacity duration-300 scale-110" />
              <motion.div
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                className="relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-[13px] font-bold text-white overflow-hidden"
                style={{
                  background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
                  boxShadow:
                    "0 2px 14px rgba(99,102,241,0.50), inset 0 1px 0 rgba(255,255,255,0.20), inset 0 -1px 0 rgba(0,0,0,0.10)",
                }}
              >
                {/* Shimmer sweep */}
                <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 ease-in-out bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-[-18deg]" />
                <span className="relative z-10 tracking-tight">Start Research</span>
                <ArrowRight
                  className="relative z-10 group-hover:translate-x-0.5 transition-transform duration-200"
                  style={{ width: 14, height: 14 }}
                />
              </motion.div>
            </Link>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen((v) => !v)}
              aria-label="Toggle menu"
              className="flex md:hidden w-9 h-9 rounded-xl border border-slate-200 items-center justify-center text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all"
            >
              <div className="flex flex-col gap-[5px]">
                <motion.span animate={mobileOpen ? { rotate: 45, y: 7 }  : { rotate: 0, y: 0 }}  transition={{ duration: 0.2 }} className="block w-4 h-0.5 bg-current rounded-full origin-center" />
                <motion.span animate={mobileOpen ? { opacity: 0, scaleX: 0 } : { opacity: 1, scaleX: 1 }} transition={{ duration: 0.2 }} className="block w-4 h-0.5 bg-current rounded-full" />
                <motion.span animate={mobileOpen ? { rotate: -45, y: -7 } : { rotate: 0, y: 0 }} transition={{ duration: 0.2 }} className="block w-4 h-0.5 bg-current rounded-full origin-center" />
              </div>
            </button>
          </div>
        </div>

        {/* ── Mobile dropdown ─────────────────────────────── */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
              className="md:hidden max-w-6xl mx-auto mt-2 navbar-glass rounded-2xl px-4 py-3 flex flex-col gap-1"
            >
              {NAV_LINKS.map(({ label, path, icon: Icon }) => {
                const active = pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                      active
                        ? "bg-indigo-50 text-indigo-700 border border-indigo-100"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <Icon style={{ width: 16, height: 16 }} className={active ? "text-indigo-500" : "text-slate-400"} />
                    {label}
                    {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500" />}
                  </Link>
                );
              })}

              <div className="mt-1 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 px-1">
                <div className="flex items-center gap-2 text-[11px] font-semibold text-emerald-600">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
                  </span>
                  35M+ Articles · Live PubMed
                </div>
                <Link
                  to="/search"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white"
                  style={{ background: "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)" }}
                >
                  Start Research
                  <ArrowRight style={{ width: 12, height: 12 }} />
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </>
  );
};

export default Navbar;
