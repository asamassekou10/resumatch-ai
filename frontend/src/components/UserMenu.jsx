import { useState, useRef, useEffect } from 'react';
import { User, Settings, CreditCard, HelpCircle, LogOut, Crown, ChevronDown } from 'lucide-react';

const UserMenu = ({ user, onLogout, setView }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Don't render if no user (must be after hooks)
  if (!user) return null;

  const creditPercentage = ((user.credits || 0) / 100) * 100;
  const creditColor = creditPercentage > 50 ? 'cyan' : creditPercentage > 20 ? 'yellow' : 'red';

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-800 transition"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm">
          {user.name?.charAt(0).toUpperCase() || 'U'}
        </div>
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium text-white">{user.name || 'User'}</p>
          <p className="text-xs text-slate-400 capitalize">{user.subscription_tier || 'free'} Plan</p>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
          {/* User Info Header */}
          <div className="p-3 border-b border-slate-700">
            <p className="text-sm font-semibold text-white">{user.name}</p>
            <p className="text-xs text-slate-400">{user.email}</p>
          </div>

          {/* Credits */}
          <div className="p-3 border-b border-slate-700">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-slate-400">Credits</span>
              <span className="text-sm font-semibold text-white">{user.credits || 0}/100</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className={`bg-${creditColor}-500 h-2 rounded-full transition-all`}
                style={{ width: `${creditPercentage}%` }}
              ></div>
            </div>
          </div>

          {/* Subscription */}
          {user.subscription_tier !== 'free' && (
            <div className="p-3 border-b border-slate-700">
              <div className="flex items-center gap-2 text-sm">
                <Crown className="w-4 h-4 text-yellow-500" />
                <span className="text-white capitalize">{user.subscription_tier} Plan</span>
              </div>
              {user.subscription_end_date && (
                <p className="text-xs text-slate-400 mt-1">
                  Renews {new Date(user.subscription_end_date).toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {/* Menu Items */}
          <div className="p-1">
            <button
              onClick={() => { setView('profile'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition"
            >
              <User className="w-4 h-4" />
              Profile
            </button>
            <button
              onClick={() => { setView('settings'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition"
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
            <button
              onClick={() => { setView('pricing'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition"
            >
              <CreditCard className="w-4 h-4" />
              Billing & Subscription
            </button>
            <button
              onClick={() => { window.open('/help', '_blank'); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition"
            >
              <HelpCircle className="w-4 h-4" />
              Help & Documentation
            </button>
          </div>

          {/* Logout */}
          <div className="p-1 border-t border-slate-700">
            <button
              onClick={() => { onLogout(); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
