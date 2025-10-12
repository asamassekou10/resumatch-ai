import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const API_URL = 'https://resumatch-backend-7qdb.onrender.com/api';

function App() {
  const [view, setView] = useState('landing');
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [analyses, setAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [aiFeedback, setAiFeedback] = useState(null);
  const [optimizedResume, setOptimizedResume] = useState(null);
  const [coverLetter, setCoverLetter] = useState(null);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [landingResumeFile, setLandingResumeFile] = useState(null);

  useEffect(() => {
    if (token) {
      fetchAnalyses();
      fetchDashboardStats();
      setView('dashboard');
    }
  }, [token]);

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
      
      if (!response.ok) throw new Error(data.error);
      
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
  };

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

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!resumeFile || !jobDescription) {
      setError('Please provide both resume and job description');
      return;
    }

    setLoading(true);
    setError('');
    
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
      
      setCurrentAnalysis(data);
      await fetchAnalyses();
      await fetchDashboardStats();
      setView('result');
      
      setResumeFile(null);
      setJobDescription('');
      setJobTitle('');
      setCompanyName('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
      setView('result');
    } catch (err) {
      setError('Failed to load analysis');
    }
  };

  const generateAIFeedback = async () => {
    if (!currentAnalysis) return;
    
    setGeneratingAI(true);
    try {
      const response = await fetch(`${API_URL}/analyze/feedback/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.error);
      
      setAiFeedback(data.feedback);
    } catch (err) {
      setError(err.message);
    } finally {
      setGeneratingAI(false);
    }
  };

  const generateOptimizedResume = async () => {
    if (!currentAnalysis) return;
    
    setGeneratingAI(true);
    try {
      const response = await fetch(`${API_URL}/analyze/optimize/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.error);
      
      setOptimizedResume(data.optimized_resume);
    } catch (err) {
      setError(err.message);
    } finally {
      setGeneratingAI(false);
    }
  };

  const generateCoverLetter = async () => {
    if (!currentAnalysis) return;
    
    setGeneratingAI(true);
    try {
      const response = await fetch(`${API_URL}/analyze/cover-letter/${currentAnalysis.analysis_id || currentAnalysis.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.error);
      
      setCoverLetter(data.cover_letter);
    } catch (err) {
      setError(err.message);
    } finally {
      setGeneratingAI(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  if (view === 'landing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Navigation */}
        <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <img 
                src="/logo192.png" 
                alt="ResumeAnalyzer AI Logo" 
                className="w-8 h-8 sm:w-10 sm:h-10 object-contain"
              />
              <h1 className="text-xl sm:text-2xl font-bold text-white">
                ResumeAnalyzer AI
              </h1>
            </div>
            
            
            <div className="flex gap-3">
              <button
                onClick={() => setView('login')}
                className="border border-slate-600 text-slate-300 hover:border-cyan-400 hover:text-cyan-400 transition px-4 py-2 rounded-lg font-medium"
              >
                Log In
              </button>
              <button
                onClick={() => setView('register')}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-2 rounded-lg font-medium transition shadow-lg hover:shadow-cyan-500/25"
              >
                Sign Up
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Elevate Your Resume with
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent block mt-2">
                AI-Powered Insights
              </span>
            </h1>
            <p className="text-xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Get instant feedback, keyword optimization, and tailored suggestions to land your dream job with cutting-edge AI technology.
            </p>
            
            {/* Drag & Drop Upload Area */}
            <div className="max-w-2xl mx-auto mb-12">
              <div 
                className="border-2 border-dashed border-slate-600 bg-slate-800/50 backdrop-blur-sm rounded-2xl p-12 hover:border-cyan-400 hover:bg-slate-800/70 transition-all duration-300 group cursor-pointer"
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
                        <h3 className="text-xl font-semibold text-green-400 mb-2">✓ File Selected</h3>
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
              className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:shadow-cyan-500/25 transition-all duration-300 transform hover:scale-105"
            >
              {landingResumeFile ? 'Continue to Sign Up' : 'Start Analyzing - It\'s Free'}
            </button>
          </div>

          {/* Key Features Section */}
          <div className="mb-32">
            <h2 className="text-4xl font-bold text-center text-white mb-16">How It Works</h2>
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            AI Resume Optimizer
          </h1>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="mb-4">
            <input
              type="email"
              placeholder="Email"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>
          
          <div className="mb-6">
            <input
              type="password"
              placeholder="Password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          
          <button
            onClick={() => handleAuth(view === 'login')}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
          >
            {loading ? 'Processing...' : (view === 'login' ? 'Login' : 'Sign Up')}
          </button>
          
          <p className="text-center mt-4 text-gray-600">
            {view === 'login' ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setView(view === 'login' ? 'register' : 'login')}
              className="text-blue-600 hover:underline"
            >
              {view === 'login' ? 'Sign Up' : 'Login'}
            </button>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 sm:gap-3">
            <img 
              src="/logo192.png" 
              alt="ResumeAnalyzer AI Logo" 
              className="w-6 h-6 sm:w-8 sm:h-8 object-contain"
            />
            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-800">ResumeAnalyzer AI</h1>
          </div>
          <div className="flex gap-1 sm:gap-2 lg:gap-4">
            <button
              onClick={() => setView('dashboard')}
              className="text-gray-700 hover:text-blue-600 transition text-xs sm:text-sm lg:text-base px-1 sm:px-2"
            >
              <span className="hidden sm:inline">Dashboard</span>
              <span className="sm:hidden">Dash</span>
            </button>
            <button
              onClick={() => setView('analyze')}
              className="bg-blue-600 text-white px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2 rounded-lg hover:bg-blue-700 transition text-xs sm:text-sm lg:text-base"
            >
              <span className="hidden sm:inline">New Analysis</span>
              <span className="sm:hidden">New</span>
            </button>
            <button
              onClick={handleLogout}
              className="text-gray-700 hover:text-red-600 transition text-xs sm:text-sm lg:text-base px-1 sm:px-2"
            >
              <span className="hidden sm:inline">Logout</span>
              <span className="sm:hidden">Exit</span>
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {view === 'dashboard' && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-800">Your Career Dashboard</h2>
            
            {dashboardStats && dashboardStats.total_analyses > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-gray-600 text-sm font-medium">Total Analyses</h3>
                  <p className="text-4xl font-bold text-blue-600">{dashboardStats.total_analyses}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-gray-600 text-sm font-medium">Average Score</h3>
                  <p className="text-4xl font-bold text-green-600">{dashboardStats.average_score}%</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-gray-600 text-sm font-medium">Top Skill Gap</h3>
                  <p className="text-2xl font-bold text-orange-600">
                    {dashboardStats.top_missing_skills && dashboardStats.top_missing_skills[0] ? dashboardStats.top_missing_skills[0].skill : 'N/A'}
                  </p>
                </div>
              </div>
            )}

            {dashboardStats && dashboardStats.score_trend && dashboardStats.score_trend.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">Match Score Trend</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardStats.score_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="job_title" angle={-45} textAnchor="end" height={100} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {dashboardStats && dashboardStats.top_missing_skills && dashboardStats.top_missing_skills.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">Top Skills to Develop</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dashboardStats.top_missing_skills.slice(0, 8)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="skill" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#F59E0B" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-xl font-semibold">Analysis History</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Match Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analyses.map((analysis) => (
                      <tr key={analysis.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {analysis.job_title || 'Untitled'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {analysis.company_name || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            analysis.match_score >= 70 ? 'bg-green-100 text-green-800' :
                            analysis.match_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {analysis.match_score}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => viewAnalysis(analysis.id)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {analyses.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No analyses yet. Create your first one!
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {view === 'analyze' && (
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Analyze Your Resume</h2>
            <div className="bg-white rounded-lg shadow p-6">
              <form onSubmit={handleAnalyze} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Resume (PDF, DOCX, or TXT)
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => setResumeFile(e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g., Senior Software Engineer"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g., Tech Corp"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Description
                  </label>
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description here..."
                    rows="10"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 font-semibold"
                >
                  {loading ? 'Analyzing...' : 'Analyze Resume'}
                </button>
              </form>
            </div>
          </div>
        )}

        {view === 'result' && currentAnalysis && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-gray-800">Analysis Results</h2>
              <button
                onClick={() => setView('dashboard')}
                className="text-blue-600 hover:text-blue-800"
              >
                Back to Dashboard
              </button>
            </div>

            {/* AI-Powered Action Buttons - MOVED TO TOP */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-lg p-6 border-2 border-purple-200">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-purple-900">
                <span className="text-2xl">🤖</span> AI-Powered Tools
              </h3>
              <p className="text-sm text-gray-600 mb-4">Click the buttons below to get personalized AI assistance</p>
              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={generateAIFeedback}
                  disabled={generatingAI}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400 font-semibold shadow-md hover:shadow-lg"
                >
                  {generatingAI && !aiFeedback ? '⏳ Generating...' : '✨ Get AI Feedback'}
                </button>
                <button
                  onClick={generateOptimizedResume}
                  disabled={generatingAI}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 font-semibold shadow-md hover:shadow-lg"
                >
                  {generatingAI && !optimizedResume ? '⏳ Generating...' : '📝 Optimize Resume'}
                </button>
                <button
                  onClick={generateCoverLetter}
                  disabled={generatingAI}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition disabled:bg-gray-400 font-semibold shadow-md hover:shadow-lg"
                >
                  {generatingAI && !coverLetter ? '⏳ Generating...' : '✉️ Generate Cover Letter'}
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-8 text-center">
              <h3 className="text-lg font-medium text-gray-600 mb-2">Match Score</h3>
              <div className={`text-6xl font-bold mb-2 ${
                currentAnalysis.match_score >= 70 ? 'text-green-600' :
                currentAnalysis.match_score >= 50 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {currentAnalysis.match_score}%
              </div>
              <p className="text-gray-600">
                {currentAnalysis.match_score >= 70 ? 'Excellent match!' :
                 currentAnalysis.match_score >= 50 ? 'Good match with room for improvement' :
                 'Consider tailoring your resume more'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4 text-green-700">Keywords Found</h3>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.keywords_found && currentAnalysis.keywords_found.map((kw, idx) => (
                    <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {kw}
                    </span>
                  ))}
                  {(!currentAnalysis.keywords_found || currentAnalysis.keywords_found.length === 0) && (
                    <p className="text-gray-500">No matching keywords found</p>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4 text-orange-700">Keywords Missing</h3>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.keywords_missing && currentAnalysis.keywords_missing.map((kw, idx) => (
                    <span key={idx} className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
                      {kw}
                    </span>
                  ))}
                  {(!currentAnalysis.keywords_missing || currentAnalysis.keywords_missing.length === 0) && (
                    <p className="text-gray-500">Great! All keywords covered</p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Suggestions for Improvement</h3>
              <p className="text-gray-700 leading-relaxed">{currentAnalysis.suggestions}</p>
            </div>

            {/* AI-Powered Features */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>🤖</span> AI-Powered Tools
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={generateAIFeedback}
                  disabled={generatingAI}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400 font-semibold"
                >
                  {generatingAI && !aiFeedback ? '⏳ Generating...' : '✨ Get AI Feedback'}
                </button>
                <button
                  onClick={generateOptimizedResume}
                  disabled={generatingAI}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 font-semibold"
                >
                  {generatingAI && !optimizedResume ? '⏳ Generating...' : '📝 Optimize Resume'}
                </button>
                <button
                  onClick={generateCoverLetter}
                  disabled={generatingAI}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition disabled:bg-gray-400 font-semibold"
                >
                  {generatingAI && !coverLetter ? '⏳ Generating...' : '✉️ Generate Cover Letter'}
                </button>
              </div>
            </div>

            {/* AI Feedback Display */}
            {aiFeedback && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">AI-Powered Personalized Feedback</h3>
                  <button
                    onClick={() => copyToClipboard(aiFeedback)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    📋 Copy
                  </button>
                </div>
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-gray-700 font-sans">{aiFeedback}</pre>
                </div>
              </div>
            )}

            {/* Optimized Resume Display */}
            {optimizedResume && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Your Optimized Resume</h3>
                  <button
                    onClick={() => copyToClipboard(optimizedResume)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    📋 Copy to Clipboard
                  </button>
                </div>
                <div className="bg-gray-50 p-6 rounded border border-gray-200">
                  <pre className="whitespace-pre-wrap text-gray-800 font-sans text-sm">{optimizedResume}</pre>
                </div>
                <p className="text-sm text-gray-600 mt-4">
                  💡 Tip: Copy this optimized version and paste it into your preferred document editor (Word, Google Docs) for final formatting.
                </p>
              </div>
            )}

            {/* Cover Letter Display */}
            {coverLetter && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Tailored Cover Letter</h3>
                  <button
                    onClick={() => copyToClipboard(coverLetter)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    📋 Copy
                  </button>
                </div>
                <div className="bg-gray-50 p-6 rounded border border-gray-200">
                  <pre className="whitespace-pre-wrap text-gray-800 font-sans">{coverLetter}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
