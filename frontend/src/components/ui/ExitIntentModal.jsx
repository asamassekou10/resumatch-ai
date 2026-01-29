import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Percent, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import ShimmerButton from './ShimmerButton';
import { trackExitIntent, trackEvent, CONVERSION_EVENTS } from '../../utils/conversionTracking';

/**
 * ExitIntentModal Component
 * Detects when user is about to leave and shows special offer
 * Only shows once per session
 */
const ExitIntentModal = ({ pageName = 'landing', onClose, className = '' }) => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [hasShown, setHasShown] = useState(false);

  useEffect(() => {
    // Check if already shown in this session
    const shownInSession = sessionStorage.getItem('exit_intent_shown');
    if (shownInSession === 'true') {
      return;
    }

    // Track mouse movement toward top of page (exit intent)
    const handleMouseLeave = (e) => {
      // Only trigger if mouse is moving upward (toward browser close button)
      if (e.clientY <= 0 && !hasShown && !shownInSession) {
        setShowModal(true);
        setHasShown(true);
        sessionStorage.setItem('exit_intent_shown', 'true');
        trackExitIntent(pageName);
      }
    };

    // Also track on beforeunload as fallback
    const handleBeforeUnload = () => {
      if (!hasShown && !shownInSession) {
        trackExitIntent(pageName);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasShown, pageName]);

  const handleClose = () => {
    setShowModal(false);
    if (onClose) {
      onClose();
    }
  };

  const handleClaimOffer = () => {
    trackEvent(CONVERSION_EVENTS.UPGRADE_CLICKED, {
      source: 'exit_intent_modal',
      page_name: pageName
    });
    navigate(ROUTES.PRICING);
    handleClose();
  };

  const handleTryFree = () => {
    trackEvent(CONVERSION_EVENTS.UPGRADE_CLICKED, {
      source: 'exit_intent_modal_free',
      page_name: pageName
    });
    navigate(ROUTES.GUEST_ANALYZE);
    handleClose();
  };

  return (
    <AnimatePresence>
      {showModal && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${className}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl border border-blue-500/30 shadow-2xl max-w-md w-full overflow-hidden">
              {/* Close button */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition z-10"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Content */}
              <div className="p-8">
                {/* Badge */}
                <div className="flex items-center justify-center mb-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-orange-500/20 to-red-500/20 border border-orange-500/30">
                    <Percent className="w-4 h-4 text-orange-400" />
                    <span className="text-xs font-semibold text-orange-300">Special Offer</span>
                  </div>
                </div>

                {/* Heading */}
                <h2 className="text-2xl font-bold text-white text-center mb-3 font-display">
                  Wait! Don't Miss Out
                </h2>

                {/* Offer */}
                <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-4 mb-6">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Percent className="w-6 h-6 text-blue-400" />
                    <span className="text-3xl font-bold text-white">20% OFF</span>
                  </div>
                  <p className="text-center text-gray-300 text-sm">
                    Your first purchase - Limited time offer
                  </p>
                </div>

                {/* Benefits */}
                <div className="space-y-2 mb-6">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    <span>Unlimited scans for 7 days</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    <span>AI-powered optimization</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    <span>Priority support</span>
                  </div>
                </div>

                {/* CTAs */}
                <div className="space-y-3">
                  <ShimmerButton
                    onClick={handleClaimOffer}
                    className="w-full"
                  >
                    <div className="flex items-center justify-center gap-2">
                      <span>Claim 20% Off Now</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </ShimmerButton>

                  <button
                    onClick={handleTryFree}
                    className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition"
                  >
                    Try Free First
                  </button>
                </div>

                {/* Trust signal */}
                <p className="text-xs text-center text-gray-500 mt-4">
                  No credit card required for free trial
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default ExitIntentModal;
