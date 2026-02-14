import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, Sparkles, ArrowRight, Calendar, Mail } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import ShimmerButton from './ui/ShimmerButton';
import SpotlightCard from './ui/SpotlightCard';
import Footer from './ui/Footer';
import UpsellModal from './ui/UpsellModal';

/**
 * PaymentSuccess Component
 *
 * Celebratory page shown after successful payment.
 * Guides users to their next steps and shows upsell offer for 7-Day Pass purchases.
 */
const PaymentSuccess = ({ token, userProfile }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [showUpsellModal, setShowUpsellModal] = useState(false);

  const purchaseType = searchParams.get('purchase_type') || 'weekly_pass';
  const sessionId = searchParams.get('session_id');

  // Show upsell modal after 2 seconds for 7-Day Pass purchases
  useEffect(() => {
    if (purchaseType === 'weekly_pass' && token) {
      const timer = setTimeout(() => {
        setShowUpsellModal(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [purchaseType, token]);

  // Get purchase details
  const getPurchaseDetails = () => {
    switch (purchaseType) {
      case 'weekly_pass':
        return {
          title: '7-Day Unlimited Pass',
          price: '$6.99',
          duration: '7 days',
          icon: Calendar,
          features: [
            'Unlimited resume scans for 7 days',
            'All keywords & AI recommendations',
            'Test multiple resume versions',
            'Full ATS optimization',
            'Priority support'
          ],
          nextSteps: [
            'Upload your resume and job description',
            'Get instant ATS compatibility score',
            'Review AI-powered recommendations',
            'Optimize and test multiple versions',
            'Download your improved resume'
          ]
        };
      case 'pro_founding':
        return {
          title: 'Pro Founding Member',
          price: '$19.99/month',
          duration: 'Monthly',
          icon: Sparkles,
          features: [
            '50 analyses per month',
            'Cover letter generation',
            'Unlimited resume templates',
            'Priority support',
            'Founding member badge'
          ],
          nextSteps: [
            'Explore your dashboard',
            'Start your first analysis',
            'Generate a cover letter',
            'Browse premium templates',
            'Join our community'
          ]
        };
      case 'elite':
        return {
          title: 'Elite Plan',
          price: '$49.99/month',
          duration: 'Monthly',
          icon: Sparkles,
          features: [
            '200 analyses per month',
            'API access & bulk uploads',
            'White-label options',
            'Dedicated account manager',
            'Priority support'
          ],
          nextSteps: [
            'Access your API keys',
            'Set up bulk upload',
            'Configure white-label settings',
            'Schedule onboarding call',
            'Start analyzing'
          ]
        };
      default:
        return {
          title: 'Pro Subscription',
          price: '$19.99/month',
          duration: 'Monthly',
          icon: Sparkles,
          features: ['Unlimited features'],
          nextSteps: ['Start analyzing']
        };
    }
  };

  const details = getPurchaseDetails();
  const IconComponent = details.icon;

  return (
    <>
      <SEO
        title="Payment Successful - Welcome!"
        description="Thank you for your purchase. Your account is now activated."
        noindex={true}
      />

      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        <div className="relative max-w-4xl mx-auto px-4 py-12 sm:py-16 z-10">
          {/* Success Icon & Title */}
          <motion.div
            className="text-center mb-12"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', duration: 0.6, delay: 0.2 }}
          >
            <div className="inline-block mb-6 relative">
              <motion.div
                className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <div className="relative bg-gradient-to-br from-blue-500 to-cyan-500 p-6 rounded-full">
                <CheckCircle className="w-16 h-16 text-white" />
              </div>
            </div>

            <motion.h1
              className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4 font-display"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              Payment Successful
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-gray-300 mb-2"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Welcome to <span className="text-cyan-400 font-semibold">{details.title}</span>
            </motion.p>

            <motion.p
              className="text-sm text-gray-400"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              Your account is now active and ready to use
            </motion.p>
          </motion.div>

          {/* Purchase Summary */}
          <motion.div
            className="mb-8"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <SpotlightCard className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-2xl p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                    <IconComponent className="w-6 h-6 text-cyan-400" />
                    {details.title}
                  </h2>
                  <p className="text-cyan-400 text-lg font-semibold">{details.price}</p>
                </div>
                <div className="text-right">
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-semibold">
                    Active
                  </span>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-400 mb-3">What You Get:</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {details.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-white/10">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Mail className="w-4 h-4" />
                  <span>Confirmation email sent to your inbox</span>
                </div>
              </div>
            </SpotlightCard>
          </motion.div>

          {/* What's Next */}
          <motion.div
            className="mb-8"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <h2 className="text-2xl font-bold text-white mb-6 text-center">What's Next?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {details.nextSteps.slice(0, 3).map((step, index) => (
                <SpotlightCard key={index} className="rounded-xl p-6">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                    <p className="text-sm text-gray-300 leading-relaxed">{step}</p>
                  </div>
                </SpotlightCard>
              ))}
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            <ShimmerButton
              onClick={() => navigate(purchaseType === 'weekly_pass' ? ROUTES.GUEST_ANALYZE : ROUTES.ANALYZE)}
              className="px-8 py-4 text-lg"
            >
              <span className="flex items-center gap-2">
                Start Your First Analysis
                <ArrowRight className="w-5 h-5" />
              </span>
            </ShimmerButton>

            {token && (
              <motion.button
                onClick={() => navigate(ROUTES.DASHBOARD)}
                className="px-8 py-4 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg text-white font-semibold transition-all"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                View Dashboard
              </motion.button>
            )}
          </motion.div>

          {/* Support Info */}
          <motion.div
            className="mt-12 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            <p className="text-sm text-gray-400 mb-2">
              Need help getting started?
            </p>
            <p className="text-sm text-gray-500">
              Contact us at{' '}
              <a
                href="mailto:support@resumeanalyzerai.com"
                className="text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                support@resumeanalyzerai.com
              </a>
            </p>
          </motion.div>
        </div>
      </div>

      <Footer />

      {/* Upsell Modal - Shows for 7-Day Pass purchases only */}
      <UpsellModal
        isOpen={showUpsellModal}
        onClose={() => setShowUpsellModal(false)}
        currentPlan={purchaseType}
        token={token}
      />
    </>
  );
};

export default PaymentSuccess;
