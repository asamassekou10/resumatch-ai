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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">R</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                ResuMatch AI
              </h1>
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setView('login')}
                className="text-gray-700 hover:text-blue-600 transition font-medium"
              >
                Login
              </button>
              <button
                onClick={() => setView('register')}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-medium"
              >
                Get Started
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Optimize Your Resume with
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> AI Power</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Stop guessing if your resume matches the job. Get instant AI-powered analysis, 
              discover missing keywords, and increase your chances of landing interviews.
            </p>
            <button
              onClick={() => setView('register')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-lg transition transform hover:scale-105"
            >
              Start Optimizing - It's Free
            </button>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-3xl">🎯</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Instant Match Score</h3>
              <p className="text-gray-600">
                Get a percentage match between your resume and any job description in seconds. 
                Know exactly where you stand.
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-3xl">🔍</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Keyword Analysis</h3>
              <p className="text-gray-600">
                Discover which keywords you have and which ones you're missing. 
                ATS systems love the right keywords!
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-3xl">📊</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Track Your Progress</h3>
              <p className="text-gray-600">
                Visual dashboard shows your improvement over time and identifies skill gaps 
                across all your applications.
              </p>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-white rounded-2xl shadow-xl p-12 mb-20">
            <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">
              How It Works
            </h2>
            <div className="grid md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold text-2xl">
                  1
                </div>
                <h4 className="text-xl font-semibold mb-2">Upload Resume</h4>
                <p className="text-gray-600">Upload your resume in PDF, DOCX, or TXT format</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold text-2xl">
                  2
                </div>
                <h4 className="text-xl font-semibold mb-2">Paste Job Description</h4>
                <p className="text-gray-600">Copy the job posting you're interested in</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold text-2xl">
                  3
                </div>
                <h4 className="text-xl font-semibold mb-2">Get AI Analysis</h4>
                <p className="text-gray-600">Our AI analyzes the match in seconds</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-pink-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold text-2xl">
                  4
                </div>
                <h4 className="text-xl font-semibold mb-2">Optimize & Apply</h4>
                <p className="text-gray-600">Update your resume and apply with confidence</p>
              </div>
            </div>
          </div>

          {/* Why Use ResuMatch */}
          <div className="grid md:grid-cols-2 gap-12 mb-20">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Why Use ResuMatch AI?
              </h2>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold">✓</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg mb-1">Beat the ATS Systems</h4>
                    <p className="text-gray-600">90% of companies use ATS to filter resumes. Make sure yours gets through.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold">✓</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg mb-1">Save Time</h4>
                    <p className="text-gray-600">No more guessing. Know exactly what to add or remove in seconds.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold">✓</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg mb-1">Data-Driven Insights</h4>
                    <p className="text-gray-600">Track which skills are most in-demand across all your job applications.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold">✓</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg mb-1">Privacy First</h4>
                    <p className="text-gray-600">Your data is secure and never shared. You own your information.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl p-8 text-white">
              <h3 className="text-3xl font-bold mb-4">Ready to Get More Interviews?</h3>
              <p className="text-blue-100 mb-6 text-lg">
                Join thousands of job seekers who have improved their resume match scores 
                and landed their dream jobs.
              </p>
              <div className="space-y-4 mb-8">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📈</span>
                  <span className="text-lg">Average 35% increase in match scores</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">⚡</span>
                  <span className="text-lg">Results in under 10 seconds</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  <span className="text-lg">Unlimited analyses</span>
                </div>
              </div>
              <button
                onClick={() => setView('register')}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition w-full"
              >
                Create Free Account
              </button>
            </div>
          </div>

          {/* Final CTA */}
          <div className="text-center bg-gray-900 rounded-2xl p-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              Stop Applying Blindly
            </h2>
            <p className="text-gray-300 text-xl mb-8 max-w-2xl mx-auto">
              Start using AI to optimize your resume for every job application. 
              It's free, fast, and proven to work.
            </p>
            <button
              onClick={() => setView('register')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-lg transition"
            >
              Get Started Now →
            </button>
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-gray-900 text-gray-400 py-8">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2025 ResuMatch AI. Built for job seekers.</p>
            <p className="text-sm mt-2">ITAI 2277 - AI Project by Alhassane Samassekou</p>
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
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">AI Resume Optimizer</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setView('dashboard')}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Dashboard
            </button>
            <button
              onClick={() => setView('analyze')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              New Analysis
            </button>
            <button
              onClick={handleLogout}
              className="text-gray-700 hover:text-red-600 transition"
            >
              Logout
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
