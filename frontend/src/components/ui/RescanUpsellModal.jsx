import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calculator, ArrowRight, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';
import { trackUpgradeClicked } from '../../utils/conversionTracking';

/**
 * RescanUpsellModal Component
 * Smart upsell when user wants to re-scan but has 0 credits
 */
const RescanUpsellModal = ({ isOpen, onClose, className = '' }) => {
  const navigate = useNavigate();

  const handleSingleScan = () => {
    trackUpgradeClicked('rescan_modal', 'single_scan');
    // Navigate to pricing page where they can purchase single scan
    navigate(`${ROUTES.PRICING}?highlight=single_scan`);
    onClose();
  };

  const handleWeeklyPass = () => {
    trackUpgradeClicked('rescan_modal', 'weekly_pass');
    // Navigate to pricing page where they can purchase weekly pass
    navigate(`${ROUTES.PRICING}?highlight=weekly_pass`);
    onClose();
  };

  // Calculate savings
  const singleScanPrice = 1.99;
  const weeklyPassPrice = 6.99;
  const scansForBreakEven = Math.ceil(weeklyPassPrice / singleScanPrice); // 4 scans
  const savingsAt5Scans = (singleScanPrice * 5) - weeklyPassPrice; // $3.96

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25 }}
            className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${className}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl border border-blue-500/30 shadow-2xl max-w-lg w-full overflow-hidden">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition z-10"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Content */}
              <div className="p-8">
                {/* Header */}
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Zap className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-2 font-display">
                    Your Edits Are Ready!
                  </h2>
                  <p className="text-gray-400">
                    See your new score now - choose the best option for you
                  </p>
                </div>

                {/* Comparison */}
                <div className="space-y-3 mb-6">
                  {/* Single Scan Option */}
                  <div className="bg-white/5 border border-white/10 rounded-lg p-4 hover:border-blue-500/30 transition cursor-pointer"
                       onClick={handleSingleScan}>
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="text-white font-semibold">Single Re-scan</h3>
                        <p className="text-gray-400 text-sm">One-time analysis</p>
                      </div>
                      <div className="text-right">
                        <p className="text-white font-bold text-xl">${singleScanPrice}</p>
                      </div>
                    </div>
                  </div>

                  {/* Weekly Pass Option - Recommended */}
                  <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border-2 border-blue-500/50 rounded-lg p-4 hover:border-blue-500 transition cursor-pointer relative"
                       onClick={handleWeeklyPass}>
                    <div className="absolute -top-2 left-4 px-2 py-0.5 bg-blue-500 rounded text-xs font-semibold text-white">
                      BEST VALUE
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="text-white font-semibold">7-Day Pass</h3>
                        <p className="text-gray-300 text-sm">Unlimited scans for 7 days</p>
                      </div>
                      <div className="text-right">
                        <p className="text-white font-bold text-xl">${weeklyPassPrice}</p>
                      </div>
                    </div>
                    {/* Savings Calculator */}
                    <div className="mt-3 pt-3 border-t border-blue-500/30">
                      <div className="flex items-center gap-2 text-xs text-blue-300">
                        <Calculator className="w-3.5 h-3.5" />
                        <span>Save ${savingsAt5Scans.toFixed(2)} if you scan 5+ times</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* CTA */}
                <ShimmerButton
                  onClick={handleWeeklyPass}
                  className="w-full mb-3"
                >
                  <div className="flex items-center justify-center gap-2">
                    <span>Get 7-Day Pass - ${weeklyPassPrice}</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </ShimmerButton>

                <button
                  onClick={handleSingleScan}
                  className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition"
                >
                  Just This Scan - ${singleScanPrice}
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default RescanUpsellModal;
