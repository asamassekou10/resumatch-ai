import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';
import ShimmerButton from './ShimmerButton';

/**
 * Trial Offer Banner Component
 * Displays 30-day mega trial offer to users who have used their free credits
 */
const TrialOfferBanner = ({ credits = 0, onStartTrial, className = '' }) => {

  // Only show when user has 3 or fewer credits left
  if (credits > 3) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 via-pink-500 to-rose-500 p-1 ${className}`}
    >
      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />

      <div className="relative bg-white rounded-xl p-6">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="flex-shrink-0">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-pink-500 rounded-xl">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
          </div>

          {/* Content */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🎉</span>
              <h3 className="text-xl font-bold text-gray-900">
                Special Launch Offer!
              </h3>
            </div>

            <p className="text-gray-700 mb-1">
              <strong>Try Pro FREE for 30 days</strong> with 30 analyses
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Experience all Pro features risk-free. No credit card required. Cancel anytime.
            </p>

            {/* Benefits */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Zap className="w-4 h-4 text-blue-600" />
                <span>AI-powered optimization</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Zap className="w-4 h-4 text-blue-600" />
                <span>Cover letter generation</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Zap className="w-4 h-4 text-blue-600" />
                <span>Priority support</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Zap className="w-4 h-4 text-blue-600" />
                <span>Unlimited templates</span>
              </div>
            </div>

            {/* CTA Button */}
            <ShimmerButton
              onClick={onStartTrial}
              className="w-full sm:w-auto"
            >
              <div className="flex items-center justify-center gap-2">
                <span>Start Free 30-Day Trial</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </ShimmerButton>

            <p className="text-xs text-gray-500 mt-2">
              After trial: $19.99/month as Founding Member (limited spots) or $24.99/month regular
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TrialOfferBanner;
