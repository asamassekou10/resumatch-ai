import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';

/**
 * StickyCTABar Component
 * Sticky CTA bar that appears at bottom of page on mobile
 */
const StickyCTABar = ({ className = '' }) => {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5 }}
      className={`fixed bottom-0 left-0 right-0 z-50 md:hidden ${className}`}
    >
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-t border-white/10 backdrop-blur-xl shadow-2xl">
        <div className="px-4 py-3 flex items-center justify-between gap-3">
          <div className="flex-1">
            <p className="text-white font-semibold text-sm">Ready to optimize your resume?</p>
            <p className="text-gray-400 text-xs">Get started in 30 seconds</p>
          </div>
          <ShimmerButton
            onClick={() => navigate(ROUTES.GUEST_ANALYZE)}
            className="px-6 py-2.5 text-sm whitespace-nowrap"
          >
            Try Free <ArrowRight className="w-4 h-4" />
          </ShimmerButton>
        </div>
      </div>
    </motion.div>
  );
};

export default StickyCTABar;
