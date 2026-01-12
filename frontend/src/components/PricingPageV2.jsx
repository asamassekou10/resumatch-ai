import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, Zap, Crown, Sparkles, ArrowRight } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import ShimmerButton from './ui/ShimmerButton';
import SpotlightCard from './ui/SpotlightCard';
import Footer from './ui/Footer';
import FoundingMemberBanner from './ui/FoundingMemberBanner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const PricingPageV2 = ({ token, userProfile }) => {
  const navigate = useNavigate();
  const [isYearly, setIsYearly] = useState(false);
  const [loading, setLoading] = useState(false);

  const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        delay: i * 0.15,
        ease: 'easeOut'
      }
    })
  };

  // Generic handler for all tier upgrades
  const handleUpgrade = async (tier) => {
    if (!token) {
      navigate(ROUTES.LOGIN);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/payments/create-checkout-session?tier=${tier}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Redirect to Stripe checkout
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to start checkout. Please try again.';
      const details = error.response?.data?.details;
      alert(`${errorMessage}${details ? `\n\nDetails: ${details}` : ''}\n\nIf this problem persists, please contact support@resumeanalyzerai.com`);
      setLoading(false);
    }
  };

  // Handle upgrade to Pro Founding Member
  const handleUpgradeToProFounding = () => handleUpgrade('pro_founding');

  // Handle upgrade to Elite
  const handleUpgradeToElite = () => handleUpgrade('elite');

  // Normalize subscription tier
  const normalizedTier = userProfile?.subscription_tier === 'premium'
    ? 'pro'
    : (userProfile?.subscription_tier || 'free');

  // Determine button configuration based on user's current plan
  const getButtonConfig = (planName) => {
    const lowerPlan = planName.toLowerCase();

    if (!token) {
      if (lowerPlan === 'free') {
        return {
          text: 'Start Free',
          action: () => navigate(ROUTES.GUEST_ANALYZE),
          variant: 'secondary',
          disabled: false
        };
      }
      return {
        text: 'Sign Up to Purchase',
        action: () => navigate(ROUTES.REGISTER),
        variant: lowerPlan === '7-day pass' ? 'primary' : 'secondary',
        disabled: false
      };
    }

    if (lowerPlan === 'free') {
      return {
        text: 'Start Analyzing',
        action: () => navigate(ROUTES.ANALYZE),
        variant: 'secondary',
        disabled: false
      };
    }

    if (lowerPlan === 'pay per scan') {
      return {
        text: 'Buy $1.99 Scan',
        action: () => navigate(ROUTES.ANALYZE),
        variant: 'secondary',
        disabled: loading
      };
    }

    if (lowerPlan === '7-day pass') {
      return {
        text: 'Get 7-Day Pass',
        action: () => navigate(ROUTES.ANALYZE),
        variant: 'primary',
        disabled: loading
      };
    }

    if (lowerPlan === 'pro monthly') {
      return {
        text: 'Subscribe to Pro',
        action: () => handleUpgrade('pro'),
        variant: 'secondary',
        disabled: loading
      };
    }
  };

  const plans = [
    {
      name: 'Free',
      description: 'Perfect to get started',
      monthlyPrice: 0,
      yearlyPrice: 0,
      credits: 1,
      features: [
        'First scan completely free',
        'Full analysis with results',
        'ATS score & feedback',
        'See all missing keywords',
        'AI recommendations',
        'No credit card required'
      ],
      notIncluded: ['Additional scans', 'Unlimited access'],
      highlighted: false,
      icon: Sparkles
    },
    {
      name: 'Pay Per Scan',
      description: 'Quick unlock when you need it',
      monthlyPrice: 1.99,
      yearlyPrice: 0,
      credits: 1,
      features: [
        'One-time payment',
        'Unlock single analysis',
        'All missing keywords revealed',
        'Full AI recommendations',
        'ATS optimization tips',
        'No subscription needed',
        '💰 Under $2 - instant access'
      ],
      notIncluded: ['Unlimited scans'],
      highlighted: false,
      icon: Zap,
      badge: 'MOST POPULAR',
      specialNote: 'Perfect for quick resume updates'
    },
    {
      name: '7-Day Pass',
      description: 'Best for active job hunting',
      monthlyPrice: 6.99,
      yearlyPrice: 0,
      credits: 'unlimited',
      features: [
        'Unlimited scans for 7 days',
        'Test multiple resume versions',
        'Try different job descriptions',
        'Full analysis every time',
        'All keywords & recommendations',
        'ATS optimization included',
        '🚀 Best value - save vs 3+ scans'
      ],
      notIncluded: ['Monthly subscription'],
      highlighted: true,
      icon: Crown,
      badge: 'BEST VALUE',
      specialNote: 'Save $3+ compared to 4 single scans'
    },
    {
      name: 'Pro Monthly',
      description: 'For serious job seekers',
      monthlyPrice: 19.99,
      yearlyPrice: 199.99,
      credits: 'unlimited',
      features: [
        'Unlimited scans forever',
        'Everything in 7-Day Pass',
        'Premium resume templates',
        'Cover letter generation',
        'Priority AI processing',
        'Advanced analytics',
        'Priority support'
      ],
      notIncluded: [],
      highlighted: false,
      icon: Crown,
      specialNote: 'Cancel anytime - no commitments'
    }
  ];

  const calculatePrice = (plan) => {
    if (isYearly) {
      return plan.yearlyPrice;
    }
    return plan.monthlyPrice;
  };

  const calculateSavings = (plan) => {
    if (!isYearly || plan.monthlyPrice === 0) return 0;
    const monthlyTotal = plan.monthlyPrice * 12;
    const savings = monthlyTotal - plan.yearlyPrice;
    const percentage = Math.round((savings / monthlyTotal) * 100);
    return { savings, percentage };
  };

  return (
    <>
      <SEO
        title="Pricing Plans"
        description="Start free, then pay only when you need it. $1.99 per scan or $6.99 for 7-day unlimited access. No monthly commitments required. AI-powered resume analysis with ATS scoring."
        keywords="pricing, pay per scan, resume analyzer pricing, AI career tools pricing, affordable resume analysis, $1.99 resume scan"
        url="https://resumeanalyzerai.com/pricing"
      />
      <div className="min-h-screen bg-black relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        <div className="relative max-w-7xl mx-auto z-10">
          {/* Header */}
        <motion.div
          className="text-center mb-12 relative z-10"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          custom={0}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4 font-display relative z-10">
            Pay only when you need it
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto relative z-10">
            Start free. Then unlock scans for $1.99 each, or get unlimited access for 7 days at $6.99. No monthly commitments.
          </p>
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          className="flex justify-center items-center gap-4 mb-12 relative z-10"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          custom={1}
        >
          <span className={`text-sm font-semibold transition-colors ${!isYearly ? 'text-white' : 'text-gray-400'}`}>
            Monthly
          </span>
          <motion.button
            onClick={() => setIsYearly(!isYearly)}
            className="relative inline-flex items-center h-10 w-20 bg-white/10 rounded-full p-1 transition-colors hover:bg-white/20"
            whileHover={{ scale: 1.05 }}
          >
            <motion.div
              className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-lg"
              layout
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </motion.button>
          <span className={`text-sm font-semibold transition-colors ${isYearly ? 'text-white' : 'text-gray-400'}`}>
            Yearly
          </span>
          {isYearly && (
            <motion.span
              className="ml-4 px-3 py-1 bg-gradient-to-r from-blue-500/20 to-blue-600/20 text-blue-400 text-xs font-semibold rounded-full border border-blue-500/30"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              Save up to 16%
            </motion.span>
          )}
        </motion.div>

        {/* Founding Member Banner */}
        <motion.div
          className="max-w-4xl mx-auto mb-8 relative z-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <FoundingMemberBanner />
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto mb-12 relative z-10">
          {plans.map((plan, i) => {
            const IconComponent = plan.icon;
            const price = calculatePrice(plan);
            const savings = calculateSavings(plan);
            const showSavings = isYearly && savings.savings > 0;

            return (
              <motion.div
                key={i}
                className="relative"
                initial="hidden"
                animate="visible"
                variants={fadeInUp}
                custom={i + 2}
              >
                {plan.highlighted && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-2xl blur-xl z-0 pointer-events-none"
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                )}

                <SpotlightCard
                  className={`relative h-full rounded-2xl p-8 transition-all duration-300 ${
                    plan.highlighted
                      ? 'border-2 border-blue-500/50 shadow-2xl shadow-blue-900/20'
                      : ''
                  }`}
                >
                  <div className="relative z-10">
                    {/* Badge - Show custom badge if present, otherwise show "POPULAR" for highlighted */}
                    {(plan.badge || plan.highlighted) && (
                      <motion.div
                        className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-20 whitespace-nowrap"
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.3 }}
                      >
                        <span className={`${plan.badge ? 'bg-gradient-to-r from-cyan-600 to-blue-600' : 'bg-blue-600'} text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-lg`}>
                          {plan.badge || 'POPULAR'}
                        </span>
                      </motion.div>
                    )}

                    {/* Plan Header */}
                    <div className="flex items-center gap-3 mb-6 relative z-10">
                      <motion.div
                        className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                      >
                        <IconComponent className="w-6 h-6 text-white" />
                      </motion.div>
                      <div>
                        <h3 className="text-xl font-bold text-white font-display relative z-10">{plan.name}</h3>
                        <p className="text-sm text-gray-400 relative z-10">{plan.description}</p>
                      </div>
                    </div>

                    {/* Price */}
                    <div className="mb-6 relative z-10">
                      <motion.div
                        key={`${price}-${isYearly}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <span className="text-4xl font-bold text-white font-display relative z-10">${price.toFixed(2)}</span>
                        <span className="text-gray-400 text-base font-normal font-sans ml-2 relative z-10">
                          {price === 0 ? '' : plan.name === 'Pay Per Scan' || plan.name === '7-Day Pass' ? '' : isYearly ? '/year' : '/mo'}
                        </span>
                      </motion.div>

                      {/* One-time payment label */}
                      {(plan.name === 'Pay Per Scan' || plan.name === '7-Day Pass') && (
                        <p className="text-cyan-400 text-sm font-semibold mt-2 relative z-10">
                          One-time payment
                        </p>
                      )}

                      {showSavings && (
                        <motion.p
                          className="text-green-400 text-sm font-semibold mt-2 relative z-10"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          Save ${savings.savings.toFixed(2)} ({savings.percentage}%)
                        </motion.p>
                      )}
                      {/* Special savings for Pro Founding and Elite */}
                      {plan.name === 'Pro Founding' && !isYearly && (
                        <motion.div
                          className="mt-2 relative z-10"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="text-gray-400 text-sm">
                            Regular price: <span className="line-through text-gray-500">$24.99/mo</span>
                          </p>
                          <p className="text-green-400 text-sm font-semibold">
                            💰 Save $5/month forever
                          </p>
                        </motion.div>
                      )}
                      {plan.name === 'Elite' && !isYearly && (
                        <motion.div
                          className="mt-2 relative z-10"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="text-gray-400 text-sm">
                            Best for professionals
                          </p>
                          <p className="text-cyan-400 text-sm font-semibold">
                            ⚡ Premium features included
                          </p>
                        </motion.div>
                      )}
                    </div>

                    {/* CTA Button */}
                    {(() => {
                      const buttonConfig = getButtonConfig(plan.name);
                      if (buttonConfig.variant === 'primary' && !buttonConfig.disabled) {
                        return (
                          <div className="mb-8 relative z-10">
                            <ShimmerButton
                              onClick={buttonConfig.action}
                              disabled={buttonConfig.disabled}
                              className="w-full"
                            >
                              {buttonConfig.text} {!buttonConfig.disabled && <ArrowRight size={16} />}
                            </ShimmerButton>
                          </div>
                        );
                      }
                      return (
                        <motion.button
                          onClick={buttonConfig.action}
                          disabled={buttonConfig.disabled}
                          className={`w-full py-3 rounded-lg font-bold mb-8 flex items-center justify-center gap-2 transition-all duration-300 border border-white/20 text-white hover:bg-white hover:text-black relative z-10 ${
                            buttonConfig.disabled ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                          whileHover={buttonConfig.disabled ? {} : { scale: 1.02 }}
                          whileTap={buttonConfig.disabled ? {} : { scale: 0.98 }}
                        >
                          {buttonConfig.text}
                        </motion.button>
                      );
                    })()}

                    {/* Features */}
                    <div className="space-y-4 border-t border-white/10 pt-8 relative z-10">
                      {/* Included Features */}
                      {plan.features.map((feature, j) => (
                        <motion.div
                          key={j}
                          className="flex items-center gap-2 relative z-10"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: j * 0.05 }}
                        >
                          <CheckCircle size={16} className={plan.highlighted ? 'text-blue-400' : 'text-white'} />
                          <span className={`text-sm ${plan.highlighted ? 'text-gray-300' : 'text-gray-400'} relative z-10`}>{feature}</span>
                        </motion.div>
                      ))}

                      {/* Not Included Features */}
                      {plan.notIncluded.length > 0 && (
                        <>
                          <div className="border-t border-white/10 pt-4 mt-4" />
                          {plan.notIncluded.map((feature, j) => (
                            <motion.div
                              key={`not-${j}`}
                              className="flex items-center gap-2 opacity-60 relative z-10"
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 0.6, x: 0 }}
                              transition={{ delay: (plan.features.length + j) * 0.05 }}
                            >
                              <CheckCircle size={16} className="text-white" />
                              <span className="text-gray-400 text-sm relative z-10">{feature}</span>
                            </motion.div>
                          ))}
                        </>
                      )}
                    </div>
                  </div>
                </SpotlightCard>
              </motion.div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <motion.div
          className="max-w-3xl mx-auto relative z-10"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <h2 className="text-3xl font-bold text-white text-center mb-8 font-display relative z-10">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              {
                q: 'Can I change plans anytime?',
                a: 'Yes! Upgrade or downgrade your plan at any time. Changes take effect on your next billing cycle.'
              },
              {
                q: 'What payment methods do you accept?',
                a: 'We accept all major credit cards (Visa, Mastercard, American Express) and process payments securely through Stripe.'
              },
              {
                q: 'Do unused credits roll over?',
                a: 'Credits renew monthly on your billing date. Unused credits expire at the end of each month.'
              },
              {
                q: 'Is there a refund policy?',
                a: 'We offer a 30-day money-back guarantee. If you\'re not satisfied, contact our support team for a full refund.'
              }
            ].map((faq, i) => (
              <SpotlightCard key={i} className="rounded-xl p-6 relative z-10">
                <h3 className="font-semibold text-white mb-2 relative z-10 font-display">{faq.q}</h3>
                <p className="text-gray-400 text-sm relative z-10">{faq.a}</p>
              </SpotlightCard>
            ))}
          </div>
        </motion.div>

        {/* Footer CTA */}
        <motion.div
          className="text-center mt-16 relative z-10"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <p className="text-gray-400 text-sm relative z-10">
            All plans include secure payment processing via Stripe. Cancel anytime, no questions asked.
          </p>
        </motion.div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default PricingPageV2;
