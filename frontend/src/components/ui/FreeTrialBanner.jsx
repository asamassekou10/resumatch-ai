import React, { useState } from 'react';
import { X, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../config/routes';

/**
 * Free Trial Banner Component
 *
 * Dismissible announcement banner for 7-day free trial promotion
 * Displays at top of landing page with eye-catching gradient design
 */
const FreeTrialBanner = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="relative z-50 bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 text-white">
      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <Sparkles className="w-5 h-5 flex-shrink-0 text-yellow-300" />
            <p className="text-sm sm:text-base font-medium">
              <span className="font-bold">New! 7-Day Free Trial</span>
              <span className="hidden sm:inline"> - Get unlimited resume analyses, AI insights, and premium features</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to={ROUTES.REGISTER}
              className="px-4 py-1.5 bg-white text-purple-600 font-bold text-sm rounded-full hover:bg-gray-100 transition-colors flex-shrink-0"
            >
              Start Free Trial
            </Link>
            <button
              onClick={() => setIsVisible(false)}
              className="p-1 hover:bg-white/10 rounded-full transition-colors flex-shrink-0"
              aria-label="Dismiss banner"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FreeTrialBanner;
