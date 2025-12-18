import React, { useState } from 'react';
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

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleNavClick = (route) => {
    navigate(route);
    onClose();
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

  // Handle close when clicking overlay
  const handleOverlayClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    onClose();
  };

  // Prevent clicks inside menu from closing it
  const handleMenuClick = (e) => {
    e.stopPropagation();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay - Click to close */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleOverlayClick}
            className="fixed inset-0 bg-black/50 z-[9998] cursor-pointer"
            style={{ touchAction: 'none' }}
          />

          {/* Menu Panel */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            onClick={handleMenuClick}
            className="fixed left-0 top-0 h-full w-80 bg-slate-900 border-r border-slate-700 z-[9999] overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h2 className="text-xl font-bold text-white">Menu</h2>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onClose();
                }}
                className="p-2 rounded-lg hover:bg-slate-800 transition cursor-pointer"
                aria-label="Close menu"
              >
                <X className="w-6 h-6 text-slate-300 pointer-events-none" />
              </button>
            </div>

            {/* User Info (if logged in) */}
            {user && (
              <div className="p-4 border-b border-slate-700 bg-slate-800/50">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
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
                        className="w-full flex items-center justify-between px-4 py-3 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition"
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
                                    ? 'bg-cyan-500/20 text-cyan-400'
                                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
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
                          ? 'bg-cyan-500 text-white'
                          : 'text-slate-300 hover:text-white hover:bg-slate-800'
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
              <div className="p-2 border-t border-slate-700 mt-auto">
                <button
                  onClick={() => {
                    handleLogout();
                    onClose();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition"
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
