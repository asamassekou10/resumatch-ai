import { Outlet } from 'react-router-dom';
import Navigation from '../Navigation';

/**
 * MainLayout Component
 *
 * Standard layout for authenticated pages (Dashboard, Profile, Settings, etc.)
 * Provides consistent navigation header across all main application pages.
 *
 * Features:
 * - Navigation bar with user menu
 * - Consistent page structure
 * - Automatic user profile context
 *
 * Uses React Router's <Outlet /> to render child routes.
 *
 * @param {Object} props
 * @param {Object} props.userProfile - Current user profile data
 * @param {string} props.token - Authentication token
 * @param {Function} props.handleLogout - Logout callback function
 */
const MainLayout = ({ userProfile, token, handleLogout }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation Header */}
      <Navigation
        user={userProfile}
        token={token}
        onLogout={handleLogout}
      />

      {/* Main Content Area - Child routes render here */}
      <main className="w-full">
        <Outlet context={{ userProfile, token }} />
      </main>
    </div>
  );
};

export default MainLayout;
