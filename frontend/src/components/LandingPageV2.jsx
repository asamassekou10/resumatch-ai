import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { CheckCircle, ArrowRight, Zap, FileText, BarChart3, Users, Star, Quote, TrendingUp, BookOpen, Code, Stethoscope, DollarSign, GraduationCap, Palette, Heart, Globe, Clipboard, ChevronDown, ChevronUp } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import ShimmerButton from './ui/ShimmerButton';
import EntranceOverlay from './ui/EntranceOverlay';
import Footer from './ui/Footer';
import SpotlightCard from './ui/SpotlightCard';
import FreeTrialBanner from './ui/FreeTrialBanner';
import { generateFAQSchema } from '../utils/structuredData';
import BLOG_POSTS from '../utils/blogContent';



// CountUp Component
const CountUp = ({ from = 0, to, duration = 2, suffix = '' }) => {
  const nodeRef = useRef();
  const inView = useInView(nodeRef, { once: true, margin: "-50px" });
  const [current, setCurrent] = useState(from);

  useEffect(() => {
    if (!inView) return;

    let startTime;
    let animationFrame;

    const update = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);

      setCurrent(Math.floor(progress * (to - from) + from));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(update);
      }
    };

    animationFrame = requestAnimationFrame(update);
    return () => cancelAnimationFrame(animationFrame);
  }, [inView, from, to, duration]);

  return <span ref={nodeRef}>{current.toLocaleString()}{suffix}</span>;
};

