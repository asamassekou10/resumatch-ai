import React, { useState } from 'react';

const Navigation = ({ view, setView, token, handleLogout, showBackButton = false, backButtonText = "Back", onBackClick }) => {
  const [showMarketMenu, setShowMarketMenu] = useState(false);

  const marketIntelligenceViews = ['market-dashboard', 'skill-gap', 'job-stats', 'skill-relationships', 'market-insights'];
  const isMarketView = marketIntelligenceViews.includes(view);

  return (
    <nav className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <img
              src="/logo192.png"
              alt="ResumeAnalyzer AI Logo"
              className="w-8 h-8 object-contain"
            />
            <h1 className="text-xl font-bold text-white">ResumeAnalyzer AI</h1>
          </div>

          {/* Navigation Links */}
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
                <button
                  onClick={() => setView('dashboard')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    view === 'dashboard'
                      ? 'bg-cyan-500 text-white'
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
                        ? 'bg-cyan-500 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    Market Intelligence
                    <svg className={`w-4 h-4 transition ${showMarketMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  </button>

                  {showMarketMenu && (
                    <div className="absolute right-0 mt-0 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-lg z-50">
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
                          setView('skill-gap');
                          setShowMarketMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                      >
                        Skill Gap Analysis
                      </button>
                      <button
                        onClick={() => {
                          setView('job-stats');
                          setShowMarketMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                      >
                        Job Statistics
                      </button>
                      <button
                        onClick={() => {
                          setView('skill-relationships');
                          setShowMarketMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition"
                      >
                        Skill Relationships
                      </button>
                      <button
                        onClick={() => {
                          setView('market-insights');
                          setShowMarketMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-700 transition last:rounded-b-lg"
                      >
                        Your Insights
                      </button>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setView('pricing')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    view === 'pricing'
                      ? 'bg-cyan-500 text-white'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  Pricing
                </button>
                
                <button
                  onClick={handleLogout}
                  className="text-slate-300 hover:text-white transition font-medium"
                >
                  Logout
                </button>
              </>
            )}
            
            {!token && view !== 'landing' && (
              <button
                onClick={() => setView('landing')}
                className="text-slate-300 hover:text-white transition font-medium"
              >
                Home
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
