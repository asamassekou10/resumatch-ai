import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';

/**
 * FloatingCTAButton Component
 * Floating CTA button that appears on desktop (bottom-right)
 */
const FloatingCTAButton = ({ className = '' }) => {
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Show after user scrolls down 300px
    const handleScroll = () => {
      if (window.scrollY > 300 && !dismissed) {
        setShow(true);
      } else if (window.scrollY <= 300) {
        setShow(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [dismissed]);

  if (dismissed) return null;

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ type: 'spring', damping: 20 }}
          className={`fixed bottom-6 right-6 z-50 hidden md:block ${className}`}
        >
          <div className="relative">
            <ShimmerButton
              onClick={() => navigate(ROUTES.GUEST_ANALYZE)}
              className="px-6 py-3 text-sm font-bold shadow-2xl"
            >
              Try Free <ArrowRight className="w-4 h-4 ml-1" />
            </ShimmerButton>
            <button
              onClick={() => {
                setDismissed(true);
                setShow(false);
              }}
              className="absolute -top-2 -right-2 w-6 h-6 bg-slate-700 hover:bg-slate-600 rounded-full flex items-center justify-center text-white transition"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FloatingCTAButton;
