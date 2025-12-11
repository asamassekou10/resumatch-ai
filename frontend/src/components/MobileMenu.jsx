import React, { useState } from 'react';
import { X, ChevronRight, ChevronDown, Home, FileText, TrendingUp, CreditCard, Settings, HelpCircle, LogIn, UserPlus, Shield, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const MobileMenu = ({ isOpen, onClose, user, view, setView, handleLogout, isAdmin }) => {
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleNavClick = (newView) => {
    setView(newView);
    onClose();
  };

  // Different menu items for logged-in vs logged-out users
  const menuItems = user ? [
    { label: 'Dashboard', view: 'dashboard', icon: Home },
    { label: 'Analyze Resume', view: 'analyze', icon: FileText },
    {
      label: 'Market Intelligence',
      icon: TrendingUp,
      expandable: true,
      children: [
        { label: 'Overview', view: 'market-dashboard' },
        { label: 'Interview Prep', view: 'interview-prep' },
        { label: 'Company Intel', view: 'company-intel' },
        { label: 'Career Path', view: 'career-path' },
        { label: 'Skill Gap', view: 'skill-gap' },
      ]
    },
    { label: 'Pricing', view: 'pricing', icon: CreditCard },
    { label: 'Settings', view: 'settings', icon: Settings },
    { label: 'Help & Support', view: 'help', icon: HelpCircle },
  ] : [
    // Logged out menu items
    { label: 'Home', view: 'landing', icon: Home },
    { label: 'Try Free', view: 'guest-analyze', icon: FileText },
    { label: 'Pricing', view: 'pricing', icon: CreditCard },
    { label: 'Login', view: 'login', icon: LogIn },
    { label: 'Sign Up', view: 'register', icon: UserPlus },
  ];

  if (user && isAdmin) {
    menuItems.push({
      label: 'Admin',
      icon: Shield,
      expandable: true,
      children: [
        { label: 'Dashboard', view: 'admin' },
        { label: 'Users', view: 'admin-users' },
        { label: 'Analytics', view: 'admin-analytics' },
      ]
    });
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Menu Panel */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed left-0 top-0 h-full w-80 bg-slate-900 border-r border-slate-700 z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h2 className="text-lg font-semibold text-white">MENU</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-slate-800 transition"
                aria-label="Close menu"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            {/* User Info */}
            {user && (
              <div className="p-4 border-b border-slate-700">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                    {user.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white truncate">{user.name}</p>
                    <p className="text-xs text-slate-400 truncate">{user.email}</p>
                    <p className="text-xs text-cyan-400 mt-1 capitalize">
                      {user.subscription_tier} • {user.credits} credits
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Menu Items */}
            <div className="p-2">
              {menuItems.map((item, index) => (
                <div key={index}>
                  {item.expandable ? (
                    <>
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

                      {expandedSections[item.label] && (
                        <div className="ml-8 mt-1 space-y-1">
                          {item.children.map((child, childIndex) => (
                            <button
                              key={childIndex}
                              onClick={() => handleNavClick(child.view)}
                              className={`w-full text-left px-4 py-2 text-sm rounded-lg transition ${
                                view === child.view
                                  ? 'bg-cyan-500 text-white'
                                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
                              }`}
                            >
                              {child.label}
                            </button>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <button
                      onClick={() => handleNavClick(item.view)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                        view === item.view
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
            </div>

            {/* Logout */}
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
