import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';

/**
 * VerifySuccess Component
 *
 * Handles email verification success redirects from backend.
 * Automatically logs in the user with the provided access token.
 */
const VerifySuccess = ({ setToken }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing'); // 'processing', 'success', 'error', 'already_verified'
  const [message, setMessage] = useState('Verifying your email...');

  useEffect(() => {
    const token = searchParams.get('token');
    const userId = searchParams.get('user_id');
    const email = searchParams.get('email');
    const alreadyVerified = searchParams.get('already_verified');
    const error = searchParams.get('error');

    // Handle error redirects
    if (error) {
      setStatus('error');
      setMessage(error);
      setTimeout(() => navigate('/login'), 3000);
      return;
    }

    // Handle already verified
    if (alreadyVerified === 'true') {
      setStatus('already_verified');
      setMessage('Your email was already verified. Please log in.');
      setTimeout(() => navigate('/login'), 2000);
      return;
    }

    // Handle successful verification with auto-login
    if (token && userId) {
      console.log('[VerifySuccess] Auto-logging in user:', email);

      // Store the access token
      setToken(token);
      localStorage.setItem('token', token);

      setStatus('success');
      setMessage(`Email verified successfully! Welcome${email ? `, ${email}` : ''}!`);

      // Redirect to dashboard after brief success message
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);
    } else {
      setStatus('error');
      setMessage('Invalid verification link. Missing required parameters.');
      setTimeout(() => navigate('/login'), 3000);
    }
  }, [searchParams, setToken, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 shadow-2xl">
        {/* Status Icon */}
        <div className="flex justify-center mb-6">
          {status === 'processing' && (
            <Loader className="w-16 h-16 text-blue-400 animate-spin" />
          )}
          {(status === 'success' || status === 'already_verified') && (
            <CheckCircle className="w-16 h-16 text-green-400" />
          )}
          {status === 'error' && (
            <AlertCircle className="w-16 h-16 text-red-400" />
          )}
        </div>

        {/* Status Title */}
        <h1 className="text-2xl font-bold text-center mb-4">
          {status === 'processing' && (
            <span className="text-white">Verifying Email...</span>
          )}
          {status === 'success' && (
            <span className="text-green-400">Email Verified!</span>
          )}
          {status === 'already_verified' && (
            <span className="text-blue-400">Already Verified</span>
          )}
          {status === 'error' && (
            <span className="text-red-400">Verification Failed</span>
          )}
        </h1>

        {/* Message */}
        <p className="text-gray-300 text-center mb-6">
          {message}
        </p>

        {/* Progress/Action */}
        {status === 'processing' && (
          <div className="flex justify-center">
            <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 h-full animate-pulse"></div>
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center">
            <p className="text-sm text-gray-400">
              Redirecting to your dashboard...
            </p>
          </div>
        )}

        {(status === 'error' || status === 'already_verified') && (
          <div className="text-center">
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition"
            >
              Go to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VerifySuccess;
