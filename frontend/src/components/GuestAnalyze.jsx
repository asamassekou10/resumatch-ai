import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUp, ArrowRight, AlertCircle, CheckCircle, Loader, Clock, FileText, Download, Sparkles, Mail, Infinity, Shield, Lock, ChevronDown, ChevronUp, Target, Search } from 'lucide-react';
import guestService from '../services/guestService';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';
import ScoreBreakdown from './ScoreBreakdown';
import { generateFAQSchema } from '../utils/structuredData';

// FAQ Accordion Component
const FAQItem = ({ question, answer, isOpen, onClick }) => (
  <motion.div
    className="border-b border-white/10 last:border-b-0"
    initial={false}
  >
    <button
      onClick={onClick}
      className="w-full py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors px-4 rounded-lg"
    >
      <span className="text-white font-medium text-sm md:text-base">{question}</span>
      {isOpen ? (
        <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
      ) : (
        <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
      )}
    </button>
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <p className="px-4 pb-4 text-gray-400 text-sm leading-relaxed">{answer}</p>
        </motion.div>
      )}
    </AnimatePresence>
  </motion.div>
);

const GuestAnalyze = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('welcome'); // welcome, analyze, results
  const [guestToken, setGuestToken] = useState(null);
  const [guestCredits, setGuestCredits] = useState(2);
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('Analyzing resume...');
  const [error, setError] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [, setSessionInfo] = useState(null);
  const [openFAQ, setOpenFAQ] = useState(null);

  // FAQ data for the page
  const faqData = [
    {
      question: "Is this really free?",
      answer: "Yes! You get 2 free resume scans every 24 hours without creating an account. For unlimited scans and premium features like AI-optimized resumes and cover letter generation, you can upgrade to a paid plan."
    },
    {
      question: "Do you sell my data or resume?",
      answer: "Absolutely not. Your privacy is our priority. We do not sell, share, or use your resume data for any purpose other than providing you with analysis results. Your resume is processed securely and never stored permanently in guest mode."
    },
    {
      question: "How accurate is the ATS analysis?",
      answer: "Our AI is trained on data from real Applicant Tracking Systems used by Fortune 500 companies. We achieve 95%+ accuracy in keyword matching and ATS compatibility predictions. However, we recommend using this as a guide alongside your own judgment."
    },
    {
      question: "What file formats are supported?",
      answer: "We support PDF (.pdf), Microsoft Word (.docx), and plain text (.txt) files. For best results, we recommend uploading your resume as a PDF to preserve formatting."
    },
    {
      question: "Why do I need to provide a job description?",
      answer: "The job description allows us to analyze how well your resume matches the specific role you're applying for. We extract keywords, required skills, and qualifications to give you a tailored compatibility score and actionable recommendations."
    }
  ];

  const faqSchema = generateFAQSchema(faqData);

  // Initialize guest session on mount
  useEffect(() => {
    const initGuestSession = async () => {
      try {
        // First, check if we have a valid existing session
        if (guestService.isGuestSessionValid()) {
          const existingToken = guestService.getGuestToken();

          // Verify the session is still valid on the server
          try {
            const sessionInfo = await guestService.getSessionInfo(existingToken);
            if (sessionInfo && sessionInfo.session) {
              setGuestToken(existingToken);
              setGuestCredits(sessionInfo.session.credits_remaining);
              setSessionInfo({
                expires_at: sessionInfo.session.expires_at,
                session_id: sessionInfo.session.id,
              });
              setStep('analyze');
              return; // Session is valid, no need to create a new one
            }
          } catch (sessionErr) {
            // Session expired or invalid on server, clear it and create new
            console.log('Existing session invalid, creating new one');
            guestService.clearGuestSession();
          }
        }

        // No valid session exists, create a new one
        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Connection timeout. Please check your internet connection.')), 10000)
        );

        const response = await Promise.race([
          guestService.createSession(),
          timeoutPromise
        ]);

        setGuestToken(response.guest_token);
        setGuestCredits(response.credits);
        setSessionInfo({
          expires_at: response.expires_at,
          session_id: response.session_id,
        });
        guestService.storeGuestToken(response.guest_token, response.expires_at);
        setStep('analyze');
      } catch (err) {
        console.error('Guest session error:', err);
        // Handle specific error cases
        const errorMessage = err.message || 'Failed to start guest session. Please try again.';

        // Clear any stale session data on errors
        guestService.clearGuestSession();

        if (errorMessage.includes('Too many guest sessions') || errorMessage.includes('RATE_LIMIT_EXCEEDED')) {
          setError('Too many sessions created. Please try again in 24 hours or create an account.');
        } else if (errorMessage.includes('Daily guest analysis limit') || errorMessage.includes('DAILY_LIMIT_EXCEEDED')) {
          setError('Daily guest limit reached. Create an account for unlimited access!');
        } else if (errorMessage.includes('timeout') || errorMessage.includes('Failed to fetch')) {
          setError('Unable to connect to server. Please try again later.');
        } else {
          setError(errorMessage);
        }
      }
    };

    initGuestSession();
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Store the File object directly (don't read as text)
      setResumeFile({
        name: file.name,
        file: file,
      });
    }
  };

  const handleAnalyze = async () => {
    if (!resumeFile || !jobDescription) {
      setError('Please upload a resume and enter a job description');
      return;
    }

    setLoading(true);
    setLoadingProgress(0);
    setLoadingMessage('Analyzing resume...');
    setError('');

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setLoadingProgress((prev) => {
        if (prev < 80) return prev + Math.random() * 30;
        return prev;
      });
    }, 500);

    const messageSequence = [
      'Analyzing resume...',
      'Extracting keywords...',
      'Matching with job description...',
      'Calculating match score...',
      'Generating insights...',
    ];
    let messageIndex = 0;
    const messageInterval = setInterval(() => {
      if (messageIndex < messageSequence.length - 1) {
        messageIndex++;
        setLoadingMessage(messageSequence[messageIndex]);
      }
    }, 1500);

    try {
      const result = await guestService.analyzeResume(
        guestToken,
        resumeFile.file,
        jobDescription,
        jobTitle,
        companyName
      );

      clearInterval(progressInterval);
      clearInterval(messageInterval);
      setLoadingProgress(100);
      setLoadingMessage('Complete!');

      setAnalysisResults(result);
      setGuestCredits(result.credits_remaining);

      // Delay to show 100% completion
      setTimeout(() => {
        setStep('results');
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      clearInterval(messageInterval);

      // Handle specific error cases
      const errorMessage = err.message || 'Analysis failed. Please try again.';

      if (errorMessage.includes('No guest credits remaining') || errorMessage.includes('INSUFFICIENT_CREDITS')) {
        setError('You\'ve used all 2 free analyses. Create an account for unlimited access!');
        setGuestCredits(0);
      } else if (errorMessage.includes('Daily guest analysis limit reached') || errorMessage.includes('DAILY_LIMIT_EXCEEDED')) {
        setError('Daily guest limit reached. Create an account for unlimited analyses!');
      } else if (errorMessage.includes('Too many guest sessions') || errorMessage.includes('RATE_LIMIT_EXCEEDED')) {
        setError('Too many sessions created. Please try again in 24 hours or create an account.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    navigate(ROUTES.PRICING);
  };

  const handleSignIn = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <>
      <SEO
        title="Free AI Resume Scanner | ATS Score & Missing Keywords in 10 Seconds"
        description="Scan your resume for free. Get your ATS compatibility score, missing keywords report, and executive summary suggestions in 10 seconds. No signup required. 2 free scans daily."
        keywords="free resume scanner, free ATS checker, resume keyword analyzer, ATS score free, resume analysis free, AI resume checker"
        url="https://resumeanalyzerai.com/guest-analyze"
        structuredData={[faqSchema]}
      />
      <div className="min-h-screen bg-black relative overflow-hidden pt-24 pb-12 px-4">
        {/* Background decorative elements */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }} />

        {/* Content container - must be above background */}
        <div className="relative z-10">
        <AnimatePresence mode="wait">
        {/* Welcome Step */}
        {step === 'welcome' && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-2xl mx-auto"
          >
            <div className="text-center relative z-10">
              <h1 className="text-4xl font-bold text-white mb-4 font-display relative z-10">Guest Access</h1>
              <p className="text-gray-300 text-lg mb-8 relative z-10">
                Get started with 2 free analyses instantly. No sign-up required.
              </p>
              <SpotlightCard className="rounded-lg p-8">
                {error ? (
                  <>
                    <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400 mb-4">{error}</p>
                    <div className="flex gap-3 justify-center relative z-10">
                      <ShimmerButton onClick={handleSignIn}>
                        Sign In
                      </ShimmerButton>
                      <button
                        onClick={() => navigate(ROUTES.PRICING)}
                        className="px-6 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold rounded-lg transition-colors relative z-10"
                      >
                        View Pricing
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <motion.div
                      className="inline-block mb-4 relative z-10"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <Clock className="w-16 h-16 text-purple-400" />
                    </motion.div>
                    <p className="text-gray-300 relative z-10">Initializing your guest session...</p>
                  </>
                )}
              </SpotlightCard>
            </div>
          </motion.div>
        )}

        {/* Analyze Step - Redesigned for Trust & Conversion */}
        {step === 'analyze' && (
          <motion.div
            key="analyze"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-6xl mx-auto relative z-10"
          >
            {/* Welcome Banner - Gift-style messaging */}
            <motion.div
              className="bg-gradient-to-r from-emerald-600/90 to-teal-600/90 backdrop-blur-sm border border-emerald-400/50 rounded-xl p-4 md:p-5 mb-8 relative z-10"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Sparkles className="w-6 h-6 text-yellow-300" />
                  </motion.div>
                  <div>
                    <p className="text-white font-bold text-base md:text-lg">Welcome! You have {guestCredits} Free Credits active today.</p>
                    <p className="text-white/80 text-sm">No account needed. Your resume stays private.</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <motion.button
                    onClick={handleSignIn}
                    className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white font-semibold text-sm transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Sign In
                  </motion.button>
                  <motion.button
                    onClick={handleUpgrade}
                    className="px-4 py-2 rounded-lg bg-white text-emerald-600 hover:bg-emerald-50 font-semibold text-sm transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Get Unlimited
                  </motion.button>
                </div>
              </div>
            </motion.div>

            {/* Main Hero Section */}
            <motion.div
              className="text-center mb-10"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 font-display">
                Free AI Resume Scanner
              </h1>
              <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto">
                See exactly what the ATS sees. Get your detailed score and keyword gaps in <span className="text-cyan-400 font-semibold">10 seconds</span>.
              </p>
            </motion.div>

            {/* Error Message */}
            {error && (
              <motion.div
                className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6 flex items-start gap-3 relative z-10 max-w-4xl mx-auto"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-400 text-sm relative z-10">{error}</p>
              </motion.div>
            )}

            {/* Two Column Layout: Form + What You Get */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 relative z-10">
              {/* Left Column: Upload Form (3/5 width) */}
              <motion.div
                className="lg:col-span-3 space-y-6"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <SpotlightCard className="rounded-xl p-6 md:p-8">
                  <div className="space-y-6">
                    {/* Resume Upload */}
                    <div>
                      <label className="block text-white font-semibold mb-3 text-lg">1. Upload Your Resume</label>
                      <div className="relative">
                        <input
                          type="file"
                          accept=".pdf,.docx,.txt"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="resume-upload"
                        />
                        <label
                          htmlFor="resume-upload"
                          className="flex items-center justify-center w-full px-4 py-10 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-purple-500 hover:bg-purple-500/5 transition-all bg-white/5 backdrop-blur-sm relative z-10"
                        >
                          {resumeFile ? (
                            <div className="text-center">
                              <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
                              <p className="text-white font-semibold">{resumeFile.name}</p>
                              <p className="text-slate-400 text-sm mt-1">Click to change file</p>
                            </div>
                          ) : (
                            <div className="text-center">
                              <FileUp className="w-12 h-12 text-purple-400 mx-auto mb-3" />
                              <p className="text-white font-semibold text-lg">Drop your resume here</p>
                              <p className="text-slate-400 text-sm mt-1">or click to browse</p>
                            </div>
                          )}
                        </label>
                      </div>
                    </div>

                    {/* Job Details */}
                    <div>
                      <label className="block text-white font-semibold mb-3 text-lg">2. Add Job Details</label>
                      <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <input
                            type="text"
                            placeholder="Company (optional)"
                            value={companyName}
                            onChange={(e) => setCompanyName(e.target.value)}
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                          />
                          <input
                            type="text"
                            placeholder="Job Title (optional)"
                            value={jobTitle}
                            onChange={(e) => setJobTitle(e.target.value)}
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                          />
                        </div>
                        <textarea
                          placeholder="Paste the job description here (required)"
                          value={jobDescription}
                          onChange={(e) => setJobDescription(e.target.value)}
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none h-36 resize-none"
                        />
                      </div>
                    </div>

                    {/* Progress Section */}
                    {loading && (
                      <motion.div
                        className="space-y-4"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-white font-semibold flex items-center gap-2">
                              <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                              >
                                <Loader className="w-5 h-5 text-purple-400" />
                              </motion.div>
                              {loadingMessage}
                            </span>
                            <span className="text-gray-400 text-sm">{Math.round(loadingProgress)}%</span>
                          </div>
                          <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500"
                              initial={{ width: '0%' }}
                              animate={{ width: `${loadingProgress}%` }}
                              transition={{ ease: 'easeOut', duration: 0.3 }}
                            />
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Analyze Button */}
                    {!loading && (
                      <div className="pt-2">
                        <ShimmerButton
                          onClick={handleAnalyze}
                          disabled={loading || !resumeFile || !jobDescription}
                          className="w-full h-14 text-lg"
                        >
                          <Search className="w-5 h-5" />
                          Scan My Resume
                          <ArrowRight className="w-5 h-5" />
                        </ShimmerButton>
                      </div>
                    )}

                    {/* Trust Badges */}
                    <div className="flex flex-wrap justify-center gap-4 md:gap-6 pt-4 border-t border-white/10">
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Lock className="w-4 h-4 text-green-400" />
                        <span>Private & Secure</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Shield className="w-4 h-4 text-blue-400" />
                        <span>No Sign-up Required</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <FileText className="w-4 h-4 text-purple-400" />
                        <span>PDF or DOCX</span>
                      </div>
                    </div>
                  </div>
                </SpotlightCard>
              </motion.div>

              {/* Right Column: What You Get (2/5 width) */}
              <motion.div
                className="lg:col-span-2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="sticky top-8 space-y-6">
                  {/* Sneak Peek Card */}
                  <SpotlightCard className="rounded-xl p-6">
                    <h3 className="text-white font-bold text-lg mb-4 font-display">What You Get</h3>

                    {/* Mock Score Preview */}
                    <div className="relative mb-6 p-4 rounded-xl bg-gradient-to-br from-slate-800/80 to-slate-700/80 border border-white/10 overflow-hidden">
                      {/* Decorative blur */}
                      <div className="absolute -top-4 -right-4 w-20 h-20 bg-cyan-500/30 rounded-full blur-xl" />
                      <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-purple-500/30 rounded-full blur-xl" />

                      <div className="relative flex items-center justify-between">
                        <div>
                          <p className="text-gray-400 text-xs uppercase tracking-wide mb-1">Resume Score</p>
                          <motion.p
                            className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 font-display"
                            animate={{ opacity: [0.7, 1, 0.7] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            85/100
                          </motion.p>
                        </div>
                        <div className="w-16 h-16 rounded-full border-4 border-cyan-400/50 flex items-center justify-center">
                          <Target className="w-8 h-8 text-cyan-400" />
                        </div>
                      </div>
                      <p className="text-gray-500 text-xs mt-3 italic">Example preview</p>
                    </div>

                    {/* Feature List */}
                    <ul className="space-y-3">
                      <li className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-white font-medium">ATS Parsability Check</p>
                          <p className="text-gray-400 text-sm">See if your resume format works with ATS systems</p>
                        </div>
                      </li>
                      <li className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-white font-medium">Missing Keyword Report</p>
                          <p className="text-gray-400 text-sm">Find keywords you're missing from the job description</p>
                        </div>
                      </li>
                      <li className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-white font-medium">Executive Summary Suggestions</p>
                          <p className="text-gray-400 text-sm">Get AI-powered tips to improve your resume</p>
                        </div>
                      </li>
                      <li className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-white font-medium">Match Score Breakdown</p>
                          <p className="text-gray-400 text-sm">Detailed analysis of how well you match the role</p>
                        </div>
                      </li>
                    </ul>
                  </SpotlightCard>

                  {/* Social Proof Mini */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <div className="flex items-center justify-between text-center">
                      <div>
                        <p className="text-white font-bold text-lg font-display">10,000+</p>
                        <p className="text-gray-400 text-xs">Resumes Scanned</p>
                      </div>
                      <div className="w-px h-10 bg-white/10" />
                      <div>
                        <p className="text-white font-bold text-lg font-display">92%</p>
                        <p className="text-gray-400 text-xs">Success Rate</p>
                      </div>
                      <div className="w-px h-10 bg-white/10" />
                      <div>
                        <p className="text-white font-bold text-lg font-display">4.8/5</p>
                        <p className="text-gray-400 text-xs">User Rating</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* FAQ Section */}
            <motion.div
              className="mt-16 max-w-3xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h2 className="text-2xl font-bold text-white mb-6 text-center font-display">
                Frequently Asked Questions
              </h2>
              <SpotlightCard className="rounded-xl overflow-hidden">
                {faqData.map((faq, index) => (
                  <FAQItem
                    key={index}
                    question={faq.question}
                    answer={faq.answer}
                    isOpen={openFAQ === index}
                    onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
                  />
                ))}
              </SpotlightCard>
            </motion.div>
          </motion.div>
        )}

        {/* Results Step - Intelligent Analysis */}
        {step === 'results' && analysisResults && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-5xl mx-auto space-y-6"
          >
            {/* Results Header */}
            <motion.div
              className="text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <h1 className="text-4xl font-bold text-white mb-2">AI-Powered Analysis Complete</h1>
              <p className="text-slate-400">Comprehensive resume evaluation & ATS optimization</p>
            </motion.div>

            {/* Overall Score Card */}
            <motion.div
              className="bg-gradient-to-br from-slate-800 to-slate-700 border border-slate-600 rounded-lg p-4 sm:p-6 md:p-8"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
                    {analysisResults.overall_score || 0}%
                  </div>
                  <p className="text-slate-300 font-semibold text-sm sm:text-base">Overall Match Score</p>
                  <p className="text-slate-400 text-xs sm:text-sm mt-2">{analysisResults.interpretation}</p>
                </div>
                <div className="flex flex-col justify-center gap-3 text-center sm:text-left">
                  <div>
                    <p className="text-slate-400 text-xs sm:text-sm mb-1">Industry</p>
                    <p className="text-white font-semibold text-sm sm:text-base">{analysisResults.job_industry || 'Unknown'}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-xs sm:text-sm mb-1">ATS Pass Rate</p>
                    <p className="text-cyan-400 font-semibold text-sm sm:text-base">{analysisResults.expected_ats_pass_rate}</p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Score Breakdown - Transparent Calculation */}
            {analysisResults.score_breakdown && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <ScoreBreakdown
                  scoreBreakdown={analysisResults.score_breakdown}
                  overallScore={analysisResults.overall_score}
                />
              </motion.div>
            )}

            {/* Match Breakdown */}
            {analysisResults.match_analysis && analysisResults.match_analysis.match_breakdown && (
              <motion.div
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <h3 className="text-white font-semibold mb-4">Match Breakdown</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(analysisResults.match_analysis.match_breakdown || {}).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-slate-400 text-sm capitalize">{key.replace('_', ' ')}</span>
                        <span className="text-cyan-400 font-semibold">{value}%</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <motion.div
                          className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                          initial={{ width: '0%' }}
                          animate={{ width: `${value}%` }}
                          transition={{ delay: 0.2, duration: 1 }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Keywords Present */}
            {analysisResults.match_analysis?.keywords_present && (
              <motion.div
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  Keywords Found ({analysisResults.match_analysis.keywords_present?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisResults.match_analysis.keywords_present?.slice(0, 15).map((keyword, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-green-900/30 text-green-300 rounded-full text-sm border border-green-700/50"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Keywords Missing */}
            {analysisResults.match_analysis?.keywords_missing && analysisResults.match_analysis.keywords_missing.length > 0 && (
              <motion.div
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
              >
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-400" />
                  Keywords to Add ({analysisResults.match_analysis.keywords_missing?.length || 0})
                </h3>
                <p className="text-slate-400 text-sm mb-3">
                  Adding these keywords could improve your match score
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysisResults.match_analysis.keywords_missing?.slice(0, 15).map((keyword, i) => {
                    const keywordText = typeof keyword === 'object' ? (keyword.keyword || keyword.name || 'N/A') : keyword;
                    return (
                      <span
                        key={i}
                        className="px-3 py-1 bg-amber-900/30 text-amber-300 rounded-full text-sm border border-amber-700/50"
                      >
                        {keywordText}
                      </span>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {/* Gaps & Recommendations - Show 3 cards, blur the last one for guests */}
            {analysisResults.recommendations && analysisResults.recommendations.priority_improvements && (
              <motion.div
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h3 className="text-white font-semibold mb-4">Priority Improvements</h3>
                <div className="space-y-3">
                  {analysisResults.recommendations.priority_improvements?.slice(0, 3).map((improvement, i) => (
                    <div key={i} className={`relative ${i === 2 ? 'overflow-hidden' : ''}`}>
                      <div className={`bg-slate-700/50 rounded-lg p-4 border border-slate-600 ${i === 2 ? 'blur-sm' : ''}`}>
                        <div className="flex justify-between items-start mb-2">
                          <p className="text-white font-semibold">{improvement.action}</p>
                          <span className="text-amber-400 text-sm">+{improvement.estimated_impact}%</span>
                        </div>
                        <p className="text-slate-400 text-sm mb-2">{improvement.why_matters}</p>
                        <p className="text-slate-500 text-sm italic">Example: {improvement.example}</p>
                      </div>
                      {/* Unlock overlay for last card */}
                      {i === 2 && (
                        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/60 rounded-lg">
                          <div className="text-center px-4">
                            <svg className="w-8 h-8 text-yellow-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            <p className="text-white font-semibold text-sm mb-2">Unlock Full Insights</p>
                            <p className="text-slate-300 text-xs mb-3">Sign up to see all recommendations</p>
                            <button
                              onClick={handleUpgrade}
                              className="px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white text-xs font-semibold rounded-lg transition-all"
                            >
                              Get Access
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* ATS Optimization Tips */}
            {analysisResults.ats_optimization?.natural_integration_tips && (
              <motion.div
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <h3 className="text-white font-semibold mb-3">ATS Optimization Tips</h3>
                <ul className="space-y-2">
                  {analysisResults.ats_optimization.natural_integration_tips?.slice(0, 3).map((tip, i) => (
                    <li key={i} className="text-slate-300 text-sm flex gap-2">
                      <span className="text-cyan-400">✓</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}

            {/* Premium Features Section */}
            <motion.div
              className="bg-gradient-to-br from-purple-900/30 via-blue-900/30 to-cyan-900/30 border-2 border-purple-500/40 rounded-xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className="text-center mb-8">
                <h3 className="text-3xl font-bold text-white mb-3 font-display">
                  Unlock Premium Features
                </h3>
                <p className="text-slate-300 text-lg">
                  Sign up to get access to powerful tools that help you land your dream job
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* Feature 1: Optimized Resume */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-purple-500/20 rounded-lg">
                      <FileText className="w-6 h-6 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">AI-Optimized Resume</h4>
                      <p className="text-slate-300 text-sm">
                        Get an AI-generated, ATS-optimized version of your resume tailored to each job application
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 2: Cover Letter Generation */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-500/20 rounded-lg">
                      <Mail className="w-6 h-6 text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">Cover Letter Generator</h4>
                      <p className="text-slate-300 text-sm">
                        Create personalized, compelling cover letters that match your resume and the job description
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 3: Advanced Feedback */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-cyan-500/20 rounded-lg">
                      <Sparkles className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">Advanced Insights</h4>
                      <p className="text-slate-300 text-sm">
                        Access detailed feedback, improvement suggestions, and personalized recommendations
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 4: Download Optimized Resume */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-green-500/20 rounded-lg">
                      <Download className="w-6 h-6 text-green-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">Download & Save</h4>
                      <p className="text-slate-300 text-sm">
                        Download your optimized resume in PDF/DOCX format and save all your analyses for future reference
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 5: Unlimited Analyses */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-yellow-500/20 rounded-lg">
                      <Infinity className="w-6 h-6 text-yellow-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">Unlimited Analyses</h4>
                      <p className="text-slate-300 text-sm">
                        Analyze as many resumes as you need without any limits - perfect for multiple job applications
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 6: History & Tracking */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-pink-500/20 rounded-lg">
                      <CheckCircle className="w-6 h-6 text-pink-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-2">Analysis History</h4>
                      <p className="text-slate-300 text-sm">
                        Keep track of all your resume analyses, compare improvements over time, and monitor your progress
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-center">
                <motion.button
                  onClick={handleUpgrade}
                  className="px-8 py-3 bg-gradient-to-r from-cyan-500 via-purple-600 to-pink-600 hover:from-cyan-600 hover:via-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg inline-flex items-center gap-2 text-lg shadow-lg shadow-purple-500/50"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Sign Up & Get Started
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
                <p className="text-slate-400 text-sm mt-4">
                  No credit card required • Start your free trial today
                </p>
              </div>
            </motion.div>

            {/* New Analysis Button */}
            <motion.button
              onClick={() => {
                setStep('analyze');
                setResumeFile(null);
                setJobDescription('');
                setJobTitle('');
                setCompanyName('');
                setError('');
              }}
              className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Run Another Analysis
            </motion.button>
          </motion.div>
        )}
        </AnimatePresence>
        </div>
      </div>
    </>
  );
};

export default GuestAnalyze;
