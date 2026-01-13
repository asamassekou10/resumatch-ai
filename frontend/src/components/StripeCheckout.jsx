import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle, AlertCircle, Shield } from 'lucide-react';

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
    icon: '⚡',
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
    icon: '⚡',
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
    icon: '👑',
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
      {/* Free Trial Information Banner */}
      <motion.div
        className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-start gap-3">
          <div className="text-3xl">🎉</div>
          <div className="flex-1">
            <h4 className="text-white font-semibold mb-2 text-lg">Start Your 7-Day Free Trial</h4>
            <p className="text-sm text-slate-300 mb-3">
              Get instant access to all Pro features with 10 credits. Your card won't be charged for 7 days.
            </p>
            <div className="flex flex-wrap gap-3 text-xs">
              <span className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 rounded-full text-green-300 border border-green-500/30">
                <CheckCircle className="w-3.5 h-3.5" />
                Cancel anytime
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 rounded-full text-green-300 border border-green-500/30">
                <CheckCircle className="w-3.5 h-3.5" />
                No charge during trial
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 rounded-full text-green-300 border border-green-500/30">
                <CheckCircle className="w-3.5 h-3.5" />
                One-click cancellation
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Order Summary */}
      <motion.div
        className="bg-slate-800 rounded-lg p-6 border border-slate-700"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Order Summary</h3>
          <span className="px-3 py-1 bg-green-500/20 text-green-300 text-xs font-semibold rounded-full border border-green-500/30">
            7-Day Free Trial
          </span>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-300">
              {tierInfo.name} Subscription
            </span>
            <span className="text-white font-semibold">
              ${tierInfo.price.toFixed(2)}/month
            </span>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-3 border border-green-500/20">
            <div className="flex justify-between items-center mb-1">
              <span className="text-green-300 text-sm font-medium">Trial Period</span>
              <span className="text-green-300 text-sm font-semibold">7 Days Free</span>
            </div>
            <div className="flex justify-between items-center text-xs text-slate-400 mt-1">
              <span>10 Credits Included</span>
              <span>First charge: {firstChargeDate}</span>
            </div>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Monthly Credits (after trial)</span>
            <span className="text-emerald-400 font-semibold">
              {tierInfo.credits} Credits
            </span>
          </div>
          <div className="border-t border-slate-700 pt-3 mt-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-white font-semibold">Today's Charge</span>
              <span className="text-2xl font-bold text-green-400">
                $0.00
              </span>
            </div>
            <p className="text-xs text-slate-500 text-right">
              After trial: ${tierInfo.price.toFixed(2)}/month
            </p>
          </div>
        </div>
      </motion.div>

      {/* Why Payment Method is Needed */}
      <motion.div
        className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <h4 className="text-white font-medium mb-2 text-sm flex items-center gap-2">
          <Lock className="w-4 h-4 text-blue-400" />
          Why do we need a payment method?
        </h4>
        <p className="text-slate-300 text-sm leading-relaxed">
          We require a payment method to start your free trial and unlock all features instantly. 
          Your card will <strong className="text-white">not be charged for 7 days</strong>, and you can 
          cancel anytime from your Settings page - even during the trial - with no charges.
        </p>
      </motion.div>

      {/* Payment Method */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <label className="block text-white font-semibold">Payment Method</label>
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
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
        className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-lg transition duration-200 flex flex-col items-center justify-center gap-1 shadow-lg shadow-green-500/20"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {isLoading ? (
          <>
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity }}
              className="flex items-center gap-2"
            >
              <Lock className="w-5 h-5" />
              <span>Processing...</span>
            </motion.span>
          </>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              <span className="text-lg">Start My 7-Day Free Trial</span>
            </div>
            <span className="text-xs opacity-90 font-normal">No charge for 7 days</span>
          </>
        )}
      </motion.button>

      {/* Enhanced Security Info */}
      <motion.div
        className="bg-slate-800/50 rounded-lg p-4 border border-slate-700"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-white font-medium text-sm mb-1">Your payment is secure</p>
            <p className="text-slate-400 text-xs mb-2 leading-relaxed">
              Powered by Stripe, the same secure payment system used by millions of companies worldwide. 
              Your card details are encrypted and never stored on our servers.
            </p>
            <div className="flex flex-wrap gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Lock className="w-3 h-3" />
                PCI DSS Compliant
              </span>
              <span className="flex items-center gap-1">
                <Lock className="w-3 h-3" />
                Bank-level Encryption
              </span>
              <span className="flex items-center gap-1">
                <Lock className="w-3 h-3" />
                256-bit SSL
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Cancellation Assurance */}
      <motion.div
        className="border-t border-slate-700 pt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-white font-medium text-sm mb-1">Cancel anytime, no questions asked</p>
            <p className="text-slate-400 text-xs leading-relaxed">
              You can cancel your subscription at any time from your Settings page. 
              If you cancel before your 7-day trial ends, you won't be charged anything. 
              Even if you cancel now, you'll still get the full 7 days of trial access.
            </p>
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
            ← Back to Pricing
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
            <div className={`bg-gradient-to-br ${tierInfo.color} rounded-lg p-8 text-white shadow-xl`}>
              <div className="text-5xl mb-4">{tierInfo.icon}</div>
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
                    <span className="text-xl mt-1">✓</span>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Billing Info */}
            <div className="bg-slate-800 rounded-lg p-6 mt-6 border border-slate-700">
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
                  <div className="animate-spin text-4xl mb-4">⏳</div>
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
