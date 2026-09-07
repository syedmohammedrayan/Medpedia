import { motion } from "framer-motion";

const DnaHelix = () => {
  return (
    <div className="flex gap-[2px] items-center h-6 overflow-hidden pr-2 border-r border-white/10 mr-4">
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="w-[2px] bg-primary/60 rounded-full"
          animate={{
            height: [8, 20, 8],
            backgroundColor: i % 2 === 0 ? "hsl(190, 90%, 50%)" : "hsl(260, 80%, 60%)"
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: i * 0.1,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
};

export default DnaHelix;

