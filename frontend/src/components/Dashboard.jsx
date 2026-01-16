import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X, ArrowRight } from 'lucide-react';
import { ROUTES } from '../config/routes';
import { getCreditsDisplay } from '../utils/credits';
import TrialOfferBanner from './ui/TrialOfferBanner';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Dashboard Component
 *
 * Main user dashboard showing:
 * - User profile stats (plan, credits)
 * - Dashboard statistics (total analyses, average score)
 * - Score trend chart
 * - Top skills to develop chart
 * - Analysis history table
 */
const Dashboard = ({ userProfile }) => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const token = localStorage.getItem('token');

  const [analyses, setAnalyses] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  const [subscriptionTier, setSubscriptionTier] = useState(null);

  // Check for payment success parameter
  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    const purchaseType = searchParams.get('purchase_type');

    if (paymentStatus === 'success') {
      // Determine what was purchased
      if (purchaseType === 'weekly_pass') {
        setSubscriptionTier('7-day-pass');
      } else if (userProfile) {
        // Normalize tier name
        const tier = userProfile.subscription_tier === 'premium' ? 'pro' : userProfile.subscription_tier;
        setSubscriptionTier(tier);
      }
      setShowSuccessNotification(true);

      // Remove query parameters from URL
      searchParams.delete('payment');
      searchParams.delete('purchase_type');
      setSearchParams(searchParams, { replace: true });

      // Auto-hide after 8 seconds
      setTimeout(() => {
        setShowSuccessNotification(false);
      }, 8000);
    }
  }, [searchParams, userProfile, setSearchParams]);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch analyses and stats in parallel
      const [analysesRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/analyses`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/dashboard/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      // Check for HTTP errors
      if (!analysesRes.ok || !statsRes.ok) {
        const status = !analysesRes.ok ? analysesRes.status : statsRes.status;
        if (status === 401) {
          // Token expired or invalid - redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('userProfile');
          window.location.href = '/login';
          return;
        }
        throw new Error(`Server error: ${status}`);
      }

      const analysesData = await analysesRes.json();
      const statsData = await statsRes.json();

      // Handle both old array format and new paginated format
      const analysesArray = analysesData.analyses || (Array.isArray(analysesData) ? analysesData : []);
      setAnalyses(analysesArray);
      setDashboardStats({
        total_analyses: statsData.total_analyses || 0,
        average_score: statsData.average_score || 0,
        score_trend: statsData.score_trend || [],
        top_missing_skills: statsData.top_missing_skills || []
      });
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch data on mount
  useEffect(() => {
    if (token) {
      fetchDashboardData();
    }
  }, [token, fetchDashboardData]);

  const viewAnalysis = async (analysisId) => {
    // Navigate to result page with analysis ID
    navigate(`/result/${analysisId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="text-center relative z-10">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-300 relative z-10">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6 relative z-10">
      {/* Payment Success Notification */}
      <AnimatePresence>
        {showSuccessNotification && subscriptionTier && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4"
          >
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 border border-green-500 rounded-xl shadow-2xl p-5">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <CheckCircle className="w-8 h-8 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-1">
                    {subscriptionTier === '7-day-pass' ? '7-Day Pass Activated!' : `Welcome to ${subscriptionTier.charAt(0).toUpperCase() + subscriptionTier.slice(1)}!`}
                  </h3>
                  <p className="text-green-50 text-sm">
                    {subscriptionTier === '7-day-pass'
                      ? 'Enjoy unlimited resume scans for the next 7 days!'
                      : `Your subscription is now active. ${subscriptionTier === 'elite' ? '200' : subscriptionTier === 'pro_founding' ? '50' : '50'} credits have been added to your account.`}
                  </p>
                </div>
                <button
                  onClick={() => setShowSuccessNotification(false)}
                  className="flex-shrink-0 text-white hover:text-green-100 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <h2 className="text-3xl font-bold text-white font-display">Your Career Dashboard</h2>
        {userProfile && (
          <div className="flex items-center gap-4 flex-wrap">
            {userProfile.is_admin && (
              <button
                onClick={() => navigate(ROUTES.ADMIN_ANALYTICS)}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-blue-500/25 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Analytics
              </button>
            )}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-2">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${userProfile.subscription_tier === 'elite' ? 'bg-amber-400' : (userProfile.subscription_tier === 'pro' || userProfile.subscription_tier === 'pro_founding') ? 'bg-cyan-400' : 'bg-gray-400'}`}></div>
                <span className="text-gray-300 text-sm">
                  {userProfile.subscription_tier === 'elite' ? 'Elite Plan' : userProfile.subscription_tier === 'pro_founding' ? 'Pro Founding' : userProfile.subscription_tier === 'pro' ? 'Pro Plan' : 'Free Plan'}
                </span>
              </div>
            </div>
            <div className={`backdrop-blur-sm border rounded-xl px-4 py-2 ${userProfile.subscription_tier === 'elite' ? 'bg-gradient-to-r from-amber-500/20 to-orange-600/20 border-amber-500/30' : (userProfile.subscription_tier === 'pro' || userProfile.subscription_tier === 'pro_founding') ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 border-cyan-500/30' : 'bg-white/10 border-white/20'}`}>
              <div className="flex items-center gap-2">
                <svg className={`w-4 h-4 ${userProfile.subscription_tier === 'elite' ? 'text-amber-400' : (userProfile.subscription_tier === 'pro' || userProfile.subscription_tier === 'pro_founding') ? 'text-cyan-400' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className={`font-semibold ${userProfile.subscription_tier === 'elite' ? 'text-amber-400' : (userProfile.subscription_tier === 'pro' || userProfile.subscription_tier === 'pro_founding') ? 'text-cyan-400' : 'text-gray-400'}`}>{getCreditsDisplay(userProfile.credits, userProfile.subscription_tier || 'free')} Credits</span>
              </div>
            </div>
            {userProfile.subscription_tier === 'free' && (
              <button
                onClick={() => navigate(ROUTES.PRICING)}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-cyan-500/25"
              >
                Upgrade Now
              </button>
            )}
            {userProfile.subscription_tier === 'pro' && (
              <button
                onClick={() => navigate(ROUTES.PRICING)}
                className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-amber-500/25"
              >
                Upgrade to Elite
              </button>
            )}
          </div>
        )}
      </div>

      {/* Trial Status Banner */}
      {userProfile && userProfile.is_trial_active && userProfile.trial_end_date && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-green-600/90 to-emerald-600/90 backdrop-blur-sm border border-green-400/50 rounded-xl p-4 md:p-5 mb-6"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="animate-pulse">
                <svg className="w-6 h-6 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-white font-bold text-base md:text-lg">
                  {(() => {
                    const trialEnd = new Date(userProfile.trial_end_date);
                    const now = new Date();
                    const daysRemaining = Math.ceil((trialEnd - now) / (1000 * 60 * 60 * 24));
                    if (daysRemaining > 0) {
                      return `Free Trial Active - ${daysRemaining} ${daysRemaining === 1 ? 'day' : 'days'} remaining`;
                    } else {
                      return 'Free Trial Expired - Upgrade to Keep Pro Benefits';
                    }
                  })()}
                </p>
                <p className="text-white/80 text-sm">
                  {(() => {
                    const trialEnd = new Date(userProfile.trial_end_date);
                    const now = new Date();
                    const daysRemaining = Math.ceil((trialEnd - now) / (1000 * 60 * 60 * 24));
                    if (daysRemaining > 2) {
                      return 'Enjoy all Pro features during your trial';
                    } else if (daysRemaining > 0) {
                      return 'Trial ending soon - Upgrade now to keep your Pro benefits';
                    } else {
                      return 'Your trial has ended. Upgrade within 3 days to keep Pro features';
                    }
                  })()}
                </p>
              </div>
            </div>
            {(() => {
              const trialEnd = new Date(userProfile.trial_end_date);
              const now = new Date();
              const daysRemaining = Math.ceil((trialEnd - now) / (1000 * 60 * 60 * 24));
              if (daysRemaining <= 2 || daysRemaining <= 0) {
                return (
                  <button
                    onClick={() => navigate(ROUTES.PRICING)}
                    className="px-4 py-2 rounded-lg bg-white text-green-600 hover:bg-green-50 font-semibold text-sm transition-all hover:scale-105 active:scale-95"
                  >
                    Upgrade Now
                  </button>
                );
              }
              return null;
            })()}
          </div>
        </motion.div>
      )}

      {/* Trial Conversion Banner for Free Users */}
      {userProfile && userProfile.subscription_tier === 'free' && !userProfile.trial_start_date && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-600/90 to-cyan-600/90 backdrop-blur-sm border border-blue-400/50 rounded-xl p-4 md:p-5 mb-6"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="animate-pulse">
                <svg className="w-6 h-6 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-white font-bold text-base md:text-lg">
                  Start Your 7-Day Free Trial
                </p>
                <p className="text-white/80 text-sm">
                  Get 10 credits and access to all Pro features - Try it free!
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                navigate(`${ROUTES.CHECKOUT}?tier=pro_founding`);
              }}
              className="px-4 py-2 rounded-lg bg-white text-blue-600 hover:bg-blue-50 font-semibold text-sm transition-all hover:scale-105 active:scale-95"
            >
              Start Free Trial
            </button>
          </div>
        </motion.div>
      )}

      {/* Trial Offer Banner for Low Credit Users */}
      {userProfile && userProfile.credits <= 3 && !userProfile.is_trial_active && userProfile.subscription_tier === 'free' && (
        <TrialOfferBanner
          credits={userProfile.credits}
          onStartTrial={() => {
            navigate(`${ROUTES.CHECKOUT}?tier=pro_founding`);
          }}
          className="mb-6"
        />
      )}

      {/* Quick Actions */}
      <div className="flex gap-4">
        <button
          onClick={() => navigate(ROUTES.ANALYZE)}
          className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          New Analysis
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Welcome/Onboarding Section for New Users */}
      {(!dashboardStats || dashboardStats.total_analyses === 0) && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 sm:p-8 md:p-12 mb-6"
        >
          {/* Background atmospheric effects */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-600/5 pointer-events-none" />
          <div 
            className="absolute inset-0 opacity-30 pointer-events-none" 
            style={{ 
              backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', 
              backgroundSize: '40px 40px' 
            }} 
          />

          <div className="text-center max-w-3xl mx-auto relative z-10">
            {/* Enhanced Icon Treatment */}
            <div className="relative inline-flex items-center justify-center mb-6 sm:mb-8">
              {/* Outer glow ring */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-600/20 blur-xl animate-pulse" />
              {/* Icon container */}
              <div className="relative w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center backdrop-blur-sm">
                <svg className="w-10 h-10 sm:w-12 sm:h-12 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            {/* Heading with gradient text treatment */}
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3 sm:mb-4 font-display px-4">
              Welcome to Your{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                Career Dashboard
              </span>
            </h2>

            {/* Description Text */}
            <p className="text-base sm:text-lg md:text-xl text-gray-300 mb-2 sm:mb-3 max-w-2xl mx-auto leading-relaxed px-4">
              Get started by analyzing your resume against any job description
            </p>
            <p className="text-sm sm:text-base text-gray-400 mb-8 sm:mb-10 max-w-2xl mx-auto px-4">
              Our AI-powered analysis helps you identify gaps, optimize keywords, and improve your match score
            </p>

            {/* Enhanced CTA Button */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-10 sm:mb-12 px-4">
              <button
                onClick={() => navigate(ROUTES.ANALYZE)}
                className="group relative overflow-hidden bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 sm:px-8 md:px-10 py-3 sm:py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-cyan-500/40 flex items-center gap-2 sm:gap-3 text-base sm:text-lg hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-black"
              >
                {/* Shimmer effect */}
                <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                <svg className="w-5 h-5 sm:w-6 sm:h-6 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="relative z-10">Start Your First Analysis</span>
                <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 relative z-10 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>

            {/* Enhanced Feature Cards Grid */}
            <div className="mt-8 sm:mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 text-left px-4">
              {/* Upload Resume Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="group relative bg-white/5 backdrop-blur-sm rounded-xl p-5 sm:p-6 border border-white/10 hover:border-cyan-500/30 transition-all duration-300 hover:bg-white/10"
              >
                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-500/0 via-blue-500/0 to-blue-600/0 group-hover:from-cyan-500/10 group-hover:via-blue-500/5 group-hover:to-blue-600/10 transition-all duration-300 pointer-events-none" />
                
                <div className="relative z-10">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-6 h-6 sm:w-7 sm:h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <h3 className="text-white font-semibold mb-2 text-base sm:text-lg">Upload Resume</h3>
                  <p className="text-gray-400 text-xs sm:text-sm leading-relaxed">Upload your resume in PDF, DOCX, or TXT format</p>
                </div>
              </motion.div>

              {/* Paste Job Description Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
                className="group relative bg-white/5 backdrop-blur-sm rounded-xl p-5 sm:p-6 border border-white/10 hover:border-cyan-500/30 transition-all duration-300 hover:bg-white/10"
              >
                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-500/0 via-blue-500/0 to-blue-600/0 group-hover:from-cyan-500/10 group-hover:via-blue-500/5 group-hover:to-blue-600/10 transition-all duration-300 pointer-events-none" />
                
                <div className="relative z-10">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-6 h-6 sm:w-7 sm:h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <h3 className="text-white font-semibold mb-2 text-base sm:text-lg">Paste Job Description</h3>
                  <p className="text-gray-400 text-xs sm:text-sm leading-relaxed">Add the job description you're applying for</p>
                </div>
              </motion.div>

              {/* Get Insights Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
                className="group relative bg-white/5 backdrop-blur-sm rounded-xl p-5 sm:p-6 border border-white/10 hover:border-cyan-500/30 transition-all duration-300 hover:bg-white/10 sm:col-span-2 lg:col-span-1"
              >
                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-500/0 via-blue-500/0 to-blue-600/0 group-hover:from-cyan-500/10 group-hover:via-blue-500/5 group-hover:to-blue-600/10 transition-all duration-300 pointer-events-none" />
                
                <div className="relative z-10">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-6 h-6 sm:w-7 sm:h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-white font-semibold mb-2 text-base sm:text-lg">Get Insights</h3>
                  <p className="text-gray-400 text-xs sm:text-sm leading-relaxed">Receive detailed analysis and improvement suggestions</p>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Stats Cards */}
      {dashboardStats && dashboardStats.total_analyses > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-gray-400 text-sm font-medium">Total Analyses</h3>
            <p className="text-4xl font-bold text-cyan-400">{dashboardStats.total_analyses}</p>
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-gray-400 text-sm font-medium">Average Score</h3>
            <p className="text-4xl font-bold text-green-400">{dashboardStats.average_score}%</p>
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-gray-400 text-sm font-medium">Top Skill Gap</h3>
            <p className="text-2xl font-bold text-orange-400">
              {dashboardStats.top_missing_skills && dashboardStats.top_missing_skills[0] ? dashboardStats.top_missing_skills[0].skill : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Score Trend Chart */}
      {dashboardStats && dashboardStats.score_trend && dashboardStats.score_trend.length > 0 && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-white font-display">Match Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dashboardStats.score_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="job_title" angle={-45} textAnchor="end" height={100} stroke="#9CA3AF" />
              <YAxis domain={[0, 100]} stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', color: '#F9FAFB' }} />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#06B6D4" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Skills to Develop Chart */}
      {dashboardStats && dashboardStats.top_missing_skills && dashboardStats.top_missing_skills.length > 0 && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-white font-display">Top Skills to Develop</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardStats.top_missing_skills.slice(0, 8)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="skill" angle={-45} textAnchor="end" height={100} stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', color: '#F9FAFB' }} />
              <Bar dataKey="count" fill="#06B6D4" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Analysis History Table */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-white/20">
          <h3 className="text-xl font-semibold text-white font-display">Analysis History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/10">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Resume</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Job Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Match Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white/5 backdrop-blur-xl divide-y divide-white/10">
              {analyses.map((analysis) => (
                <tr key={analysis.id} className="hover:bg-white/10 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-cyan-400">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="truncate max-w-[150px]" title={analysis.resume_filename}>
                        {analysis.resume_filename || 'Unknown'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                    {analysis.job_title || 'Untitled'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {analysis.company_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      analysis.match_score >= 70 ? 'bg-green-900/50 text-green-300 border border-green-500/30' :
                      analysis.match_score >= 50 ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-500/30' :
                      'bg-red-900/50 text-red-300 border border-red-500/30'
                    }`}>
                      {analysis.match_score}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => viewAnalysis(analysis.id)}
                      className="text-cyan-400 hover:text-cyan-300 transition font-medium"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {analyses.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <div className="text-cyan-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-lg">No analyses yet</p>
              <p className="text-sm mb-4">Create your first analysis to get started!</p>
              <button
                onClick={() => navigate(ROUTES.ANALYZE)}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-2 rounded-lg font-semibold transition"
              >
                Start Your First Analysis
              </button>
            </div>
          )}
        </div>
      </div>
      </div>
    </div>
  );
};

export default Dashboard;
