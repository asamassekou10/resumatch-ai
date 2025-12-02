import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Gift, LogIn, Zap, Clock } from 'lucide-react';

const GuestModeBanner = ({ isGuest, guestCreditsRemaining, timeRemaining, onUpgrade, onLogin, onDismiss }) => {
  const [displayTime, setDisplayTime] = useState(timeRemaining);

  useEffect(() => {
    if (isGuest && timeRemaining > 0) {
      const timer = setInterval(() => {
        setDisplayTime(prev => Math.max(0, prev - 1));
      }, 60000); // Update every minute
      return () => clearInterval(timer);
    }
  }, [isGuest, timeRemaining]);

  if (!isGuest) return null;

  const hours = Math.floor(displayTime / 60);
  const minutes = displayTime % 60;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-gradient-to-r from-purple-600/90 to-cyan-600/90 backdrop-blur-sm border border-purple-400/50 rounded-lg p-4 mb-6"
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Left: Status Info */}
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0">
              <Gift className="w-6 h-6 text-yellow-300" />
            </div>
            <div>
              <p className="text-white font-semibold text-sm sm:text-base">
                You're using Guest Mode
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs sm:text-sm text-white/90">
                <div className="flex items-center gap-1">
                  <Zap className="w-4 h-4" />
                  <span>{guestCreditsRemaining} credits remaining</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{hours}h {minutes}m left</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Action Buttons */}
          <div className="flex items-center gap-3">
            <motion.button
              onClick={onLogin}
              className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white font-semibold text-sm transition-colors flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <LogIn className="w-4 h-4" />
              Sign In
            </motion.button>
            <motion.button
              onClick={onUpgrade}
              className="px-4 py-2 rounded-lg bg-white text-purple-600 hover:bg-purple-50 font-semibold text-sm transition-colors flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Zap className="w-4 h-4" />
              Upgrade
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default GuestModeBanner;
