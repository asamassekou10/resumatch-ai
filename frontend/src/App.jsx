import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import Navigation from './components/Navigation';
import Breadcrumb from './components/Breadcrumb';
import AdminDashboard from './components/AdminDashboard';
import MarketIntelligenceDashboard from './components/MarketIntelligenceDashboard';
import SkillGapAnalysis from './components/SkillGapAnalysis';
import JobMarketStats from './components/JobMarketStats';
import SkillRelationships from './components/SkillRelationships';
import JobSeekerInsights from './components/JobSeekerInsights';
import PreferenceQuestionnaire from './components/PreferenceQuestionnaire';
import RepersonalizeButton from './components/RepersonalizeButton';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';


  function App() {
    const navigate = useNavigate();
    const location = useLocation();

    // Map URL paths to view states
    const pathToView = {
      '/': 'landing',
      '/login': 'login',
      '/register': 'register',
      '/dashboard': 'dashboard',
      '/analyze': 'analyze',
      '/result': 'result',
      '/pricing': 'pricing',
      '/admin': 'admin',
      '/auth/callback': 'auth-callback',
      '/market/dashboard': 'market-dashboard',
      '/market/skill-gap': 'skill-gap',
      '/market/job-stats': 'job-stats',
      '/market/skill-relationships': 'skill-relationships',
      '/market/insights': 'market-insights',
    };

    // Initialize view from URL path
    const getViewFromPath = (pathname) => {
      return pathToView[pathname] || 'landing';
    };

    // Map view states back to URLs
    const viewToPath = {
      'landing': '/',
      'login': '/login',
      'register': '/register',
      'dashboard': '/dashboard',
      'analyze': '/analyze',
      'result': '/result',
      'pricing': '/pricing',
      'admin': '/admin',
      'auth-callback': '/auth/callback',
      'market-dashboard': '/market/dashboard',
      'skill-gap': '/market/skill-gap',
      'job-stats': '/market/job-stats',
      'skill-relationships': '/market/skill-relationships',
      'market-insights': '/market/insights',
    };

    const [view, setViewState] = useState(() => getViewFromPath(location.pathname));
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [formData, setFormData] = useState({ email: '', password: '' });

    // Sync URL with view state changes
    const setView = (newView) => {
      setViewState(newView);
      const path = viewToPath[newView] || '/';
      navigate(path, { replace: false });
    };

    // Sync view state when URL changes (for back/forward buttons)
    useEffect(() => {
      const newView = getViewFromPath(location.pathname);
      setViewState(newView);
    }, [location.pathname]);
    const [analyses, setAnalyses] = useState([]);
    const [currentAnalysis, setCurrentAnalysis] = useState(null);
    const [dashboardStats, setDashboardStats] = useState(null);
    const [loading, setLoading] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisMessage, setAnalysisMessage] = useState('');
    const [error, setError] = useState('');
    const [resumeFile, setResumeFile] = useState(null);
    const [jobDescription, setJobDescription] = useState('');
    const [jobTitle, setJobTitle] = useState('');
    const [companyName, setCompanyName] = useState('');
    const [aiFeedback, setAiFeedback] = useState(null);
    const [optimizedResume, setOptimizedResume] = useState(null);
  const [coverLetter, setCoverLetter] = useState(null);
  // Separate loading states for each AI action
  const [generatingFeedback, setGeneratingFeedback] = useState(false);
  const [generatingOptimized, setGeneratingOptimized] = useState(false);
  const [generatingCoverLetter, setGeneratingCoverLetter] = useState(false);
  const [aiLoadingMessage, setAiLoadingMessage] = useState('');
  const [aiProgress, setAiProgress] = useState(0);
  const [landingResumeFile, setLandingResumeFile] = useState(null);
  //Password validation state
  const [passwordError, setPasswordError] = useState('');
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);
  // User profile and subscription state
  const [userProfile, setUserProfile] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  // Admin state
  const [isAdmin, setIsAdmin] = useState(false);
  // Extracted skills feedback state
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(null);
  // Preference questionnaire state
  const [showPreferenceQuestionnaire, setShowPreferenceQuestionnaire] = useState(false);
  const [showRepersonalizeModal, setShowRepersonalizeModal] = useState(false);
  const [preferencesHandled, setPreferencesHandled] = useState(false);
    //Password validation function
    const validatePassword = (password) => {
      if (password.length < 8) {
        return 'Password must be at least 8 characters';
      }
      if (!/[A-Z]/.test(password)) {
        return 'Password must contain an uppercase letter';
      }
      if (!/[a-z]/.test(password)) {
        return 'Password must contain a lowercase letter';
      }
      if (!/[0-9]/.test(password)) {
        return 'Password must contain a number';
      }
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return 'Password must contain a special character';
      }
      return '';
    };
  
    useEffect(() => {
      if (token) {
        // Only fetch dashboard data for dashboard-related pages
        const dashboardPages = ['dashboard', 'analyze', 'result', 'admin'];
        if (dashboardPages.includes(view)) {
          fetchAnalyses();
          fetchDashboardStats();
          fetchUserProfile();
        } else {
          // For market pages, just fetch user profile to check admin status
          fetchUserProfile();
        }
      }
    }, [token, view]);

  // Show preference questionnaire on first market page visit
  useEffect(() => {
    const marketPages = ['market-dashboard', 'skill-gap', 'job-stats', 'skill-relationships', 'market-insights'];
    if (token && userProfile && marketPages.includes(view) && !preferencesHandled) {
      if (!userProfile.preferences_completed) {
        setShowPreferenceQuestionnaire(true);
      }
    }
  }, [token, userProfile, view, preferencesHandled]);

  const handlePreferenceComplete = () => {
    setShowPreferenceQuestionnaire(false);
    setPreferencesHandled(true); // Prevent showing again this session
    fetchUserProfile(); // Refresh profile to get updated preferences
  };

  const handlePreferenceSkip = () => {
    setShowPreferenceQuestionnaire(false);
    setPreferencesHandled(true); // Prevent showing again this session
    fetchUserProfile(); // Refresh profile to mark as skipped
  };

  const handleOpenRepersonalize = () => {
    setShowRepersonalizeModal(true);
    setShowPreferenceQuestionnaire(true);
  };

  const handleRepersonalizeComplete = () => {
    setShowPreferenceQuestionnaire(false);
    setShowRepersonalizeModal(false);
    fetchUserProfile();
  };

  const handleRepersonalizeSkip = () => {
    setShowPreferenceQuestionnaire(false);
    setShowRepersonalizeModal(false);
  };

  const handleAuth = async (isLogin) => {
    setLoading(true);
    setError('');
    try {
      const endpoint = isLogin ? 'login' : 'register';
      const response = await fetch(`${API_URL}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      
      if (!response.ok) {
        // Handle unverified email error
        if (response.status === 403 && !data.email_verified) {
          setError(data.error + '. Check your email for the verification link.');
          return;
        }
        throw new Error(data.error);
      }
      
      // Handle registration success
      if (!isLogin && data.verification_required) {
        setError('');
        alert('Registration successful! Please check your email to verify your account before logging in.');
        setView('login');
        setFormData({ email: '', password: '' });
        return;
      }
      
      // Handle login success
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      setView('dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    setView('login');
    setAnalyses([]);
    setCurrentAnalysis(null);
    setIsAdmin(false);
    setUserProfile(null);
  };

  const handleGoogleLogin = () => {
    // Redirect to backend Google OAuth endpoint
    window.location.href = `${API_URL}/auth/google`;
  };

  // Handle OAuth callback AND email verification - ONLY ONE useEffect
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);

    // Get all possible params
    const tokenParam = urlParams.get('token');
    const userId = urlParams.get('user');
    const verify = urlParams.get('verify');
    const errorMessage = urlParams.get('message');
    const payment = urlParams.get('payment');
    
    // --- Logic Priority ---

    // 1. Check for email verification first
    if (verify === 'true' && userId && tokenParam) {
      console.log('Verifying email...');
      setLoading(true);
      
      fetch(`${API_URL}/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userId, 
          token: tokenParam // The token from the URL is the verification token
        })
      })
      .then(res => res.json())
      .then(data => {
        setLoading(false);
        if (data.access_token) {
          setToken(data.access_token);
          localStorage.setItem('token', data.access_token);
          setError('');
          alert('Email verified successfully! Welcome to ResuMatch AI!');
          setView('dashboard');
        } else {
          setError(data.error || 'Verification failed');
          alert('Error: ' + (data.error || 'Verification failed. Please try again or contact support.'));
          setView('login');
        }
        // Clean the URL
        window.history.replaceState({}, document.title, '/');
      })
      .catch(err => {
        setLoading(false);
        console.error('Verification error:', err);
        setError('Verification failed. Please try again or contact support.');
        alert('Verification failed. Please try again or contact support.');
        setView('login');
        window.history.replaceState({}, document.title, '/');
      });
    }
    // 2. Check for Google OAuth success
    else if (tokenParam && userId) {
      console.log('OAuth success - setting token and redirecting to dashboard');
      setToken(tokenParam);
      localStorage.setItem('token', tokenParam); // This token is the access_token from Google
      setView('dashboard');
      // Clean the URL
      window.history.replaceState({}, document.title, '/');
    }
    // 2b. Check for LinkedIn OAuth success (has token and provider, no userId)
    else if (tokenParam && urlParams.get('provider') === 'linkedin') {
      console.log('LinkedIn OAuth success - setting token and redirecting to dashboard');
      setToken(tokenParam);
      localStorage.setItem('token', tokenParam);
      setView('dashboard');
      // Clean the URL
      window.history.replaceState({}, document.title, '/');
    } 
    // 3. Check for payment success/cancel
    else if (payment) {
      console.log('Payment result:', payment);
      if (payment === 'success') {
        alert('Payment successful! Welcome to Pro! Your credits have been added.');
        // Refresh user profile to get updated subscription and credits
        if (token) {
          fetchUserProfile();
        }
      } else if (payment === 'cancel') {
        alert('Payment cancelled. You can upgrade anytime from your dashboard.');
      }
      setView('dashboard');
      // Clean the URL
      window.history.replaceState({}, document.title, '/');
    }
    // 4. Check for any error message
    else if (errorMessage) {
      console.log('OAuth or other error:', errorMessage);
      setError(decodeURIComponent(errorMessage));
      setView('login');
      // Clean the URL
      window.history.replaceState({}, document.title, '/');
    }
    // 4b. Check for error param (from LinkedIn OAuth)
    else if (urlParams.get('error')) {
      const errorParam = urlParams.get('error');
      console.log('OAuth error:', errorParam);
      if (errorParam === 'linkedin_auth_failed') {
        setError('LinkedIn authentication failed. Please try again or use email login.');
      } else if (errorParam === 'invalid_state') {
        setError('Security validation failed. Please try again.');
      } else {
        setError(decodeURIComponent(errorParam));
      }
      setView('login');
      // Clean the URL
      window.history.replaceState({}, document.title, '/');
    }
  }, []); // Empty dependency array ensures this runs only once on mount


  const fetchAnalyses = async () => {
    try {
      const response = await fetch(`${API_URL}/analyses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setAnalyses(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch analyses:', err);
      setAnalyses([]);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${API_URL}/dashboard/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setDashboardStats({
        total_analyses: data.total_analyses || 0,
        average_score: data.average_score || 0,
        score_trend: data.score_trend || [],
        top_missing_skills: data.top_missing_skills || []
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
      setDashboardStats({
        total_analyses: 0,
        average_score: 0,
        score_trend: [],
        top_missing_skills: []
      });
    }
  };

  const fetchUserProfile = async () => {
    try {
      // Use direct URL path since user profile is at /api/user/profile not /api/v1/user/profile
      const baseURL = API_URL.replace('/v1', '');
      const response = await fetch(`${baseURL}/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUserProfile(data);
      // Check if user is admin
      if (data.is_admin) {
        setIsAdmin(true);
      }
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
    }
  };

  const handleUpgrade = async (tier = 'pro') => {
    try {
      const response = await fetch(`${API_URL}/payments/create-checkout-session?tier=${tier}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.error);

      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpgradeToPro = () => handleUpgrade('pro');
  const handleUpgradeToElite = () => handleUpgrade('elite');

  // Analysis loading messages
  const analysisLoadingMessages = [
    'Uploading your resume...',
    'Parsing document content...',
    'Analyzing job requirements...',
    'Matching skills and keywords...',
    'Calculating compatibility score...',
    'Generating detailed insights...',
    'Finalizing your analysis...'
  ];

  // Simulate analysis progress
  const simulateAnalysisProgress = () => {
    setAnalysisProgress(0);
    setAnalysisMessage(analysisLoadingMessages[0]);

    let progress = 0;
    let messageIndex = 0;

    const interval = setInterval(() => {
      const increment = progress < 40 ? 12 : progress < 70 ? 6 : 2;
      progress = Math.min(progress + increment, 92);
      setAnalysisProgress(progress);

      const newIndex = Math.min(Math.floor(progress / 14), analysisLoadingMessages.length - 1);
      if (newIndex !== messageIndex) {
        messageIndex = newIndex;
        setAnalysisMessage(analysisLoadingMessages[messageIndex]);
      }
    }, 600);

    return () => clearInterval(interval);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!resumeFile || !jobDescription) {
      setError('Please provide both resume and job description');
      return;
    }

    setLoading(true);
    setError('');
    const stopProgress = simulateAnalysisProgress();

    const formDataObj = new FormData();
    formDataObj.append('resume', resumeFile);
    formDataObj.append('job_description', jobDescription);
    formDataObj.append('job_title', jobTitle);
    formDataObj.append('company_name', companyName);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formDataObj
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.error);

      setAnalysisProgress(100);
      setAnalysisMessage('Analysis complete!');

      setCurrentAnalysis(data);
      await fetchAnalyses();
      await fetchDashboardStats();
      setView('result');
      // Fetch extracted skills for the new analysis
      fetchExtractedSkills(data.analysis_id || data.id);

      setResumeFile(null);
      setJobDescription('');
      setJobTitle('');
      setCompanyName('');
    } catch (err) {
      setError(err.message);
    } finally {
      stopProgress();
      setTimeout(() => {
        setLoading(false);
        setAnalysisProgress(0);
        setAnalysisMessage('');
      }, 500);
    }
  };

  const viewAnalysis = async (id) => {
    try {
      const response = await fetch(`${API_URL}/analyses/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setCurrentAnalysis(data);
      setAiFeedback(null);
      setOptimizedResume(null);
      setCoverLetter(null);
      setExtractedSkills([]);
      setView('result');
      // Fetch extracted skills for feedback
      fetchExtractedSkills(id);
    } catch (err) {
      setError('Failed to load analysis');
    }
  };

  // AI loading messages for better UX
  const aiLoadingMessages = [
    'Analyzing your resume...',
    'Processing content...',
    'Generating insights...',
    'Crafting recommendations...',
    'Almost there...',
    'Finalizing...'
  ];

  // Simulate progress with dynamic messages
  const simulateAIProgress = (setLoading) => {
    setAiProgress(0);
    setAiLoadingMessage(aiLoadingMessages[0]);

    let progress = 0;
    let messageIndex = 0;

    const interval = setInterval(() => {
      // Increment progress (slow down as we get closer to 90%)
      const increment = progress < 50 ? 15 : progress < 80 ? 8 : 3;
      progress = Math.min(progress + increment, 90);
      setAiProgress(progress);

      // Update message based on progress
      const newIndex = Math.min(Math.floor(progress / 18), aiLoadingMessages.length - 1);
      if (newIndex !== messageIndex) {
        messageIndex = newIndex;
        setAiLoadingMessage(aiLoadingMessages[messageIndex]);
      }
    }, 800);

    return () => clearInterval(interval);
  };

  const generateAIFeedback = async () => {
    if (!currentAnalysis) return;

    setGeneratingFeedback(true);
    const stopProgress = simulateAIProgress(setGeneratingFeedback);

    try {
      const response = await fetch(`${API_URL}/analyze/feedback/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 402) {
          setShowUpgradeModal(true);
          return;
        }
        throw new Error(data.error);
      }

      setAiProgress(100);
      setAiLoadingMessage('Complete!');
      setAiFeedback(data.feedback);
      fetchUserProfile();
    } catch (err) {
      setError(err.message);
    } finally {
      stopProgress();
      setTimeout(() => {
        setGeneratingFeedback(false);
        setAiProgress(0);
        setAiLoadingMessage('');
      }, 500);
    }
  };

  const generateOptimizedResume = async () => {
    if (!currentAnalysis) return;

    setGeneratingOptimized(true);
    const stopProgress = simulateAIProgress(setGeneratingOptimized);

    try {
      const response = await fetch(`${API_URL}/analyze/optimize/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 402) {
          setShowUpgradeModal(true);
          return;
        }
        throw new Error(data.error);
      }

      setAiProgress(100);
      setAiLoadingMessage('Complete!');
      setOptimizedResume(data.optimized_resume);
      fetchUserProfile();
    } catch (err) {
      setError(err.message);
    } finally {
      stopProgress();
      setTimeout(() => {
        setGeneratingOptimized(false);
        setAiProgress(0);
        setAiLoadingMessage('');
      }, 500);
    }
  };

  const generateCoverLetter = async () => {
    if (!currentAnalysis) return;

    setGeneratingCoverLetter(true);
    const stopProgress = simulateAIProgress(setGeneratingCoverLetter);

    try {
      const response = await fetch(`${API_URL}/analyze/cover-letter/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 402) {
          setShowUpgradeModal(true);
          return;
        }
        throw new Error(data.error);
      }

      setAiProgress(100);
      setAiLoadingMessage('Complete!');
      setCoverLetter(data.cover_letter);
      fetchUserProfile();
    } catch (err) {
      setError(err.message);
    } finally {
      stopProgress();
      setTimeout(() => {
        setGeneratingCoverLetter(false);
        setAiProgress(0);
        setAiLoadingMessage('');
      }, 500);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  // Fetch extracted skills for an analysis
  const fetchExtractedSkills = async (analysisId) => {
    if (!analysisId) {
      console.log('No analysis ID provided for skill extraction');
      return;
    }
    setLoadingSkills(true);
    try {
      console.log(`Fetching extracted skills for analysis ${analysisId}`);
      const response = await fetch(`${API_URL}/skills/extract/${analysisId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      console.log('Extracted skills response:', data);
      if (response.ok) {
        // Backend returns 'skills' not 'extractions'
        const skills = data.skills || [];
        console.log(`Loaded ${skills.length} extracted skills`);
        setExtractedSkills(skills);
      } else {
        console.error('Failed to fetch extracted skills:', data.error);
        setExtractedSkills([]);
      }
    } catch (err) {
      console.error('Error fetching extracted skills:', err);
      setExtractedSkills([]);
    } finally {
      setLoadingSkills(false);
    }
  };

  // Submit skill feedback (confirm or reject)
  const submitSkillFeedback = async (extractionId, confirmed) => {
    setFeedbackSubmitting(extractionId);
    try {
      const response = await fetch(`${API_URL}/skills/extract/${extractionId}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          confirmed: confirmed,
          rejected: !confirmed
        })
      });
      const data = await response.json();
      if (response.ok) {
        // Update the skill in the list
        setExtractedSkills(prev => prev.map(skill =>
          skill.id === extractionId
            ? { ...skill, user_confirmed: confirmed, user_rejected: !confirmed }
            : skill
        ));
      } else {
        console.error('Failed to submit feedback:', data.error);
      }
    } catch (err) {
      console.error('Error submitting skill feedback:', err);
    } finally {
      setFeedbackSubmitting(null);
    }
  };

  const resendAnalysisEmail = async (analysisId) => {
    try {
      const response = await fetch(`${API_URL}/analyses/${analysisId}/resend-email`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.error);
      
      alert('Email sent successfully!');
    } catch (err) {
      setError(err.message);
    }
  };

  // Upgrade Modal Component
  const UpgradeModal = () => {
    if (!showUpgradeModal) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-slate-800 rounded-2xl p-8 max-w-md w-full border border-slate-700">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">Upgrade to Pro</h3>
            <p className="text-slate-300 mb-6">
              This feature requires Pro credits. Get unlimited access to all AI-powered tools with our Pro plan.
            </p>
            <div className="space-y-4">
              <button
                onClick={handleUpgradeToPro}
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25"
              >
                Upgrade to Pro - $19.99/month
              </button>
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-semibold transition"
              >
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (view === 'pricing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Navigation */}
        <Navigation 
          view={view}
          setView={setView}
          token={token}
          handleLogout={handleLogout}
          showBackButton={true}
          backButtonText="Back to Dashboard"
          onBackClick={() => setView('dashboard')}
        />

        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">Choose Your Plan</h1>
            <p className="text-slate-300 text-lg">Unlock the full potential of AI-powered resume optimization</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Free Plan */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Free</h3>
                <div className="text-4xl font-bold text-slate-300 mb-2">$0</div>
                <p className="text-slate-400">5 credits on signup</p>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  5 free credits
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Resume analysis
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Keyword matching
                </li>
                <li className="flex items-center text-slate-400">
                  <svg className="w-5 h-5 text-slate-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Limited AI features
                </li>
              </ul>
              <button
                onClick={() => setView('dashboard')}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-semibold transition"
              >
                Current Plan
              </button>
            </div>

            {/* Pro Plan */}
            <div className="bg-gradient-to-br from-cyan-500/10 to-purple-600/10 backdrop-blur-sm border-2 border-cyan-500/50 rounded-2xl p-8 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Pro</h3>
                <div className="text-4xl font-bold text-cyan-400 mb-2">$9.99</div>
                <p className="text-slate-400">per month • 100 credits</p>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  100 credits/month
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Unlimited analyses
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  AI feedback
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Resume optimization
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Cover letter generation
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Priority support
                </li>
              </ul>
              <button
                onClick={handleUpgradeToPro}
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25"
              >
                Upgrade to Pro
              </button>
            </div>

            {/* Elite Plan */}
            <div className="bg-gradient-to-br from-amber-500/10 to-orange-600/10 backdrop-blur-sm border-2 border-amber-500/50 rounded-2xl p-8 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-amber-500 to-orange-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                  Premium
                </span>
              </div>
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Elite</h3>
                <div className="text-4xl font-bold text-amber-400 mb-2">$49.99</div>
                <p className="text-slate-400">per month • 1000 credits</p>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  1000 credits/month
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Everything in Pro
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Unlimited API access
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Custom integrations
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Advanced analytics
                </li>
                <li className="flex items-center text-slate-300">
                  <svg className="w-5 h-5 text-green-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Dedicated support
                </li>
              </ul>
              <button
                onClick={handleUpgradeToElite}
                className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-amber-500/25"
              >
                Upgrade to Elite
              </button>
            </div>
          </div>

          <div className="text-center mt-12">
            <p className="text-slate-400 text-sm">
              All plans include secure payment processing via Stripe. Cancel anytime.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (view === 'landing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Navigation */}
        <Navigation 
          view={view}
          setView={setView}
          token={token}
          handleLogout={handleLogout}
        />

        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="text-center mb-16">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold text-white mb-4 sm:mb-6 leading-tight px-4">
              Elevate Your Resume with
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent block mt-1 sm:mt-2">
                AI-Powered Insights
              </span>
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-slate-300 mb-8 sm:mb-12 max-w-3xl mx-auto leading-relaxed px-4">
              Get instant feedback, keyword optimization, and tailored suggestions to land your dream job with cutting-edge AI technology.
            </p>
            
            {/* Drag & Drop Upload Area */}
            <div className="max-w-2xl mx-auto mb-8 sm:mb-12 px-4">
              <div 
                className="border-2 border-dashed border-slate-600 bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 sm:p-8 md:p-12 hover:border-cyan-400 hover:bg-slate-800/70 transition-all duration-300 group cursor-pointer"
                onClick={() => document.getElementById('landing-file-input').click()}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.currentTarget.classList.add('border-cyan-400', 'bg-slate-800/70');
                }}
                onDragLeave={(e) => {
                  e.currentTarget.classList.remove('border-cyan-400', 'bg-slate-800/70');
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.currentTarget.classList.remove('border-cyan-400', 'bg-slate-800/70');
                  const files = e.dataTransfer.files;
                  if (files.length > 0) {
                    setLandingResumeFile(files[0]);
                  }
                }}
              >
                <input
                  id="landing-file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => setLandingResumeFile(e.target.files[0])}
                  className="hidden"
                />
                <div className="flex flex-col items-center gap-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div className="text-center">
                    {landingResumeFile ? (
                      <>
                        <h3 className="text-xl font-semibold text-green-400 mb-2 flex items-center gap-2">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          File Selected
                        </h3>
                        <p className="text-slate-300">{landingResumeFile.name}</p>
                        <p className="text-sm text-slate-500 mt-2">Click "Start Analyzing" to continue</p>
                      </>
                    ) : (
                      <>
                        <h3 className="text-xl font-semibold text-white mb-2">Drag & Drop Your Resume Here</h3>
                        <p className="text-slate-400">or click to browse files</p>
                        <p className="text-sm text-slate-500 mt-2">Supports PDF, DOCX, TXT files</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => {
                if (landingResumeFile) {
                  // Store the file for later use and redirect to register
                  setResumeFile(landingResumeFile);
                  setView('register');
                } else {
                  setView('register');
                }
              }}
              className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl text-base sm:text-lg font-semibold hover:shadow-2xl hover:shadow-cyan-500/25 transition-all duration-300 transform hover:scale-105 mx-4"
            >
              {landingResumeFile ? 'Continue to Sign Up' : 'Start Analyzing - It\'s Free'}
            </button>
          </div>

          {/* Key Features Section */}
          <div className="mb-16 sm:mb-24 md:mb-32">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-center text-white mb-8 sm:mb-12 md:mb-16 px-4">How It Works</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 hover:border-cyan-400 hover:bg-slate-800/70 transition-all duration-300 group">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">AI Analysis</h3>
                <p className="text-slate-300 leading-relaxed">
                  Advanced artificial intelligence scans your resume and identifies strengths, weaknesses, and optimization opportunities with precision.
                </p>
              </div>

              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 hover:border-cyan-400 hover:bg-slate-800/70 transition-all duration-300 group">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Smart Formatting</h3>
                <p className="text-slate-300 leading-relaxed">
                  Get intelligent formatting suggestions and structure optimization to ensure your resume passes ATS systems and impresses recruiters.
                </p>
              </div>

              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 hover:border-cyan-400 hover:bg-slate-800/70 transition-all duration-300 group">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Keyword Optimization</h3>
                <p className="text-slate-300 leading-relaxed">
                  Target the right keywords and phrases that recruiters and ATS systems are looking for to maximize your application success rate.
                </p>
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <footer className="bg-slate-900 border-t border-slate-700 py-8">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center gap-3 mb-4 md:mb-0">
                <img 
                  src="/logo192.png" 
                  alt="ResumeAnalyzer AI Logo" 
                  className="w-6 h-6 object-contain"
                />
                <h3 className="text-lg font-bold text-white">ResumeAnalyzer AI</h3>
              </div>
              <p className="text-slate-500 text-sm">
                &copy; 2025 ResumeAnalyzer AI. ITAI 2277 - AI Project by Alhassane Samassekou
              </p>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  if (view === 'login' || view === 'register') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Navigation */}
        <Navigation 
          view={view}
          setView={setView}
          token={token}
          handleLogout={handleLogout}
          showBackButton={true}
          backButtonText="Back to Home"
          onBackClick={() => setView('landing')}
        />

        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[calc(100vh-200px)]">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl shadow-2xl p-8 max-w-md w-full">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">
                  {view === 'login' ? 'Welcome Back' : 'Create Account'}
                </h1>
                <p className="text-slate-400">
                  {view === 'login' ? 'Sign in to continue' : 'Join us to get started'}
                </p>
              </div>
              
              {error && (
                <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
                  {error}
                </div>
              )}

              {error && error.includes('verify your email') && (
                <div className="bg-blue-900/50 border border-blue-500 text-blue-300 px-4 py-3 rounded-lg mb-6 text-center">
                  <p className="mb-2">Didn't receive the verification email?</p>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(`${API_URL}/auth/resend-verification`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ email: formData.email })
                        });
                        const data = await response.json();
                        alert(data.message || 'Verification email sent!');
                      } catch (err) {
                        alert('Failed to resend email. Please try again.');
                      }
                    }}
                    className="text-cyan-400 hover:text-cyan-300 font-medium underline"
                  >
                    Resend Verification Email
                  </button>
                </div>
              )}

              <div className="space-y-6">
                {/* Google Sign-in Button */}
                <button
                  onClick={handleGoogleLogin}
                  className="w-full bg-white hover:bg-gray-50 text-gray-900 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-lg border border-gray-300 flex items-center justify-center gap-3"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>

                {/* LinkedIn Sign-in Button */}
                <button
                  onClick={() => window.location.href = `${API_URL}/auth/linkedin/login`}
                  className="w-full bg-[#0077B5] hover:bg-[#006097] text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-lg flex items-center justify-center gap-3"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                  </svg>
                  Continue with LinkedIn
                </button>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-600"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-slate-800 text-slate-400">Or continue with email</span>
                  </div>
                </div>

                <div>
                  <input
                    type="email"
                    placeholder="Email address"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
                
                <div>
                  <input
                    type="password"
                    placeholder="Password"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({...formData, password: e.target.value});
                      if (view === 'register') {
                        const error = validatePassword(e.target.value);
                        setPasswordError(error);
                        setShowPasswordRequirements(true);
                      }
                    }}
                    onFocus={() => view === 'register' && setShowPasswordRequirements(true)}
                  />
                  
                  {/* Password Requirements - Only show on register */}
                  {view === 'register' && showPasswordRequirements && (
                    <div className="mt-3 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                      <p className="text-sm font-medium text-slate-300 mb-2">Password must contain:</p>
                      <ul className="space-y-1 text-sm">
                        <li className={`flex items-center gap-2 ${formData.password.length >= 8 ? 'text-green-400' : 'text-slate-400'}`}>
                          <span className={formData.password.length >= 8 ? 'text-green-400' : 'text-slate-500'}>{formData.password.length >= 8 ? '●' : '○'}</span>
                          At least 8 characters
                        </li>
                        <li className={`flex items-center gap-2 ${/[A-Z]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                          <span className={/[A-Z]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[A-Z]/.test(formData.password) ? '●' : '○'}</span>
                          One uppercase letter
                        </li>
                        <li className={`flex items-center gap-2 ${/[a-z]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                          <span className={/[a-z]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[a-z]/.test(formData.password) ? '●' : '○'}</span>
                          One lowercase letter
                        </li>
                        <li className={`flex items-center gap-2 ${/[0-9]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                          <span className={/[0-9]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[0-9]/.test(formData.password) ? '●' : '○'}</span>
                          One number
                        </li>
                        <li className={`flex items-center gap-2 ${/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? 'text-green-400' : 'text-slate-400'}`}>
                          <span className={/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'}>{/[!@#$%^&*(),.?":{}|<>]/.test(formData.password) ? '●' : '○'}</span>
                          One special character (!@#$%^&*)
                        </li>
                      </ul>
                      {passwordError && (
                        <p className="text-red-400 text-sm mt-3 font-medium">{passwordError}</p>
                      )}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => {
                    // Validate password on register
                    if (view === 'register') {
                      const error = validatePassword(formData.password);
                      if (error) {
                        setError(error);
                        return;
                      }
                    }
                    handleAuth(view === 'login');
                  }}
                  disabled={loading || (view === 'register' && passwordError)}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : (view === 'login' ? 'Sign In with Email' : 'Create Account')}
                </button>
              </div>
              
              <div className="text-center mt-6">
                <p className="text-slate-400">
                  {view === 'login' ? "Don't have an account? " : "Already have an account? "}
                  <button
                    onClick={() => setView(view === 'login' ? 'register' : 'login')}
                    className="text-cyan-400 hover:text-cyan-300 transition font-medium"
                  >
                    {view === 'login' ? 'Sign Up' : 'Sign In'}
                  </button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading && view !== 'analyze' && view !== 'dashboard') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mb-4"></div>
          <p className="text-white text-xl">Verifying your email...</p>
        </div>
      </div>
    );
  }

  // Admin Dashboard View
  if (view === 'admin' && isAdmin && token) {
    return (
      <AdminDashboard
        token={token}
        onLogout={handleLogout}
        onNavigate={setView}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <Navigation 
        view={view}
        setView={setView}
        token={token}
        handleLogout={handleLogout}
        showBackButton={view === 'result'}
        backButtonText="Back to Dashboard"
        onBackClick={() => setView('dashboard')}
      />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {view === 'dashboard' && (
          <div className="space-y-6">
            <Breadcrumb view={view} setView={setView} token={token} />
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-white">Your Career Dashboard</h2>
              {userProfile && (
                <div className="flex items-center gap-4">
                  {isAdmin && (
                    <button
                      onClick={() => setView('admin')}
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
                      onClick={() => setView('pricing')}
                      className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-cyan-500/25"
                    >
                      Upgrade Now
                    </button>
                  )}
                  {userProfile.subscription_tier === 'pro' && (
                    <button
                      onClick={() => setView('pricing')}
                      className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-amber-500/25"
                    >
                      Upgrade to Elite
                    </button>
                  )}
                </div>
              )}
            </div>
            
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
                    <p className="text-sm">Create your first analysis to get started!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {view === 'analyze' && (
          <div className="max-w-3xl mx-auto">
            <Breadcrumb view={view} setView={setView} token={token} />
            <h2 className="text-3xl font-bold text-white mb-6">Analyze Your Resume</h2>
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <form onSubmit={handleAnalyze} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Upload Resume (PDF, DOCX, or TXT)
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => setResumeFile(e.target.files[0])}
                    className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-700 file:text-slate-300 hover:file:bg-slate-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Job Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g., Senior Software Engineer"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Company Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g., Tech Corp"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Job Description
                  </label>
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description here..."
                    rows="10"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition resize-none"
                  />
                </div>

                {/* Analysis Progress Indicator */}
                {loading && (
                  <div className="p-4 bg-slate-700/50 rounded-xl border border-slate-600">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-cyan-400 font-medium flex items-center gap-2">
                        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {analysisMessage || 'Processing...'}
                      </span>
                      <span className="text-slate-400 text-sm">{analysisProgress}%</span>
                    </div>
                    <div className="w-full bg-slate-600 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${analysisProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing Resume...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                      </svg>
                      Analyze Resume
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        )}

        {view === 'result' && currentAnalysis && (
          <div className="max-w-4xl mx-auto space-y-6">
            <Breadcrumb view={view} setView={setView} token={token} currentAnalysis={currentAnalysis} />
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-white">Analysis Results</h2>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => resendAnalysisEmail(currentAnalysis.analysis_id || currentAnalysis.id)}
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-400 hover:to-green-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg hover:shadow-green-500/25 flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Resend Email
                </button>
                <div className="text-slate-400 text-sm">
                  {currentAnalysis.job_title && `${currentAnalysis.job_title} • `}
                  {currentAnalysis.company_name || 'Analysis'}
                </div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 text-center">
              <h3 className="text-lg font-medium text-slate-400 mb-2">Match Score</h3>
              <div className={`text-6xl font-bold mb-2 ${
                currentAnalysis.match_score >= 70 ? 'text-green-400' :
                currentAnalysis.match_score >= 50 ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {currentAnalysis.match_score}%
              </div>
              <p className="text-slate-300">
                {currentAnalysis.match_score >= 70 ? 'Excellent match!' :
                 currentAnalysis.match_score >= 50 ? 'Good match with room for improvement' :
                 'Consider tailoring your resume more'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-4 text-green-400">Keywords Found</h3>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.keywords_found && currentAnalysis.keywords_found.map((kw, idx) => (
                    <span key={idx} className="px-3 py-1 bg-green-900/50 text-green-300 border border-green-500/30 rounded-full text-sm">
                      {kw}
                    </span>
                  ))}
                  {(!currentAnalysis.keywords_found || currentAnalysis.keywords_found.length === 0) && (
                    <p className="text-slate-400">No matching keywords found</p>
                  )}
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-4 text-orange-400">Keywords Missing</h3>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.keywords_missing && currentAnalysis.keywords_missing.map((kw, idx) => (
                    <span key={idx} className="px-3 py-1 bg-orange-900/50 text-orange-300 border border-orange-500/30 rounded-full text-sm">
                      {kw}
                    </span>
                  ))}
                  {(!currentAnalysis.keywords_missing || currentAnalysis.keywords_missing.length === 0) && (
                    <p className="text-slate-400">Great! All keywords covered</p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-white">Suggestions for Improvement</h3>
              <p className="text-slate-300 leading-relaxed">{currentAnalysis.suggestions}</p>
            </div>

            {/* Skill Feedback Section - Self-Learning */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    Help Us Learn - Skill Verification
                  </h3>
                  <p className="text-slate-400 text-sm mt-1">
                    Confirm or reject extracted skills to improve our AI accuracy
                  </p>
                </div>
                {extractedSkills.length > 0 && (
                  <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full">
                    {extractedSkills.filter(s => s.user_confirmed || s.user_rejected).length}/{extractedSkills.length} reviewed
                  </span>
                )}
              </div>

              {loadingSkills ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
                  <span className="ml-3 text-slate-400">Loading extracted skills...</span>
                </div>
              ) : extractedSkills.length > 0 ? (
                <div className="space-y-3">
                  {extractedSkills.map((skill) => (
                    <div
                      key={skill.id}
                      className={`flex items-center justify-between p-3 rounded-lg border transition ${
                        skill.user_confirmed
                          ? 'bg-green-900/20 border-green-500/30'
                          : skill.user_rejected
                          ? 'bg-red-900/20 border-red-500/30'
                          : 'bg-slate-700/30 border-slate-600 hover:border-slate-500'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex flex-col">
                          <span className="text-white font-medium">{skill.name || skill.extracted_text}</span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-slate-400">
                              Confidence: {Math.round((skill.confidence || 0) * 100)}%
                            </span>
                            {(skill.method || skill.extraction_method) && (
                              <span className="text-xs bg-slate-600 text-slate-300 px-2 py-0.5 rounded">
                                {skill.method || skill.extraction_method}
                              </span>
                            )}
                            {skill.matched_keyword && (
                              <span className="text-xs text-cyan-400">
                                Matched: {skill.matched_keyword.name || skill.matched_keyword}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {skill.user_confirmed ? (
                          <span className="flex items-center gap-1 text-green-400 text-sm">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Confirmed
                          </span>
                        ) : skill.user_rejected ? (
                          <span className="flex items-center gap-1 text-red-400 text-sm">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            Rejected
                          </span>
                        ) : (
                          <>
                            <button
                              onClick={() => submitSkillFeedback(skill.id, true)}
                              disabled={feedbackSubmitting === skill.id}
                              className="p-2 rounded-lg bg-green-600/20 hover:bg-green-600/40 text-green-400 transition disabled:opacity-50"
                              title="Confirm - This skill is correct"
                            >
                              {feedbackSubmitting === skill.id ? (
                                <div className="w-5 h-5 animate-spin rounded-full border-2 border-green-400 border-t-transparent"></div>
                              ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </button>
                            <button
                              onClick={() => submitSkillFeedback(skill.id, false)}
                              disabled={feedbackSubmitting === skill.id}
                              className="p-2 rounded-lg bg-red-600/20 hover:bg-red-600/40 text-red-400 transition disabled:opacity-50"
                              title="Reject - This skill is incorrect"
                            >
                              {feedbackSubmitting === skill.id ? (
                                <div className="w-5 h-5 animate-spin rounded-full border-2 border-red-400 border-t-transparent"></div>
                              ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              )}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  <svg className="w-12 h-12 mx-auto mb-3 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <p>No extracted skills available for feedback</p>
                  <p className="text-sm mt-1">Skills will appear here after analysis</p>
                </div>
              )}
            </div>

            {/* AI-Powered Features */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-white">
                AI-Powered Enhancement Tools
              </h3>
              <p className="text-slate-400 mb-6">Get personalized AI assistance to improve your resume and application</p>

              {/* Progress indicator - shows when any AI action is in progress */}
              {(generatingFeedback || generatingOptimized || generatingCoverLetter) && (
                <div className="mb-6 p-4 bg-slate-700/50 rounded-xl border border-slate-600">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-cyan-400 font-medium flex items-center gap-2">
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {aiLoadingMessage || 'Processing...'}
                    </span>
                    <span className="text-slate-400 text-sm">{aiProgress}%</span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${aiProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={generateAIFeedback}
                  disabled={generatingFeedback || generatingOptimized || generatingCoverLetter}
                  className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white px-6 py-3 rounded-lg transition shadow-lg hover:shadow-purple-500/25 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center gap-2"
                >
                  {generatingFeedback ? (
                    <>
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                      </svg>
                      Generating Feedback...
                    </>
                  ) : 'Get AI Feedback'}
                </button>
                <button
                  onClick={generateOptimizedResume}
                  disabled={generatingFeedback || generatingOptimized || generatingCoverLetter}
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-lg transition shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center gap-2"
                >
                  {generatingOptimized ? (
                    <>
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                      </svg>
                      Optimizing Resume...
                    </>
                  ) : 'Optimize Resume'}
                </button>
                <button
                  onClick={generateCoverLetter}
                  disabled={generatingFeedback || generatingOptimized || generatingCoverLetter}
                  className="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white px-6 py-3 rounded-lg transition shadow-lg hover:shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center gap-2"
                >
                  {generatingCoverLetter ? (
                    <>
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                      </svg>
                      Writing Cover Letter...
                    </>
                  ) : 'Generate Cover Letter'}
                </button>
              </div>
            </div>

            {/* AI Feedback Display */}
            {aiFeedback && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-white">AI-Powered Personalized Feedback</h3>
                  <button
                    onClick={() => copyToClipboard(aiFeedback)}
                    className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition"
                  >
                    Copy to Clipboard
                  </button>
                </div>
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-slate-300 font-sans bg-slate-700/30 p-4 rounded-lg border border-slate-600">{aiFeedback}</pre>
                </div>
              </div>
            )}

            {/* Optimized Resume Display */}
            {optimizedResume && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-white">Your Optimized Resume</h3>
                  <button
                    onClick={() => copyToClipboard(optimizedResume)}
                    className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition"
                  >
                    Copy to Clipboard
                  </button>
                </div>
                <div className="bg-slate-700/30 p-6 rounded-lg border border-slate-600">
                  <pre className="whitespace-pre-wrap text-slate-300 font-sans text-sm">{optimizedResume}</pre>
                </div>
                <p className="text-sm text-slate-400 mt-4">
                  Tip: Copy this optimized version and paste it into your preferred document editor for final formatting.
                </p>
              </div>
            )}

            {/* Cover Letter Display */}
            {coverLetter && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-white">Tailored Cover Letter</h3>
                  <button
                    onClick={() => copyToClipboard(coverLetter)}
                    className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition"
                  >
                    Copy to Clipboard
                  </button>
                </div>
                <div className="bg-slate-700/30 p-6 rounded-lg border border-slate-600">
                  <pre className="whitespace-pre-wrap text-slate-300 font-sans">{coverLetter}</pre>
                </div>
              </div>
            )}
          </div>
        )}

        {view === 'market-dashboard' && (
          <div>
            <Breadcrumb view={view} setView={setView} token={token} />
            <MarketIntelligenceDashboard userProfile={userProfile} onRepersonalize={handleOpenRepersonalize} />
          </div>
        )}

        {view === 'skill-gap' && (
          <div>
            <Breadcrumb view={view} setView={setView} token={token} />
            <SkillGapAnalysis userProfile={userProfile} onRepersonalize={handleOpenRepersonalize} />
          </div>
        )}

        {view === 'job-stats' && (
          <div>
            <Breadcrumb view={view} setView={setView} token={token} />
            <JobMarketStats userProfile={userProfile} onRepersonalize={handleOpenRepersonalize} />
          </div>
        )}

        {view === 'skill-relationships' && (
          <div>
            <Breadcrumb view={view} setView={setView} token={token} />
            <SkillRelationships userProfile={userProfile} onRepersonalize={handleOpenRepersonalize} />
          </div>
        )}

        {view === 'market-insights' && (
          <div>
            <Breadcrumb view={view} setView={setView} token={token} />
            <JobSeekerInsights userProfile={userProfile} onRepersonalize={handleOpenRepersonalize} />
          </div>
        )}
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal />

      {/* Preference Questionnaire Modal */}
      {showPreferenceQuestionnaire && (
        <PreferenceQuestionnaire
          token={token}
          onComplete={showRepersonalizeModal ? handleRepersonalizeComplete : handlePreferenceComplete}
          onSkip={showRepersonalizeModal ? handleRepersonalizeSkip : handlePreferenceSkip}
          isUpdate={showRepersonalizeModal}
        />
      )}
    </div>
  );
}

export default App;