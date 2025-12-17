import { Outlet } from 'react-router-dom';
import Navigation from '../Navigation';

/**
 * PublicLayout Component
 *
 * Layout for public pages (Landing, Pricing, Guest Analyze, etc.)
 * Provides consistent navigation header across all public pages.
 *
 * Features:
 * - Navigation bar (same as authenticated pages)
 * - Consistent page structure
 * - No authentication required
 *
 * Uses React Router's <Outlet /> to render child routes.
 *
 * @param {Object} props
 * @param {Object} props.userProfile - Current user profile data (may be null)
 * @param {string} props.token - Authentication token (may be null)
 * @param {Function} props.handleLogout - Logout callback function
 * @param {Function} props.handleLogin - Login callback function
 */
const PublicLayout = ({ userProfile, token, handleLogout, handleLogin }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation Header */}
      <Navigation
        user={userProfile}
        token={token}
        onLogout={handleLogout}
        onLogin={handleLogin}
      />

      {/* Main Content Area - Child routes render here */}
      <main className="w-full">
        <Outlet context={{ userProfile, token, handleLogin }} />
      </main>
    </div>
  );
};

export default PublicLayout;
