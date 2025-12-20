import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { CheckCircle, ArrowRight, Zap, FileText, BarChart3, Users, Star, Quote, TrendingUp } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import ShimmerButton from './ui/ShimmerButton';
import EntranceOverlay from './ui/EntranceOverlay';
import Footer from './ui/Footer';
import SpotlightCard from './ui/SpotlightCard';



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
      <AnimatePresence>
        {showEntrance && <EntranceOverlay onComplete={() => setShowEntrance(false)} />}
      </AnimatePresence>
      {!showEntrance && (
      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background atmosphere - Reduced opacity */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/10 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 z-0 pointer-events-none" />

        {/* Grid Pattern */}
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        {/* Hero Section */}
      <div className="relative pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        {/* Premium Moon/Arc Effect - Animated Breathing */}
        <motion.div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[180vw] h-[180vw] sm:w-[120vw] sm:h-[120vw] -translate-y-[75%] sm:-translate-y-[80%] rounded-full border border-white/5 bg-white/[0.01] shadow-[0_0_120px_rgba(59,130,246,0.1)] z-0 pointer-events-none"
          animate={{
            scale: [1, 1.02, 1],
            opacity: [0.8, 1, 0.8]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[150vw] h-[150vw] sm:w-[90vw] sm:h-[90vw] -translate-y-[70%] sm:-translate-y-[75%] rounded-full border border-white/[0.08] z-0 pointer-events-none opacity-50" />

        {/* Animated background elements */}
        <motion.div
          className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/30 rounded-full blur-[100px] opacity-30 z-0 pointer-events-none"
          animate={{ y: [0, 30, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] opacity-30 z-0 pointer-events-none"
          animate={{ y: [0, -30, 0] }}
          transition={{ duration: 8, repeat: Infinity, delay: 1 }}
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
              Resume perfection <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 animate-gradient-x">
                powered by intelligence.
              </span>
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-gray-400 mb-8 max-w-2xl mx-auto leading-relaxed relative z-10 font-light"
              variants={fadeInUp}
              custom={2}
            >
              Beat the ATS and land your dream job. Our advanced AI analyzes your resume against millions of data points to ensure you stand out.
            </motion.p>

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
            initial={{ opacity: 0, y: 100, rotateX: 20 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ delay: 0.8, duration: 1.2, type: "spring", bounce: 0.2 }}
            style={{ transformPerspective: '1000px' }}
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
                <div className="h-24 w-full bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded border border-white/10 flex items-center justify-center flex-col group hover:border-purple-500/50 transition-colors">
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
                      className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4"
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
                {/* Connector Line */}
                {i < steps.length - 1 && (
                  <motion.div
                    className="hidden lg:block absolute top-24 left-[50%] w-[calc(100%+24px)] h-1 bg-gradient-to-r from-blue-500 to-purple-600 z-0"
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: i * 0.1 }}
                    style={{ transformOrigin: 'left' }}
                  />
                )}

                <SpotlightCard className="rounded-2xl p-8 h-full relative z-10">
                  <motion.div
                    className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 mx-auto"
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

      {/* Stats Section */}
      <div className="py-12 px-4 sm:px-6 lg:px-8 bg-white/5 border-y border-white/10 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="relative z-10"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2 font-display relative z-10">
                <CountUp to={10000} />+
              </div>
              <p className="text-gray-400 relative z-10">Resumes Analyzed</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative z-10"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2 font-display relative z-10">
                <CountUp to={92} suffix="%" />
              </div>
              <p className="text-gray-400 relative z-10">Success Rate</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="relative z-10"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2 font-display relative z-10">
                <CountUp to={500} />+
              </div>
              <p className="text-gray-400 relative z-10">Companies Hiring</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="relative z-10"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2 font-display relative z-10">
                <CountUp to={4} suffix=".8" />
                <Star className="inline w-6 h-6 text-yellow-400 fill-yellow-400 ml-2" />
              </div>
              <p className="text-gray-400 relative z-10">Average Rating</p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
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
              Success Stories
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto relative z-10">
              Join thousands of professionals who accelerated their careers
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Johnson",
                role: "Software Engineer",
                text: "After using ResumeAnalyzer, I got 3 interviews in one week. The keyword optimization is a game changer.",
                stars: 5
              },
              {
                name: "David Chen",
                role: "Product Manager",
                text: "The scoring system gave me a clear roadmap. It's like having a professional career coach in your pocket.",
                stars: 5
              },
              {
                name: "Elena Rodriguez",
                role: "Marketing Director",
                text: "Simple, fast, and effective. I didn't realize my formatting was breaking ATS parsers until I ran the scan.",
                stars: 5
              }
            ].map((testimonial, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <SpotlightCard className="p-8 rounded-2xl h-full group">
                  <Quote className="text-purple-500 mb-4 opacity-50 group-hover:opacity-100 transition-opacity" size={32} />
                  <p className="text-gray-300 mb-6 leading-relaxed">"{testimonial.text}"</p>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold font-display text-lg">
                      {testimonial.name[0]}
                    </div>
                    <div>
                      <h4 className="text-white font-bold text-sm font-display">{testimonial.name}</h4>
                      <p className="text-xs text-gray-500">{testimonial.role}</p>
                    </div>
                  </div>
                  <div className="flex gap-1 mt-4 text-yellow-500">
                    {[...Array(testimonial.stars)].map((_, j) => (
                      <Star key={j} size={14} fill="currentColor" />
                    ))}
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

          <motion.div
            className="flex gap-16 whitespace-nowrap"
            animate={{ x: [0, "-50%"] }}
            transition={{
              duration: 30,
              ease: "linear",
              repeat: Infinity
            }}
          >
            {["TECHCORP", "INNOVATE", "FUTURELABS", "GLOBALAI", "NEXTGEN", "DATASYSTEMS", "ORBITAL", "SYNTHWAVE", "TECHCORP", "INNOVATE", "FUTURELABS", "GLOBALAI", "NEXTGEN", "DATASYSTEMS", "ORBITAL", "SYNTHWAVE"].map((company, index) => (
              <span key={index} className="text-xl md:text-2xl font-bold text-white/30 hover:text-white transition-colors cursor-default select-none font-display">
                {company}
              </span>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-purple-900/20 z-0 pointer-events-none" />
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

      <Footer />
      </div>
      )}
    </>
  );
};

export default LandingPageV2;