const LandingPageV2 = ({ token }) => {
  const navigate = useNavigate();
  const [showEntrance, setShowEntrance] = useState(true);
  const [openFAQIndex, setOpenFAQIndex] = useState(null);

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

  // FAQ data for homepage
  const homepageFAQs = [
    {
      question: 'Is ResumeAnalyzer AI free?',
      answer: 'Yes! We offer a free tier that includes 10 resume analysis credits per month. You can analyze your resume and get basic feedback at no cost. Upgrade to Pro or Elite plans for more credits and advanced features like AI-powered optimization and cover letter generation.'
    },
    {
      question: 'How accurate is the AI resume analysis?',
      answer: 'Our AI is trained on thousands of successful resumes and hiring patterns across multiple industries. It provides industry-standard feedback with 95%+ accuracy. However, we recommend using it as a guide alongside professional resume services for best results.'
    },
    {
      question: 'What file formats are supported?',
      answer: 'We support PDF (.pdf), Microsoft Word (.docx), and plain text (.txt) files. For best results, we recommend using PDF format as it preserves formatting and structure better than other formats.'
    },
    {
      question: 'How does ATS optimization work?',
      answer: 'Our AI analyzes your resume for ATS compatibility by checking formatting, keyword usage, section organization, and readability. We provide an ATS score and specific recommendations to improve your resume\'s chances of passing automated screening systems used by 99% of Fortune 500 companies.'
    },
    {
      question: 'Can I use this for any job role?',
      answer: 'Absolutely! ResumeAnalyzer AI works for all job roles and industries. We have specialized landing pages for specific roles (software engineer, nurse, marketing manager, etc.) with role-specific tips and keywords. Our AI adapts its analysis based on the job description you provide.'
    }
  ];

  const faqSchema = generateFAQSchema(homepageFAQs);

  return (
    <>
      <SEO
        title="ResumeAnalyzer AI | Free ATS Resume Scanner & Optimizer"
        description="Optimize your resume with AI-powered analysis, ATS scoring, skill gap analysis, and personalized job matching. Get hired faster with ResumeAnalyzer AI. 2 free scans daily."
        keywords="resume analyzer, AI resume, ATS score, job matching, career tools, resume optimization, free resume scanner, ATS checker"
        url="https://resumeanalyzerai.com/"
        structuredData={[faqSchema]}
      />
      <AnimatePresence>
        {showEntrance && <EntranceOverlay onComplete={() => setShowEntrance(false)} />}
      </AnimatePresence>
      {!showEntrance && (
      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Free Trial Banner */}
        <FreeTrialBanner />

        {/* Background atmosphere - Reduced opacity */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/10 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 z-0 pointer-events-none" />

        {/* Grid Pattern */}
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        {/* Hero Section */}
      <div className="relative pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        {/* Premium Moon/Arc Effect */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[180vw] h-[180vw] sm:w-[120vw] sm:h-[120vw] -translate-y-[75%] sm:-translate-y-[80%] rounded-full border border-white/5 bg-white/[0.01] shadow-[0_0_120px_rgba(59,130,246,0.1)] z-0 pointer-events-none"
        />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[150vw] h-[150vw] sm:w-[90vw] sm:h-[90vw] -translate-y-[70%] sm:-translate-y-[75%] rounded-full border border-white/[0.08] z-0 pointer-events-none opacity-50" />

        {/* Background blur elements */}
        <div
          className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/30 rounded-full blur-[100px] opacity-30 z-0 pointer-events-none"
        />
        <div
          className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] opacity-30 z-0 pointer-events-none"
        />

        <div className="relative max-w-7xl mx-auto">
          {/* Hero Content */}
          <motion.div
            className="text-center mb-16 relative z-10"
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            custom={0}
          >
            {/* Status Badge */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm relative z-10"
            >
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs font-medium text-gray-300 uppercase tracking-widest">AI-Powered Resume Analysis</span>
            </motion.div>

            <motion.h1
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight font-display relative z-10"
              variants={fadeInUp}
              custom={1}
            >
              ResumeAnalyzer AI <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-cyan-500 animate-gradient-x">
                Free ATS Resume Scanner & Optimizer
              </span>
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-gray-400 mb-4 max-w-2xl mx-auto leading-relaxed relative z-10 font-light"
              variants={fadeInUp}
              custom={2}
            >
              Beat the ATS and land your dream job. Our advanced AI analyzes your resume against millions of data points to ensure you stand out.
            </motion.p>

            {/* Free Credits Badge */}
            <motion.div
              className="mb-8 max-w-2xl mx-auto relative z-10"
              variants={fadeInUp}
              custom={2.5}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-white font-semibold">10 Free Analyses</span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">No Credit Card Required</span>
              </div>
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center items-center relative z-10"
              variants={fadeInUp}
              custom={3}
            >
              <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                Try For Free <ArrowRight size={16} />
              </ShimmerButton>

              <motion.button
                onClick={() => navigate(ROUTES.PRICING)}
                className="px-8 py-3 rounded-full font-bold text-sm text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition-all hover:border-white/30 relative z-10"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                View Pricing
              </motion.button>
            </motion.div>

            {/* Speed Indicator */}
            <motion.div
              className="mt-12 flex justify-center items-center text-gray-400 text-sm relative z-10"
              variants={fadeInUp}
              custom={4}
            >
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                <span>Get results in under 2 minutes</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Dashboard Preview Mockup */}
          <motion.div
            className="mt-20 mx-auto max-w-5xl rounded-xl border border-white/10 bg-gray-900/50 backdrop-blur-sm shadow-2xl overflow-hidden relative z-10"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <div className="flex items-center gap-2 px-4 py-3 bg-white/5 border-b border-white/10">
              <div className="w-3 h-3 rounded-full bg-red-500/50" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
              <div className="w-3 h-3 rounded-full bg-green-500/50" />
              <div className="ml-4 h-6 w-64 bg-white/5 rounded-md" />
            </div>
            <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8 text-left relative">
              {/* Glow behind dashboard */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-blue-500/10 blur-[100px] pointer-events-none" />

              <div className="col-span-2 space-y-4 relative z-10">
                <div className="h-4 w-3/4 bg-white/10 rounded animate-pulse" />
                <div className="h-4 w-1/2 bg-white/10 rounded animate-pulse" />
                <div className="h-32 w-full bg-white/5 rounded border border-white/10 p-4 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm text-gray-400">Analysis Score</div>
                    <div className="text-green-400 font-bold text-xl flex items-center font-display">
                      <CountUp to={92} />/100
                    </div>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2 mb-4 overflow-hidden">
                    <motion.div
                      className="bg-gradient-to-r from-blue-500 to-green-400 h-2 rounded-full"
                      initial={{ width: 0 }}
                      whileInView={{ width: "92%" }}
                      transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
                      viewport={{ once: true }}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                      <CheckCircle size={12} className="text-green-400" /> Strong action verbs used
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                      <CheckCircle size={12} className="text-green-400" /> Quantifiable achievements detected
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-span-1 space-y-4 relative z-10">
                <div className="h-24 w-full bg-gradient-to-br from-blue-900/40 to-blue-900/40 rounded border border-white/10 flex items-center justify-center flex-col group hover:border-blue-500/50 transition-colors">
                  <Zap className="text-yellow-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-xs text-gray-400">ATS Compatible</span>
                </div>
                <div className="h-24 w-full bg-white/5 rounded border border-white/10 flex items-center justify-center flex-col group hover:border-blue-500/50 transition-colors">
                  <TrendingUp className="text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-xs text-gray-400">Job Match: High</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16 relative z-10"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 font-display relative z-10">
              Powerful Features to Elevate Your Career
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto relative z-10">
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
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={scaleIn}
                  custom={i}
                >
                  <SpotlightCard className="rounded-2xl p-8 h-full">
                    <motion.div
                      className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      <IconComponent className="w-6 h-6 text-white" />
                    </motion.div>
                    <h3 className="text-xl font-bold text-white mb-2 font-display">{feature.title}</h3>
                    <p className="text-gray-400">{feature.description}</p>
                  </SpotlightCard>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-12 px-4 sm:px-6 lg:px-8 bg-white/5 relative z-10">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16 relative z-10"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 font-display relative z-10">
              Simple, Fast, Effective
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto relative z-10">
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

                <SpotlightCard className="rounded-2xl p-8 h-full relative z-10">
                  <motion.div
                    className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mb-4 mx-auto"
                    whileHover={{ scale: 1.1 }}
                  >
                    <span className="text-2xl font-bold text-white">{step.number}</span>
                  </motion.div>
                  <div className="text-center">
                    <h3 className="text-lg font-bold text-white mb-2 font-display">{step.title}</h3>
                    <p className="text-gray-400 text-sm">{step.description}</p>
                  </div>
                </SpotlightCard>
              </motion.div>
            ))}
          </div>
        </div>
      </div>


      {/* Trusted By Section - Marquee */}
      <div className="py-12 bg-black border-y border-white/5 overflow-hidden relative z-10">
        <div className="max-w-7xl mx-auto px-6 text-center mb-8 relative z-10">
          <p className="text-sm text-gray-500 uppercase tracking-widest font-medium relative z-10">Trusted by candidates at</p>
        </div>
        <div className="flex w-full overflow-hidden relative">
          <div className="absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none" />
          <div className="absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none" />

          <div
            className="flex gap-16 whitespace-nowrap"
          >
            {["TECHCORP", "INNOVATE", "FUTURELABS", "GLOBALAI", "NEXTGEN", "DATASYSTEMS", "ORBITAL", "SYNTHWAVE", "TECHCORP", "INNOVATE", "FUTURELABS", "GLOBALAI", "NEXTGEN", "DATASYSTEMS", "ORBITAL", "SYNTHWAVE"].map((company, index) => (
              <span key={index} className="text-xl md:text-2xl font-bold text-white/30 hover:text-white transition-colors cursor-default select-none font-display">
                {company}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-blue-900/20 z-0 pointer-events-none" />
        <motion.div
          className="max-w-4xl mx-auto text-center relative z-10"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          custom={0}
        >
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 font-display relative z-10">
            Ready to Land Your Dream Job?
          </h2>
          <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto relative z-10">
            Join 10,000+ job seekers who transformed their careers with AI-powered insights
          </p>
          <ShimmerButton
            onClick={() => navigate(token ? ROUTES.DASHBOARD : ROUTES.GUEST_ANALYZE)}
            className="px-12 py-5 h-16 text-lg"
          >
            {token ? 'Go to Dashboard' : 'Try For Free'} <ArrowRight size={20} />
          </ShimmerButton>
        </motion.div>
      </div>

      {/* FAQ Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="text-center mb-12"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
              Frequently Asked Questions
            </h2>
            <p className="text-gray-400">
              Everything you need to know about ResumeAnalyzer AI
            </p>
          </motion.div>

          <div className="space-y-3">
            {homepageFAQs.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05 }}
              >
                <SpotlightCard className="rounded-xl overflow-hidden">
                  <button
                    onClick={() => setOpenFAQIndex(openFAQIndex === index ? null : index)}
                    className="w-full flex items-center justify-between p-6 text-left hover:bg-white/5 transition-colors"
                  >
                    <h3 className="text-lg font-bold text-white font-display pr-4">
                      {faq.question}
                    </h3>
                    {openFAQIndex === index ? (
                      <ChevronUp className="w-5 h-5 text-blue-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                  </button>
                  <AnimatePresence>
                    {openFAQIndex === index && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        <div className="px-6 pb-6 pt-0">
                          <p className="text-gray-300 leading-relaxed">
                            {faq.answer}
                          </p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </SpotlightCard>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Resume Tips Blog Section - Internal Links for SEO */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 relative z-10 border-t border-white/10">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-12"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            custom={0}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <BookOpen className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-300">Resume Tips & Guides</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
              Expert Resume Advice by Industry
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Get industry-specific tips to optimize your resume and land more interviews
            </p>
          </motion.div>

          {/* Blog Posts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {BLOG_POSTS.slice(0, 9).map((post, index) => (
              <motion.div
                key={post.slug}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05 }}
              >
                <Link to={`/blog/${post.slug}`}>
                  <SpotlightCard className="rounded-xl p-5 h-full hover:border-blue-500/50 transition-all group">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-blue-500/20 flex items-center justify-center flex-shrink-0 group-hover:from-blue-500/30 group-hover:to-blue-500/30 transition-all">
                        <FileText className="w-5 h-5 text-blue-400" />
                      </div>
                      <div className="flex-grow min-w-0">
                        <h3 className="text-white font-semibold text-sm mb-1 group-hover:text-blue-300 transition-colors line-clamp-2">
                          {post.title.replace(' | Free ATS Checker', '').replace(' | ResumeAnalyzer AI', '')}
                        </h3>
                        <p className="text-gray-500 text-xs line-clamp-2">{post.excerpt}</p>
                        <span className="text-blue-400 text-xs mt-2 inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                          Read more <ArrowRight className="w-3 h-3" />
                        </span>
                      </div>
                    </div>
                  </SpotlightCard>
                </Link>
              </motion.div>
            ))}
          </div>

          {/* View All Link */}
          <motion.div
            className="text-center mt-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <Link
              to="/blog"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 hover:border-blue-500/50 transition-all group"
            >
              View All {BLOG_POSTS.length} Articles
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Resume Guides by Job Role Section */}
      <div className="py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <FileText className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-300">Role-Specific Guides</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
              Resume Examples by Job Role
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Get tailored resume tips, keywords, and examples for your specific role
            </p>
          </motion.div>

          {/* Job Roles Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {[
              { slug: 'software-engineer', label: 'Software Engineer', icon: Code },
              { slug: 'nursing-student', label: 'Nursing Student', icon: Stethoscope },
              { slug: 'marketing-manager', label: 'Marketing Manager', icon: BarChart3 },
              { slug: 'data-analyst', label: 'Data Analyst', icon: TrendingUp },
              { slug: 'project-manager', label: 'Project Manager', icon: Clipboard },
              { slug: 'accountant', label: 'Accountant', icon: DollarSign },
              { slug: 'teacher', label: 'Teacher', icon: GraduationCap },
              { slug: 'sales-representative', label: 'Sales Rep', icon: Users },
              { slug: 'graphic-designer', label: 'Graphic Designer', icon: Palette },
              { slug: 'registered-nurse', label: 'Registered Nurse', icon: Heart },
              { slug: 'web-developer', label: 'Web Developer', icon: Globe },
              { slug: 'financial-analyst', label: 'Financial Analyst', icon: TrendingUp }
            ].map((role, index) => {
              const IconComponent = role.icon;
              return (
                <motion.div
                  key={role.slug}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.03 }}
                >
                  <Link to={`/resume-for/${role.slug}`}>
                    <SpotlightCard className="rounded-lg p-4 h-full hover:border-blue-500/50 transition-all group">
                      <div className="text-center">
                        <div className="flex items-center justify-center mb-2">
                          <IconComponent className="w-8 h-8 text-blue-400 group-hover:text-blue-300 transition-colors" />
                        </div>
                        <div className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">
                          {role.label}
                        </div>
                      </div>
                    </SpotlightCard>
                  </Link>
                </motion.div>
              );
            })}
          </div>

          {/* View All Link */}
          <motion.div
            className="text-center mt-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <p className="text-gray-500 text-sm">
              ...and 9 more specialized roles
            </p>
          </motion.div>
        </div>
      </div>

      <Footer />
      </div>
      )}
    </>
  );
};

export default LandingPageV2;
