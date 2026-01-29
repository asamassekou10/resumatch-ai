import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';

/**
 * ProTrialBanner Component
 * Professional banner for free users to encourage Pro subscription with 7-day free trial
 * No emojis, respects web app branding (blue theme)
 */
const ProTrialBanner = ({ className = '' }) => {
  const navigate = useNavigate();

  const handleStartTrial = () => {
    navigate(`${ROUTES.CHECKOUT}?tier=pro_founding`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-500/20 via-blue-600/20 to-cyan-500/20 backdrop-blur-sm border border-blue-500/30 ${className}`}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent" />
      
      <div className="relative p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          {/* Left Content */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Star className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-1">
                  Unlock Pro Features with 7-Day Free Trial
                </h3>
                <p className="text-sm text-gray-300">
                  Experience unlimited scans, AI optimization, and premium tools
                </p>
              </div>
            </div>

            {/* Features Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span>Unlimited scans</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span>AI optimization</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span>Cover letters</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span>Priority support</span>
              </div>
            </div>
          </div>

          {/* Right CTA */}
          <div className="flex-shrink-0">
            <ShimmerButton
              onClick={handleStartTrial}
              className="w-full md:w-auto"
            >
              <div className="flex items-center gap-2">
                <span>Start Free Trial</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </ShimmerButton>
            <p className="text-xs text-gray-400 text-center md:text-right mt-2">
              No credit card required • Cancel anytime
            </p>
          </div>
        </div>
      </div>

    </motion.div>
  );
};

export default ProTrialBanner;
