import React from 'react';

const Navigation = ({ 
  view, 
  setView, 
  token, 
  handleLogout, 
  showBackButton = false, 
  backButtonText = "Back to Home",
  onBackClick = null 
}) => {
  const handleBackClick = () => {
    if (onBackClick) {
      onBackClick();
    } else {
      // Default back behavior
      if (token) {
        setView('dashboard');
      } else {
        setView('landing');
      }
    }
  };

  return (
    <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        {/* Logo and Brand */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button 
            onClick={() => setView(token ? 'dashboard' : 'landing')}
            className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity"
          >
            <img 
              src="/logo192.png" 
              alt="ResumeAnalyzer AI Logo" 
              className="w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10 object-contain"
            />
            <h1 className="text-lg sm:text-xl md:text-2xl font-bold text-white">
              ResumeAnalyzer AI
            </h1>
          </button>
        </div>
        
        {/* Navigation Links */}
        <div className="flex items-center gap-2 sm:gap-3 lg:gap-4">
          {showBackButton && (
            <button
              onClick={handleBackClick}
              className="text-slate-300 hover:text-cyan-400 transition font-medium text-sm sm:text-base flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="hidden sm:inline">{backButtonText}</span>
              <span className="sm:hidden">Back</span>
            </button>
          )}

          {token ? (
            // Authenticated user navigation
            <>
              {view !== 'dashboard' && (
                <button
                  onClick={() => setView('dashboard')}
                  className="text-slate-300 hover:text-cyan-400 transition text-xs sm:text-sm lg:text-base px-1 sm:px-2"
                >
                  <span className="hidden sm:inline">Dashboard</span>
                  <span className="sm:hidden">Dash</span>
                </button>
              )}
              
              {view !== 'analyze' && (
                <button
                  onClick={() => setView('analyze')}
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2 rounded-lg transition shadow-lg hover:shadow-cyan-500/25 text-xs sm:text-sm lg:text-base"
                >
                  <span className="hidden sm:inline">New Analysis</span>
                  <span className="sm:hidden">New</span>
                </button>
              )}
              
              <button
                onClick={handleLogout}
                className="text-slate-300 hover:text-red-400 transition text-xs sm:text-sm lg:text-base px-1 sm:px-2"
              >
                <span className="hidden sm:inline">Logout</span>
                <span className="sm:hidden">Exit</span>
              </button>
            </>
          ) : (
            // Non-authenticated user navigation
            <>
              {view !== 'login' && (
                <button
                  onClick={() => setView('login')}
                  className="hidden sm:block border border-slate-600 text-slate-300 hover:border-cyan-400 hover:text-cyan-400 transition px-3 sm:px-4 py-2 rounded-lg font-medium text-sm sm:text-base"
                >
                  Log In
                </button>
              )}
              
              {view !== 'register' && (
                <button
                  onClick={() => setView('register')}
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-4 sm:px-6 py-2 rounded-lg font-medium transition shadow-lg hover:shadow-cyan-500/25 text-sm sm:text-base"
                >
                  Sign Up
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
