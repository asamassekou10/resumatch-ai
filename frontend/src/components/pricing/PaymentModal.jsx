import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CreditCard, Lock, AlertCircle, CheckCircle, Loader, Mail, User } from 'lucide-react';
import InlineLoginForm from './InlineLoginForm';
import { trackPaymentModalOpened, trackCheckoutStarted } from '../../utils/conversionTracking';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * GuestPaymentForm Component (Internal)
 *
 * Handles guest checkout for micro-purchases (no account required)
 */
const GuestPaymentForm = ({ selectedPlan, guestToken, onSuccess, onError, onClose }) => {

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleEmailChange = (e) => {
    const value = e.target.value.trim().toLowerCase();
    setEmail(value);
    if (value && !validateEmail(value)) {
      setEmailError('Please enter a valid email address');
    } else {
      setEmailError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !validateEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    setProcessing(true);
    setError(null);
    setEmailError('');

    try {
      // Create Stripe Checkout Session for guest
      const payload = {
        email: email,
        purchase_type: selectedPlan.type
      };
      if (guestToken) {
        payload.guest_token = guestToken;
      }

      const response = await fetch(`${API_URL}/payments/create-micro-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...payload
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to create checkout');
      }

      if (data.checkout_url) {
        // Track checkout started
        trackCheckoutStarted(selectedPlan.type, selectedPlan.price);
        
        // Clear abandoned cart tracking (if authenticated)
        const authToken = localStorage.getItem('token');
        if (authToken) {
          fetch(`${API_URL}/analytics/clear-abandoned-cart`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${authToken}`
            }
          }).catch(err => console.warn('Failed to clear abandoned cart:', err));
        }
        
        // Redirect to Stripe's hosted checkout page
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (err) {
      console.error('Payment error:', err);
      setError(err.message || 'Payment failed. Please try again.');
      setProcessing(false);
      onError(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
        <div className="flex-1 flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold">1</div>
          <span className="text-gray-300">Payment Details</span>
        </div>
        <div className="w-8 h-px bg-gray-600" />
        <div className="flex-1 flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gray-600 text-gray-400 flex items-center justify-center text-xs">2</div>
          <span>Complete</span>
        </div>
      </div>

      {/* Plan Summary */}
      <div className="bg-white/5 border border-cyan-500/20 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">Selected Plan</span>
          <span className="text-white font-bold text-lg">${selectedPlan.price}</span>
        </div>
        <p className="text-gray-300 text-sm">{selectedPlan.description}</p>
        {selectedPlan.type === 'weekly_pass' && (
          <div className="mt-2 text-xs text-cyan-400">
            Unlimited scans for 7 days starting now
          </div>
        )}
        <div className="mt-2 flex items-center gap-2 text-xs text-cyan-400">
          <User className="w-3 h-3" />
          <span>Pay as guest - No account required</span>
        </div>
      </div>

      {/* Email Input */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Email Address <span className="text-red-400">*</span>
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="email"
            value={email}
            onChange={handleEmailChange}
            placeholder="your@email.com"
            className={`w-full pl-10 pr-4 py-3 bg-white/5 border ${
              emailError ? 'border-red-500' : 'border-white/10'
            } rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors`}
            required
          />
        </div>
        {emailError && (
          <p className="mt-1 text-xs text-red-400">{emailError}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          We'll send your receipt and results to this email. You'll be redirected to Stripe's secure checkout page.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
        >
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-400 text-sm">{error}</p>
        </motion.div>
      )}

      {/* Trust Signals */}
      <div className="grid grid-cols-3 gap-2 py-3 border-t border-white/10">
        <div className="flex flex-col items-center gap-1">
          <Lock className="w-5 h-5 text-cyan-400" />
          <p className="text-xs text-gray-400 text-center">256-bit SSL</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <p className="text-xs text-gray-400 text-center">Stripe Secured</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <CreditCard className="w-5 h-5 text-blue-400" />
          <p className="text-xs text-gray-400 text-center">PCI Compliant</p>
        </div>
      </div>

      {/* Security Notice */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Lock className="w-4 h-4" />
        <span>Secured by Stripe. Your payment info is encrypted and secure.</span>
      </div>

      {/* What Happens Next */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="text-white font-semibold text-sm mb-2">What happens next:</h4>
        <ul className="space-y-1.5 text-xs text-gray-300">
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>You'll be redirected to Stripe's secure checkout</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>Complete payment with any major credit card</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>Get instant access to unlimited scans for 7 days</span>
          </li>
        </ul>
      </div>

      {/* Value Reminder */}
      {selectedPlan.type === 'weekly_pass' && (
        <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-lg p-3 text-center">
          <p className="text-sm text-cyan-300 font-semibold">
            You're getting unlimited scans for 7 days - perfect for active job hunting!
          </p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onClose}
          disabled={processing}
          className="flex-1 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={processing || !email || emailError}
          className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {processing ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <CreditCard className="w-5 h-5" />
              Pay ${selectedPlan.price}
            </>
          )}
        </button>
      </div>

      {/* Money-back guarantee */}
      <p className="text-center text-xs text-gray-500">
        <span className="font-semibold text-green-400">7-day money-back guarantee</span> - If you're not satisfied, contact support for a full refund
      </p>
    </form>
  );
};

/**
 * PaymentForm Component (Internal)
 *
 * Handles Stripe checkout session creation for authenticated users.
 * Redirects to Stripe's hosted checkout page.
 */
const PaymentForm = ({ selectedPlan, onSuccess, onError, onClose }) => {
  const token = localStorage.getItem('token');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token) {
      setError('Please log in to continue.');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      // Create Stripe Checkout Session for authenticated user
      const response = await fetch(`${API_URL}/payments/create-micro-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          purchase_type: selectedPlan.type
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to create checkout');
      }

      if (data.checkout_url) {
        // Track checkout started
        trackCheckoutStarted(selectedPlan.type, selectedPlan.price);
        
        // Clear abandoned cart tracking (if authenticated)
        const authToken = localStorage.getItem('token');
        if (authToken) {
          fetch(`${API_URL}/analytics/clear-abandoned-cart`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${authToken}`
            }
          }).catch(err => console.warn('Failed to clear abandoned cart:', err));
        }
        
        // Redirect to Stripe's hosted checkout page
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (err) {
      console.error('Payment error:', err);
      setError(err.message || 'Payment failed. Please try again.');
      setProcessing(false);
      onError(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
        <div className="flex-1 flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold">1</div>
          <span className="text-gray-300">Payment Details</span>
        </div>
        <div className="w-8 h-px bg-gray-600" />
        <div className="flex-1 flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gray-600 text-gray-400 flex items-center justify-center text-xs">2</div>
          <span>Complete</span>
        </div>
      </div>

      {/* Plan Summary */}
      <div className="bg-white/5 border border-cyan-500/20 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">Selected Plan</span>
          <span className="text-white font-bold text-lg">${selectedPlan.price}</span>
        </div>
        <p className="text-gray-300 text-sm">{selectedPlan.description}</p>
        {selectedPlan.type === 'weekly_pass' && (
          <div className="mt-2 text-xs text-cyan-400">
            Unlimited scans for 7 days starting now
          </div>
        )}
        <div className="mt-2 flex items-center gap-2 text-xs text-cyan-400">
          <User className="w-3 h-3" />
          <span>You'll be redirected to Stripe's secure checkout page</span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
        >
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-400 text-sm">{error}</p>
        </motion.div>
      )}

      {/* Trust Signals */}
      <div className="grid grid-cols-3 gap-2 py-3 border-t border-white/10">
        <div className="flex flex-col items-center gap-1">
          <Lock className="w-5 h-5 text-cyan-400" />
          <p className="text-xs text-gray-400 text-center">256-bit SSL</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <p className="text-xs text-gray-400 text-center">Stripe Secured</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <CreditCard className="w-5 h-5 text-blue-400" />
          <p className="text-xs text-gray-400 text-center">PCI Compliant</p>
        </div>
      </div>

      {/* Security Notice */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Lock className="w-4 h-4" />
        <span>Secured by Stripe. Your payment info is encrypted and secure.</span>
      </div>

      {/* What Happens Next */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h4 className="text-white font-semibold text-sm mb-2">What happens next:</h4>
        <ul className="space-y-1.5 text-xs text-gray-300">
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>You'll be redirected to Stripe's secure checkout</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>Complete payment with any major credit card</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <span>Get instant access to unlimited scans for 7 days</span>
          </li>
        </ul>
      </div>

      {/* Value Reminder */}
      {selectedPlan.type === 'weekly_pass' && (
        <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-lg p-3 text-center">
          <p className="text-sm text-cyan-300 font-semibold">
            You're getting unlimited scans for 7 days - perfect for active job hunting!
          </p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onClose}
          disabled={processing}
          className="flex-1 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={processing}
          className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {processing ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <CreditCard className="w-5 h-5" />
              Pay ${selectedPlan.price}
            </>
          )}
        </button>
      </div>

      {/* Money-back guarantee */}
      <p className="text-center text-xs text-gray-500">
        <span className="font-semibold text-green-400">7-day money-back guarantee</span> - If you're not satisfied, contact support for a full refund
      </p>
    </form>
  );
};

/**
 * PaymentModal Component
 *
 * Modal for processing Stripe payments for micro-transactions.
 * Supports Apple Pay, Google Pay, and credit cards.
 *
 * Props:
 * - isOpen: Boolean to control modal visibility
 * - onClose: Callback to close modal
 * - selectedPlan: Plan object selected by user
 * - onSuccess: Callback when payment succeeds (receives purchase data)
 * - onError: Callback when payment fails (receives error)
 */
const PaymentModal = ({
  isOpen,
  onClose,
  selectedPlan,
  onSuccess,
  onError,
  guestToken
}) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [isGuestCheckout, setIsGuestCheckout] = useState(true); // Default to guest checkout
  const [showLoginForm, setShowLoginForm] = useState(false);

  // Update token state when localStorage changes
  useEffect(() => {
    const handleStorageChange = () => {
      setToken(localStorage.getItem('token'));
    };
    window.addEventListener('storage', handleStorageChange);
    // Also check periodically in case storage event doesn't fire (same tab)
    const interval = setInterval(() => {
      const currentToken = localStorage.getItem('token');
      if (currentToken !== token) {
        setToken(currentToken);
      }
    }, 500);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [token]);

  // Check for token changes (e.g., after login)
  useEffect(() => {
    const currentToken = localStorage.getItem('token');
    if (currentToken && !token) {
      // Token was just added (user logged in)
      setShowLoginForm(false);
      setIsGuestCheckout(false);
    }
  }, [token]);

  // Track abandoned cart when modal opens
  useEffect(() => {
    if (isOpen && selectedPlan) {
      trackPaymentModalOpened(selectedPlan.type);
      
      // Track abandoned cart on backend
      const currentToken = localStorage.getItem('token');
      if (currentToken) {
        fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/analytics/track-abandoned-cart`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${currentToken}`
          },
          body: JSON.stringify({
            plan_type: selectedPlan.type,
            price: selectedPlan.price
          })
        }).catch(err => console.warn('Failed to track abandoned cart:', err));
      }
    }
  }, [isOpen, selectedPlan]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setPaymentSuccess(false);
      setShowLoginForm(false);
      // Default to guest checkout if no token
      const currentToken = localStorage.getItem('token');
      setIsGuestCheckout(!currentToken);
    } else {
      // When modal opens, default to guest checkout if no token
      const currentToken = localStorage.getItem('token');
      if (!currentToken) {
        setIsGuestCheckout(true);
        setShowLoginForm(false);
      } else {
        setIsGuestCheckout(false);
        setShowLoginForm(false);
      }
    }
  }, [isOpen, selectedPlan]);

  const handleSuccess = (data) => {
    setPaymentSuccess(true);
    // Wait 2 seconds to show success message, then call onSuccess
    setTimeout(() => {
      onSuccess(data);
      onClose();
    }, 2000);
  };

  if (!isOpen || !selectedPlan) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 backdrop-blur-sm" onClick={onClose}>
        <div className="min-h-screen px-4 py-8 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl border border-cyan-500/20 shadow-2xl"
          >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>

          {/* Header */}
          <div className="relative p-6 border-b border-white/10">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-blue-500/5 to-purple-500/5" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-2 rounded-lg">
                  <CreditCard className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Complete Payment</h2>
              </div>
              <p className="text-gray-400 text-sm">
                Secure checkout powered by Stripe
              </p>
            </div>
          </div>

          {/* Guest Checkout Toggle (for weekly pass purchases) */}
          {selectedPlan?.type === 'weekly_pass' && (
            <div className="px-6 pt-4 pb-2 border-b border-white/10">
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <div className="flex-1">
                  <p className="text-white text-sm font-medium">Checkout Options</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className={`flex-1 text-xs px-2 py-1 rounded ${isGuestCheckout ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-400'}`}>
                      {isGuestCheckout ? '✓ Guest Checkout' : 'Guest Checkout'}
                    </div>
                    <div className={`flex-1 text-xs px-2 py-1 rounded ${!isGuestCheckout ? 'bg-purple-500/20 text-purple-400' : 'text-gray-400'}`}>
                      {!isGuestCheckout ? '✓ Sign In' : 'Sign In'}
                    </div>
                  </div>
                  <p className="text-gray-400 text-xs mt-2">
                    {isGuestCheckout 
                      ? 'No account required - Fast checkout'
                      : token 
                        ? 'Your results will be saved to your account'
                        : 'Sign in to save results and access them anytime'}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    if (!token && !isGuestCheckout) {
                      // Show inline login form instead of redirecting
                      setShowLoginForm(true);
                      setIsGuestCheckout(false);
                    } else if (!token && isGuestCheckout) {
                      // Switch to login mode - show inline login
                      setShowLoginForm(true);
                      setIsGuestCheckout(false);
                    } else {
                      // User is logged in - just toggle between modes
                      setIsGuestCheckout(!isGuestCheckout);
                      setShowLoginForm(false);
                    }
                  }}
                  className="relative ml-3 inline-flex h-6 w-11 items-center rounded-full bg-cyan-500/20 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
                  title={isGuestCheckout ? 'Switch to Sign In' : 'Switch to Guest Checkout'}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      isGuestCheckout ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          )}

          {/* Content */}
          <div className="p-6">
            {paymentSuccess ? (
              // Success State
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center py-8"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                  className="inline-block mb-4"
                >
                  <div className="bg-green-500/20 p-4 rounded-full">
                    <CheckCircle className="w-16 h-16 text-green-400" />
                  </div>
                </motion.div>
                <h3 className="text-2xl font-bold text-white mb-2">Payment Successful!</h3>
                <p className="text-gray-400 mb-4">
                  {selectedPlan.type === 'weekly_pass'
                    ? 'Your 7-day unlimited pass is now active.'
                    : 'You can now view your full analysis results.'}
                </p>
                <div className="flex items-center justify-center gap-2 text-cyan-400 text-sm">
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Redirecting...</span>
                </div>
              </motion.div>
            ) : (
              // Payment Form - Show login form, guest, or authenticated form
              <>
                {showLoginForm && !token ? (
                  <InlineLoginForm
                    onLoginSuccess={(newToken, user) => {
                      // After successful login, switch to authenticated payment
                      setShowLoginForm(false);
                      setIsGuestCheckout(false);
                      // Force re-render by updating state
                      // The token is already in localStorage, just need to refresh component
                    }}
                    onContinueAsGuest={() => {
                      setShowLoginForm(false);
                      setIsGuestCheckout(true);
                    }}
                    onError={onError}
                  />
                ) : isGuestCheckout && selectedPlan?.type === 'weekly_pass' && !token ? (
                  <GuestPaymentForm
                    selectedPlan={selectedPlan}
                    guestToken={guestToken}
                    onSuccess={handleSuccess}
                    onError={onError}
                    onClose={onClose}
                  />
                ) : (
                  <PaymentForm
                    selectedPlan={selectedPlan}
                    onSuccess={handleSuccess}
                    onError={onError}
                    onClose={onClose}
                  />
                )}
              </>
            )}
          </div>
        </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
};

export default PaymentModal;
