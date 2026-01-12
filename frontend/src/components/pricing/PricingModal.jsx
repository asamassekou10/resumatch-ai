import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, Zap, Clock, Sparkles, TrendingUp, Shield, Users } from 'lucide-react';

/**
 * PricingModal Component
 *
 * Modal that displays pricing tiers with urgency and social proof elements.
 * Drives conversion by highlighting value and creating FOMO.
 *
 * Props:
 * - isOpen: Boolean to control modal visibility
 * - onClose: Callback to close modal
 * - onSelectPlan: Callback when user selects a plan (plan object)
 * - upgradeOptions: Array of pricing options from API
 * - userEmail: Optional user email for personalization
 * - creditsRemaining: Optional credits count for urgency messaging
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
  const [timeLeft, setTimeLeft] = useState({ minutes: 14, seconds: 59 });

  // Countdown timer for urgency (resets every time modal opens)
  useEffect(() => {
    if (!isOpen) return;

    // Reset timer when modal opens
    setTimeLeft({ minutes: 14, seconds: 59 });

    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { minutes: prev.minutes - 1, seconds: 59 };
        }
        return prev;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen]);

  // Find plan types
  const singleScan = upgradeOptions.find(opt => opt.type === 'single_rescan');
  const weeklyPass = upgradeOptions.find(opt => opt.type === 'weekly_pass');
  const monthlyPro = upgradeOptions.find(opt => opt.type === 'monthly_pro');

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    onSelectPlan(plan);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-4xl bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl border border-cyan-500/20 shadow-2xl overflow-hidden"
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
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-blue-500/5 to-purple-500/5" />

            <div className="relative">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="inline-block mb-4"
              >
                <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-3 rounded-full">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
              </motion.div>

              <h2 className="text-3xl font-bold text-white mb-2">
                Unlock Your Full Resume Potential
              </h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                {creditsRemaining === 0
                  ? "You've used your free scan. Choose a plan to continue optimizing your resume and land more interviews."
                  : "Get instant access to AI recommendations, missing keywords, and ATS optimization tips."}
              </p>

              {/* Urgency Timer */}
              <motion.div
                animate={{ scale: [1, 1.02, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-full"
              >
                <Clock className="w-4 h-4 text-red-400" />
                <span className="text-red-400 text-sm font-semibold">
                  Special offer expires in {timeLeft.minutes}:{timeLeft.seconds.toString().padStart(2, '0')}
                </span>
              </motion.div>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Single Re-scan */}
              {singleScan && (
                <motion.div
                  whileHover={{ y: -4 }}
                  className={`relative bg-white/5 border ${
                    selectedPlan?.type === 'single_rescan'
                      ? 'border-cyan-500 shadow-lg shadow-cyan-500/20'
                      : 'border-white/10'
                  } rounded-xl p-6 cursor-pointer transition-all`}
                  onClick={() => handleSelectPlan(singleScan)}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <h3 className="text-lg font-bold text-white">Quick Unlock</h3>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-white">${singleScan.price}</span>
                      <span className="text-gray-500 text-sm">one-time</span>
                    </div>
                    <p className="text-gray-400 text-sm mt-2">{singleScan.description}</p>
                  </div>

                  <ul className="space-y-3 mb-6">
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>Unlock current analysis results</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>All missing keywords revealed</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>AI recommendations included</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-400">
                      <X className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
                      <span>Single use only</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSelectPlan(singleScan)}
                    className="w-full py-3 bg-white/10 hover:bg-white/20 border border-cyan-500/30 rounded-lg text-white font-semibold transition-all"
                  >
                    Select Plan
                  </button>

                  <p className="text-center text-xs text-gray-500 mt-3">Perfect for one-time use</p>
                </motion.div>
              )}

              {/* Weekly Pass - Recommended */}
              {weeklyPass && (
                <motion.div
                  whileHover={{ y: -4 }}
                  className={`relative bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-2 ${
                    selectedPlan?.type === 'weekly_pass'
                      ? 'border-cyan-400 shadow-xl shadow-cyan-500/30'
                      : 'border-cyan-500/50'
                  } rounded-xl p-6 cursor-pointer transition-all`}
                  onClick={() => handleSelectPlan(weeklyPass)}
                >
                  {/* Best Value Badge */}
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-orange-400 text-black text-xs font-bold px-4 py-1 rounded-full flex items-center gap-1 shadow-lg">
                    <Sparkles className="w-3 h-3" />
                    MOST POPULAR
                  </div>

                  <div className="flex items-center gap-2 mb-4 mt-2">
                    <TrendingUp className="w-5 h-5 text-cyan-400" />
                    <h3 className="text-lg font-bold text-white">7-Day Pass</h3>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-cyan-400">${weeklyPass.price}</span>
                      <span className="text-gray-400 text-sm">for 7 days</span>
                    </div>
                    <p className="text-gray-300 text-sm mt-2 font-medium">{weeklyPass.description}</p>
                    <div className="inline-block bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded mt-2">
                      Save ${((singleScan?.price || 0) * 3 - weeklyPass.price).toFixed(2)} vs 3 single scans
                    </div>
                  </div>

                  <ul className="space-y-3 mb-6">
                    <li className="flex items-start gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span className="font-medium">Unlimited scans for 7 days</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span className="font-medium">All keywords & recommendations</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span className="font-medium">Perfect for job hunting</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span className="font-medium">Test multiple resumes</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSelectPlan(weeklyPass)}
                    className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg text-white font-bold transition-all shadow-lg shadow-cyan-500/30"
                  >
                    Get Started Now
                  </button>

                  <p className="text-center text-xs text-cyan-400 mt-3 font-medium">Best value for job seekers</p>
                </motion.div>
              )}

              {/* Monthly Pro */}
              {monthlyPro && (
                <motion.div
                  whileHover={{ y: -4 }}
                  className={`relative bg-white/5 border ${
                    selectedPlan?.type === 'monthly_pro'
                      ? 'border-purple-500 shadow-lg shadow-purple-500/20'
                      : 'border-white/10'
                  } rounded-xl p-6 cursor-pointer transition-all`}
                  onClick={() => handleSelectPlan(monthlyPro)}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-purple-400" />
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
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>Unlimited scans forever</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>Premium resume templates</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>Priority AI processing</span>
                    </li>
                    <li className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>Cover letter generator</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSelectPlan(monthlyPro)}
                    className="w-full py-3 bg-white/10 hover:bg-white/20 border border-purple-500/30 rounded-lg text-white font-semibold transition-all"
                  >
                    Select Plan
                  </button>

                  <p className="text-center text-xs text-gray-500 mt-3">For serious job seekers</p>
                </motion.div>
              )}
            </div>

            {/* Social Proof */}
            <div className="mt-8 pt-6 border-t border-white/10">
              <div className="flex items-center justify-center gap-8 text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-cyan-400" />
                  <span>2,847 users upgraded today</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-green-400" />
                  <span>Secure payment by Stripe</span>
                </div>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-yellow-400" />
                  <span>Money-back guarantee</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PricingModal;
