import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, TrendingUp, Shield, Lock } from 'lucide-react';

/**
 * PricingModal Component
 *
 * Modal that displays pricing tiers.
 *
 * Props:
 * - isOpen: Boolean to control modal visibility
 * - onClose: Callback to close modal
 * - onSelectPlan: Callback when user selects a plan (plan object)
 * - upgradeOptions: Array of pricing options from API
 * - userEmail: Optional user email for personalization
 * - creditsRemaining: Optional credits count for messaging
 */
const PricingModal = ({
  isOpen,
  onClose,
  onSelectPlan,
  upgradeOptions = [],
  userEmail,
  creditsRemaining = 0
}) => {
  const [selectedPlan, setSelectedPlan] = useState(null);

  // Find plan types
  const weeklyPass = upgradeOptions.find(opt => opt.type === 'weekly_pass');
  const monthlyPro = upgradeOptions.find(opt => opt.type === 'monthly_pro');

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    onSelectPlan(plan);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 backdrop-blur-sm" onClick={onClose}>
        <div className="min-h-screen px-4 py-8 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-4xl bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 rounded-2xl border border-white/10 shadow-2xl"
          >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>

          {/* Header Section */}
          <div className="relative p-8 text-center border-b border-white/10">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">
              Unlock Full Resume Analysis
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              {creditsRemaining === 0
                ? "You've used your free scan. Choose a plan to continue optimizing your resume."
                : "Get full access to AI recommendations, missing keywords, and ATS optimization tips."}
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
              {/* Weekly Pass - Recommended */}
              {weeklyPass && (
                <motion.div
                  whileHover={{ y: -2 }}
                  transition={{ duration: 0.15 }}
                  className={`relative bg-blue-500/5 border-2 ${
                    selectedPlan?.type === 'weekly_pass'
                      ? 'border-blue-400 shadow-lg shadow-blue-500/20'
                      : 'border-blue-500/30'
                  } rounded-xl p-6 cursor-pointer transition-all`}
                  onClick={() => handleSelectPlan(weeklyPass)}
                >
                  {/* Recommended Badge */}
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-semibold px-4 py-1 rounded-full shadow-md">
                    RECOMMENDED
                  </div>

                  <div className="flex items-center gap-2 mb-4 mt-2">
                    <TrendingUp className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-bold text-white">7-Day Pass</h3>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-white">${weeklyPass.price}</span>
                      <span className="text-gray-400 text-sm">for 7 days</span>
                    </div>
                    <p className="text-gray-300 text-sm mt-2">{weeklyPass.description}</p>
                  </div>

                  <ul className="space-y-3 mb-6">
                    <li className="flex items-start gap-2 text-sm text-gray-200">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Unlimited scans for 7 days</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-200">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>All keywords & recommendations</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-200">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>AI-optimized resume & cover letter</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-200">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Test multiple resumes</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSelectPlan(weeklyPass)}
                    className="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-400 hover:to-blue-500 rounded-lg text-white font-bold transition-all"
                  >
                    Get 7-Day Pass
                  </button>
                </motion.div>
              )}

              {/* Monthly Pro */}
              {monthlyPro && (
                <motion.div
                  whileHover={{ y: -2 }}
                  transition={{ duration: 0.15 }}
                  className={`relative bg-white/5 border ${
                    selectedPlan?.type === 'monthly_pro'
                      ? 'border-blue-400 shadow-lg shadow-blue-500/10'
                      : 'border-white/10'
                  } rounded-xl p-6 cursor-pointer transition-all`}
                  onClick={() => handleSelectPlan(monthlyPro)}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-bold text-white">Pro Plan</h3>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-white">${monthlyPro.price}</span>
                      <span className="text-gray-500 text-sm">/month</span>
                    </div>
                    <p className="text-gray-400 text-sm mt-2">{monthlyPro.description}</p>
                  </div>

                  <ul className="space-y-3 mb-6">
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Unlimited scans forever</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Premium resume templates</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Priority AI processing</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>Cover letter generator</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSelectPlan(monthlyPro)}
                    className="w-full py-3 bg-white/10 hover:bg-white/15 border border-white/10 rounded-lg text-white font-semibold transition-all"
                  >
                    Select Plan
                  </button>
                </motion.div>
              )}
            </div>

            {/* Trust Signals */}
            <div className="mt-8 pt-6 border-t border-white/10">
              <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-gray-500" />
                  <span>Secure payment by Stripe</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-gray-500" />
                  <span>Cancel anytime</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
};

export default PricingModal;
