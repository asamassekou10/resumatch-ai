/**
 * JobApplicationsPage Component
 * Main page for job application tracking
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus, Search, Star, Archive, RefreshCw,
  TrendingUp, Briefcase, Phone, Gift, Clock
} from 'lucide-react';
import config from '../config';
import JobApplicationCard from './JobApplicationCard';
import JobApplicationModal from './JobApplicationModal';
import SpotlightCard from './ui/SpotlightCard';
import SEO from './common/SEO';

const API_URL = config.api.baseURL;

const FILTER_OPTIONS = [
  { value: '', label: 'All Applications' },
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'phone_screen', label: 'Phone Screen' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'withdrawn', label: 'Withdrawn' }
];

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Date Added' },
  { value: 'date_applied', label: 'Date Applied' },
  { value: 'company_name', label: 'Company Name' },
  { value: 'job_title', label: 'Job Title' },
  { value: 'follow_up_date', label: 'Follow-up Date' }
];

const JobApplicationsPage = ({ token }) => {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showStarredOnly, setShowStarredOnly] = useState(false);
  const [showArchived, setShowArchived] = useState(false);
  const [sortBy, setSortBy] = useState('created_at');
  const sortOrder = 'desc'; // Fixed to descending for now

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingApplication, setEditingApplication] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  // Fetch applications
  const fetchApplications = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (showStarredOnly) params.append('starred', 'true');
      if (showArchived) params.append('archived', 'true');
      if (searchQuery) params.append('search', searchQuery);
      params.append('sort', sortBy);
      params.append('order', sortOrder);

      const response = await fetch(`${API_URL}/api/job-applications?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch applications');

      const data = await response.json();
      setApplications(data.data.applications || []);
      setError('');
    } catch (err) {
      setError('Failed to load applications. Please try again.');
      console.error('Error fetching applications:', err);
    } finally {
      setLoading(false);
    }
  }, [token, statusFilter, showStarredOnly, showArchived, searchQuery, sortBy, sortOrder]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/job-applications/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, [token]);

  useEffect(() => {
    fetchApplications();
    fetchStats();
  }, [fetchApplications, fetchStats]);

  // Handle save (create or update)
  const handleSave = async (formData) => {
    try {
      setIsSaving(true);
      const isEditing = !!editingApplication;
      const url = isEditing
        ? `${API_URL}/api/job-applications/${editingApplication.id}`
        : `${API_URL}/api/job-applications`;

      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to save application');
      }

      setShowModal(false);
      setEditingApplication(null);
      fetchApplications();
      fetchStats();
    } catch (err) {
      console.error('Error saving application:', err);
      alert(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle status change
  const handleStatusChange = async (id, newStatus) => {
    try {
      const response = await fetch(`${API_URL}/api/job-applications/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) throw new Error('Failed to update status');

      // Optimistic update
      setApplications(prev =>
        prev.map(app => (app.id === id ? { ...app, status: newStatus } : app))
      );
      fetchStats();
    } catch (err) {
      console.error('Error updating status:', err);
      fetchApplications();
    }
  };

  // Handle toggle star
  const handleToggleStar = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/job-applications/${id}/star`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to toggle star');

      const data = await response.json();
      setApplications(prev =>
        prev.map(app => (app.id === id ? { ...app, is_starred: data.data.is_starred } : app))
      );
    } catch (err) {
      console.error('Error toggling star:', err);
    }
  };

  // Handle toggle archive
  const handleToggleArchive = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/job-applications/${id}/archive`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to toggle archive');

      fetchApplications();
      fetchStats();
    } catch (err) {
      console.error('Error toggling archive:', err);
    }
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this application?')) return;

    try {
      const response = await fetch(`${API_URL}/api/job-applications/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to delete application');

      setApplications(prev => prev.filter(app => app.id !== id));
      fetchStats();
    } catch (err) {
      console.error('Error deleting application:', err);
    }
  };

  // Handle edit
  const handleEdit = (application) => {
    setEditingApplication(application);
    setShowModal(true);
  };

  // Stats cards data
  const statCards = stats ? [
    { label: 'Total', value: stats.total, icon: Briefcase, color: 'blue' },
    { label: 'Applied', value: stats.by_status?.applied || 0, icon: TrendingUp, color: 'blue' },
    { label: 'Interviews', value: (stats.by_status?.phone_screen || 0) + (stats.by_status?.interview || 0), icon: Phone, color: 'amber' },
    { label: 'Offers', value: stats.by_status?.offer || 0, icon: Gift, color: 'green' },
    { label: 'Follow-ups', value: stats.upcoming_followups || 0, icon: Clock, color: 'purple' }
  ] : [];

  return (
    <>
      <SEO
        title="Job Application Tracker"
        description="Track all your job applications in one place. Monitor status, set follow-up reminders, and organize your job search."
        keywords="job application tracker, job search, application status, interview tracking"
      />

      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 py-8 relative z-10">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white font-display">Job Application Tracker</h1>
              <p className="text-gray-400 mt-1">Track and manage all your job applications in one place</p>
            </div>
            <button
              onClick={() => {
                setEditingApplication(null);
                setShowModal(true);
              }}
              className="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition shadow-lg shadow-blue-500/25"
            >
              <Plus className="w-5 h-5" />
              Add Application
            </button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
              {statCards.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <SpotlightCard className="p-4 rounded-xl">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-${stat.color}-500/20`}>
                          <Icon className={`w-5 h-5 text-${stat.color}-400`} />
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-white">{stat.value}</p>
                          <p className="text-sm text-gray-400">{stat.label}</p>
                        </div>
                      </div>
                    </SpotlightCard>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* Response Rate Banner */}
          {stats && stats.response_rate > 0 && (
            <div className="mb-6 p-4 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-xl">
              <p className="text-gray-300">
                Your response rate: <span className="text-green-400 font-bold">{Math.round(stats.response_rate * 100)}%</span>
                {stats.applications_this_week > 0 && (
                  <span className="ml-4 text-gray-400">
                    {stats.applications_this_week} applications this week
                  </span>
                )}
              </p>
            </div>
          )}

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search companies or job titles..."
                className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
            >
              {FILTER_OPTIONS.map(option => (
                <option key={option.value} value={option.value} className="bg-gray-900">
                  {option.label}
                </option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
            >
              {SORT_OPTIONS.map(option => (
                <option key={option.value} value={option.value} className="bg-gray-900">
                  {option.label}
                </option>
              ))}
            </select>

            {/* Toggle buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setShowStarredOnly(!showStarredOnly)}
                className={`p-3 rounded-lg border transition ${
                  showStarredOnly
                    ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'
                }`}
                title="Show starred only"
              >
                <Star className={`w-5 h-5 ${showStarredOnly ? 'fill-current' : ''}`} />
              </button>

              <button
                onClick={() => setShowArchived(!showArchived)}
                className={`p-3 rounded-lg border transition ${
                  showArchived
                    ? 'bg-purple-500/20 border-purple-500/30 text-purple-400'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'
                }`}
                title="Show archived"
              >
                <Archive className="w-5 h-5" />
              </button>

              <button
                onClick={() => {
                  fetchApplications();
                  fetchStats();
                }}
                className="p-3 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white transition"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="p-4 mb-6 bg-red-500/10 border border-red-500/20 rounded-xl">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            </div>
          )}

          {/* Empty State */}
          {!loading && applications.length === 0 && (
            <SpotlightCard className="p-12 rounded-2xl text-center">
              <Briefcase className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2 font-display">
                {searchQuery || statusFilter || showStarredOnly
                  ? 'No applications match your filters'
                  : 'No applications yet'}
              </h3>
              <p className="text-gray-400 mb-6">
                {searchQuery || statusFilter || showStarredOnly
                  ? 'Try adjusting your search or filters'
                  : 'Start tracking your job applications by adding your first one'}
              </p>
              {!searchQuery && !statusFilter && !showStarredOnly && (
                <button
                  onClick={() => {
                    setEditingApplication(null);
                    setShowModal(true);
                  }}
                  className="inline-flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition"
                >
                  <Plus className="w-5 h-5" />
                  Add Your First Application
                </button>
              )}
            </SpotlightCard>
          )}

          {/* Applications List */}
          {!loading && applications.length > 0 && (
            <div className="space-y-4">
              <AnimatePresence>
                {applications.map((app, index) => (
                  <motion.div
                    key={app.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.03 }}
                  >
                    <JobApplicationCard
                      application={app}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                      onStatusChange={handleStatusChange}
                      onToggleStar={handleToggleStar}
                      onToggleArchive={handleToggleArchive}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Add/Edit Modal */}
        <JobApplicationModal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            setEditingApplication(null);
          }}
          onSave={handleSave}
          application={editingApplication}
          isLoading={isSaving}
        />
      </div>
    </>
  );
};

export default JobApplicationsPage;
