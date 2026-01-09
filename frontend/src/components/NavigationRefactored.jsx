import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import UserMenu from './UserMenu';
import MobileMenu from './MobileMenu';
import { ROUTES } from '../config/routes';

/**
 * Navigation Component (Refactored with Glassmorphism Design)
 *
 * Main navigation bar with React Router integration.
 * Features smooth glassmorphism effect and scroll-reactive styling.
 *
 * @param {Object} props
 * @param {string} props.token - Authentication token
 * @param {Function} props.onLogout - Logout handler
 * @param {Object} props.user - User profile data
 */
const Navigation = ({ token, onLogout, user }) => {
  const [showMarketMenu, setShowMarketMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Handle scroll effect for glassmorphism
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <motion.nav
        className={`fixed top-0 w-full z-40 transition-all duration-500 ${
          scrolled
            ? 'bg-black/60 backdrop-blur-xl border-b border-white/5 py-3'
            : 'bg-transparent py-6'
        }`}
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <div className="container mx-auto px-6 flex justify-between items-center">
          {/* Logo Section */}
          <Link
            to={token ? ROUTES.DASHBOARD : ROUTES.LANDING}
            className="text-xl md:text-2xl font-bold tracking-tighter text-white flex items-center gap-2 cursor-pointer group font-display"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center group-hover:rotate-12 transition-transform duration-300">
              <FileText size={18} className="text-white" />
            </div>
            <span className="group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-400 transition-all">
              ResumeAnalyzer AI
            </span>
          </Link>

          {/* Desktop Menu - Authenticated */}
          {token && (
            <div className="hidden md:flex items-center gap-6">
              <Link
                to={ROUTES.DASHBOARD}
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
              >
                Dashboard
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
              </Link>

              {/* Market Intelligence Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowMarketMenu(!showMarketMenu)}
                  onBlur={() => setTimeout(() => setShowMarketMenu(false), 200)}
                  className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group flex items-center gap-1"
                >
                  Market Intelligence
                  <svg
                    className={`w-3 h-3 transition-transform ${showMarketMenu ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
                </button>

                <AnimatePresence>
                  {showMarketMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 mt-2 w-56 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden"
                    >
                      {[
                        { to: ROUTES.MARKET_DASHBOARD, label: 'Overview & Dashboard' },
                        { to: ROUTES.MARKET_INTERVIEW_PREP, label: 'Interview Prep' },
                        { to: ROUTES.MARKET_COMPANY_INTEL, label: 'Company Intel' },
                        { to: ROUTES.MARKET_CAREER_PATH, label: 'Career Path' },
                        { to: ROUTES.MARKET_SKILL_GAP, label: 'Skill Gap Analysis' }
                      ].map((item, i) => (
                        <Link
                          key={i}
                          to={item.to}
                          onClick={() => setShowMarketMenu(false)}
                          className="block px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                        >
                          {item.label}
                        </Link>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <Link
                to={ROUTES.PRICING}
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
              >
                Pricing
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
              </Link>

              <UserMenu user={user} onLogout={onLogout} />
            </div>
          )}

          {/* Desktop Menu - Not Authenticated */}
          {!token && (
            <div className="hidden md:flex items-center gap-6">
              <Link
                to={ROUTES.LANDING}
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
              >
                Home
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
              </Link>
              <Link
                to="/blog"
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
              >
                Blog
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
              </Link>
              <Link
                to={ROUTES.PRICING}
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
              >
                Pricing
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full" />
              </Link>
              <Link
                to={ROUTES.LOGIN}
                className="text-white text-sm font-medium hover:text-blue-400 transition-colors"
              >
                Login
              </Link>
              <Link
                to={ROUTES.REGISTER}
                className="bg-white text-black px-5 py-2 rounded-full text-sm font-bold hover:bg-gray-200 transition-all transform hover:scale-105 active:scale-95 duration-200 shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_25px_rgba(255,255,255,0.5)]"
              >
                Sign Up
              </Link>
            </div>
          )}

          {/* Mobile Toggle */}
          <button
            className="md:hidden text-white p-2 hover:bg-white/10 rounded-lg transition"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          >
            {isMobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </motion.nav>

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
