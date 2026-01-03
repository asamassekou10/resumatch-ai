import React, { useState, useEffect, useCallback } from 'react';
import { Users, Activity, UserCheck, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import LoadingSpinner from './common/LoadingSpinner';
import SpotlightCard from './ui/SpotlightCard';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const AdminAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [recentUsers, setRecentUsers] = useState([]);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState(30);

  const token = localStorage.getItem('token');

  // Color scheme for charts
  const COLORS = {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    teal: '#14b8a6'
  };

  const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch all analytics data in parallel
      const [overviewRes, timelineRes, usersRes] = await Promise.all([
        axios.get(`${API_URL}/analytics/overview`, { headers }),
        axios.get(`${API_URL}/analytics/signups/timeline?days=${timeRange}`, { headers }),
        axios.get(`${API_URL}/analytics/recent-users?limit=10`, { headers })
      ]);

      setOverview(overviewRes.data.data);
      setTimeline(timelineRes.data.data.timeline);
      setRecentUsers(usersRes.data.data.users);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.response?.data?.error || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [timeRange, token]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-400 mb-4">Error Loading Analytics</h2>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  if (!overview) return null;

  // Prepare data for charts
  const subscriptionData = Object.entries(overview.subscriptions || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  const authProviderData = Object.entries(overview.auth_providers || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Analytics Dashboard</h1>
          <p className="text-gray-400">Real-time insights into your user base and platform activity</p>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Users */}
          <SpotlightCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <Users className="w-6 h-6 text-blue-400" />
                </div>
                <div className="text-sm text-gray-400">All Time</div>
              </div>
              <div className="text-3xl font-bold mb-1">{overview.users.total.toLocaleString()}</div>
              <div className="text-sm text-gray-400">Total Users</div>
              <div className="mt-2 text-xs text-green-400">
                +{overview.users.signups_today} today
              </div>
            </div>
          </SpotlightCard>

          {/* Active Users */}
          <SpotlightCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <Activity className="w-6 h-6 text-green-400" />
                </div>
                <div className="text-sm text-gray-400">Last 30 Days</div>
              </div>
              <div className="text-3xl font-bold mb-1">{overview.users.active_last_30_days.toLocaleString()}</div>
              <div className="text-sm text-gray-400">Active Users</div>
              <div className="mt-2 text-xs text-gray-500">
                {((overview.users.active_last_30_days / overview.users.total) * 100).toFixed(1)}% of total
              </div>
            </div>
          </SpotlightCard>

          {/* Email Verified */}
          <SpotlightCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <UserCheck className="w-6 h-6 text-purple-400" />
                </div>
                <div className="text-sm text-gray-400">Verified</div>
              </div>
              <div className="text-3xl font-bold mb-1">{overview.users.email_verified.toLocaleString()}</div>
              <div className="text-sm text-gray-400">Email Verified</div>
              <div className="mt-2 text-xs text-purple-400">
                {overview.users.verification_rate}% rate
              </div>
            </div>
          </SpotlightCard>

          {/* Total Analyses */}
          <SpotlightCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-500/10 rounded-lg">
                  <LineChartIcon className="w-6 h-6 text-orange-400" />
                </div>
                <div className="text-sm text-gray-400">All Time</div>
              </div>
              <div className="text-3xl font-bold mb-1">{overview.analyses.total.toLocaleString()}</div>
              <div className="text-sm text-gray-400">Total Analyses</div>
              <div className="mt-2 text-xs text-orange-400">
                {overview.analyses.avg_per_user} avg/user
              </div>
            </div>
          </SpotlightCard>
        </div>

        {/* Weekly Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SpotlightCard>
            <div className="p-6">
              <div className="text-sm text-gray-400 mb-2">Signups This Week</div>
              <div className="text-2xl font-bold text-blue-400">{overview.users.signups_week}</div>
            </div>
          </SpotlightCard>

          <SpotlightCard>
            <div className="p-6">
              <div className="text-sm text-gray-400 mb-2">Analyses This Week</div>
              <div className="text-2xl font-bold text-green-400">{overview.analyses.week}</div>
            </div>
          </SpotlightCard>

          <SpotlightCard>
            <div className="p-6">
              <div className="text-sm text-gray-400 mb-2">Guest Conversion Rate</div>
              <div className="text-2xl font-bold text-purple-400">{overview.guest_activity.conversion_rate}%</div>
            </div>
          </SpotlightCard>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Signup Timeline */}
          <SpotlightCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">Signup Trend</h2>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(Number(e.target.value))}
                  className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm"
                >
                  <option value={7}>Last 7 Days</option>
                  <option value={30}>Last 30 Days</option>
                  <option value={90}>Last 90 Days</option>
                </select>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="date"
                    stroke="#9ca3af"
                    tick={{ fill: '#9ca3af' }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                    labelStyle={{ color: '#f3f4f6' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="signups"
                    stroke={COLORS.primary}
                    strokeWidth={2}
                    dot={{ fill: COLORS.primary, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </SpotlightCard>

          {/* Subscription Tiers */}
          <SpotlightCard>
            <div className="p-6">
              <h2 className="text-xl font-bold mb-6">Subscription Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={subscriptionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {subscriptionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </SpotlightCard>
        </div>

        {/* Auth Providers Chart */}
        <div className="mb-8">
          <SpotlightCard>
            <div className="p-6">
              <h2 className="text-xl font-bold mb-6">Sign-up Methods</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={authProviderData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                  />
                  <Bar dataKey="value" fill={COLORS.success} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SpotlightCard>
        </div>

        {/* Recent Users Table */}
        <SpotlightCard>
          <div className="p-6">
            <h2 className="text-xl font-bold mb-6">Recent Signups</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Email</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Name</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Provider</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Tier</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Verified</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {recentUsers.map((user) => (
                    <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 text-sm">{user.email}</td>
                      <td className="py-3 px-4 text-sm">{user.name || '-'}</td>
                      <td className="py-3 px-4 text-sm">
                        <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs">
                          {user.auth_provider}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${
                          user.subscription_tier === 'elite' ? 'bg-purple-500/10 text-purple-400' :
                          user.subscription_tier === 'pro' ? 'bg-green-500/10 text-green-400' :
                          user.subscription_tier === 'student' ? 'bg-blue-500/10 text-blue-400' :
                          user.subscription_tier === 'basic' ? 'bg-yellow-500/10 text-yellow-400' :
                          'bg-gray-500/10 text-gray-400'
                        }`}>
                          {user.subscription_tier}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {user.email_verified ? (
                          <span className="text-green-400">✓</span>
                        ) : (
                          <span className="text-red-400">✗</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-400">
                        {new Date(user.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </SpotlightCard>
      </div>
    </div>
  );
};

export default AdminAnalytics;
