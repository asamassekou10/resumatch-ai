import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import UserMenu from './UserMenu';
import MobileMenu from './MobileMenu';

const Navigation = ({ view, setView, token, handleLogout, showBackButton = false, backButtonText = "Back", onBackClick, user, isAdmin }) => {
  const [showMarketMenu, setShowMarketMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const marketIntelligenceViews = ['market-dashboard', 'skill-gap', 'job-stats', 'skill-relationships', 'market-insights', 'interview-prep', 'company-intel', 'career-path'];
  const isMarketView = marketIntelligenceViews.includes(view);

  return (
    <>
      <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-lg border-b border-slate-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Mobile Hamburger & Logo */}
            <div className="flex items-center gap-3">
              {/* Hamburger Menu - Only show on mobile when logged in */}
              {token && (
                <button
                  onClick={() => setIsMobileMenuOpen(true)}
                  className="md:hidden p-2 rounded-lg hover:bg-slate-800 transition"
                  aria-label="Open menu"
                >
                  <Menu className="w-6 h-6 text-slate-300" />
                </button>
              )}

              {/* Logo - Clickable */}
              <button
                onClick={() => setView(token ? 'dashboard' : 'landing')}
                className="flex items-center gap-3 hover:opacity-80 transition"
              >
                <img
                  src="/logo192.png"
                  alt="ResumeAnalyzer AI Logo"
                  className="w-8 h-8 object-contain"
                />
                <h1 className="text-xl font-bold text-white">ResumeAnalyzer AI</h1>
              </button>
            </div>

          {/* Desktop Navigation Links - Hidden on mobile */}
          <div className="flex items-center gap-4">
            {showBackButton && (
              <button
                onClick={onBackClick}
                className="text-slate-300 hover:text-white transition font-medium"
              >
                ← {backButtonText}
              </button>
            )}

            {token && (
              <>
                <div className="hidden md:flex items-center gap-4">
                  <button
                    onClick={() => setView('dashboard')}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      view === 'dashboard'
                        ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/50'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    Dashboard
                  </button>

                  {/* Market Intelligence Menu */}
                  <div className="relative">
                    <button
                      onClick={() => setShowMarketMenu(!showMarketMenu)}
                      className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-1 ${
                        isMarketView
                          ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/50'
                          : 'text-slate-300 hover:text-white hover:bg-slate-800'
                      }`}
                    >
                      Market Intelligence
                      <svg className={`w-4 h-4 transition ${showMarketMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </button>

                    {showMarketMenu && (
                      <div className="absolute right-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                        <button
                          onClick={() => {
                            setView('market-dashboard');
                            setShowMarketMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition first:rounded-t-lg"
                        >
                          Overview & Dashboard
                        </button>
                        <button
                          onClick={() => {
                            setView('interview-prep');
                            setShowMarketMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                        >
                          Interview Prep
                        </button>
                        <button
                          onClick={() => {
                            setView('company-intel');
                            setShowMarketMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                        >
                          Company Intel
                        </button>
                        <button
                          onClick={() => {
                            setView('career-path');
                            setShowMarketMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                        >
                          Career Path
                        </button>
                        <button
                          onClick={() => {
                            setView('skill-gap');
                            setShowMarketMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition last:rounded-b-lg"
                        >
                          Skill Gap Analysis
                        </button>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => setView('pricing')}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      view === 'pricing'
                        ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/50'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    Pricing
                  </button>
                </div>

                {/* User Menu - Replace Logout button */}
                <UserMenu user={user} onLogout={handleLogout} setView={setView} />
              </>
            )}

            {/* Logged Out Navigation */}
            {!token && (
              <div className="hidden md:flex items-center gap-4">
                {view !== 'landing' && (
                  <button
                    onClick={() => setView('landing')}
                    className="text-slate-300 hover:text-white transition font-medium"
                  >
                    Home
                  </button>
                )}
                <button
                  onClick={() => setView('pricing')}
                  className="text-slate-300 hover:text-white transition font-medium"
                >
                  Pricing
                </button>
                <button
                  onClick={() => setView('login')}
                  className="px-4 py-2 text-slate-300 hover:text-white transition font-medium rounded-lg hover:bg-slate-800"
                >
                  Login
                </button>
                <button
                  onClick={() => setView('register')}
                  className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition"
                >
                  Sign Up
                </button>
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
      view={view}
      setView={setView}
      handleLogout={handleLogout}
      isAdmin={isAdmin}
    />
  </>
  );
};

export default Navigation;
