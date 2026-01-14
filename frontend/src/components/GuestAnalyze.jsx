import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
// Framer Motion removed to fix animation compatibility issues
import { FileUp, ArrowRight, AlertCircle, CheckCircle, Loader, Clock, FileText, Download, Sparkles, Mail, Infinity, Shield, Lock, ChevronDown, ChevronUp, Target, Search } from 'lucide-react';
import guestService from '../services/guestService';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';
import ScoreBreakdown from './ScoreBreakdown';
import { generateFAQSchema } from '../utils/structuredData';
import { isPrerendering } from '../utils/prerender';
import BlurredSection from './pricing/BlurredSection';
import PricingModal from './pricing/PricingModal';
import PaymentModal from './pricing/PaymentModal';

// FAQ Accordion Component - Using CSS transitions instead of Framer Motion
const FAQItem = ({ question, answer, isOpen, onClick }) => (
  <div className="border-b border-white/10 last:border-b-0">
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
    {isOpen && (
      <div className="overflow-hidden">
        <p className="px-4 pb-4 text-gray-400 text-sm leading-relaxed">{answer}</p>
      </div>
    )}
  </div>
);

const GuestAnalyze = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [step, setStep] = useState('welcome'); // welcome, analyze, analyzing, complete, results
  const [guestToken, setGuestToken] = useState(null);
  const [guestCredits, setGuestCredits] = useState(1);
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
  const [showComplete, setShowComplete] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    if (paymentStatus !== 'success') {
      return;
    }

    const activeGuestToken = guestToken || guestService.getGuestToken();
    if (!activeGuestToken) {
      setSearchParams({});
      return;
    }

    const refreshGuestCredits = async () => {
      try {
        const sessionInfo = await guestService.getSessionInfo(activeGuestToken);
        if (sessionInfo?.session?.credits_remaining !== undefined) {
          setGuestCredits(sessionInfo.session.credits_remaining);
          setError('');
          setShowPricingModal(false);
          setShowPaymentModal(false);
        }
      } catch (err) {
        console.error('Error refreshing guest credits:', err);
      } finally {
        setSearchParams({});
      }
    };

    refreshGuestCredits();
  }, [guestToken, searchParams, setSearchParams]);

  // FAQ data for the page
  const faqData = [
    {
      question: "Is this really free?",
      answer: "Yes! You get 1 free resume scan without creating an account. Sign up for a free account to get 10 analyses per month plus access to premium features like AI-optimized resumes and cover letter generation."
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
    // Skip API calls during prerendering
    if (isPrerendering()) {
      setStep('analyze'); // Just show the form during prerendering
      return;
    }

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
      setLoadingMessage('Analysis Complete!');

      setAnalysisResults(result);
      setGuestCredits(result.credits_remaining);

      // Show completion state with checkmark animation
      setShowComplete(true);

      // Delay to show completion animation before transitioning to results
      setTimeout(() => {
        setLoading(false);
        setShowComplete(false);
        setStep('results');
      }, 1500);
    } catch (err) {
      clearInterval(progressInterval);
      clearInterval(messageInterval);

      // Handle specific error cases
      const errorMessage = err.message || 'Analysis failed. Please try again.';

      if (errorMessage.includes('No guest credits remaining') || errorMessage.includes('INSUFFICIENT_CREDITS')) {
        setGuestCredits(0);
        setShowPricingModal(true);
      } else if (errorMessage.includes('Daily guest analysis limit reached') || errorMessage.includes('DAILY_LIMIT_EXCEEDED') || errorMessage.includes('Guest analysis limit reached')) {
        setShowPricingModal(true);
      } else if (errorMessage.includes('Too many guest sessions') || errorMessage.includes('RATE_LIMIT_EXCEEDED')) {
        setError('⏰ Too many sessions created. Please try again later or sign up for a free account!');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    setShowPricingModal(true);
  };

  const handleSelectPlan = (plan) => {
    // For $1.99 single_rescan, show payment modal directly (with guest checkout option)
    if (plan.type === 'single_rescan' && plan.price === 1.99) {
      setSelectedPlan(plan);
      setShowPricingModal(false);
      setShowPaymentModal(true);
      return;
    }
    
    const microPurchases = ['single_rescan', 'weekly_pass'];
    
    if (microPurchases.includes(plan.type)) {
      // For other micro-purchases, show payment modal
      setSelectedPlan(plan);
      setShowPricingModal(false);
      setShowPaymentModal(true);
    } else {
      // Subscription plans go to checkout (require signup)
      localStorage.setItem('selected_plan', JSON.stringify(plan));
      localStorage.setItem('redirect_after_auth', 'checkout'); // Store redirect in localStorage
      navigate(`${ROUTES.REGISTER}?redirect=checkout`);
    }
  };

  const handlePaymentSuccess = (purchaseData) => {
    setShowPaymentModal(false);
    // Refresh guest credits or show success message
    if (purchaseData?.user_info?.credits) {
      // If user got credits, they can now analyze
      setError('');
      // Optionally refresh the page or show success message
    }
  };

  const handlePaymentError = (error) => {
    setError(error?.message || 'Payment failed. Please try again.');
  };

  const handleSignUp = () => {
    navigate(ROUTES.REGISTER);
  };

  const handleSignIn = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <>
      <SEO
        title="Free AI Resume Scanner | ATS Score & Missing Keywords in 10 Seconds"
        description="Scan your resume for free. Get your ATS compatibility score, missing keywords report, and executive summary suggestions in 10 seconds. No signup required. 1 free scan for guests."
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
        {/* Welcome Step */}
        {step === 'welcome' && (
          <div className="max-w-2xl mx-auto relative z-10">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-4 font-display">Guest Access</h1>
              <p className="text-gray-300 text-lg mb-8">
                Try 1 free analysis instantly. No sign-up required.
              </p>
              <SpotlightCard className="rounded-lg p-8">
                {error ? (
                  <>
                    <Sparkles className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                    <p className="text-gray-300 mb-6 text-lg leading-relaxed">{error}</p>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center relative z-10">
                      <ShimmerButton onClick={() => navigate(ROUTES.REGISTER)}>
                        Sign Up Free <ArrowRight className="ml-1" size={16} />
                      </ShimmerButton>
                      <button
                        onClick={handleSignIn}
                        className="px-6 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold rounded-lg transition-colors relative z-10"
                      >
                        Sign In
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="inline-block mb-4 relative z-10 animate-spin" style={{ animationDuration: '2s' }}>
                      <Clock className="w-16 h-16 text-blue-400" />
                    </div>
                    <p className="text-gray-300 relative z-10">Initializing your guest session...</p>
                  </>
                )}
              </SpotlightCard>
            </div>
          </div>
        )}

        {/* Analyze Step - Redesigned for Trust & Conversion */}
        {step === 'analyze' && (
          <div className="max-w-6xl mx-auto relative z-10">
            {/* Welcome Banner - Gift-style messaging */}
            <div className="bg-gradient-to-r from-emerald-600/90 to-teal-600/90 backdrop-blur-sm border border-emerald-400/50 rounded-xl p-4 md:p-5 mb-8">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <div className="animate-pulse">
                    <Sparkles className="w-6 h-6 text-yellow-300" />
                  </div>
                  <div>
                    <p className="text-white font-bold text-base md:text-lg">Welcome! You have {guestCredits} Free Analysis available.</p>
                    <p className="text-white/80 text-sm">No account needed. Sign up for 10 free analyses/month!</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleSignIn}
                    className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white font-semibold text-sm transition-all hover:scale-105 active:scale-95"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={handleUpgrade}
                    className="px-4 py-2 rounded-lg bg-white text-emerald-600 hover:bg-emerald-50 font-semibold text-sm transition-all hover:scale-105 active:scale-95"
                  >
                    Get Unlimited
                  </button>
                </div>
              </div>
            </div>

            {/* Main Hero Section */}
            <div className="text-center mb-10">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 font-display">
                Free AI Resume Scanner
              </h1>
              <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto">
                See exactly what the ATS sees. Get your detailed score and keyword gaps in <span className="text-cyan-400 font-semibold">10 seconds</span>.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6 flex items-start gap-3 relative z-10 max-w-4xl mx-auto">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-400 text-sm relative z-10">{error}</p>
              </div>
            )}

            {/* Two Column Layout: Form + What You Get */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 relative z-10">
              {/* Left Column: Upload Form (3/5 width) */}
              <div className="lg:col-span-3 space-y-6">
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
                          className="flex items-center justify-center w-full px-4 py-10 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-500/5 transition-all bg-white/5 backdrop-blur-sm relative z-10"
                        >
                          {resumeFile ? (
                            <div className="text-center">
                              <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
                              <p className="text-white font-semibold">{resumeFile.name}</p>
                              <p className="text-slate-400 text-sm mt-1">Click to change file</p>
                            </div>
                          ) : (
                            <div className="text-center">
                              <FileUp className="w-12 h-12 text-blue-400 mx-auto mb-3" />
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
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
                          />
                          <input
                            type="text"
                            placeholder="Job Title (optional)"
                            value={jobTitle}
                            onChange={(e) => setJobTitle(e.target.value)}
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
                          />
                        </div>
                        <textarea
                          placeholder="Paste the job description here (required)"
                          value={jobDescription}
                          onChange={(e) => setJobDescription(e.target.value)}
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none h-36 resize-none"
                        />
                      </div>
                    </div>

                    {/* Progress Section */}
                    {loading && (
                      <div className="space-y-4">
                        {showComplete ? (
                          // Completion state with checkmark animation
                          <div className="text-center py-6">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 mb-4">
                              <CheckCircle className="w-10 h-10 text-white" />
                            </div>
                            <p className="text-white font-bold text-xl mb-2">Analysis Complete!</p>
                            <p className="text-gray-400 text-sm">Preparing your results...</p>
                          </div>
                        ) : (
                          // Loading state with progress bar
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-white font-semibold flex items-center gap-2">
                                <div className="animate-spin" style={{ animationDuration: '2s' }}>
                                  <Loader className="w-5 h-5 text-blue-400" />
                                </div>
                                {loadingMessage}
                              </span>
                              <span className="text-gray-400 text-sm">{Math.round(loadingProgress)}%</span>
                            </div>
                            <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-blue-500 via-blue-500 to-cyan-500 transition-all duration-300"
                                style={{ width: `${loadingProgress}%` }}
                              />
                            </div>
                            {/* Loading step indicators */}
                            <div className="flex justify-between text-xs text-gray-500 pt-2">
                              <span className={loadingProgress >= 20 ? 'text-blue-400' : ''}>Parsing</span>
                              <span className={loadingProgress >= 40 ? 'text-blue-400' : ''}>Analyzing</span>
                              <span className={loadingProgress >= 60 ? 'text-cyan-400' : ''}>Matching</span>
                              <span className={loadingProgress >= 80 ? 'text-green-400' : ''}>Scoring</span>
                            </div>
                          </div>
                        )}
                      </div>
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
                        <FileText className="w-4 h-4 text-blue-400" />
                        <span>PDF or DOCX</span>
                      </div>
                    </div>
                  </div>
                </SpotlightCard>
              </div>

              {/* Right Column: What You Get (2/5 width) */}
              <div className="lg:col-span-2">
                <div className="sticky top-8 space-y-6">
                  {/* Sneak Peek Card */}
                  <SpotlightCard className="rounded-xl p-6">
                    <h3 className="text-white font-bold text-lg mb-4 font-display">What You Get</h3>

                    {/* Mock Score Preview */}
                    <div className="relative mb-6 p-4 rounded-xl bg-gradient-to-br from-slate-800/80 to-slate-700/80 border border-white/10 overflow-hidden">
                      {/* Decorative blur */}
                      <div className="absolute -top-4 -right-4 w-20 h-20 bg-cyan-500/30 rounded-full blur-xl" />
                      <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-blue-500/30 rounded-full blur-xl" />

                      <div className="relative flex items-center justify-between">
                        <div>
                          <p className="text-gray-400 text-xs uppercase tracking-wide mb-1">Resume Score</p>
                          <p className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 font-display animate-pulse">
                            85/100
                          </p>
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
              </div>
            </div>

            {/* FAQ Section */}
            <div className="mt-16 max-w-3xl mx-auto">
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
            </div>
          </div>
        )}

        {/* Results Step - Intelligent Analysis */}
        {step === 'results' && analysisResults && (
          <div className="max-w-5xl mx-auto space-y-6 relative z-10">
            {/* Results Header */}
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-2">AI-Powered Analysis Complete</h1>
              <p className="text-slate-400">Comprehensive resume evaluation & ATS optimization</p>
            </div>

            {/* Overall Score Card */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 border border-slate-600 rounded-lg p-4 sm:p-6 md:p-8">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2">
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
            </div>

            {/* Score Breakdown - Transparent Calculation */}
            {analysisResults.score_breakdown && (
              <div>
                <ScoreBreakdown
                  scoreBreakdown={analysisResults.score_breakdown}
                  overallScore={analysisResults.overall_score}
                />
              </div>
            )}

            {/* Match Breakdown */}
            {analysisResults.match_analysis && analysisResults.match_analysis.match_breakdown && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 sm:p-6">
                <h3 className="text-white font-semibold mb-4">Match Breakdown</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {Object.entries(analysisResults.match_analysis.match_breakdown || {}).map(([key, rawValue]) => {
                    // Extract numeric value - handle objects with score property
                    const value = typeof rawValue === 'object' && rawValue !== null
                      ? (rawValue.score || rawValue.value || 0)
                      : (typeof rawValue === 'number' ? rawValue : 0);
                    return (
                      <div key={key} className="bg-slate-700/30 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-slate-300 text-sm capitalize font-medium">{key.replace(/_/g, ' ')}</span>
                          <span className="text-cyan-400 font-semibold">{value}%</span>
                        </div>
                        <div className="w-full bg-slate-600 rounded-full h-2.5">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-1000"
                            style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Keywords Present */}
            {analysisResults.match_analysis?.keywords_present && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
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
              </div>
            )}

            {/* Keywords Missing */}
            {analysisResults.match_analysis?.keywords_missing && analysisResults.match_analysis.keywords_missing.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-400" />
                  Keywords to Add ({analysisResults.match_analysis?.blurred_keywords_count ? analysisResults.match_analysis.keywords_missing.length + analysisResults.match_analysis.blurred_keywords_count : analysisResults.match_analysis.keywords_missing.length})
                </h3>
                <p className="text-slate-400 text-sm mb-3">
                  Adding these keywords could improve your match score
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysisResults.match_analysis.keywords_missing.map((keyword, i) => {
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

                {/* Blur Overlay for Additional Keywords */}
                {analysisResults.is_blurred && analysisResults.match_analysis?.blurred_keywords_count > 0 && (
                  <div className="mt-4">
                    <BlurredSection
                      title="Additional Missing Keywords"
                      blurredCount={analysisResults.match_analysis.blurred_keywords_count}
                      upgradeOptions={analysisResults.upgrade_options || []}
                      onUpgrade={() => navigate(ROUTES.REGISTER)}
                      message={analysisResults.upgrade_message || "Sign up to see all missing keywords"}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Gaps & Recommendations - Show 3 cards, blur the last one for guests */}
            {analysisResults.recommendations && analysisResults.recommendations.priority_improvements && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
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
                              className="px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white text-xs font-semibold rounded-lg transition-all"
                            >
                              Get Access
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ATS Optimization Tips */}
            {analysisResults.is_blurred && analysisResults.ats_optimization?.blurred ? (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                <BlurredSection
                  title="ATS Optimization Tips"
                  blurredCount={5}
                  upgradeOptions={analysisResults.upgrade_options || []}
                  onUpgrade={() => navigate(ROUTES.REGISTER)}
                  message="Sign up to unlock professional ATS strategies"
                  icon={Target}
                />
              </div>
            ) : (
              analysisResults.ats_optimization?.natural_integration_tips && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-3">ATS Optimization Tips</h3>
                  <ul className="space-y-2">
                    {analysisResults.ats_optimization.natural_integration_tips?.slice(0, 3).map((tip, i) => (
                      <li key={i} className="text-slate-300 text-sm flex gap-2">
                        <span className="text-cyan-400">✓</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            )}

            {/* Premium Features Section */}
            <div className="bg-gradient-to-br from-blue-900/30 via-blue-900/30 to-cyan-900/30 border-2 border-blue-500/40 rounded-xl p-8">
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-500/20 rounded-lg">
                      <FileText className="w-6 h-6 text-blue-400" />
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
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
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
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
                <button
                  onClick={handleSignUp}
                  className="px-8 py-3 bg-gradient-to-r from-cyan-500 via-blue-600 to-pink-600 hover:from-cyan-600 hover:via-blue-700 hover:to-pink-700 text-white font-semibold rounded-lg inline-flex items-center gap-2 text-lg shadow-lg shadow-blue-500/50 transition-transform hover:scale-105 active:scale-95"
                >
                  Sign Up & Get Started
                  <ArrowRight className="w-5 h-5" />
                </button>
                <p className="text-slate-400 text-sm mt-4">
                  Get started with 10 free credits today
                </p>
              </div>
            </div>

            {/* New Analysis Button */}
            <button
              onClick={() => {
                setStep('analyze');
                setResumeFile(null);
                setJobDescription('');
                setJobTitle('');
                setCompanyName('');
                setError('');
              }}
              className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors hover:scale-[1.02] active:scale-[0.98]"
            >
              Run Another Analysis
            </button>
          </div>
        )}
        </div>
      </div>

      {/* Pricing Modal for guests who run out of credits */}
      <PricingModal
        isOpen={showPricingModal}
        onClose={() => setShowPricingModal(false)}
        onSelectPlan={handleSelectPlan}
        upgradeOptions={[
          { type: 'single_rescan', price: 1.99, description: 'Re-scan once to see improvements' },
          { type: 'weekly_pass', price: 6.99, description: '7 days unlimited scans', recommended: true },
          { type: 'monthly_pro', price: 19.99, description: 'Full Pro features + templates' }
        ]}
        creditsRemaining={guestCredits}
      />

      {/* Payment Modal for micro-purchases */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setSelectedPlan(null);
        }}
        selectedPlan={selectedPlan}
        onSuccess={handlePaymentSuccess}
        onError={handlePaymentError}
        guestToken={guestToken}
      />
    </>
  );
};

export default GuestAnalyze;
