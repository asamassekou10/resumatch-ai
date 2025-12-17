import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUp, LogIn, Zap, ArrowRight, AlertCircle, CheckCircle, Loader, Clock } from 'lucide-react';
import guestService from '../services/guestService';
import { ROUTES } from '../config/routes';
import SEO from './common/SEO';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
  const [sessionInfo, setSessionInfo] = useState(null);

  // Initialize guest session on mount
  useEffect(() => {
    const initGuestSession = async () => {
      try {
        const response = await guestService.createSession();
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

        if (errorMessage.includes('Too many guest sessions') || errorMessage.includes('RATE_LIMIT_EXCEEDED')) {
          setError('Too many sessions created. Please try again in 24 hours or create an account.');
        } else if (errorMessage.includes('Daily guest analysis limit') || errorMessage.includes('DAILY_LIMIT_EXCEEDED')) {
          setError('Daily guest limit reached. Create an account for unlimited access!');
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
        title="Free Resume Analysis"
        description="Try ResuMatch AI for free! Get instant AI-powered resume analysis, ATS scoring, and personalized improvement suggestions without signing up."
        keywords="free resume analysis, AI resume checker, ATS score free, resume feedback"
        url="https://resumeanalyzerai.com/guest-analyze"
      />
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
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
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-4">Guest Access</h1>
              <p className="text-slate-300 text-lg mb-8">
                Get started with 2 free analyses instantly. No sign-up required.
              </p>
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
                {error ? (
                  <>
                    <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400 mb-4">{error}</p>
                    <div className="flex gap-3 justify-center">
                      <button
                        onClick={handleSignIn}
                        className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-semibold rounded-lg"
                      >
                        Sign In
                      </button>
                      <button
                        onClick={() => navigate(ROUTES.PRICING)}
                        className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg"
                      >
                        View Pricing
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <motion.div
                      className="inline-block mb-4"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <Clock className="w-16 h-16 text-cyan-400" />
                    </motion.div>
                    <p className="text-slate-300">Initializing your guest session...</p>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Analyze Step */}
        {step === 'analyze' && (
          <motion.div
            key="analyze"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-4xl mx-auto"
          >
            {/* Guest Mode Banner */}
            <motion.div
              className="bg-gradient-to-r from-purple-600/90 to-cyan-600/90 backdrop-blur-sm border border-purple-400/50 rounded-lg p-4 mb-6"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-yellow-300" />
                  <div>
                    <p className="text-white font-semibold text-sm">Guest Mode Active</p>
                    <p className="text-white/80 text-xs">{guestCredits} credits available • 24 hours access</p>
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
                    className="px-4 py-2 rounded-lg bg-white text-purple-600 hover:bg-purple-50 font-semibold text-sm transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Upgrade
                  </motion.button>
                </div>
              </div>
            </motion.div>

            {/* Error Message */}
            {error && (
              <motion.div
                className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6 flex items-start gap-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-400 text-sm">{error}</p>
              </motion.div>
            )}

            {/* Form */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Resume Upload */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <label className="block text-white font-semibold mb-3">Resume File</label>
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
                    className="flex items-center justify-center w-full px-4 py-8 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-cyan-500 transition-colors bg-slate-800/30"
                  >
                    {resumeFile ? (
                      <div className="text-center">
                        <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                        <p className="text-white font-semibold text-sm">{resumeFile.name}</p>
                        <p className="text-slate-400 text-xs mt-1">Click to change</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <FileUp className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-white font-semibold text-sm">Upload Your Resume</p>
                        <p className="text-slate-400 text-xs mt-1">PDF, DOCX, or TXT</p>
                      </div>
                    )}
                  </label>
                </div>
              </motion.div>

              {/* Job Details */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <label className="block text-white font-semibold mb-3">Job Details</label>
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Company (optional)"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Job Title (optional)"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                  />
                  <textarea
                    placeholder="Paste job description here (required)"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none h-32 resize-none"
                  />
                </div>
              </motion.div>
            </div>

            {/* Progress Section */}
            {loading && (
              <motion.div
                className="mt-6 space-y-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-white font-semibold flex items-center gap-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Loader className="w-4 h-4 text-cyan-400" />
                      </motion.div>
                      {loadingMessage}
                    </span>
                    <span className="text-slate-400 text-sm">{Math.round(loadingProgress)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-cyan-500 to-purple-600"
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
              <motion.button
                onClick={handleAnalyze}
                disabled={loading || !resumeFile || !jobDescription}
                className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-all"
                whileHover={!loading && resumeFile && jobDescription ? { scale: 1.02 } : {}}
                whileTap={!loading && resumeFile && jobDescription ? { scale: 0.98 } : {}}
              >
                Start Analysis
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            )}
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
              className="bg-gradient-to-br from-slate-800 to-slate-700 border border-slate-600 rounded-lg p-8"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
                    {analysisResults.overall_score || 0}%
                  </div>
                  <p className="text-slate-300 font-semibold">Overall Match Score</p>
                  <p className="text-slate-400 text-sm mt-2">{analysisResults.interpretation}</p>
                </div>
                <div className="flex flex-col justify-center gap-3">
                  <div>
                    <p className="text-slate-400 text-sm mb-1">Industry</p>
                    <p className="text-white font-semibold">{analysisResults.job_industry || 'Unknown'}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm mb-1">ATS Pass Rate</p>
                    <p className="text-cyan-400 font-semibold">{analysisResults.expected_ats_pass_rate}</p>
                  </div>
                </div>
              </div>
            </motion.div>

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

            {/* Upgrade CTA */}
            <motion.div
              className="bg-gradient-to-r from-purple-600/20 to-cyan-600/20 border border-purple-400/30 rounded-lg p-6 text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p className="text-slate-300 mb-4">
                Create an account to save your analyses, unlock unlimited analyses, and get advanced features.
              </p>
              <motion.button
                onClick={handleUpgrade}
                className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-semibold rounded-lg inline-flex items-center gap-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Upgrade Now
                <ArrowRight className="w-4 h-4" />
              </motion.button>
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
    </>
  );
};

export default GuestAnalyze;
