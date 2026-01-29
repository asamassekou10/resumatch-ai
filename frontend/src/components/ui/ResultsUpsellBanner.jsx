import React from 'react';
import { motion } from 'framer-motion';
import { Lock, ArrowRight, CheckCircle, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';
import { trackUpgradeClicked } from '../../utils/conversionTracking';

/**
 * ResultsUpsellBanner Component
 * Shows upsell banner after analysis results with comparison and benefits
 */
const ResultsUpsellBanner = ({ 
  visibleKeywords = 3, 
  totalKeywords = 12,
  className = '' 
}) => {
  const navigate = useNavigate();

  const handleUpgrade = () => {
    trackUpgradeClicked('results_upsell_banner', 'weekly_pass');
    // For weekly_pass, use payment modal instead of checkout (it's a micro-purchase)
    // Navigate to pricing page where they can purchase
    navigate(`${ROUTES.PRICING}?highlight=weekly_pass`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-500/20 via-blue-600/20 to-cyan-500/20 backdrop-blur-sm border border-blue-500/30 ${className}`}
    >
      <div className="p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Left Content */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Lock className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-1">
                  Unlock Full Analysis
                </h3>
                <p className="text-sm text-gray-300">
                  You're seeing {visibleKeywords} of {totalKeywords} missing keywords. Unlock all for $6.99
                </p>
              </div>
            </div>

            {/* Comparison */}
            <div className="bg-white/5 rounded-lg p-3 mt-3 mb-3">
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-gray-400 mb-1">Free Preview</p>
                  <p className="text-gray-300 font-semibold">{visibleKeywords} keywords shown</p>
                </div>
                <div className="border-l border-white/10 pl-3">
                  <p className="text-blue-400 mb-1">Full Analysis</p>
                  <p className="text-white font-semibold">All {totalKeywords} keywords + insights</p>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="flex flex-wrap gap-3">
              <div className="flex items-center gap-2 text-xs text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-blue-400" />
                <span>All {totalKeywords} missing keywords</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-blue-400" />
                <span>AI optimization tips</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-blue-400" />
                <span>7 days unlimited scans</span>
              </div>
            </div>

            {/* Testimonial Snippet */}
            <div className="mt-3 pt-3 border-t border-white/10">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                <span className="italic">"Sarah improved her score from 65% to 92%"</span>
              </div>
            </div>
          </div>

          {/* Right CTA */}
          <div className="flex-shrink-0 flex flex-col items-end gap-2">
            <div className="text-right mb-2">
              <p className="text-xs text-gray-400 mb-1">Most Popular</p>
              <p className="text-sm text-cyan-400 font-semibold">Best Value</p>
            </div>
            <ShimmerButton
              onClick={handleUpgrade}
              className="w-full md:w-auto"
            >
              <div className="flex items-center gap-2">
                <span>Unlock for $6.99</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </ShimmerButton>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ResultsUpsellBanner;
