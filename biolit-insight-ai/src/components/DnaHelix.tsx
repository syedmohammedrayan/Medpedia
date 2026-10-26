import { motion } from "framer-motion";

const DnaHelix = () => {
  return (
    <div className="flex gap-[2px] items-center h-6 overflow-hidden pr-2 border-r border-[#DDE3E8] mr-3">
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="w-[2px] rounded-full"
          animate={{
            height: [8, 20, 8],
            backgroundColor: i % 2 === 0 ? "#EAAA00" : "#3A0F34"
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
