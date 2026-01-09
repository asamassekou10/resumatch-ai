import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Zap, TrendingUp, Crown, Sparkles } from 'lucide-react';
import ShimmerButton from './ShimmerButton';

/**
 * Upgrade Modal Component
 * Displayed when user runs out of credits or tries to access premium features
 */
const UpgradeModal = ({
  isOpen,
  onClose,
  creditsNeeded = 1,
  creditsAvailable = 0,
  feature = 'resume analysis',
  tier = 'free'
}) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleUpgrade = () => {
    navigate('/pricing');
    onClose();
  };

  const getTierRecommendation = () => {
    if (tier === 'free') {
      return {
        name: 'Starter',
        price: '$9.99/mo',
        credits: 15,
        icon: Sparkles,
        color: 'from-blue-500 to-cyan-500'
      };
    } else if (tier === 'starter') {
      return {
        name: 'Pro',
        price: '$24.99/mo',
        credits: 50,
        icon: Zap,
        color: 'from-blue-500 to-pink-500'
      };
    }
    return {
      name: 'Elite',
      price: '$49.99/mo',
      credits: 200,
      icon: Crown,
      color: 'from-yellow-500 to-orange-500'
    };
  };

  const recommendation = getTierRecommendation();
  const RecommendedIcon = recommendation.icon;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden"
        >
          {/* Header with gradient */}
          <div className={`bg-gradient-to-r ${recommendation.color} p-6 text-white`}>
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-white/20 rounded-xl">
                <RecommendedIcon className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Out of Credits</h2>
                <p className="text-white/90 text-sm">Upgrade to continue analyzing</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Credit status */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl mb-6">
              <div>
                <div className="text-sm text-gray-600 mb-1">Your Balance</div>
                <div className="text-2xl font-bold text-gray-900">
                  {creditsAvailable} {creditsAvailable === 1 ? 'Credit' : 'Credits'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Needed</div>
                <div className="text-2xl font-bold text-red-600">
                  {creditsNeeded} {creditsNeeded === 1 ? 'Credit' : 'Credits'}
                </div>
              </div>
            </div>

            {/* Message */}
            <p className="text-gray-700 mb-6">
              You need <span className="font-semibold">{creditsNeeded} credit{creditsNeeded !== 1 ? 's' : ''}</span> to perform {feature},
              but you only have <span className="font-semibold">{creditsAvailable}</span>.
            </p>

            {/* Recommended plan */}
            <div className="border-2 border-blue-200 rounded-xl p-4 mb-6 bg-blue-50/50">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-sm text-blue-600 font-semibold uppercase tracking-wide mb-1">
                    Recommended
                  </div>
                  <div className="text-xl font-bold text-gray-900">{recommendation.name} Plan</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">{recommendation.price}</div>
                  <div className="text-sm text-gray-600">per month</div>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Zap className="w-4 h-4 text-blue-600" />
                <span><strong>{recommendation.credits} credits/month</strong> - analyze {recommendation.credits} resumes</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
              >
                Maybe Later
              </button>
              <ShimmerButton
                onClick={handleUpgrade}
                className="flex-1 px-4 py-3"
              >
                <div className="flex items-center justify-center gap-2">
                  <span>View Plans</span>
                  <TrendingUp className="w-4 h-4" />
                </div>
              </ShimmerButton>
            </div>

            {/* Footer note */}
            <p className="text-xs text-gray-500 text-center mt-4">
              Credits reset monthly. Cancel anytime.
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default UpgradeModal;
