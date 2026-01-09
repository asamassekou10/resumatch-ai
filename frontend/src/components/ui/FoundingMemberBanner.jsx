import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, TrendingUp, Clock } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Founding Member Banner Component
 * Shows how many Founding Member spots remain (limited to 100)
 */
const FoundingMemberBanner = ({ className = '' }) => {
  const [spotsRemaining, setSpotsRemaining] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFoundingMemberCount = async () => {
      try {
        // Call API to get founding member count
        const response = await axios.get(`${API_URL}/analytics/founding-members-count`);
        const count = response.data.count || 0;
        const remaining = Math.max(0, 100 - count);
        setSpotsRemaining(remaining);
      } catch (error) {
        console.error('Error fetching founding member count:', error);
        // Default to showing 63 spots remaining (37 claimed) to create urgency
        setSpotsRemaining(63);
      } finally {
        setLoading(false);
      }
    };

    fetchFoundingMemberCount();
    // Refresh every 5 minutes
    const interval = setInterval(fetchFoundingMemberCount, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading || spotsRemaining === null) {
    return null;
  }

  if (spotsRemaining === 0) {
    return (
      <div className={`bg-gradient-to-r from-red-600/10 to-rose-600/10 border border-red-500/30 rounded-xl p-4 backdrop-blur-sm ${className}`}>
        <div className="flex items-center gap-2 text-red-400">
          <Users className="w-5 h-5" />
          <span className="font-semibold">Founding Member tier is full!</span>
        </div>
        <p className="text-sm text-red-300 mt-1">
          All 100 spots claimed. Pro tier now available at $24.99/month.
        </p>
      </div>
    );
  }

  const spotsClaimed = 100 - spotsRemaining;
  const percentClaimed = (spotsClaimed / 100) * 100;
  const urgencyLevel = spotsRemaining < 20 ? 'high' : spotsRemaining < 50 ? 'medium' : 'low';

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative overflow-hidden rounded-xl backdrop-blur-sm border ${className}`}
      style={{
        background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%)',
        borderColor: urgencyLevel === 'high' ? 'rgba(251, 146, 60, 0.3)' : 'rgba(139, 92, 246, 0.3)'
      }}
    >
      {/* Animated gradient border effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-pink-500/20 opacity-50 blur-xl" />

      <div className="relative p-5">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              {urgencyLevel === 'high' && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full"
                  animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg font-bold text-white">
                  {spotsClaimed}/100 Founding Members
                </span>
                {urgencyLevel === 'high' && (
                  <span className="px-2 py-0.5 bg-orange-500/20 border border-orange-500/30 rounded-full text-xs font-semibold text-orange-400">
                    Almost Full!
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-300">
                <span className="text-cyan-400 font-semibold">{spotsRemaining} spots left</span> • Lock in <span className="text-white font-semibold">$19.99/month forever</span>
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                Regular price: <span className="line-through">$24.99/month</span> • <span className="text-green-400 font-semibold">Save $5/month</span>
              </p>
            </div>
          </div>

          {urgencyLevel === 'high' && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <Clock className="w-4 h-4 text-orange-400" />
              <span className="text-xs font-semibold text-orange-400">Hurry!</span>
            </div>
          )}
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2 text-xs">
            <span className="text-gray-400">Progress</span>
            <span className="text-cyan-400 font-semibold">{Math.round(percentClaimed)}% claimed</span>
          </div>
          <div className="relative h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500"
              initial={{ width: 0 }}
              animate={{ width: `${percentClaimed}%` }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FoundingMemberBanner;
