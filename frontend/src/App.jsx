import { useState, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './components/routing/AppRoutes';
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
  const [loading, setLoading] = useState(true);

  // ============================================
  // EFFECTS
  // ============================================

  /**
   * Fetch user profile on mount if token exists
   */
  useEffect(() => {
    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  // ============================================
  // API FUNCTIONS
  // ============================================

  /**
   * Fetch user profile from API
   */
  const fetchUserProfile = async () => {
    try {
      console.log('[App] Fetching user profile...');
      const response = await axios.get(`${API_URL}/users/profile`, {
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
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // AUTH HANDLERS
  // ============================================

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

  /**
   * Handle logout
   */
  const handleLogout = () => {
    console.log('[App] Logging out');
    setToken(null);
    setUserProfile(null);
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
  };

  // ============================================
  // LOADING STATE
  // ============================================

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-300 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // ============================================
  // RENDER
  // ============================================

  return (
    <BrowserRouter>
      <AppRoutes
        userProfile={userProfile}
        token={token}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
      />
    </BrowserRouter>
  );
}

export default App;
