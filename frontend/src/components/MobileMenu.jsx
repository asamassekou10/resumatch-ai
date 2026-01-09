import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { X, ChevronRight, ChevronDown, Home, FileText, TrendingUp, CreditCard, Settings, HelpCircle, LogIn, UserPlus, Shield, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ROUTES } from '../config/routes';

/**
 * MobileMenu Component
 *
 * Sliding mobile navigation menu with React Router integration.
 * Supports authenticated and unauthenticated states, expandable sections, and admin access.
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether menu is open
 * @param {Function} props.onClose - Close menu callback
 * @param {Object} props.user - User profile data
 * @param {Function} props.handleLogout - Logout handler
 * @param {boolean} props.isAdmin - Whether user is admin
 */
const MobileMenu = ({ isOpen, onClose, user, handleLogout, isAdmin }) => {
  const [expandedSections, setExpandedSections] = useState({});
  const navigate = useNavigate();
  const location = useLocation();

  // Memoized close handler to ensure consistent reference
  const handleClose = useCallback(() => {
    if (onClose && typeof onClose === 'function') {
      onClose();
    }
  }, [onClose]);

  // Lock body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.body.style.touchAction = 'none';
    } else {
      document.body.style.overflow = '';
      document.body.style.touchAction = '';
    }
    return () => {
      document.body.style.overflow = '';
      document.body.style.touchAction = '';
    };
  }, [isOpen]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, handleClose]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleNavClick = (route) => {
    navigate(route);
    handleClose();
  };

  // Menu configuration for logged-in users
  const authenticatedMenuItems = [
    { label: 'Dashboard', route: ROUTES.DASHBOARD, icon: Home },
    { label: 'Analyze Resume', route: ROUTES.ANALYZE, icon: FileText },
    {
      label: 'Market Intelligence',
      icon: TrendingUp,
      expandable: true,
      children: [
        { label: 'Overview', route: ROUTES.MARKET_DASHBOARD },
        { label: 'Interview Prep', route: ROUTES.MARKET_INTERVIEW_PREP },
        { label: 'Company Intel', route: ROUTES.MARKET_COMPANY_INTEL },
        { label: 'Career Path', route: ROUTES.MARKET_CAREER_PATH },
        { label: 'Skill Gap', route: ROUTES.MARKET_SKILL_GAP },
      ]
    },
    { label: 'Pricing', route: ROUTES.PRICING, icon: CreditCard },
    { label: 'Settings', route: ROUTES.SETTINGS, icon: Settings },
    { label: 'Help & Support', route: ROUTES.HELP, icon: HelpCircle },
  ];

  // Menu configuration for logged-out users
  const publicMenuItems = [
    { label: 'Home', route: ROUTES.LANDING, icon: Home },
    { label: 'Try Free', route: ROUTES.GUEST_ANALYZE, icon: FileText },
    { label: 'Pricing', route: ROUTES.PRICING, icon: CreditCard },
    { label: 'Login', route: ROUTES.LOGIN, icon: LogIn },
    { label: 'Sign Up', route: ROUTES.REGISTER, icon: UserPlus },
  ];

  // Admin menu items
  const adminMenuItem = {
    label: 'Admin',
    icon: Shield,
    expandable: true,
    children: [
      { label: 'Dashboard', route: ROUTES.ADMIN },
      { label: 'Users', route: ROUTES.ADMIN_USERS },
      { label: 'Analytics', route: ROUTES.ADMIN_ANALYTICS },
    ]
  };

  // Build menu items based on user state
  let menuItems = user ? [...authenticatedMenuItems] : [...publicMenuItems];

  // Add admin section if user is admin
  if (user && isAdmin) {
    menuItems.push(adminMenuItem);
  }

  // Check if route is active
  const isActiveRoute = (route) => location.pathname === route;

  // Handle overlay interaction (both click and touch)
  const handleOverlayInteraction = useCallback((e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    handleClose();
  }, [handleClose]);

  // Handle close button click
  const handleCloseButtonClick = useCallback((e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    handleClose();
  }, [handleClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay - Click/Touch to close */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleOverlayInteraction}
            onTouchEnd={handleOverlayInteraction}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[9998] cursor-pointer"
            style={{ touchAction: 'manipulation' }}
            role="button"
            tabIndex={0}
            aria-label="Close menu"
          />

          {/* Menu Panel */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            onClick={(e) => e.stopPropagation()}
            className="fixed left-0 top-0 h-full w-80 max-w-[85vw] bg-black/95 backdrop-blur-xl border-r border-white/10 z-[9999] overflow-y-auto"
            style={{ touchAction: 'pan-y' }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <h2 className="text-xl font-bold text-white font-display">Menu</h2>
              <button
                type="button"
                onClick={handleCloseButtonClick}
                onTouchEnd={handleCloseButtonClick}
                className="p-2 rounded-lg hover:bg-white/10 active:bg-white/5 transition cursor-pointer touch-manipulation"
                aria-label="Close menu"
                style={{ WebkitTapHighlightColor: 'transparent' }}
              >
                <X className="w-6 h-6 text-gray-300" />
              </button>
            </div>

            {/* User Info (if logged in) */}
            {user && (
              <div className="p-4 border-b border-white/10 bg-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
                    {user.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-semibold truncate">{user.name || 'User'}</p>
                    <p className="text-slate-400 text-sm truncate">{user.email}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Menu Items */}
            <nav className="p-2">
              {menuItems.map((item, index) => (
                <div key={index}>
                  {item.expandable ? (
                    // Expandable section
                    <div>
                      <button
                        onClick={() => toggleSection(item.label)}
                        className="w-full flex items-center justify-between px-4 py-3 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition"
                      >
                        <span className="flex items-center gap-3">
                          {item.icon && <item.icon className="w-5 h-5" />}
                          <span className="font-medium">{item.label}</span>
                        </span>
                        {expandedSections[item.label] ? (
                          <ChevronDown className="w-5 h-5" />
                        ) : (
                          <ChevronRight className="w-5 h-5" />
                        )}
                      </button>

                      {/* Expanded children */}
                      <AnimatePresence>
                        {expandedSections[item.label] && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="ml-4 mt-1 space-y-1 overflow-hidden"
                          >
                            {item.children.map((child, childIndex) => (
                              <button
                                key={childIndex}
                                onClick={() => handleNavClick(child.route)}
                                className={`w-full text-left px-4 py-2 rounded-lg transition ${
                                  isActiveRoute(child.route)
                                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                                }`}
                              >
                                {child.label}
                              </button>
                            ))}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  ) : (
                    // Regular menu item
                    <button
                      onClick={() => handleNavClick(item.route)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition ${
                        isActiveRoute(item.route)
                          ? 'bg-gradient-to-r from-blue-500/20 to-blue-500/20 text-white border border-blue-500/30'
                          : 'text-gray-300 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      {item.icon && <item.icon className="w-5 h-5" />}
                      <span className="font-medium">{item.label}</span>
                    </button>
                  )}
                </div>
              ))}
            </nav>

            {/* Logout Button (if logged in) */}
            {user && (
              <div className="p-2 border-t border-white/10 mt-auto">
                <button
                  onClick={() => {
                    handleLogout();
                    handleClose();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-transparent hover:border-red-500/30 rounded-lg transition touch-manipulation"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="font-medium">Logout</span>
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default MobileMenu;
