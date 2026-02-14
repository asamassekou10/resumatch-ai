import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight, Sparkles, Crown, CheckCircle } from 'lucide-react';
import axios from 'axios';
import ShimmerButton from './ShimmerButton';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * UpsellModal Component
 *
 * Shows after successful 7-Day Pass purchase
 * Offers one-click upgrade to Pro plan with saved payment method
 *
 * @param {boolean} isOpen - Whether modal is visible
 * @param {Function} onClose - Close callback
 * @param {string} currentPlan - User's current plan ('weekly_pass')
 * @param {string} token - Auth token
 */
const UpsellModal = ({ isOpen, onClose, currentPlan = 'weekly_pass', token }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (currentPlan !== 'weekly_pass') {
    return null; // Only show for 7-Day Pass purchases
  }

  const upsellOffer = {
    from: '7-Day Pass',
    to: 'Pro Founding Member',
    originalPrice: 19.99,
    alreadyPaid: 6.99,
    upgradePrice: 13.00, // $19.99 - $6.99
    savings: 5.00, // Pro normally costs $24.99, they're getting it for $19.99
    features: [
      '50 analyses per month',
      'Cover letter generation',
      'Unlimited resume templates',
      'Priority support',
      'Founding member badge',
      'Locked-in pricing forever'
    ]
  };

  const handleUpgrade = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${API_URL}/payments/create-checkout-session?tier=pro_founding`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      console.error('Upsell upgrade error:', err);
      setError('Failed to start upgrade. Please try again.');
      setLoading(false);
    }
  };

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
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
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
                {/* Badge */}
                <div className="flex items-center justify-center mb-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30">
                    <Crown className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-semibold text-amber-300">Exclusive Offer</span>
                  </div>
                </div>

                {/* Heading */}
                <h2 className="text-2xl font-bold text-white text-center mb-2 font-display">
                  Upgrade to Pro Founding Member
                </h2>
                <p className="text-center text-gray-400 text-sm mb-6">
                  Limited spots available - Lock in $19.99/mo forever
                </p>

                {/* Price Breakdown */}
                <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-5 mb-6">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">You already paid:</span>
                      <span className="text-white font-semibold">${upsellOffer.alreadyPaid.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Pro Founding Member:</span>
                      <span className="text-white font-semibold">${upsellOffer.originalPrice.toFixed(2)}/mo</span>
                    </div>
                    <div className="border-t border-white/10 pt-3 flex items-center justify-between">
                      <span className="text-white font-bold">Upgrade today for only:</span>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-cyan-400">${upsellOffer.upgradePrice.toFixed(2)}</div>
                        <div className="text-xs text-green-400">Save ${upsellOffer.savings.toFixed(2)}/mo</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">What You Get:</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {upsellOffer.features.map((feature, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Urgency */}
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 mb-6">
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-semibold text-amber-300 mb-1">Founding Member Special</p>
                      <p className="text-xs text-gray-400">
                        Only 23 spots left at $19.99/mo. After 100 members, price increases to $24.99/mo.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <p className="text-red-400 text-sm text-center">{error}</p>
                  </div>
                )}

                {/* CTAs */}
                <div className="space-y-3">
                  <ShimmerButton
                    onClick={handleUpgrade}
                    disabled={loading}
                    className="w-full"
                  >
                    <div className="flex items-center justify-center gap-2">
                      {loading ? (
                        <span>Processing...</span>
                      ) : (
                        <>
                          <span>Upgrade for ${upsellOffer.upgradePrice.toFixed(2)}</span>
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </div>
                  </ShimmerButton>

                  <button
                    onClick={onClose}
                    disabled={loading}
                    className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition"
                  >
                    Maybe Later
                  </button>
                </div>

                {/* Trust signal */}
                <p className="text-xs text-center text-gray-500 mt-4">
                  One-time payment using your saved payment method. Cancel anytime.
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpsellModal;
