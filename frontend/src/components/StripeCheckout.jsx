import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle, AlertCircle, Shield, Zap, Crown, Loader2, Gift, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Tier information
const TIER_INFO = {
  pro: {
    name: 'Pro',
    price: 9.99,
    credits: 100,
    description: 'Perfect for active job seekers',
    features: [
      '100 AI Credits/month',
      'Resume Analysis & Optimization',
      'Job Match Scoring',
      'Skills Gap Analysis',
      'Priority Support',
    ],
    color: 'from-cyan-500 to-blue-600',
    icon: Zap,
  },
  pro_founding: {
    name: 'Pro Founding Member',
    price: 19.99,
    credits: 50,
    description: 'Lock in $19.99 forever',
    features: [
      '50 AI Credits/month',
      'Resume Analysis & Optimization',
      'Job Match Scoring',
      'Skills Gap Analysis',
      'Priority Support',
      'Founding Member Badge',
      'Price locked forever',
    ],
    color: 'from-cyan-500 to-blue-600',
    icon: Zap,
  },
  elite: {
    name: 'Elite',
    price: 49.99,
    credits: 1000,
    description: 'For power users',
    features: [
      '1000 AI Credits/month',
      'Everything in Pro',
      'Unlimited Analyses',
      'Cover Letter Generation',
      '24/7 Priority Support',
      'Custom Feedback',
    ],
    color: 'from-amber-500 to-orange-600',
    icon: Crown,
  },
};

