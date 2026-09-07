import { motion } from "framer-motion";

const BioluminescentBackground = () => {
  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden bg-[#0a0c10]">
      {/* Cinematic Fog / Lighting */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,_rgba(34,211,238,0.05)_0%,_transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_rgba(139,92,246,0.05)_0%,_transparent_50%)]" />
      
      {/* Floating Protein Structures (CSS-based shapes) */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={`protein-${i}`}
          className="absolute rounded-full border border-primary/20 backdrop-blur-3xl"
          style={{
            width: Math.random() * 300 + 100,
            height: Math.random() * 300 + 100,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            opacity: 0.1,
          }}
          animate={{
            x: [0, Math.random() * 50 - 25],
            y: [0, Math.random() * 50 - 25],
            rotate: [0, 360],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "linear",
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-secondary/10 rounded-full" />
        </motion.div>
      ))}

      {/* Grid Overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(34,211,238, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238, 0.2) 1px, transparent 1px)`,
          backgroundSize: '100px 100px'
        }}
      />
      
      {/* Bioluminescent Neural Strands (SVG) */}
      <svg className="absolute inset-0 h-full w-full opacity-[0.05]" xmlns="http://www.w3.org/2000/svg">
        <filter id="glow">
          <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <motion.path
          d="M -100 500 Q 400 100 900 600 T 1920 400"
          stroke="url(#grad1)"
          strokeWidth="2"
          fill="none"
          filter="url(#glow)"
          animate={{
            d: [
               "M -100 500 Q 400 100 900 600 T 1920 400",
               "M -100 400 Q 500 200 800 500 T 1920 500",
               "M -100 500 Q 400 100 900 600 T 1920 400"
            ]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        />
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(190, 90%, 50%)" />
            <stop offset="100%" stopColor="hsl(260, 80%, 60%)" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
};

export default BioluminescentBackground;

