import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X } from 'lucide-react';
import { ROUTES } from '../config/routes';

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
    if (paymentStatus === 'success' && userProfile) {
      // Normalize tier name
      const tier = userProfile.subscription_tier === 'premium' ? 'pro' : userProfile.subscription_tier;
      setSubscriptionTier(tier);
      setShowSuccessNotification(true);

      // Remove query parameter from URL
      searchParams.delete('payment');
      setSearchParams(searchParams, { replace: true });

      // Auto-hide after 8 seconds
      setTimeout(() => {
        setShowSuccessNotification(false);
      }, 8000);
    }
  }, [searchParams, userProfile, setSearchParams]);

  // Fetch data on mount
  useEffect(() => {
    if (token) {
      fetchDashboardData();
    }
  }, [token]);

  const fetchDashboardData = async () => {
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
  };

  const viewAnalysis = async (analysisId) => {
    // Navigate to result page with analysis ID
    navigate(`/result/${analysisId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-300">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
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
                    Welcome to {subscriptionTier.charAt(0).toUpperCase() + subscriptionTier.slice(1)}!
                  </h3>
                  <p className="text-green-50 text-sm">
                    Your subscription is now active. {subscriptionTier === 'elite' ? '1,000' : '100'} credits have been added to your account.
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
        <h2 className="text-3xl font-bold text-white">Your Career Dashboard</h2>
        {userProfile && (
          <div className="flex items-center gap-4 flex-wrap">
            {userProfile.is_admin && (
              <button
                onClick={() => navigate(ROUTES.ADMIN)}
                className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-purple-500/25 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                Admin
              </button>
            )}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg px-4 py-2">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${userProfile.subscription_tier === 'elite' ? 'bg-amber-400' : userProfile.subscription_tier === 'pro' ? 'bg-cyan-400' : 'bg-slate-400'}`}></div>
                <span className="text-slate-300 text-sm">
                  {userProfile.subscription_tier === 'elite' ? 'Elite Plan' : userProfile.subscription_tier === 'pro' ? 'Pro Plan' : 'Free Plan'}
                </span>
              </div>
            </div>
            <div className={`backdrop-blur-sm border rounded-lg px-4 py-2 ${userProfile.subscription_tier === 'elite' ? 'bg-gradient-to-r from-amber-500/20 to-orange-600/20 border-amber-500/30' : userProfile.subscription_tier === 'pro' ? 'bg-gradient-to-r from-cyan-500/20 to-purple-600/20 border-cyan-500/30' : 'bg-slate-700/30 border-slate-600/50'}`}>
              <div className="flex items-center gap-2">
                <svg className={`w-4 h-4 ${userProfile.subscription_tier === 'elite' ? 'text-amber-400' : userProfile.subscription_tier === 'pro' ? 'text-cyan-400' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className={`font-semibold ${userProfile.subscription_tier === 'elite' ? 'text-amber-400' : userProfile.subscription_tier === 'pro' ? 'text-cyan-400' : 'text-slate-400'}`}>{userProfile.credits} Credits</span>
              </div>
            </div>
            {userProfile.subscription_tier === 'free' && (
              <button
                onClick={() => navigate(ROUTES.PRICING)}
                className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-cyan-500/25"
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

      {/* Quick Actions */}
      <div className="flex gap-4">
        <button
          onClick={() => navigate(ROUTES.ANALYZE)}
          className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 flex items-center gap-2"
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

      {/* Stats Cards */}
      {dashboardStats && dashboardStats.total_analyses > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-slate-400 text-sm font-medium">Total Analyses</h3>
            <p className="text-4xl font-bold text-cyan-400">{dashboardStats.total_analyses}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-slate-400 text-sm font-medium">Average Score</h3>
            <p className="text-4xl font-bold text-green-400">{dashboardStats.average_score}%</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-cyan-400/50 transition">
            <h3 className="text-slate-400 text-sm font-medium">Top Skill Gap</h3>
            <p className="text-2xl font-bold text-orange-400">
              {dashboardStats.top_missing_skills && dashboardStats.top_missing_skills[0] ? dashboardStats.top_missing_skills[0].skill : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Score Trend Chart */}
      {dashboardStats && dashboardStats.score_trend && dashboardStats.score_trend.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-white">Match Score Trend</h3>
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
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-white">Top Skills to Develop</h3>
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
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-600">
          <h3 className="text-xl font-semibold text-white">Analysis History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-600">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Resume</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Job Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Match Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-slate-800/30 divide-y divide-slate-600">
              {analyses.map((analysis) => (
                <tr key={analysis.id} className="hover:bg-slate-700/30 transition">
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
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
            <div className="text-center py-12 text-slate-400">
              <div className="text-cyan-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-lg">No analyses yet</p>
              <p className="text-sm mb-4">Create your first analysis to get started!</p>
              <button
                onClick={() => navigate(ROUTES.ANALYZE)}
                className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-6 py-2 rounded-lg font-semibold transition"
              >
                Start Your First Analysis
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
