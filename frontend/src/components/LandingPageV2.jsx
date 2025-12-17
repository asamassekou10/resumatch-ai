import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight, Zap, FileText, BarChart3, Users, ArrowUpRight, Star } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';

const LandingPageV2 = ({ token }) => {
  const navigate = useNavigate();
  const [hoveredFeature, setHoveredFeature] = useState(null);

  // Animation variants
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

  const scaleIn = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: (i) => ({
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.6,
        delay: i * 0.1,
        ease: 'easeOut'
      }
    })
  };

  const features = [
    {
      icon: FileText,
      title: 'Smart Resume Analysis',
      description: 'AI-powered analysis that identifies strengths and improvement areas in seconds'
    },
    {
      icon: Zap,
      title: 'Keyword Optimization',
      description: 'Match your resume to job descriptions with intelligent keyword recommendations'
    },
    {
      icon: BarChart3,
      title: 'Compatibility Scoring',
      description: 'Get instant compatibility scores to understand job match percentages'
    },
    {
      icon: Users,
      title: 'Expert Feedback',
      description: 'Receive personalized suggestions from AI trained on industry best practices'
    }
  ];

  const steps = [
    {
      number: '01',
      title: 'Upload Your Resume',
      description: 'Simply drag and drop your resume in PDF, DOCX, or TXT format'
    },
    {
      number: '02',
      title: 'Add Job Details',
      description: 'Provide the job description or title you\'re targeting'
    },
    {
      number: '03',
      title: 'Get AI Insights',
      description: 'Receive comprehensive analysis and optimization recommendations'
    },
    {
      number: '04',
      title: 'Optimize & Apply',
      description: 'Apply the suggestions and land your dream job'
    }
  ];

  return (
    <>
      <SEO
        title="AI-Powered Resume Analysis & Job Matching"
        description="Optimize your resume with AI-powered analysis, ATS scoring, skill gap analysis, and personalized job matching. Get hired faster with ResumeAnalyzer AI."
        keywords="resume analyzer, AI resume, ATS score, job matching, career tools, resume optimization"
        url="https://resumeanalyzerai.com/"
      />
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
        {/* Hero Section */}
      <div className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        {/* Animated background elements */}
        <motion.div
          className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl"
          animate={{ y: [0, 30, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
          animate={{ y: [0, -30, 0] }}
          transition={{ duration: 8, repeat: Infinity, delay: 1 }}
        />

        <div className="relative max-w-7xl mx-auto">
          {/* Hero Content */}
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            custom={0}
          >
            <motion.h1
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight"
              variants={fadeInUp}
              custom={1}
            >
              Land Your Dream Job
              <span className="block bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mt-2 pb-4">
                with AI-Powered Insights
              </span>
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed"
              variants={fadeInUp}
              custom={2}
            >
              Transform your resume with cutting-edge AI analysis. Get instant feedback, keyword optimization, and personalized recommendations to stand out to recruiters.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
              variants={fadeInUp}
              custom={3}
            >
              <motion.button
                onClick={() => navigate(ROUTES.GUEST_ANALYZE)}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-semibold rounded-lg flex items-center gap-2 hover:shadow-lg hover:shadow-cyan-500/50 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Try Free (5 Credits)
                <ArrowRight className="w-5 h-5" />
              </motion.button>
              <motion.button
                onClick={() => navigate(ROUTES.PRICING)}
                className="px-8 py-4 border-2 border-cyan-500/50 text-white font-semibold rounded-lg hover:bg-slate-800/50 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                View Pricing
              </motion.button>
            </motion.div>

            {/* Speed Indicator */}
            <motion.div
              className="mt-12 flex justify-center items-center text-slate-400 text-sm"
              variants={fadeInUp}
              custom={4}
            >
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                <span>Get results in under 2 minutes</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
              Powerful Features to Elevate Your Career
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Everything you need to optimize your resume and land interviews
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, i) => {
              const IconComponent = feature.icon;
              return (
                <motion.div
                  key={i}
                  className="relative group"
                  onMouseEnter={() => setHoveredFeature(i)}
                  onMouseLeave={() => setHoveredFeature(null)}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={scaleIn}
                  custom={i}
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    animate={{ rotate: hoveredFeature === i ? 360 : 0 }}
                    transition={{ duration: 4, repeat: Infinity }}
                  />
                  <div className="relative bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 hover:border-cyan-500/30 transition-all duration-300">
                    <motion.div
                      className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-xl flex items-center justify-center mb-4"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      <IconComponent className="w-6 h-6 text-white" />
                    </motion.div>
                    <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                    <p className="text-slate-400">{feature.description}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
              Simple, Fast, Effective
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Get professional resume insights in just 4 simple steps
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, i) => (
              <motion.div
                key={i}
                className="relative"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
                custom={i}
              >
                {/* Connector Line */}
                {i < steps.length - 1 && (
                  <motion.div
                    className="hidden lg:block absolute top-24 left-[50%] w-[calc(100%+24px)] h-1 bg-gradient-to-r from-cyan-500 to-purple-600"
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: i * 0.1 }}
                    style={{ transformOrigin: 'left' }}
                  />
                )}

                <div className="relative">
                  <motion.div
                    className="w-20 h-20 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full flex items-center justify-center mb-4 mx-auto"
                    whileHover={{ scale: 1.1 }}
                  >
                    <span className="text-2xl font-bold text-white">{step.number}</span>
                  </motion.div>
                  <div className="text-center">
                    <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                    <p className="text-slate-400 text-sm">{step.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Resume?
          </h2>
          <p className="text-lg text-slate-400 mb-8">
            Join thousands of job seekers who have already improved their applications
          </p>
          <motion.button
            onClick={() => navigate(token ? ROUTES.DASHBOARD : ROUTES.GUEST_ANALYZE)}
            className="px-10 py-4 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-semibold rounded-lg flex items-center gap-2 hover:shadow-lg hover:shadow-cyan-500/50 transition-all duration-300 mx-auto"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {token ? 'Go to Dashboard' : 'Try Free Analysis'}
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>
      </div>
      </div>
    </>
  );
};

export default LandingPageV2;
