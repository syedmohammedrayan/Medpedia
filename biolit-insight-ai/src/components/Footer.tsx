import { Stethoscope, Heart } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => (
  <footer className="border-t border-slate-100 bg-white py-10 mt-auto">
    <div className="max-w-6xl mx-auto px-6">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center shadow-sm shadow-indigo-300/30">
            <Stethoscope className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">Medical Research Assistant</p>
            <p className="text-xs text-slate-400 mt-0.5">AI-powered clinical evidence synthesis</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
          <Link to="/" className="hover:text-indigo-600 transition-colors font-medium">Home</Link>
          <Link to="/search" className="hover:text-indigo-600 transition-colors font-medium">Research</Link>
          <a href="mailto:ahs462agk@gmail.com" className="hover:text-indigo-600 transition-colors">
            ahs462agk@gmail.com
          </a>
          <span className="flex items-center gap-1">
            Made with <Heart className="w-3 h-3 text-rose-500 fill-rose-500 mx-0.5" /> 🇵🇰
          </span>
          <span>© 2026</span>
        </div>
      </div>
    </div>
  </footer>
);

export default Footer;
