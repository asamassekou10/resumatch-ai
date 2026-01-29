import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, AlertCircle, CheckCircle, Loader } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * UnverifiedEmailPrompt Component
 * 
 * Shows when user tries to login with unverified email
 * Provides clear path to verify email
 */
const UnverifiedEmailPrompt = ({ email, onResendSuccess }) => {
  const [resending, setResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleResendVerification = async () => {
    setResending(true);
    setError('');
    setResendSuccess(false);

    try {
      const response = await fetch(`${API_URL}/auth/resend-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setResendSuccess(true);
        if (onResendSuccess) {
          onResendSuccess();
        }
        // Reset success message after 5 seconds
        setTimeout(() => setResendSuccess(false), 5000);
      } else {
        setError(data.error || 'Failed to resend verification email');
      }
    } catch (err) {
      setError('Network error. Please try again later.');
    } finally {
      setResending(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/30 rounded-xl p-6 mb-6"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
            <Mail className="w-6 h-6 text-blue-400" />
          </div>
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            Email Verification Required
          </h3>
          
          <p className="text-gray-300 mb-4">
            Your email address <span className="font-semibold text-white">{email}</span> hasn't been verified yet. 
            Please check your inbox for the verification email.
          </p>

          {resendSuccess && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-4 p-3 bg-green-500/20 border border-green-500/30 rounded-lg flex items-center gap-2"
            >
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
              <p className="text-green-300 text-sm">
                Verification email sent! Please check your inbox (and spam folder).
              </p>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg"
            >
              <p className="text-red-300 text-sm">{error}</p>
            </motion.div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleResendVerification}
              disabled={resending || resendSuccess}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {resending ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Sending...
                </>
              ) : resendSuccess ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Email Sent!
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4" />
                  Resend Verification Email
                </>
              )}
            </button>
          </div>

          <div className="mt-4 pt-4 border-t border-white/10">
            <p className="text-xs text-gray-400 mb-2">
              <strong>Tips:</strong>
            </p>
            <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
              <li>Check your spam/junk folder if you don't see the email</li>
              <li>Make sure you're checking the correct email address</li>
              <li>The verification link expires in 7 days</li>
              <li>Need help? Contact <a href="mailto:support@resumeanalyzerai.com" className="text-blue-400 hover:underline">support@resumeanalyzerai.com</a></li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default UnverifiedEmailPrompt;
