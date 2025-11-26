import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';

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
    color: 'from-cyan-500 to-purple-600',
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

  const tierInfo = TIER_INFO[tier];

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

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Order Summary */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">Order Summary</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-300">
              {tierInfo.name} Subscription
            </span>
            <span className="text-white font-semibold">
              ${tierInfo.price.toFixed(2)}/month
            </span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Monthly Credits</span>
            <span className="text-emerald-400 font-semibold">
              {tierInfo.credits} Credits
            </span>
          </div>
          <div className="border-t border-slate-700 pt-3 mt-3">
            <div className="flex justify-between items-center">
              <span className="text-white font-semibold">Total</span>
              <span className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
                ${tierInfo.price.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Method */}
      <div className="space-y-3">
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
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
          <p className="text-red-400 text-sm">{errorMessage}</p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !stripe || !elements}
        className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition duration-200 flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <span className="animate-spin">⏳</span>
            Processing...
          </>
        ) : (
          <>
            <span>🔒</span>
            Pay ${tierInfo.price.toFixed(2)}
          </>
        )}
      </button>

      {/* Security Info */}
      <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
        <span>🛡️</span>
        <p>Secure payment powered by Stripe. Your information is encrypted.</p>
      </div>
    </form>
  );
};

const StripeCheckout = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tier = searchParams.get('tier') || 'pro';
  const [stripePromise, setStripePromise] = useState(null);
  const [clientSecret, setClientSecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const token = localStorage.getItem('resume_analyzer_token');

  const tierInfo = TIER_INFO[tier];

  useEffect(() => {
    const initializeCheckout = async () => {
      try {
        // Get publishable key and client secret from backend
        const response = await fetch(
          `/api/payments/create-payment-intent?tier=${tier}`,
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
      const response = await fetch('/api/payments/confirm-subscription', {
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
            Upgrade to {tierInfo.name}
          </h1>
          <p className="text-slate-400">{tierInfo.description}</p>
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
