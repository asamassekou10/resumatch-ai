import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import {
  UsersIcon, CheckCircleIcon, RefreshIcon, TrendingUpIcon,
  ChartBarIcon, ClipboardIcon, DollarIcon, AwardIcon
} from './Icons';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Icon map for StatCard
const iconMap = {
  users: UsersIcon,
  check: CheckCircleIcon,
  lock: () => (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  ),
  trending: TrendingUpIcon,
  chart: ChartBarIcon,
  calendar: () => (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  ),
  star: AwardIcon,
  clipboard: ClipboardIcon,
  dollar: DollarIcon
};

const AdminDashboard = ({ token, onLogout, onNavigate }) => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [jobSources, setJobSources] = useState(null);
  const [jobStats, setJobStats] = useState(null);
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState(null);

  useEffect(() => {
    fetchDashboardStats();
    fetchUsers();
    fetchJobSources();
    fetchJobStats();
  }, [page]);

  const fetchDashboardStats = async () => {
    setLoading(true);
    try {
      // API_URL already includes /v1, so just append admin/dashboard/stats
      const response = await fetch(`${API_URL}/admin/dashboard/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setStats(data.data);
      } else {
        setError(data.message || 'Failed to fetch stats');
      }
    } catch (err) {
      console.error('Dashboard stats error:', err);
      setError('Failed to fetch dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch(
        `${API_URL}/admin/users?page=${page}&limit=10${searchQuery ? `&search=${searchQuery}` : ''}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const data = await response.json();
      if (data.status === 'success') {
        setUsers(data.data.users);
      }
    } catch (err) {
      console.error('Fetch users error:', err);
      setError('Failed to fetch users');
    }
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
    setPage(1);
  };

  const fetchJobSources = async () => {
    try {
      const response = await fetch(`${API_URL}/jobs/sources`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setJobSources(data);
    } catch (err) {
      console.error('Job sources error:', err);
    }
  };

  const fetchJobStats = async () => {
    try {
      const response = await fetch(`${API_URL}/jobs/statistics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setJobStats(data);
    } catch (err) {
      console.error('Job stats error:', err);
    }
  };

  const handleIngestRealJobs = async () => {
    setIngesting(true);
    setIngestResult(null);
    try {
      const response = await fetch(`${API_URL}/jobs/ingest-real`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setIngestResult(data);
      if (data.success) {
        fetchJobStats();
      }
    } catch (err) {
      setIngestResult({ success: false, error: err.message });
    } finally {
      setIngesting(false);
    }
  };

  const StatCard = ({ title, value, iconName, color }) => {
    const IconComponent = iconMap[iconName];
    return (
      <div className={`bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:border-${color}-400/50 transition`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
            <p className={`text-4xl font-bold text-${color}-400 mt-2`}>{value}</p>
          </div>
          <div className={`text-${color}-400 opacity-30`}>
            {IconComponent && <IconComponent className="w-12 h-12" />}
          </div>
        </div>
      </div>
    );
  };

  if (!stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mb-4"></div>
          <p className="text-white text-xl">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
              <p className="text-slate-400 mt-1">System overview and management</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={fetchDashboardStats}
                className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition flex items-center gap-2"
              >
                <RefreshIcon className="w-4 h-4" />
                <span>Refresh</span>
              </button>
              <button
                onClick={onLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-8 border-b border-slate-700 overflow-x-auto">
          {['overview', 'users', 'job-data', 'analytics', 'settings'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-semibold transition-colors border-b-2 capitalize ${
                activeTab === tab
                  ? 'text-cyan-400 border-cyan-400'
                  : 'text-slate-400 border-transparent hover:text-slate-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Key Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  title="Total Users"
                  value={stats.metrics?.total_users || 0}
                  iconName="users"
                  color="cyan"
                />
                <StatCard
                  title="Active Users"
                  value={stats.metrics?.active_users || 0}
                  iconName="check"
                  color="green"
                />
                <StatCard
                  title="Admin Users"
                  value={stats.metrics?.admin_users || 0}
                  iconName="lock"
                  color="purple"
                />
                <StatCard
                  title="New Users (30d)"
                  value={stats.metrics?.new_users_30d || 0}
                  iconName="trending"
                  color="blue"
                />
              </div>
            </div>

            {/* Analysis Metrics */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Analysis Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                  title="Total Analyses"
                  value={stats.metrics?.total_analyses || 0}
                  iconName="chart"
                  color="yellow"
                />
                <StatCard
                  title="Analyses (30d)"
                  value={stats.metrics?.analyses_30d || 0}
                  iconName="calendar"
                  color="orange"
                />
                <StatCard
                  title="Avg Match Score"
                  value={`${(stats.metrics?.avg_match_score || 0).toFixed(1)}%`}
                  iconName="star"
                  color="green"
                />
              </div>
            </div>

            {/* Trends */}
            {stats.trends && (
              <div className="space-y-8">
                {stats.trends.signup_trend && stats.trends.signup_trend.length > 0 && (
                  <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                    <h3 className="text-xl font-semibold mb-4 text-white">User Signup Trend (30 Days)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={stats.trends.signup_trend}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#F9FAFB'
                          }}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="count"
                          stroke="#06B6D4"
                          strokeWidth={2}
                          name="New Signups"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {stats.trends.analyses_trend && stats.trends.analyses_trend.length > 0 && (
                  <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                    <h3 className="text-xl font-semibold mb-4 text-white">Analyses Trend (30 Days)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={stats.trends.analyses_trend}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#F9FAFB'
                          }}
                        />
                        <Legend />
                        <Bar dataKey="count" fill="#06B6D4" name="Analyses" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Search users by email..."
                value={searchQuery}
                onChange={handleSearch}
                className="flex-1 px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-600">
                  <thead className="bg-slate-700/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Joined</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Last Login</th>
                    </tr>
                  </thead>
                  <tbody className="bg-slate-800/30 divide-y divide-slate-600">
                    {users.map(user => (
                      <tr key={user.id} className="hover:bg-slate-700/30 transition">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{user.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            user.is_active
                              ? 'bg-green-900/50 text-green-300 border border-green-500/30'
                              : 'bg-red-900/50 text-red-300 border border-red-500/30'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            user.is_admin
                              ? 'bg-purple-900/50 text-purple-300 border border-purple-500/30'
                              : 'bg-slate-700/50 text-slate-300 border border-slate-600/30'
                          }`}>
                            {user.is_admin ? 'Admin' : 'User'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                          {user.last_login
                            ? new Date(user.last_login).toLocaleDateString()
                            : 'Never'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Job Data Tab */}
        {activeTab === 'job-data' && (
          <div className="space-y-8">
            {/* Job Sources */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Job Data Sources</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {jobSources?.sources && Object.entries(jobSources.sources).map(([key, source]) => (
                  <div key={key} className={`bg-slate-800/50 backdrop-blur-sm border rounded-xl p-4 ${
                    source.available ? 'border-green-500/50' : 'border-slate-600'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-white font-semibold">{source.name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        source.available
                          ? 'bg-green-900/50 text-green-300 border border-green-500/30'
                          : 'bg-red-900/50 text-red-300 border border-red-500/30'
                      }`}>
                        {source.available ? 'Active' : 'Not Configured'}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm">{source.description}</p>
                  </div>
                ))}
              </div>
              <p className="text-slate-400 text-sm mt-4">
                {jobSources?.available_sources || 0} of {jobSources?.total_sources || 0} sources configured
              </p>
            </div>

            {/* Job Statistics */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Job Posting Statistics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                  title="Total Job Postings"
                  value={jobStats?.total_postings || 0}
                  iconName="clipboard"
                  color="cyan"
                />
                <StatCard
                  title="Average Salary"
                  value={jobStats?.salary_statistics?.average
                    ? `$${Math.round(jobStats.salary_statistics.average).toLocaleString()}`
                    : 'N/A'}
                  iconName="dollar"
                  color="green"
                />
                <StatCard
                  title="Postings with Salary"
                  value={jobStats?.salary_statistics?.postings_with_salary || 0}
                  iconName="chart"
                  color="purple"
                />
              </div>
            </div>

            {/* Sources Breakdown */}
            {jobStats?.sources && Object.keys(jobStats.sources).length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-4 text-white">Postings by Source</h3>
                <div className="space-y-3">
                  {Object.entries(jobStats.sources).map(([source, count]) => (
                    <div key={source} className="flex items-center justify-between">
                      <span className="text-slate-300 capitalize">{source}</span>
                      <div className="flex items-center gap-4">
                        <div className="w-48 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-cyan-500 h-2 rounded-full"
                            style={{ width: `${(count / jobStats.total_postings) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-white font-semibold w-16 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Ingest Real Jobs */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-white">Ingest Real Job Postings</h3>
              <p className="text-slate-400 mb-6">
                Fetch and ingest real job postings from all configured external APIs (RemoteOK, JSearch, Adzuna).
              </p>
              <button
                onClick={handleIngestRealJobs}
                disabled={ingesting}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {ingesting ? 'Ingesting...' : 'Ingest Real Jobs Now'}
              </button>

              {ingestResult && (
                <div className={`mt-4 p-4 rounded-lg ${
                  ingestResult.success
                    ? 'bg-green-900/50 border border-green-500 text-green-300'
                    : 'bg-red-900/50 border border-red-500 text-red-300'
                }`}>
                  {ingestResult.success ? (
                    <div>
                      <p className="font-semibold">Ingestion Complete!</p>
                      <p>Postings ingested: {ingestResult.details?.postings_ingested || 0}</p>
                      <p>Skills extracted: {ingestResult.details?.skills_extracted || 0}</p>
                    </div>
                  ) : (
                    <p>Error: {ingestResult.error || 'Ingestion failed'}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-white">User Growth</h3>
              <p className="text-slate-400 mb-6 text-sm">Cumulative and daily new user registrations</p>
              {/* More detailed analytics would go here */}
              <div className="text-center py-12 text-slate-400">
                <p>Analytics visualizations loading...</p>
              </div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-white">System Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-white font-medium">Maintenance Mode</h4>
                    <p className="text-slate-400 text-sm">Temporarily disable user access</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
