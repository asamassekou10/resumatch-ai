import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Sparkles, TrendingUp, Target, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import { ROUTES } from '../config/routes';

const SubscriptionRequired = ({ feature }) => {
  const navigate = useNavigate();
  const features = [
    {
      icon: <TrendingUp className="w-5 h-5" />,
      title: 'Real-Time Market Trends',
      description: 'AI-powered insights on job market conditions and hiring trends'
    },
    {
      icon: <Target className="w-5 h-5" />,
      title: 'Smart Job Matching',
      description: 'Personalized job recommendations with AI match scoring'
    },
    {
      icon: <Sparkles className="w-5 h-5" />,
      title: 'Company Intelligence',
      description: 'Deep insights into company culture and interview processes'
    },
    {
      icon: <Zap className="w-5 h-5" />,
      title: 'Salary Intelligence',
      description: 'Real-time salary data with AI negotiation strategies'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="inline-block mb-6"
            animate={{
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          >
            <div className="relative">
              <div className="absolute inset-0 bg-purple-500/30 blur-xl rounded-full"></div>
              <Lock className="w-20 h-20 text-purple-400 relative z-10" />
            </div>
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              {feature || 'Market Intelligence'}
            </span>
            <br />
            <span className="text-2xl md:text-3xl text-slate-300">is a Premium Feature</span>
          </h1>

          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Unlock AI-powered market insights, real-time job intelligence, and advanced career tools to accelerate your job search
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {features.map((item, index) => (
            <motion.div
              key={index}
              className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-purple-500/50 transition-all"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-gradient-to-br from-purple-500/20 to-cyan-500/20 rounded-lg text-purple-400">
                  {item.icon}
                </div>
                <div>
                  <h3 className="text-white font-semibold mb-2">{item.title}</h3>
                  <p className="text-slate-400 text-sm">{item.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* What You Get Card */}
        <motion.div
          className="bg-gradient-to-br from-purple-900/30 to-cyan-900/30 border border-purple-500/30 rounded-xl p-8 mb-8"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-400" />
            What You Get with Premium
          </h2>

          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">Unlimited Resume Analyses</p>
                <p className="text-slate-400 text-sm">Analyze as many resumes as you need with AI-powered insights</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">Market Intelligence Dashboard</p>
                <p className="text-slate-400 text-sm">Real-time job market trends, salary data, and company insights</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">AI Job Matching</p>
                <p className="text-slate-400 text-sm">Personalized job recommendations with smart match scoring</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">Interview Preparation</p>
                <p className="text-slate-400 text-sm">Company-specific interview questions and AI-generated answers</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">Application Tracking</p>
                <p className="text-slate-400 text-sm">AI-powered insights on when to follow up and what to say</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-white font-medium">Skills Gap Analysis</p>
                <p className="text-slate-400 text-sm">Personalized learning paths to close your skills gaps</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <motion.button
            onClick={() => navigate(ROUTES.PRICING)}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white rounded-lg font-semibold text-lg flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles className="w-5 h-5" />
            View Pricing Plans
            <ArrowRight className="w-5 h-5" />
          </motion.button>

          <motion.button
            onClick={() => navigate(ROUTES.DASHBOARD)}
            className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-semibold text-lg border border-slate-700 hover:border-slate-600 transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Back to Dashboard
          </motion.button>
        </motion.div>

        {/* Pricing Preview */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <p className="text-slate-400 mb-2">Starting at</p>
          <p className="text-4xl font-bold text-white mb-1">
            <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              $29
            </span>
            <span className="text-xl text-slate-400">/month</span>
          </p>
          <p className="text-slate-500 text-sm">Cancel anytime • No commitment</p>
        </motion.div>
      </div>
    </div>
  );
};

export default SubscriptionRequired;
