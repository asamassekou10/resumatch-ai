import React, { useState } from 'react';
import { X, Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../config/routes';

/**
 * Free Trial Banner Component
 *
 * Dismissible announcement banner for 7-day free trial promotion
 * Professional design with subtle styling
 */
const FreeTrialBanner = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="relative z-50 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-white/10 text-white">
      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
              <span className="text-sm sm:text-base font-bold text-white">
                Try Premium Free for 7 Days
              </span>
              <span className="text-xs sm:text-sm text-gray-300">
                Unlimited analyses • AI insights • 100% free for 7 days
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to={ROUTES.PRICING}
              className="group px-5 py-2 bg-white text-slate-900 font-semibold text-sm rounded-lg hover:bg-gray-100 transition-all flex items-center gap-2 flex-shrink-0 shadow-lg hover:shadow-xl"
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <button
              onClick={() => setIsVisible(false)}
              className="p-1.5 hover:bg-white/10 rounded-lg transition-colors flex-shrink-0"
              aria-label="Dismiss banner"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FreeTrialBanner;
