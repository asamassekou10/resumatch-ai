import React from 'react';
import { motion } from 'framer-motion';

/**
 * EntranceOverlay - Animated entrance screen with shutter effect
 *
 * @param {Object} props
 * @param {Function} props.onComplete - Callback when animation completes
 */
const EntranceOverlay = ({ onComplete }) => {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black"
      initial={{ clipPath: "inset(0 0 0 0)" }}
      animate={{ clipPath: "inset(100% 0 0 0)" }}
      transition={{ duration: 1, delay: 2.2, ease: [0.87, 0, 0.13, 1] }}
      onAnimationComplete={onComplete}
    >
      <div className="relative z-10">
        <div className="overflow-hidden mb-2">
          <motion.h1
            className="text-5xl md:text-8xl font-bold text-white tracking-tighter font-display"
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          >
            ResumeAnalyzer
          </motion.h1>
        </div>
        <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
            initial={{ x: "-100%" }}
            animate={{ x: "100%" }}
            transition={{ duration: 1.5, ease: "easeInOut", repeat: Infinity }}
          />
        </div>
        <motion.p
          className="text-center text-gray-500 mt-4 text-sm uppercase tracking-[0.3em] font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Initializing AI Core
        </motion.p>
      </div>
    </motion.div>
  );
};

export default EntranceOverlay;
