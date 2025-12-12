import { Outlet } from 'react-router-dom';
import Navigation from '../Navigation';

/**
 * MarketLayout Component
 *
 * Specialized layout for Market Intelligence features.
 * Provides consistent navigation and structure for all market-related pages.
 *
 * Features:
 * - Main navigation bar
 * - Market-specific navigation (could be extended)
 * - Subscription validation context
 * - Consistent styling for market intelligence pages
 *
 * Uses React Router's <Outlet /> to render child routes.
 *
 * Pages using this layout:
 * - Market Dashboard
 * - Skill Gap Analysis
 * - Job Statistics
 * - Skill Relationships
 * - Market Insights
 * - Interview Prep
 * - Company Intel
 * - Career Path
 *
 * @param {Object} props
 * @param {Object} props.userProfile - Current user profile data
 * @param {string} props.token - Authentication token
 * @param {Function} props.handleLogout - Logout callback function
 */
const MarketLayout = ({ userProfile, token, handleLogout }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Main Navigation Header */}
      <Navigation
        user={userProfile}
        token={token}
        onLogout={handleLogout}
      />

      {/*
        Optional: Add market-specific sub-navigation here
        For example, a breadcrumb or tabs for market intelligence sections
      */}

      {/* Main Content Area - Child market routes render here */}
      <main className="w-full">
        <Outlet context={{ userProfile, token }} />
      </main>
    </div>
  );
};

export default MarketLayout;
