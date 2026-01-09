import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scan, Sparkles, ArrowRight, Shield } from 'lucide-react';

/**
 * FreeScannerWidget - High-conversion CTA component for blog posts
 *
 * A "Trojan Horse" style mini-tool widget that drives traffic to /guest-analyze
 * Designed to look like a tool preview rather than a banner ad
 *
 * @param {Object} props
 * @param {string} props.headline - Custom headline text (optional)
 * @param {string} props.subtext - Custom subtext (optional)
 */
const FreeScannerWidget = ({
  headline = "Will your resume pass the ATS?",
  subtext = "Get your ATS Score + Missing Keywords in 10 seconds. Works for any job, any industry."
}) => {
  return (
    <motion.div
      className="my-10 relative overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      {/* Main Container - Gradient border effect */}
      <div className="relative rounded-2xl p-[2px] bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-500">
        {/* Inner Container */}
        <div className="relative rounded-2xl bg-slate-900/95 backdrop-blur-sm p-6 md:p-8">
          {/* Background glow effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-blue-600/10 to-cyan-600/10 rounded-2xl pointer-events-none" />

          {/* Badge - Top right */}
          <div className="absolute -top-3 right-6 md:right-8">
            <motion.div
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-lg shadow-green-500/25 flex items-center gap-1.5"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Sparkles className="w-3 h-3" />
              2 Free Scans / 24h included
            </motion.div>
          </div>

          <div className="relative z-10 flex flex-col lg:flex-row items-center gap-6 lg:gap-8">
            {/* Left: Icon/Visual */}
            <div className="flex-shrink-0">
              <motion.div
                className="w-20 h-20 md:w-24 md:h-24 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/25"
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Scan className="w-10 h-10 md:w-12 md:h-12 text-white" />
              </motion.div>
            </div>

            {/* Center: Copy */}
            <div className="flex-grow text-center lg:text-left">
              <h3 className="text-xl md:text-2xl font-bold text-white mb-2 font-display">
                {headline}
              </h3>
              <p className="text-gray-300 text-sm md:text-base mb-4">
                {subtext}
              </p>

              {/* Trust indicators */}
              <div className="flex flex-wrap justify-center lg:justify-start gap-4 text-xs text-gray-400">
                <span className="flex items-center gap-1">
                  <Shield className="w-3 h-3 text-green-400" />
                  No signup required
                </span>
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-blue-400" />
                  AI-powered analysis
                </span>
              </div>
            </div>

            {/* Right: CTA Button */}
            <div className="flex-shrink-0">
              <Link to="/guest-analyze">
                <motion.button
                  className="group relative inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-bold text-white rounded-full overflow-hidden"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {/* Button gradient background */}
                  <span className="absolute inset-0 bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-500" />

                  {/* Shimmer effect */}
                  <span className="absolute inset-[-1000%] animate-[spin_3s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#60A5FA_0%,#2563EB_50%,#60A5FA_100%)] opacity-30" />

                  {/* Button content */}
                  <span className="relative flex items-center gap-2">
                    Analyze My Resume
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </motion.button>
              </Link>
            </div>
          </div>

          {/* Bottom: Mini stats/social proof */}
          <div className="relative z-10 mt-6 pt-4 border-t border-white/10 flex flex-wrap justify-center gap-6 text-xs text-gray-400">
            <span>
              <span className="text-white font-bold">10,000+</span> resumes analyzed
            </span>
            <span>
              <span className="text-white font-bold">92%</span> success rate
            </span>
            <span>
              <span className="text-white font-bold">4.8/5</span> user rating
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FreeScannerWidget;