const CheckoutForm = ({ tier, clientSecret, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const tierInfo = TIER_INFO[tier] || TIER_INFO.pro;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      // Confirm the setup intent with payment element
      const { error } = await stripe.confirmSetup({
        elements,
        clientSecret,
        confirm: true,
        redirect: 'if_required',
      });

      if (error) {
        setErrorMessage(error.message || 'Payment failed. Please try again.');
        onError(error.message);
      } else {
        onSuccess();
      }
    } catch (err) {
      setErrorMessage('An unexpected error occurred. Please try again.');
      onError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate trial end date (7 days from now)
  const trialEndDate = new Date();
  trialEndDate.setDate(trialEndDate.getDate() + 7);
  const firstChargeDate = trialEndDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Simplified Trial Banner */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 flex items-center justify-center">
            <Gift className="w-5 h-5 text-green-400" />
          </div>
          <div className="flex-1">
            <h4 className="text-white font-semibold text-base">7-Day Free Trial</h4>
            <p className="text-sm text-slate-400">
              No charge for 7 days • Cancel anytime
            </p>
          </div>
        </div>
      </motion.div>

      {/* Simplified Order Summary */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-lg font-semibold text-white mb-4">Order Summary</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <span className="text-slate-300">{tierInfo.name}</span>
            <span className="text-white font-semibold">${tierInfo.price.toFixed(2)}/month</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Trial Period</span>
            <span className="text-green-400 font-medium">7 days free</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Trial Credits</span>
            <span className="text-white font-medium">10 credits</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Monthly Credits</span>
            <span className="text-white font-medium">{tierInfo.credits} credits</span>
          </div>
          <div className="pt-3 mt-3 border-t border-white/10">
            <div className="flex justify-between items-center">
              <span className="text-white font-semibold">Today's Charge</span>
              <span className="text-2xl font-bold text-green-400">$0.00</span>
            </div>
            <p className="text-xs text-slate-500 text-right mt-1">
              First charge: {firstChargeDate}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Payment Method */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <label className="block text-white font-semibold">Payment Method</label>
        <div className="bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10">
          <PaymentElement
            options={{
              layout: 'tabs',
              defaultValues: {
                billingDetails: {
                  name: '',
                  email: '',
                  phone: '',
                  address: {
                    country: 'US',
                  },
                },
              },
            }}
          />
        </div>
      </motion.div>

      {/* Error Message */}
      <AnimatePresence>
        {errorMessage && (
          <motion.div
            className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start gap-3"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-400 text-sm">{errorMessage}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Submit Button */}
      <motion.button
        type="submit"
        disabled={isLoading || !stripe || !elements}
        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl transition duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
        whileHover={{ scale: isLoading ? 1 : 1.02 }}
        whileTap={{ scale: isLoading ? 1 : 0.98 }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Processing...</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-5 h-5" />
            <span className="text-lg">Start My 7-Day Free Trial</span>
          </>
        )}
      </motion.button>

      {/* Consolidated Trust & Security Info */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl rounded-xl p-4 border border-white/10"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1 space-y-2">
            <p className="text-white font-medium text-sm">Secure & Cancel Anytime</p>
            <p className="text-slate-400 text-xs leading-relaxed">
              Your payment is secured by Stripe. Cancel anytime from Settings - no charges if canceled before trial ends.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-slate-500 pt-1">
              <span className="flex items-center gap-1.5">
                <Lock className="w-3 h-3" />
                PCI DSS Compliant
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3" />
                Cancel Anytime
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </form>
  );
};

const StripeCheckout = ({ token, navigate: parentNavigate }) => {
  const [searchParams] = useSearchParams();
  const routerNavigate = useNavigate();
  // Use passed navigate from props, fall back to router navigate if needed
  const navigate = parentNavigate || routerNavigate;
  const tier = searchParams.get('tier') || 'pro';
  const [stripePromise, setStripePromise] = useState(null);
  const [clientSecret, setClientSecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const tierInfo = TIER_INFO[tier] || TIER_INFO.pro;

  useEffect(() => {
    const initializeCheckout = async () => {
      try {
        // Get publishable key and client secret from backend
        const response = await fetch(
          `${API_URL}/payments/create-payment-intent?tier=${tier}`,
          {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to initialize checkout');
        }

        const data = await response.json();
        setClientSecret(data.client_secret);

        // Load Stripe
        if (data.publishable_key) {
          const stripe = await loadStripe(data.publishable_key);
          setStripePromise(stripe);
        }
      } catch (err) {
        setError(err.message || 'Failed to load checkout');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      initializeCheckout();
    } else {
      navigate('/login');
    }
  }, [tier, token, navigate]);

  const handlePaymentSuccess = async () => {
    // Create the subscription with the saved payment method
    try {
      const response = await fetch(`${API_URL}/payments/confirm-subscription`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tier }),
      });

      if (response.ok) {
        navigate('/dashboard?payment=success');
      } else {
        setError('Failed to confirm subscription');
      }
    } catch (err) {
      setError('Failed to process subscription');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <button
            onClick={() => navigate('/pricing')}
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Pricing
          </button>
          <h1 className="text-4xl font-bold text-white mb-2">
            Start Your 7-Day Free Trial
          </h1>
          <p className="text-slate-400 text-lg">
            Try {tierInfo.name} free for 7 days • No charge during trial • Cancel anytime
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Tier Details */}
          <div className="lg:col-span-1">
            <div className={`bg-gradient-to-br ${tierInfo.color} rounded-xl p-8 text-white shadow-xl`}>
              <div className="mb-4">
                <IconComponent className="w-12 h-12" />
              </div>
              <h2 className="text-3xl font-bold mb-2">{tierInfo.name}</h2>
              <div className="mb-6">
                <span className="text-5xl font-bold">${tierInfo.price.toFixed(2)}</span>
                <span className="text-sm ml-2 opacity-90">/month</span>
              </div>

              <div className="bg-white/10 rounded-lg p-4 mb-6">
                <p className="text-center text-lg font-semibold">
                  {tierInfo.credits} Credits
                </p>
                <p className="text-center text-xs opacity-90 mt-1">
                  per month
                </p>
              </div>

              <ul className="space-y-3">
                {tierInfo.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Billing Info */}
            <div className="bg-white/5 backdrop-blur-xl rounded-xl p-6 mt-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4">Billing Details</h3>
              <div className="space-y-2 text-sm text-slate-400">
                <p>• Charged monthly on the same date</p>
                <p>• Cancel anytime from settings</p>
                <p>• 30-day money-back guarantee</p>
              </div>
            </div>
          </div>

          {/* Right: Checkout Form */}
          <div className="lg:col-span-2">
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <Loader2 className="w-12 h-12 animate-spin text-cyan-400 mx-auto mb-4" />
                  <p className="text-slate-400">Loading checkout...</p>
                </div>
              </div>
            ) : error ? (
              <div className="bg-red-900/20 border border-red-700 rounded-lg p-6">
                <h3 className="text-red-400 font-semibold mb-2">Checkout Error</h3>
                <p className="text-red-300 text-sm">{error}</p>
                <button
                  onClick={() => navigate('/pricing')}
                  className="mt-4 text-red-400 hover:text-red-300 text-sm font-semibold"
                >
                  Back to Pricing
                </button>
              </div>
            ) : stripePromise && clientSecret ? (
              <Elements stripe={stripePromise} options={{ clientSecret }}>
                <CheckoutForm
                  tier={tier}
                  clientSecret={clientSecret}
                  onSuccess={handlePaymentSuccess}
                  onError={(msg) => setError(msg)}
                />
              </Elements>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StripeCheckout;
