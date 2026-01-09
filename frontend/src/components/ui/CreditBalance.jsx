import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, TrendingUp, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * Credit Balance Display Component
 * Shows user's current credit balance with visual indicators
 */
const CreditBalance = ({ credits = 0, tier = 'free', showUpgrade = true, size = 'md' }) => {
  const navigate = useNavigate();

  // Credit thresholds for visual indicators
  const getCreditStatus = (credits) => {
    if (credits === 0) return 'empty';
    if (credits <= 3) return 'low';
    if (credits <= 10) return 'medium';
    return 'healthy';
  };

  const status = getCreditStatus(credits);

  // Styling based on status
  const statusConfig = {
    empty: {
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      icon: AlertCircle,
      message: 'Out of credits'
    },
    low: {
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      icon: AlertCircle,
      message: 'Low credits'
    },
    medium: {
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      icon: Zap,
      message: 'Running low'
    },
    healthy: {
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      icon: Zap,
      message: 'Good balance'
    }
  };

  const config = statusConfig[status];
  const StatusIcon = config.icon;

  // Size variants
  const sizeClasses = {
    sm: {
      container: 'px-3 py-1.5',
      text: 'text-sm',
      icon: 'w-4 h-4',
      badge: 'text-xs px-2 py-0.5'
    },
    md: {
      container: 'px-4 py-2',
      text: 'text-base',
      icon: 'w-5 h-5',
      badge: 'text-sm px-2.5 py-1'
    },
    lg: {
      container: 'px-6 py-3',
      text: 'text-lg',
      icon: 'w-6 h-6',
      badge: 'text-base px-3 py-1.5'
    }
  };

  const sizeClass = sizeClasses[size];

  return (
    <div className={`flex items-center gap-3 ${config.bgColor} ${config.borderColor} border rounded-lg ${sizeClass.container}`}>
      <StatusIcon className={`${config.color} ${sizeClass.icon}`} />

      <div className="flex-1">
        <div className={`font-semibold ${config.color} ${sizeClass.text}`}>
          {credits} {credits === 1 ? 'Credit' : 'Credits'}
        </div>
        {size !== 'sm' && (
          <div className={`text-xs ${config.color} opacity-75`}>
            {config.message}
          </div>
        )}
      </div>

      {/* Tier badge */}
      <div className={`${sizeClass.badge} bg-white/50 rounded-full font-medium ${config.color} uppercase tracking-wide`}>
        {tier}
      </div>

      {/* Upgrade button for low/empty status */}
      {showUpgrade && (status === 'empty' || status === 'low') && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/pricing')}
          className={`flex items-center gap-1 ${sizeClass.badge} bg-gradient-to-r from-blue-500 to-pink-500 text-white rounded-full font-semibold hover:shadow-lg transition-shadow`}
        >
          Upgrade
          <TrendingUp className="w-3 h-3" />
        </motion.button>
      )}
    </div>
  );
};

export default CreditBalance;
