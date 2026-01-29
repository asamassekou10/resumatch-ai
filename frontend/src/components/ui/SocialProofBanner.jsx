import React from 'react';
import { motion } from 'framer-motion';
import { Users, TrendingUp } from 'lucide-react';

/**
 * SocialProofBanner Component
 * Displays user count and activity to build trust
 */
const SocialProofBanner = ({ className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-r from-blue-500/10 via-cyan-500/10 to-blue-500/10 border border-blue-500/20 rounded-xl p-4 ${className}`}
    >
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-center sm:text-left">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0">
            <Users className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-lg font-display">10,000+</p>
            <p className="text-gray-400 text-xs">Job seekers improved their resumes</p>
          </div>
        </div>
        
        <div className="hidden sm:block w-px h-10 bg-white/10" />
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-lg font-display">500+</p>
            <p className="text-gray-400 text-xs">Analyzing resumes today</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SocialProofBanner;
