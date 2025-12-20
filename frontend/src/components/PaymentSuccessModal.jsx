import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Sparkles, Crown, Zap } from 'lucide-react';

const TIER_INFO = {
  pro: {
    name: 'Pro',
    credits: 100,
    color: 'from-cyan-500 to-purple-600',
    bgColor: 'bg-gradient-to-r from-cyan-500/20 to-purple-600/20',
    borderColor: 'border-cyan-500/50',
    textColor: 'text-cyan-400',
    features: [
      '100 AI Credits/month',
      'Resume Analysis & Optimization',
      'Job Match Scoring',
      'Skills Gap Analysis',
      'Priority Support'
    ]
  },
  elite: {
    name: 'Elite',
    credits: 1000,
    color: 'from-amber-500 to-orange-600',
    bgColor: 'bg-gradient-to-r from-amber-500/20 to-orange-600/20',
    borderColor: 'border-amber-500/50',
    textColor: 'text-amber-400',
    features: [
      '1000 AI Credits/month',
      'Everything in Pro',
      'Unlimited Analyses',
      'Cover Letter Generation',
      '24/7 Priority Support',
      'Custom AI Feedback'
    ]
  }
};

const PaymentSuccessModal = ({ isOpen, onClose, tier = 'pro', userCredits }) => {
  const tierInfo = TIER_INFO[tier] || TIER_INFO.pro;
  const IconComponent = tier === 'elite' ? Crown : Zap;

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - no click to dismiss */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className={`relative w-full max-w-md bg-slate-900 rounded-2xl border ${tierInfo.borderColor} shadow-2xl overflow-hidden`}>
              {/* Animated background glow */}
              <div className={`absolute inset-0 ${tierInfo.bgColor} opacity-30`} />
              
              {/* Confetti/sparkle effect */}
              <div className="absolute inset-0 overflow-hidden">
                {[...Array(20)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ 
                      opacity: 0, 
                      y: -20, 
                      x: Math.random() * 400 - 200,
                      rotate: Math.random() * 360 
                    }}
                    animate={{ 
                      opacity: [0, 1, 0], 
                      y: [0, 400],
                      rotate: Math.random() * 720
                    }}
                    transition={{ 
                      duration: 2 + Math.random() * 2, 
                      delay: Math.random() * 0.5,
                      repeat: Infinity,
                      repeatDelay: Math.random() * 3
                    }}
                    className={`absolute w-2 h-2 ${tier === 'elite' ? 'bg-amber-400' : 'bg-cyan-400'} rounded-full`}
                    style={{ left: `${Math.random() * 100}%` }}
                  />
                ))}
              </div>

              {/* Content */}
              <div className="relative p-8 text-center">
                {/* Success icon */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', delay: 0.2, damping: 15 }}
                  className="flex justify-center mb-6"
                >
                  <div className={`relative p-4 rounded-full bg-gradient-to-r ${tierInfo.color}`}>
                    <CheckCircle className="w-12 h-12 text-white" />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="absolute inset-0 rounded-full bg-white/20"
                    />
                  </div>
                </motion.div>

                {/* Title */}
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-2xl font-bold text-white mb-2"
                >
                  Welcome to {tierInfo.name}!
                </motion.h2>

                {/* Subtitle */}
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-slate-400 mb-6"
                >
                  Your subscription is now active. Thank you for upgrading!
                </motion.p>

                {/* Credits display */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className={`inline-flex items-center gap-3 px-6 py-3 rounded-xl ${tierInfo.bgColor} border ${tierInfo.borderColor} mb-6`}
                >
                  <IconComponent className={`w-6 h-6 ${tierInfo.textColor}`} />
                  <div className="text-left">
                    <p className="text-xs text-slate-400">Your Credits</p>
                    <p className={`text-xl font-bold ${tierInfo.textColor}`}>
                      {userCredits || tierInfo.credits} Credits
                    </p>
                  </div>
                </motion.div>

                {/* Features list */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="text-left mb-8 space-y-2"
                >
                  <p className="text-sm text-slate-400 mb-3">Your {tierInfo.name} benefits:</p>
                  {tierInfo.features.slice(0, 4).map((feature, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                      className="flex items-center gap-2 text-sm text-slate-300"
                    >
                      <Sparkles className={`w-4 h-4 ${tierInfo.textColor}`} />
                      {feature}
                    </motion.div>
                  ))}
                </motion.div>

                {/* CTA Button */}
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={onClose}
                  className={`w-full py-4 px-6 rounded-xl bg-gradient-to-r ${tierInfo.color} text-white font-semibold text-lg shadow-lg hover:shadow-xl transition-shadow`}
                >
                  Get Started
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default PaymentSuccessModal;

