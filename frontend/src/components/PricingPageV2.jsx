import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, FileText, Calendar, Star, Briefcase, ArrowRight } from 'lucide-react';
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

  // Determine button configuration based on user's current plan
  const getButtonConfig = (planName) => {
    const lowerPlan = planName.toLowerCase();

    if (!token) {
      if (lowerPlan === 'free') {
        return {
          text: 'Try Free Now',
          action: () => navigate(ROUTES.GUEST_ANALYZE),
          variant: 'secondary',
          disabled: false
        };
      }
      if (lowerPlan === '7-day pass') {
        return {
          text: 'Get 7-Day Pass - $6.99',
          action: () => navigate(ROUTES.REGISTER),
          variant: 'primary',
          disabled: false
        };
      }
      return {
        text: 'Sign Up to Get Started',
        action: () => navigate(ROUTES.REGISTER),
        variant: 'secondary',
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

    if (lowerPlan === '7-day pass') {
      return {
        text: 'Get Started - $6.99',
        action: () => navigate(ROUTES.ANALYZE),
        variant: 'primary',
        disabled: loading
      };
    }

    if (lowerPlan === 'pro founding') {
      return {
        text: 'Lock In $19.99/mo',
        action: handleUpgradeToProFounding,
        variant: 'primary',
        disabled: loading
      };
    }

    if (lowerPlan === 'elite') {
      return {
        text: 'Get Elite - $49.99/mo',
        action: handleUpgradeToElite,
        variant: 'secondary',
        disabled: loading
      };
    }
  };

  const plans = [
    {
      name: 'Free',
      description: 'Try it risk-free',
      monthlyPrice: 0,
      yearlyPrice: 0,
      credits: 1,
      features: [
        '1 free analysis',
        'ATS score & feedback',
        'Top 3 missing keywords',
        'Basic recommendations'
      ],
      highlighted: false,
      icon: FileText
    },
    {
      name: '7-Day Pass',
      description: 'Best for active job hunting',
      monthlyPrice: 6.99,
      yearlyPrice: 6.99,
      credits: 'unlimited',
      features: [
        'Unlimited scans for 7 days',
        'All keywords & AI recommendations',
        'Test multiple resume versions',
        'Full ATS optimization'
      ],
      highlighted: true,
      icon: Calendar,
      badge: 'BEST VALUE',
      specialNote: 'Perfect for testing multiple resume versions'
    },
    {
      name: 'Pro Founding',
      description: 'Lock in $19.99 forever',
      monthlyPrice: 19.99,
      yearlyPrice: 199.99,
      credits: 50,
      features: [
        '50 analyses/month',
        'Cover letter generation',
        'Unlimited templates',
        'Priority support + Founding badge'
      ],
      highlighted: false,
      icon: Star,
      badge: 'Limited: First 100 Only',
      specialNote: 'Regular price $24.99 - Save $5/month forever'
    },
    {
      name: 'Elite',
      description: 'For recruiters & coaches',
      monthlyPrice: 49.99,
      yearlyPrice: 499.99,
      credits: 200,
      features: [
        '200 analyses/month',
        'API access & bulk uploads',
        'White-label options',
        'Dedicated support'
      ],
      highlighted: false,
      icon: Briefcase
    }
  ];

  const calculatePrice = (plan) => {
    // 7-Day Pass should always show the same price regardless of toggle
    if (plan.name === '7-Day Pass') {
      return plan.monthlyPrice;
    }
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
        description="Start free, then get unlimited scans for 7 days at $6.99 or subscribe monthly. No long-term commitments required. AI-powered resume analysis with ATS scoring."
        keywords="pricing, resume analyzer pricing, AI career tools pricing, affordable resume analysis, 7-day pass, unlimited resume scans"
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
            Simple, flexible pricing
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto relative z-10">
            Start free. Then get unlimited scans for 7 days at $6.99, or subscribe monthly for ongoing access. No long-term commitments.
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
          <button
            onClick={() => setIsYearly(!isYearly)}
            className="relative inline-flex items-center h-10 w-20 bg-white/10 rounded-full p-1 transition-colors hover:bg-white/20"
          >
            <motion.div
              className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-lg"
              initial={false}
              animate={{ x: isYearly ? 40 : 0 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </button>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-12 relative z-10">
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
                  className={`relative rounded-2xl p-6 transition-all duration-300 flex flex-col min-h-[520px] ${
                    plan.highlighted
                      ? 'border-2 border-blue-500/50 shadow-2xl shadow-blue-900/20 scale-105'
                      : ''
                  }`}
                >
                  <div className="relative z-10 flex flex-col h-full">
                    {/* Badge - Show custom badge if present, otherwise show "POPULAR" for highlighted */}
                    {(plan.badge || plan.highlighted) && (
                      <motion.div
                        className="absolute -top-3 left-1/2 transform -translate-x-1/2 z-20 whitespace-nowrap"
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
                    <div className="flex items-center gap-3 mb-4 relative z-10">
                      <motion.div
                        className={`w-12 h-12 bg-gradient-to-br ${plan.highlighted ? 'from-blue-500 to-cyan-500' : 'from-blue-500 to-blue-600'} rounded-lg flex items-center justify-center flex-shrink-0`}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                      >
                        <IconComponent className="w-6 h-6 text-white" />
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-xl font-bold ${plan.highlighted ? 'text-white' : 'text-white'} font-display relative z-10`}>{plan.name}</h3>
                        <p className="text-sm text-gray-400 relative z-10 truncate">{plan.description}</p>
                      </div>
                    </div>

                    {/* Price */}
                    <div className="mb-5 relative z-10">
                      <motion.div
                        key={`${price}-${isYearly}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="flex items-baseline">
                          <span className="text-4xl font-bold text-white font-display relative z-10">${price.toFixed(2)}</span>
                          <span className="text-gray-400 text-base font-normal font-sans ml-2 relative z-10">
                            {price === 0 ? '' : plan.name === '7-Day Pass' ? '' : isYearly ? '/year' : '/mo'}
                          </span>
                        </div>
                      </motion.div>

                      {/* One-time payment label */}
                      {plan.name === '7-Day Pass' && (
                        <p className="text-cyan-400 text-xs font-semibold mt-1 relative z-10">
                          One-time payment
                        </p>
                      )}

                      {showSavings && (
                        <motion.p
                          className="text-green-400 text-xs font-semibold mt-1 relative z-10"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          Save ${savings.savings.toFixed(2)} ({savings.percentage}%)
                        </motion.p>
                      )}
                      {/* Special savings for Pro Founding */}
                      {plan.name === 'Pro Founding' && !isYearly && (
                        <motion.div
                          className="mt-1 relative z-10"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="text-gray-400 text-xs">
                            <span className="line-through text-gray-500">$24.99/mo</span> → Save $5/month
                          </p>
                        </motion.div>
                      )}
                    </div>

                    {/* Features */}
                    <div className="space-y-3 border-t border-white/10 pt-5 relative z-10 flex-1 mb-6">
                      {/* Included Features */}
                      {plan.features.map((feature, j) => (
                        <motion.div
                          key={j}
                          className="flex items-start gap-2.5 relative z-10"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: j * 0.05 }}
                        >
                          <CheckCircle size={18} className={`flex-shrink-0 mt-0.5 ${plan.highlighted ? 'text-blue-400' : 'text-blue-500'}`} />
                          <span className={`text-sm leading-relaxed ${plan.highlighted ? 'text-gray-200' : 'text-gray-300'} relative z-10`}>{feature}</span>
                        </motion.div>
                      ))}
                    </div>

                    {/* CTA Button - Always at bottom */}
                    <div className="mt-auto pt-4 border-t border-white/10 relative z-10">
                      {(() => {
                        const buttonConfig = getButtonConfig(plan.name);
                        if (buttonConfig.variant === 'primary' && !buttonConfig.disabled) {
                          return (
                            <ShimmerButton
                              onClick={buttonConfig.action}
                              disabled={buttonConfig.disabled}
                              className="w-full"
                            >
                              {buttonConfig.text} {!buttonConfig.disabled && <ArrowRight size={16} />}
                            </ShimmerButton>
                          );
                        }
                        return (
                          <motion.button
                            onClick={buttonConfig.action}
                            disabled={buttonConfig.disabled}
                            className={`w-full py-3 rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-300 border ${plan.highlighted ? 'border-blue-500/50 bg-blue-500/10 text-white hover:bg-blue-500/20' : 'border-white/20 text-white hover:bg-white/10'} relative z-10 ${
                              buttonConfig.disabled ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                            whileHover={buttonConfig.disabled ? {} : { scale: 1.02 }}
                            whileTap={buttonConfig.disabled ? {} : { scale: 0.98 }}
                          >
                            {buttonConfig.text}
                          </motion.button>
                        );
                      })()}
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
