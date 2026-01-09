import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import UserMenu from './UserMenu';
import MobileMenu from './MobileMenu';
import { ROUTES } from '../config/routes';

/**
 * Navigation Component
 *
 * Main navigation bar with React Router integration.
 * Supports both desktop and mobile layouts.
 *
 * @param {Object} props
 * @param {string} props.token - Authentication token
 * @param {Function} props.onLogout - Logout handler
 * @param {Object} props.user - User profile data
 */
const Navigation = ({ token, onLogout, user }) => {
  const location = useLocation();
  const [showMarketMenu, setShowMarketMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Check if current route is a market intelligence page
  const isMarketRoute = location.pathname.startsWith('/market');

  // Check if current path matches a route (for active styling)
  const isActive = (path) => location.pathname === path;

  return (
    <>
      <nav className="sticky top-0 z-50 bg-black/40 backdrop-blur-xl border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Mobile Hamburger & Logo */}
            <div className="flex items-center gap-3">
              {/* Hamburger Menu - Show on mobile for all users */}
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="md:hidden p-2 rounded-lg hover:bg-white/10 transition"
                aria-label="Open menu"
              >
                <Menu className="w-6 h-6 text-gray-300" />
              </button>

              {/* Logo - Clickable */}
              <Link
                to={token ? ROUTES.DASHBOARD : ROUTES.LANDING}
                className="flex items-center gap-3 hover:opacity-80 transition"
              >
                <img
                  src="/logo192.png"
                  alt="ResumeAnalyzer AI Logo"
                  className="w-8 h-8 object-contain"
                />
                <h1 className="text-xl font-bold text-white">ResumeAnalyzer AI</h1>
              </Link>
            </div>

            {/* Desktop Navigation Links - Hidden on mobile */}
            <div className="flex items-center gap-4">
              {token && (
                <>
                  <div className="hidden md:flex items-center gap-4">
                    <Link
                      to={ROUTES.DASHBOARD}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        isActive(ROUTES.DASHBOARD)
                          ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30'
                          : 'text-gray-300 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Dashboard
                    </Link>

                    {/* Market Intelligence Menu */}
                    <div className="relative">
                      <button
                        onClick={() => setShowMarketMenu(!showMarketMenu)}
                        className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-1 ${
                          isMarketRoute
                            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30'
                            : 'text-gray-300 hover:text-white hover:bg-white/10'
                        }`}
                      >
                        Market Intelligence
                        <svg className={`w-4 h-4 transition ${showMarketMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                        </svg>
                      </button>

                      {showMarketMenu && (
                        <div className="absolute right-0 mt-2 w-56 bg-black/80 backdrop-blur-xl border border-white/10 rounded-lg shadow-xl z-50">
                          <Link
                            to={ROUTES.MARKET_DASHBOARD}
                            onClick={() => setShowMarketMenu(false)}
                            className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 transition first:rounded-t-lg"
                          >
                            Overview & Dashboard
                          </Link>
                          <Link
                            to={ROUTES.MARKET_INTERVIEW_PREP}
                            onClick={() => setShowMarketMenu(false)}
                            className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 transition"
                          >
                            Interview Prep
                          </Link>
                          <Link
                            to={ROUTES.MARKET_COMPANY_INTEL}
                            onClick={() => setShowMarketMenu(false)}
                            className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 transition"
                          >
                            Company Intel
                          </Link>
                          <Link
                            to={ROUTES.MARKET_CAREER_PATH}
                            onClick={() => setShowMarketMenu(false)}
                            className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 transition"
                          >
                            Career Path
                          </Link>
                          <Link
                            to={ROUTES.MARKET_SKILL_GAP}
                            onClick={() => setShowMarketMenu(false)}
                            className="block w-full text-left px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 transition last:rounded-b-lg"
                          >
                            Skill Gap Analysis
                          </Link>
                        </div>
                      )}
                    </div>

                    <Link
                      to={ROUTES.PRICING}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        isActive(ROUTES.PRICING)
                          ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30'
                          : 'text-gray-300 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Pricing
                    </Link>
                  </div>

                  {/* User Menu */}
                  <UserMenu user={user} onLogout={onLogout} />
                </>
              )}

              {/* Logged Out Navigation */}
              {!token && (
                <div className="hidden md:flex items-center gap-6">
                  {!isActive(ROUTES.LANDING) && (
                    <Link
                      to={ROUTES.LANDING}
                      className="text-gray-300 hover:text-white transition font-medium"
                    >
                      Home
                    </Link>
                  )}
                  <Link
                    to="/blog"
                    className="text-gray-300 hover:text-white transition font-medium"
                  >
                    Blog
                  </Link>
                  <Link
                    to={ROUTES.PRICING}
                    className="text-gray-300 hover:text-white transition font-medium"
                  >
                    Pricing
                  </Link>
                  <Link
                    to={ROUTES.LOGIN}
                    className="text-gray-300 hover:text-white transition font-medium"
                  >
                    Login
                  </Link>
                  <Link
                    to={ROUTES.REGISTER}
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-blue-500/50 transition"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        user={user}
        handleLogout={onLogout}
        isAdmin={user?.is_admin}
      />
    </>
  );
};

export default Navigation;
