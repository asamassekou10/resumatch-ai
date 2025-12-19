import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Briefcase, MapPin, DollarSign, Clock, Bookmark, ExternalLink,
  Sparkles, Building, TrendingUp, X
} from 'lucide-react';
import axios from 'axios';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';
import '../styles/JobMatches.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const JobMatches = ({ industry, userProfile }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, saved, high-match
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchJobMatches();
  }, [industry]);

  const fetchJobMatches = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/job-matches/?industry=${industry}&limit=20&refresh=${forceRefresh}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMatches(response.data.matches || []);
    } catch (error) {
      console.error('Error fetching job matches:', error);
      if (error.response?.status === 403) {
        setError('Active subscription required to access job matches');
      } else {
        setError('Failed to load job matches. Please try again.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchJobMatches(true);
  };

  const saveJob = async (matchId) => {
    try {
      const token = localStorage.getItem('token');
      const match = matches.find(m => m.id === matchId);

      if (match.is_saved) {
        // Unsave
        await axios.post(
          `${API_URL}/job-matches/${matchId}/unsave`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        // Save
        await axios.post(
          `${API_URL}/job-matches/${matchId}/save`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      // Update local state
      setMatches(matches.map(m =>
        m.id === matchId ? { ...m, is_saved: !m.is_saved } : m
      ));
    } catch (error) {
      console.error('Error saving job:', error);
    }
  };

  const markApplied = async (matchId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/job-matches/${matchId}/apply`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update local state
      setMatches(matches.map(m =>
        m.id === matchId ? { ...m, is_applied: true } : m
      ));
    } catch (error) {
      console.error('Error marking job as applied:', error);
    }
  };

  const dismissJob = async (matchId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/job-matches/${matchId}/dismiss`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Remove from local state
      setMatches(matches.filter(m => m.id !== matchId));
    } catch (error) {
      console.error('Error dismissing job:', error);
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const getMatchScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    return 'Fair Match';
  };

  const filteredMatches = matches.filter(match => {
    if (filter === 'saved') return match.is_saved;
    if (filter === 'high-match') return match.match_score >= 70;
    return true;
  });

  if (loading && matches.length === 0) {
    return (
      <div className="job-matches-loading">
        <div className="spinner-large"></div>
        <p>Finding your perfect job matches with AI...</p>
        <p className="loading-subtext">Analyzing {industry} opportunities</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="job-matches-error">
        <div className="error-icon">⚠️</div>
        <h3>Unable to Load Matches</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => fetchJobMatches()}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="job-matches-container min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="relative z-10">
      {/* Header with filters */}
      <div className="job-matches-header relative z-10">
        <div className="header-left relative z-10">
          <h2 className="font-display">AI-Powered Job Matches</h2>
          <p className="subtitle text-gray-400">
            {matches.length} opportunities in {industry}
          </p>
        </div>
        <div className="header-right relative z-10">
          <ShimmerButton
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <TrendingUp className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh Matches'}
          </ShimmerButton>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Matches ({matches.length})
        </button>
        <button
          className={`filter-btn ${filter === 'high-match' ? 'active' : ''}`}
          onClick={() => setFilter('high-match')}
        >
          <Sparkles className="w-4 h-4" />
          High Match ({matches.filter(m => m.match_score >= 70).length})
        </button>
        <button
          className={`filter-btn ${filter === 'saved' ? 'active' : ''}`}
          onClick={() => setFilter('saved')}
        >
          <Bookmark className="w-4 h-4" />
          Saved ({matches.filter(m => m.is_saved).length})
        </button>
      </div>

      {/* Job Cards Grid */}
      <div className="job-cards-grid">
        {filteredMatches.map((match, index) => (
          <motion.div
            key={match.id}
            className="job-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            {/* Dismiss button */}
            <button
              className="dismiss-btn"
              onClick={() => dismissJob(match.id)}
              title="Dismiss this job"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Match Score Badge */}
            <div
              className="match-score-badge"
              style={{ background: getMatchScoreColor(match.match_score) }}
            >
              <Sparkles className="w-4 h-4" />
              {Math.round(match.match_score)}% Match
            </div>

            {/* Applied Badge */}
            {match.is_applied && (
              <div className="applied-badge">
                ✓ Applied
              </div>
            )}

            {/* Job Header */}
            <div className="job-header">
              <div className="job-title-section">
                <h3>{match.job?.title}</h3>
                <div className="company-info">
                  <Building className="w-4 h-4" />
                  <span>{match.job?.company}</span>
                </div>
              </div>
              <button
                className={`save-btn ${match.is_saved ? 'saved' : ''}`}
                onClick={() => saveJob(match.id)}
                title={match.is_saved ? 'Remove from saved' : 'Save for later'}
              >
                <Bookmark
                  className="w-5 h-5"
                  fill={match.is_saved ? 'currentColor' : 'none'}
                />
              </button>
            </div>

            {/* Job Details */}
            <div className="job-details">
              {match.job?.location && (
                <div className="detail">
                  <MapPin className="w-4 h-4" />
                  <span>{match.job.location}</span>
                </div>
              )}
              {match.job?.salary_range && (
                <div className="detail">
                  <DollarSign className="w-4 h-4" />
                  <span>{match.job.salary_range}</span>
                </div>
              )}
              {match.job?.posted_days_ago !== undefined && (
                <div className="detail">
                  <Clock className="w-4 h-4" />
                  <span>
                    {match.job.posted_days_ago === 0
                      ? 'Posted today'
                      : `Posted ${match.job.posted_days_ago}d ago`}
                  </span>
                </div>
              )}
              {match.job?.remote_type && (
                <div className={`detail remote-badge ${match.job.remote_type}`}>
                  {match.job.remote_type === 'remote' ? '🏠 Remote' :
                   match.job.remote_type === 'hybrid' ? '🏢 Hybrid' :
                   '🏢 On-site'}
                </div>
              )}
            </div>

            {/* AI Explanation */}
            <div className="ai-explanation">
              <div className="ai-badge">
                <Sparkles className="w-3 h-3" />
                AI Analysis
              </div>
              <p>{match.ai_explanation || 'AI-powered match analysis'}</p>
              <div className="match-quality">
                {getMatchScoreLabel(match.match_score)}
              </div>
            </div>

            {/* Skills Match */}
            <div className="skills-match">
              {match.matching_skills && match.matching_skills.length > 0 && (
                <div className="matching-skills">
                  <p className="label">✓ Your Matching Skills:</p>
                  <div className="skills-tags">
                    {match.matching_skills.slice(0, 5).map(skill => (
                      <span key={skill} className="skill-tag match">{skill}</span>
                    ))}
                    {match.matching_skills.length > 5 && (
                      <span className="skill-tag more">+{match.matching_skills.length - 5} more</span>
                    )}
                  </div>
                </div>
              )}

              {match.missing_skills && match.missing_skills.length > 0 && (
                <div className="missing-skills">
                  <p className="label">📚 Skills to Learn:</p>
                  <div className="skills-tags">
                    {match.missing_skills.slice(0, 4).map(skill => (
                      <span key={skill} className="skill-tag missing">{skill}</span>
                    ))}
                    {match.missing_skills.length > 4 && (
                      <span className="skill-tag more">+{match.missing_skills.length - 4} more</span>
                    )}
                  </div>
                </div>
              )}

              {match.skill_match_percentage !== null && (
                <div className="skill-match-bar">
                  <div className="skill-match-label">
                    Skill Match: {Math.round(match.skill_match_percentage)}%
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${match.skill_match_percentage}%`,
                        background: getMatchScoreColor(match.skill_match_percentage)
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="job-actions">
              {!match.is_applied ? (
                <button
                  className="btn-primary"
                  onClick={() => {
                    if (match.job?.external_url) {
                      window.open(match.job.external_url, '_blank');
                      markApplied(match.id);
                    }
                  }}
                >
                  <ExternalLink className="w-4 h-4" />
                  View & Apply
                </button>
              ) : (
                <button className="btn-applied" disabled>
                  ✓ Already Applied
                </button>
              )}
              <button
                className="btn-secondary"
                onClick={() => {
                  // Could open a detailed modal here
                  alert('Job details view coming soon!');
                }}
              >
                View Details
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* No matches state */}
      {filteredMatches.length === 0 && matches.length > 0 && (
        <div className="no-matches">
          <Briefcase className="w-16 h-16 text-slate-400" />
          <h3>No matches found</h3>
          <p>Try adjusting your filters or updating your resume to get more matches</p>
        </div>
      )}

      {/* Empty state */}
      {matches.length === 0 && !loading && (
        <SpotlightCard className="no-matches relative z-10">
          <Briefcase className="w-16 h-16 text-gray-400 relative z-10" />
          <h3 className="font-display relative z-10">No job matches yet</h3>
          <p className="text-gray-400 relative z-10">We're working on finding the perfect opportunities for you in {industry}</p>
          <ShimmerButton onClick={handleRefresh} className="flex items-center gap-2 relative z-10">
            <TrendingUp className="w-4 h-4" />
            Find Matches
          </ShimmerButton>
        </SpotlightCard>
      )}
      </div>
    </div>
  );
};

export default JobMatches;
