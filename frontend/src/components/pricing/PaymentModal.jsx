import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CreditCard, Lock, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

/**
 * PaymentForm Component (Internal)
 *
 * Handles Stripe payment flow within the modal.
 */
const PaymentForm = ({ selectedPlan, onSuccess, onError, onClose }) => {
  const stripe = useStripe();
  const elements = useElements();
  const token = localStorage.getItem('token');

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cardComplete, setCardComplete] = useState(false);

  const handleCardChange = (event) => {
    setCardComplete(event.complete);
    if (event.error) {
      setError(event.error.message);
    } else {
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      setError('Stripe has not loaded yet. Please wait.');
      return;
    }

    if (!cardComplete) {
      setError('Please complete your card details.');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      // Step 1: Create PaymentIntent on backend
      const response = await fetch(`${API_URL}/payments/create-micro-purchase`, {
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
        throw new Error(data.message || 'Failed to create payment');
      }

      const { client_secret, purchase_id } = data;

      // Step 2: Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: elements.getElement(CardElement),
        }
      });

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      // Step 3: Confirm purchase on backend
      const confirmResponse = await fetch(`${API_URL}/payments/confirm-micro-purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          purchase_id,
          payment_intent_id: paymentIntent.id
        })
      });

      const confirmData = await confirmResponse.json();

      if (!confirmResponse.ok) {
        throw new Error(confirmData.message || 'Failed to confirm payment');
      }

      // Success!
      onSuccess(confirmData);
    } catch (err) {
      console.error('Payment error:', err);
      setError(err.message || 'Payment failed. Please try again.');
      onError(err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
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
      </div>

      {/* Card Input */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Card Details
        </label>
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 hover:border-cyan-500/30 transition-colors">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#ffffff',
                  fontFamily: '"Inter", system-ui, sans-serif',
                  '::placeholder': {
                    color: '#6b7280',
                  },
                  iconColor: '#06b6d4'
                },
                invalid: {
                  color: '#ef4444',
                  iconColor: '#ef4444'
                }
              },
              hidePostalCode: false
            }}
            onChange={handleCardChange}
          />
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

      {/* Security Notice */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Lock className="w-4 h-4" />
        <span>Secured by Stripe. Your payment info is encrypted and secure.</span>
      </div>

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
          disabled={processing || !stripe || !cardComplete}
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
        100% money-back guarantee within 24 hours if you're not satisfied
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
  onError
}) => {
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  // Reset success state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setPaymentSuccess(false);
    }
  }, [isOpen]);

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
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-md bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl border border-cyan-500/20 shadow-2xl my-8"
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
              // Payment Form
              <Elements stripe={stripePromise}>
                <PaymentForm
                  selectedPlan={selectedPlan}
                  onSuccess={handleSuccess}
                  onError={onError}
                  onClose={onClose}
                />
              </Elements>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PaymentModal;
