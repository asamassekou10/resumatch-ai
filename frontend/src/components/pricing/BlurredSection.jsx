import React from 'react';
import { motion } from 'framer-motion';
import { Lock, Sparkles, Zap } from 'lucide-react';

/**
 * BlurredSection Component
 *
 * Displays a glassmorphism blur overlay over restricted content to drive conversions.
 * Shows preview content (e.g., first 3 keywords) and hides the rest behind a blur with upgrade CTA.
 *
 * Props:
 * - title: Section title (e.g., "Missing Keywords", "AI Recommendations")
 * - previewContent: Content to show (React node or string)
 * - blurredCount: Number of items hidden (e.g., "9 more keywords")
 * - upgradeOptions: Array of pricing options from API
 * - onUpgrade: Callback to open payment modal with selected option
 * - icon: Optional icon component (defaults to Lock)
 * - message: Optional custom message (defaults based on blurredCount)
 */
const BlurredSection = ({
  title,
  previewContent,
  blurredCount = 0,
  upgradeOptions = [],
  onUpgrade,
  icon: Icon = Lock,
  message
}) => {
  // Find recommended option (usually weekly pass)
  const recommendedOption = upgradeOptions.find(opt => opt.recommended) || upgradeOptions[0];
  const singleScan = upgradeOptions.find(opt => opt.type === 'single_rescan');

  // Default message based on blurred count
  const defaultMessage = blurredCount > 0
    ? `Unlock ${blurredCount} more ${blurredCount === 1 ? 'item' : 'items'} to improve your resume`
    : 'Unlock full AI recommendations and insights';

  return (
    <div className="relative">
      {/* Preview Content (Always Visible) */}
      {previewContent && (
        <div className="mb-4">
          {previewContent}
        </div>
      )}

      {/* Blurred Content Overlay */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative rounded-xl overflow-hidden"
      >
        {/* Glassmorphism Blur Effect */}
        <div className="relative bg-gradient-to-br from-gray-900/95 via-gray-800/90 to-gray-900/95 backdrop-blur-xl border border-cyan-500/20 rounded-xl p-8">
          {/* Gradient Glow Effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-blue-500/5 to-purple-500/5 pointer-events-none" />

          {/* Lock Icon with Glow */}
          <div className="relative flex flex-col items-center justify-center text-center space-y-4">
            <motion.div
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="relative"
            >
              <div className="absolute inset-0 bg-cyan-500/20 blur-2xl rounded-full" />
              <div className="relative bg-gradient-to-br from-cyan-500/10 to-blue-500/10 p-4 rounded-2xl border border-cyan-500/30">
                <Icon className="w-8 h-8 text-cyan-400" />
              </div>
            </motion.div>

            {/* Title */}
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-white">
                {message || defaultMessage}
              </h3>
              {blurredCount > 0 && (
                <p className="text-gray-400 text-sm">
                  <span className="text-cyan-400 font-semibold">{blurredCount} more insights available</span> - Unlock the full analysis to optimize your resume.
                </p>
              )}
            </div>

            {/* Hover Preview Hint */}
            <div className="mt-2 text-xs text-gray-500 italic">
              Hover to see preview
            </div>

            {/* Pricing Options */}
            <div className="flex flex-col sm:flex-row gap-3 w-full max-w-lg mt-6">
              {/* Single Re-scan Option */}
              {singleScan && (
                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onUpgrade(singleScan)}
                  className="flex-1 bg-white/5 hover:bg-white/10 border border-cyan-500/30 hover:border-cyan-400/50 rounded-lg p-4 transition-all group"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-left">
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-cyan-400" />
                        <span className="text-white font-semibold text-sm">Quick Unlock</span>
                      </div>
                      <p className="text-gray-400 text-xs mt-1">{singleScan.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-cyan-400">
                        ${singleScan.price}
                      </div>
                      <div className="text-xs text-gray-500">one-time</div>
                    </div>
                  </div>
                </motion.button>
              )}

              {/* Recommended Option (Weekly Pass) */}
              {recommendedOption && (
                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onUpgrade(recommendedOption)}
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg p-4 transition-all group relative overflow-hidden"
                >
                  {/* Shimmer Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />

                  {recommendedOption.recommended && (
                    <div className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs font-bold px-2 py-1 rounded-bl-lg rounded-tr-lg flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      BEST VALUE
                    </div>
                  )}

                  <div className="relative flex items-center justify-between">
                    <div className="text-left">
                      <div className="text-white font-semibold text-sm">
                        {recommendedOption.type === 'weekly_pass' ? '7-Day Pass' : 'Recommended'}
                      </div>
                      <p className="text-white/80 text-xs mt-1">{recommendedOption.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">
                        ${recommendedOption.price}
                      </div>
                      <div className="text-xs text-white/70">unlimited</div>
                    </div>
                  </div>
                </motion.button>
              )}
            </div>

            {/* Additional CTA */}
            <p className="text-xs text-gray-500 mt-4">
              Secure payment powered by Stripe • Money-back guarantee
            </p>
          </div>
        </div>

        {/* Subtle Border Animation */}
        <motion.div
          className="absolute inset-0 rounded-xl pointer-events-none"
          animate={{
            boxShadow: [
              '0 0 20px rgba(6, 182, 212, 0.1)',
              '0 0 40px rgba(6, 182, 212, 0.2)',
              '0 0 20px rgba(6, 182, 212, 0.1)',
            ]
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.div>
    </div>
  );
};

export default BlurredSection;
