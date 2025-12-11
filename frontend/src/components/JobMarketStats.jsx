import { useState, useEffect } from 'react';
import ApiService, { handleApiError } from '../services/api';
import { ChartBarIcon, RefreshIcon, LoadingIcon, ClipboardIcon, BuildingIcon, DollarIcon, DatabaseIcon, MapPinIcon } from './Icons';
import RepersonalizeButton from './RepersonalizeButton';
import '../styles/JobMarket.css';

export default function JobMarketStats({ userProfile, onRepersonalize }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Derive industry from user profile
  const userIndustry = userProfile?.preferred_industry ||
                       userProfile?.detected_industries?.[0]?.industry ||
                       null;

  useEffect(() => {
    console.log('[JobMarketStats] UserProfile:', userProfile);
    console.log('[JobMarketStats] Derived industry:', userIndustry);
    loadStats();
  }, [userIndustry]); // Re-fetch when user's industry changes

  const loadStats = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('[JobMarketStats] Fetching stats with industry filter:', userIndustry);
      // Pass industry parameter to filter stats by user's industry
      const data = await ApiService.getJobStatistics(userIndustry);
      console.log('[JobMarketStats] Stats response:', data);
      setStats(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const salaryStats = stats?.salary_statistics || {};

  return (
    <div className="job-market-stats">
      <div className="stats-header">
        <div className="header-title">
          <ChartBarIcon className="w-8 h-8" />
          <div>
            <h1>Job Market Statistics</h1>
            {userIndustry && <p className="subtitle" style={{ fontSize: '0.875rem', opacity: 0.8, marginTop: '0.25rem' }}>Filtering by: {userIndustry}</p>}
          </div>
        </div>
        <div className="header-actions">
          {userProfile?.preferences_completed && onRepersonalize && (
            <RepersonalizeButton onClick={onRepersonalize} />
          )}
          <button className="btn btn-secondary" onClick={loadStats} disabled={loading}>
          {loading ? (
            <LoadingIcon className="w-4 h-4" />
          ) : (
            <>
              <RefreshIcon className="w-4 h-4" />
              <span>Refresh</span>
            </>
          )}
        </button>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading statistics...</p>
        </div>
      ) : stats ? (
        <div className="stats-content">
          {/* Main Metrics */}
          <div className="metrics-grid">
            <div className="metric-card large">
              <div className="metric-icon">
                <ClipboardIcon className="w-6 h-6" />
              </div>
              <div className="metric-body">
                <h3>Total Postings</h3>
                <p className="metric-value">{stats.total_postings}</p>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">
                <BuildingIcon className="w-6 h-6" />
              </div>
              <div className="metric-body">
                <h3>Industries</h3>
                <p className="metric-value">{Object.keys(stats.industries || {}).length}</p>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">
                <MapPinIcon className="w-6 h-6" />
              </div>
              <div className="metric-body">
                <h3>Salary Tracked</h3>
                <p className="metric-value">{salaryStats.postings_with_salary || 0}</p>
              </div>
            </div>
          </div>

          {/* Industries */}
          <div className="section">
            <h2>
              <BuildingIcon className="w-5 h-5" />
              <span>Industries</span>
            </h2>
            <div className="industries-list">
              {Object.entries(stats.industries || {}).map(([industry, count]) => (
                <div key={industry} className="industry-item">
                  <span className="industry-name">{industry}</span>
                  <div className="industry-bar">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${(count / stats.total_postings) * 100}%`
                      }}
                    ></div>
                  </div>
                  <span className="industry-count">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Sources */}
          {stats.sources && Object.keys(stats.sources).length > 0 && (
            <div className="section">
              <h2>
                <DatabaseIcon className="w-5 h-5" />
                <span>Sources</span>
              </h2>
              <div className="sources-grid">
                {Object.entries(stats.sources).map(([source, count]) => (
                  <div key={source} className="source-card">
                    <span className="source-name">{source}</span>
                    <span className="source-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Salary Statistics */}
          <div className="section">
            <h2>
              <DollarIcon className="w-5 h-5" />
              <span>Salary Statistics</span>
            </h2>
            <div className="salary-detail-grid">
              <div className="salary-detail">
                <span className="label">Minimum</span>
                <span className="value">${(salaryStats.min || 0).toLocaleString()}</span>
              </div>
              <div className="salary-detail">
                <span className="label">Average</span>
                <span className="value">${(salaryStats.average || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="salary-detail">
                <span className="label">Median</span>
                <span className="value">${(salaryStats.median || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="salary-detail">
                <span className="label">Maximum</span>
                <span className="value">${(salaryStats.max || 0).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <ChartBarIcon className="w-12 h-12" />
          <p>No data available. Load sample data from the Market Intelligence Dashboard.</p>
        </div>
      )}
    </div>
  );
}
