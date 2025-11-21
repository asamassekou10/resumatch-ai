import React from 'react';

const Navigation = ({ view, setView, token, handleLogout, showBackButton = false, backButtonText = "Back", onBackClick }) => {
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
