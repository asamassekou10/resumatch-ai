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
        // Default to showing some spots remaining on error
        setSpotsRemaining(85);
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
      <div className={`bg-red-50 border border-red-200 rounded-lg p-3 ${className}`}>
        <div className="flex items-center gap-2 text-red-700">
          <Users className="w-5 h-5" />
          <span className="font-semibold">Founding Member tier is full!</span>
        </div>
        <p className="text-sm text-red-600 mt-1">
          All 100 spots claimed. Pro tier now available at $24.99/month.
        </p>
      </div>
    );
  }

  const percentRemaining = (spotsRemaining / 100) * 100;
  const urgencyLevel = percentRemaining < 20 ? 'high' : percentRemaining < 50 ? 'medium' : 'low';

  const urgencyColors = {
    high: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
      accent: 'text-red-600',
      pulse: 'bg-red-500'
    },
    medium: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-orange-700',
      accent: 'text-orange-600',
      pulse: 'bg-orange-500'
    },
    low: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-700',
      accent: 'text-blue-600',
      pulse: 'bg-blue-500'
    }
  };

  const colors = urgencyColors[urgencyLevel];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`${colors.bg} border ${colors.border} rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="relative">
              <Users className={`w-5 h-5 ${colors.text}`} />
              {urgencyLevel === 'high' && (
                <motion.div
                  className={`absolute -top-1 -right-1 w-2 h-2 ${colors.pulse} rounded-full`}
                  animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </div>
            <span className={`font-bold ${colors.text}`}>
              {spotsRemaining} / 100 Founding Member Spots Left
            </span>
          </div>

          <p className={`text-sm ${colors.accent}`}>
            {urgencyLevel === 'high' && '🔥 Almost gone! '}
            Lock in $19.99/month forever. Regular price $24.99.
          </p>

          {/* Progress bar */}
          <div className="mt-3 bg-white/50 rounded-full h-2 overflow-hidden">
            <motion.div
              className={`h-full ${colors.pulse}`}
              initial={{ width: 0 }}
              animate={{ width: `${percentRemaining}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>
        </div>

        {urgencyLevel === 'high' && (
          <div className="flex items-center gap-1 text-sm">
            <Clock className={`w-4 h-4 ${colors.accent}`} />
            <span className={`font-semibold ${colors.accent}`}>Hurry!</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default FoundingMemberBanner;
