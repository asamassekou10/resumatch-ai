import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './components/routing/AppRoutes';
import ErrorBoundary from './components/common/ErrorBoundary';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Main App Component
 *
 * Root component with React Router integration.
 * Handles:
 * - Global authentication state
 * - User profile management
 * - Route configuration
 * - Initial data loading
 *
 * Architecture:
 * - Uses BrowserRouter for URL-based routing
 * - Delegates route rendering to AppRoutes component
 * - Provides auth context to all child routes
 * - Manages token and user profile in localStorage
 */
function App() {
  // ============================================
  // STATE MANAGEMENT
  // ============================================

  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userProfile, setUserProfile] = useState(null);

  // ============================================
  // EFFECTS
  // ============================================

  /**
   * Handle OAuth callbacks, email verification, and payment redirects
   * This runs once on mount to check URL params
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);

    // Get all possible params
    const tokenParam = urlParams.get('token');
    const userId = urlParams.get('user');
    const verify = urlParams.get('verify');
    const errorMessage = urlParams.get('message');
    const payment = urlParams.get('payment');
    const provider = urlParams.get('provider');
    const errorParam = urlParams.get('error');

    // 1. Check for email verification
    if (verify === 'true' && userId && tokenParam) {
      console.log('[App] Verifying email...');

      fetch(`${API_URL}/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          token: tokenParam
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          setToken(data.access_token);
          localStorage.setItem('token', data.access_token);
          alert('Email verified successfully! Welcome to ResumeAnalyzer AI!');
        } else {
          alert('Error: ' + (data.error || 'Verification failed. Please try again.'));
        }
        // Clean the URL and redirect to dashboard
        window.history.replaceState({}, document.title, '/dashboard');
      })
      .catch(err => {
        console.error('[App] Verification error:', err);
        alert('Verification failed. Please try again.');
        window.history.replaceState({}, document.title, '/login');
      });
    }
    // 2. Check for OAuth callback (Google or LinkedIn)
    else if (tokenParam && !verify) {
      console.log('[App] OAuth callback - setting token', provider || 'google');
      setToken(tokenParam);
      localStorage.setItem('token', tokenParam);
      // Clean the URL and redirect to dashboard
      window.history.replaceState({}, document.title, '/dashboard');
    }
    // 3. Check for payment success/cancel
    else if (payment) {
      console.log('[App] Payment result:', payment);
      if (payment === 'success') {
        alert('Payment successful! Welcome to Pro! Your credits have been added.');
      } else if (payment === 'cancel') {
        alert('Payment cancelled. You can upgrade anytime from your dashboard.');
      }
      // Clean the URL
      window.history.replaceState({}, document.title, '/dashboard');
    }
    // 4. Check for error message
    else if (errorMessage) {
      console.log('[App] OAuth or other error:', errorMessage);
      alert('Error: ' + decodeURIComponent(errorMessage));
      window.history.replaceState({}, document.title, '/login');
    }
    // 5. Check for error param (from LinkedIn OAuth)
    else if (errorParam) {
      console.log('[App] OAuth error:', errorParam);
      let errorText = 'Authentication failed. Please try again.';
      if (errorParam === 'linkedin_auth_failed') {
        errorText = 'LinkedIn authentication failed. Please try again or use email login.';
      } else if (errorParam === 'invalid_state') {
        errorText = 'Security validation failed. Please try again.';
      }
      alert(errorText);
      window.history.replaceState({}, document.title, '/login');
    }
  }, []); // Empty dependency array - runs once on mount

  // ============================================
  // AUTH HANDLERS
  // ============================================

  /**
   * Handle logout
   */
  const handleLogout = useCallback(() => {
    console.log('[App] Logging out');
    setToken(null);
    setUserProfile(null);
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
  }, []);

  // ============================================
  // API FUNCTIONS
  // ============================================

  /**
   * Fetch user profile from API
   */
  const fetchUserProfile = useCallback(async () => {
    try {
      console.log('[App] Fetching user profile...');
      const response = await axios.get(`${API_URL}/user/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      console.log('[App] User profile fetched:', response.data);
      setUserProfile(response.data);
      localStorage.setItem('userProfile', JSON.stringify(response.data));
    } catch (error) {
      console.error('[App] Error fetching profile:', error);

      // If unauthorized, clear token and profile
      if (error.response?.status === 401) {
        console.log('[App] Unauthorized, clearing auth state');
        handleLogout();
      }
    }
  }, [token, handleLogout]);

  /**
   * Fetch user profile on mount if token exists
   */
  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token, fetchUserProfile]);

  /**
   * Handle successful login
   * @param {string} newToken - JWT token
   * @param {Object} profile - User profile data
   */
  const handleLogin = (newToken, profile) => {
    console.log('[App] Login successful');
    setToken(newToken);
    setUserProfile(profile);
    localStorage.setItem('token', newToken);
    localStorage.setItem('userProfile', JSON.stringify(profile));
  };

  // ============================================
  // RENDER
  // ============================================

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppRoutes
          userProfile={userProfile}
          token={token}
          handleLogin={handleLogin}
          handleLogout={handleLogout}
        />
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
