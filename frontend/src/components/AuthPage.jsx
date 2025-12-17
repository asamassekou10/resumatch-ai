import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROUTES } from '../config/routes';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * AuthPage Component
 *
 * Handles both login and registration with:
 * - Email/password authentication
 * - Google OAuth
 * - LinkedIn OAuth
 * - Password validation for registration
 * - Email verification flow
 *
 * @param {Object} props
 * @param {string} props.mode - 'login' or 'register'
 * @param {Function} props.onLogin - Callback after successful login
 */
const AuthPage = ({ mode = 'login', onLogin }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isLogin = mode === 'login';

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

  // Password validation function
  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain an uppercase letter';
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain a lowercase letter';
    }
    if (!/[0-9]/.test(password)) {
      return 'Password must contain a number';
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return 'Password must contain a special character';
    }
    return '';
  };

  const handleAuth = async () => {
    setLoading(true);
    setError('');

    // Validate password on register
    if (!isLogin) {
      const validationError = validatePassword(formData.password);
      if (validationError) {
        setError(validationError);
        setLoading(false);
        return;
      }
    }

    try {
      const endpoint = isLogin ? 'login' : 'register';
      const response = await fetch(`${API_URL}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();

      if (!response.ok) {
        // Handle unverified email error
        if (response.status === 403 && !data.email_verified) {
          setError(data.error + '. Check your email for the verification link.');
          return;
        }
        throw new Error(data.error);
      }

      // Handle registration success
      if (!isLogin && data.verification_required) {
        setError('');
        alert('Registration successful! Please check your email to verify your account before logging in.');
        navigate(ROUTES.LOGIN);
        setFormData({ email: '', password: '' });
        return;
      }

      // Handle login success - backend returns 'access_token' not 'token'
      const token = data.access_token || data.token;
      if (token) {
        localStorage.setItem('token', token);
        if (data.user) {
          localStorage.setItem('userProfile', JSON.stringify(data.user));
        }
        if (onLogin) {
          onLogin(token, data.user);
        }
        // Redirect to dashboard or intended destination
        const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
        navigate(from, { replace: true });
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${API_URL}/auth/google`;
  };

  const handleLinkedInLogin = () => {
    window.location.href = `${API_URL}/auth/linkedin/login`;
  };

  const handleResendVerification = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/resend-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      const data = await response.json();
      alert(data.message || 'Verification email sent!');
    } catch (err) {
      alert('Failed to resend email. Please try again.');
    }
  };

  const switchMode = () => {
    navigate(isLogin ? ROUTES.REGISTER : ROUTES.LOGIN);
  };

  return (
    <div className="py-8">
      <div className="flex items-center justify-center min-h-[calc(100vh-200px)]">
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl shadow-2xl p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h1>
            <p className="text-slate-400">
              {isLogin ? 'Sign in to continue' : 'Join us to get started'}
            </p>
          </div>

          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {error && error.includes('verify your email') && (
            <div className="bg-blue-900/50 border border-blue-500 text-blue-300 px-4 py-3 rounded-lg mb-6 text-center">
              <p className="mb-2">Didn't receive the verification email?</p>
              <button
                onClick={handleResendVerification}
                className="text-cyan-400 hover:text-cyan-300 font-medium underline"
              >
                Resend Verification Email
              </button>
            </div>
          )}

          <div className="space-y-6">
            {/* Google Sign-in Button */}
            <button
              onClick={handleGoogleLogin}
              className="w-full bg-white hover:bg-gray-50 text-gray-900 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-lg border border-gray-300 flex items-center justify-center gap-3"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            {/* LinkedIn Sign-in Button */}
            <button
              onClick={handleLinkedInLogin}
              className="w-full bg-[#0077B5] hover:bg-[#006097] text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-lg flex items-center justify-center gap-3"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
              </svg>
              Continue with LinkedIn
            </button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-slate-800 text-slate-400">Or continue with email</span>
              </div>
            </div>

            <div>
              <input
                type="email"
                placeholder="Email address"
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Password"
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                value={formData.password}
                onChange={(e) => {
                  setFormData({...formData, password: e.target.value});
                  if (!isLogin) {
                    const validationError = validatePassword(e.target.value);
                    setPasswordError(validationError);
                    setShowPasswordRequirements(true);
                  }
                }}
                onFocus={() => !isLogin && setShowPasswordRequirements(true)}
                onKeyDown={(e) => e.key === 'Enter' && handleAuth()}
              />

              {/* Password Requirements - Only show on register */}
              {!isLogin && showPasswordRequirements && (
                <div className="mt-3 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                  <p className="text-sm font-medium text-slate-300 mb-2">Password must contain:</p>
                  <ul className="space-y-1 text-sm">
                    <li className={`flex items-center gap-2 ${formData.password.length >= 8 ? 'text-green-400' : 'text-slate-400'}`}>
                      <span className={formData.password.length >= 8 ? 'text-green-400' : 'text-slate-500'}>{formData.password.length >= 8 ? '●' : '○'}</span>
                      At least 8 characters
                    </li>
                    <li className={`flex items-center gap-2 ${/[A-Z]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                      <span className={/[A-Z]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[A-Z]/.test(formData.password) ? '●' : '○'}</span>
                      One uppercase letter
                    </li>
                    <li className={`flex items-center gap-2 ${/[a-z]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                      <span className={/[a-z]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[a-z]/.test(formData.password) ? '●' : '○'}</span>
                      One lowercase letter
                    </li>
                    <li className={`flex items-center gap-2 ${/[0-9]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                      <span className={/[0-9]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[0-9]/.test(formData.password) ? '●' : '○'}</span>
                      One number
                    </li>
                    <li className={`flex items-center gap-2 ${/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                      <span className={/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? '●' : '○'}</span>
                      One special character (!@#$%^&*)
                    </li>
                  </ul>
                  {passwordError && (
                    <p className="text-red-400 text-sm mt-3 font-medium">{passwordError}</p>
                  )}
                </div>
              )}
            </div>

            <button
              onClick={handleAuth}
              disabled={loading || (!isLogin && passwordError)}
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In with Email' : 'Create Account')}
            </button>
          </div>

          <div className="text-center mt-6">
            <p className="text-slate-400">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button
                onClick={switchMode}
                className="text-cyan-400 hover:text-cyan-300 transition font-medium"
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
