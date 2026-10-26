import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { ArrowLeft } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: Non-existent route accessed:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="editorial-paper min-h-screen flex flex-col text-[#211B20]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-6 py-32">
        <div className="editorial-card rounded-3xl p-8 sm:p-14 max-w-lg text-center space-y-6 border border-[#DDE3E8] bg-white shadow-sm">
          <div className="space-y-2">
            <span className="text-[11px] font-mono font-bold tracking-widest text-[#EAAA00] uppercase">
              ARCHIVE NOTATION · ERROR 404
            </span>
            <h1 className="text-6xl sm:text-7xl font-extrabold text-[#3A0F34] font-heading tracking-tight">
              404
            </h1>
            <h2 className="text-lg font-bold text-[#211B20] font-heading">
              Publication or Route Not Located
            </h2>
          </div>

          <p className="text-xs sm:text-sm text-[#6B5F69] leading-relaxed max-w-sm mx-auto">
            The requested resource citation or page address could not be verified in the index.
          </p>

          <div className="pt-2">
            <Link
              to="/"
              className="btn-editorial-primary inline-flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-heading font-semibold uppercase tracking-wider"
            >
              <ArrowLeft className="w-3.5 h-3.5 text-[#EAAA00]" />
              <span>Return to Index</span>
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default NotFound;
