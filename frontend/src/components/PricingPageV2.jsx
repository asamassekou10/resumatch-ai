import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Zap, Crown, Sparkles, ArrowRight } from 'lucide-react';

const PricingPageV2 = ({ setView, handleUpgradeToPro, handleUpgradeToElite, token }) => {
  const [isYearly, setIsYearly] = useState(false);

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

  const plans = [
    {
      name: 'Free',
      description: 'Perfect to get started',
      monthlyPrice: 0,
      yearlyPrice: 0,
      credits: 5,
      features: [
        '5 free credits/month',
        'Resume analysis',
        'Keyword matching',
        'Basic feedback',
        'Community support'
      ],
      notIncluded: ['AI-powered optimization', 'Cover letter generation', 'Priority support', 'Advanced analytics'],
      highlighted: false,
      icon: Sparkles,
      buttonText: 'Current Plan',
      buttonAction: () => setView('dashboard'),
      buttonVariant: 'secondary'
    },
    {
      name: 'Pro',
      description: 'For active job seekers',
      monthlyPrice: 9.99,
      yearlyPrice: 99.99,
      credits: 100,
      features: [
        '100 credits/month',
        'Unlimited analyses',
        'AI feedback generation',
        'Resume optimization',
        'Cover letter generation',
        'Priority support'
      ],
      notIncluded: ['Unlimited API access', 'Custom integrations'],
      highlighted: true,
      icon: Zap,
      buttonText: 'Choose Pro',
      buttonAction: handleUpgradeToPro,
      buttonVariant: 'primary'
    },
    {
      name: 'Elite',
      description: 'For power users',
      monthlyPrice: 49.99,
      yearlyPrice: 499.99,
      credits: 1000,
      features: [
        '1000 credits/month',
        'Everything in Pro',
        'Unlimited API access',
        'Custom integrations',
        'Advanced analytics',
        'Dedicated support'
      ],
      notIncluded: [],
      highlighted: false,
      icon: Crown,
      buttonText: 'Choose Elite',
      buttonAction: handleUpgradeToElite,
      buttonVariant: 'primary'
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          custom={0}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Choose the perfect plan for your job search journey
          </p>
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          className="flex justify-center items-center gap-4 mb-12"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          custom={1}
        >
          <span className={`text-sm font-semibold transition-colors ${!isYearly ? 'text-white' : 'text-slate-400'}`}>
            Monthly
          </span>
          <motion.button
            onClick={() => setIsYearly(!isYearly)}
            className="relative inline-flex items-center h-10 w-20 bg-slate-700 rounded-full p-1 transition-colors hover:bg-slate-600"
            whileHover={{ scale: 1.05 }}
          >
            <motion.div
              className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full shadow-lg"
              layout
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </motion.button>
          <span className={`text-sm font-semibold transition-colors ${isYearly ? 'text-white' : 'text-slate-400'}`}>
            Yearly
          </span>
          {isYearly && (
            <motion.span
              className="ml-4 px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-purple-600/20 text-cyan-400 text-xs font-semibold rounded-full border border-cyan-500/30"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              Save up to 16%
            </motion.span>
          )}
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
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
                    className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-600/10 rounded-2xl blur-xl"
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                )}

                <div
                  className={`relative h-full rounded-2xl p-8 transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-gradient-to-br from-slate-800 border-2 border-cyan-500/50 shadow-2xl shadow-cyan-500/20'
                      : 'bg-slate-800/50 border border-slate-700 hover:border-slate-600'
                  }`}
                >
                  {/* Badge */}
                  {plan.highlighted && (
                    <motion.div
                      className="absolute -top-4 left-1/2 transform -translate-x-1/2"
                      initial={{ y: -20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.3 }}
                    >
                      <span className="bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </motion.div>
                  )}

                  {/* Plan Header */}
                  <div className="flex items-center gap-3 mb-6">
                    <motion.div
                      className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      <IconComponent className="w-6 h-6 text-white" />
                    </motion.div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">{plan.name}</h3>
                      <p className="text-sm text-slate-400">{plan.description}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-6">
                    <motion.div
                      key={`${price}-${isYearly}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <span className="text-4xl font-bold text-white">${price.toFixed(2)}</span>
                      <span className="text-slate-400 text-sm ml-2">
                        {price === 0 ? 'forever' : isYearly ? '/year' : '/month'}
                      </span>
                    </motion.div>
                    {showSavings && (
                      <motion.p
                        className="text-green-400 text-sm font-semibold mt-2"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                      >
                        Save ${savings.savings.toFixed(2)} ({savings.percentage}%)
                      </motion.p>
                    )}
                    <div className="mt-4 p-3 bg-slate-900/50 rounded-lg">
                      <span className="text-sm text-slate-300">
                        <strong>{plan.credits}</strong> credits/month
                      </span>
                    </div>
                  </div>

                  {/* CTA Button */}
                  <motion.button
                    onClick={plan.buttonAction}
                    className={`w-full py-3 rounded-lg font-semibold mb-8 flex items-center justify-center gap-2 transition-all duration-300 ${
                      plan.buttonVariant === 'primary'
                        ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white hover:shadow-lg hover:shadow-cyan-500/50'
                        : 'bg-slate-700 text-white hover:bg-slate-600'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {plan.buttonText}
                    {plan.buttonVariant === 'primary' && <ArrowRight className="w-4 h-4" />}
                  </motion.button>

                  {/* Features */}
                  <div className="space-y-4 border-t border-slate-700 pt-8">
                    {/* Included Features */}
                    {plan.features.map((feature, j) => (
                      <motion.div
                        key={j}
                        className="flex items-start gap-3"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: j * 0.05 }}
                      >
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-300 text-sm">{feature}</span>
                      </motion.div>
                    ))}

                    {/* Not Included Features */}
                    {plan.notIncluded.length > 0 && (
                      <>
                        <div className="border-t border-slate-700 pt-4 mt-4" />
                        {plan.notIncluded.map((feature, j) => (
                          <motion.div
                            key={`not-${j}`}
                            className="flex items-start gap-3 opacity-60"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 0.6, x: 0 }}
                            transition={{ delay: (plan.features.length + j) * 0.05 }}
                          >
                            <div className="w-5 h-5 rounded-full border border-slate-600 flex-shrink-0 mt-0.5" />
                            <span className="text-slate-500 text-sm">{feature}</span>
                          </motion.div>
                        ))}
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <motion.div
          className="max-w-3xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <h2 className="text-3xl font-bold text-white text-center mb-8">Frequently Asked Questions</h2>
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
              <motion.div
                key={i}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-all"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <h3 className="font-semibold text-white mb-2">{faq.q}</h3>
                <p className="text-slate-400 text-sm">{faq.a}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Footer CTA */}
        <motion.div
          className="text-center mt-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <p className="text-slate-400 text-sm">
            All plans include secure payment processing via Stripe. Cancel anytime, no questions asked.
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default PricingPageV2;
