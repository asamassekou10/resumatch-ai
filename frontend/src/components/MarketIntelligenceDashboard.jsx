import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell,
  Area, AreaChart, RadialBarChart, RadialBar
} from 'recharts';
import ApiService, { handleApiError } from '../services/api';
import {
  ChartBarIcon, PieChartIcon, TrendingUpIcon, TargetIcon, FireIcon,
  BriefcaseIcon, BuildingIcon, DollarIcon, RefreshIcon, LoadingIcon,
  ClipboardIcon, DatabaseIcon, LayersIcon
} from './Icons';
import RepersonalizeButton from './RepersonalizeButton';
import '../styles/theme.css';
import '../styles/MarketDashboard.css';

// Modern chart color palette
const CHART_COLORS = {
  primary: '#06b6d4',
  secondary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  purple: '#8b5cf6',
  pink: '#ec4899'
};

const COLORS = [
  CHART_COLORS.primary,
  CHART_COLORS.secondary,
  CHART_COLORS.success,
  CHART_COLORS.warning,
  CHART_COLORS.error,
  CHART_COLORS.purple,
  CHART_COLORS.pink
];

// Custom Tooltip Component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-label">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="tooltip-value" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number'
              ? entry.value.toLocaleString()
              : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// KPI Card Component
const KPICard = ({ icon: Icon, label, value, trend, color = 'primary' }) => (
  <div className={`kpi-card kpi-${color}`}>
    <div className={`kpi-icon kpi-icon-${color}`}>
      <Icon className="w-6 h-6" />
    </div>
    <div className="kpi-info">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {trend && (
        <div className={`kpi-trend ${trend > 0 ? 'positive' : 'negative'}`}>
          <TrendingUpIcon className="w-3 h-3" />
          <span>{Math.abs(trend)}%</span>
        </div>
      )}
    </div>
  </div>
);

export default function MarketIntelligenceDashboard({ userProfile, onRepersonalize }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [marketData, setMarketData] = useState(null);
  const [jobStats, setJobStats] = useState(null);
  const [topSkills, setTopSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [salaryTrends, setSalaryTrends] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const summaryData = await ApiService.getMarketSummary();
      setMarketData(summaryData);

      const jobData = await ApiService.getJobStatistics();
      setJobStats(jobData);

      const skillsData = await ApiService.getTopDemandedSkills(15, 90);
      setTopSkills(skillsData.top_skills || []);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const loadSampleData = async () => {
    setLoading(true);
    try {
      await ApiService.loadSampleData();
      await loadDashboardData();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSkillClick = async (skillId) => {
    try {
      const trends = await ApiService.getSalaryTrends(skillId);
      setSalaryTrends(trends);
      setSelectedSkill(skillId);
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const industryData = jobStats?.industries ?
    Object.entries(jobStats.industries).map(([name, count]) => ({ name, value: count })) : [];

  const salaryStats = jobStats?.salary_statistics || {};

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: ChartBarIcon },
    { id: 'skills', label: 'Top Skills', icon: BriefcaseIcon },
    { id: 'industries', label: 'Industries', icon: BuildingIcon },
    { id: 'salaries', label: 'Salaries', icon: DollarIcon }
  ];

  return (
    <div className="market-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-icon">
            <ChartBarIcon className="w-8 h-8" />
          </div>
          <div>
            <h1>Market Intelligence Dashboard</h1>
            <p>Real-time job market analysis and skill demand insights</p>
          </div>
        </div>
        <div className="header-actions">
          {userProfile?.preferences_completed && onRepersonalize && (
            <RepersonalizeButton onClick={onRepersonalize} />
          )}
          {!jobStats?.total_postings && (
            <button className="btn btn-primary" onClick={loadSampleData} disabled={loading}>
              {loading ? <LoadingIcon className="w-4 h-4" /> : <DatabaseIcon className="w-4 h-4" />}
              <span>{loading ? 'Loading...' : 'Load Sample Data'}</span>
            </button>
          )}
          <button className="btn btn-secondary" onClick={loadDashboardData} disabled={loading}>
            {loading ? <LoadingIcon className="w-4 h-4" /> : <RefreshIcon className="w-4 h-4" />}
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && <div className="error-alert">{error}</div>}

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {loading && activeTab === 'overview' ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading market data...</p>
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && marketData && jobStats && (
            <div className="tab-content animate-fade-in">
              {/* KPI Cards */}
              <div className="kpi-grid">
                <KPICard
                  icon={ClipboardIcon}
                  label="Total Postings"
                  value={jobStats.total_postings?.toLocaleString() || 0}
                  color="primary"
                />
                <KPICard
                  icon={TargetIcon}
                  label="Unique Skills"
                  value={marketData.summary?.total_unique_skills?.toLocaleString() || 0}
                  color="secondary"
                />
                <KPICard
                  icon={DollarIcon}
                  label="Avg Salary"
                  value={`$${(salaryStats.average || 0).toLocaleString('en-US', {maximumFractionDigits: 0})}`}
                  color="success"
                />
                <KPICard
                  icon={FireIcon}
                  label="Fastest Growing"
                  value={marketData.summary?.fastest_growing_skill?.skill_name || 'N/A'}
                  color="warning"
                />
              </div>

              {/* Charts Row */}
              <div className="charts-row">
                {/* Industry Distribution Chart */}
                <div className="chart-container">
                  <h3>
                    <PieChartIcon className="w-5 h-5" />
                    Industry Distribution
                  </h3>
                  <div className="chart-wrapper">
                    <ResponsiveContainer width="100%" height={320}>
                      <PieChart>
                        <Pie
                          data={industryData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                          animationBegin={0}
                          animationDuration={800}
                        >
                          {industryData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={COLORS[index % COLORS.length]}
                              stroke="transparent"
                            />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                          layout="vertical"
                          align="right"
                          verticalAlign="middle"
                          formatter={(value) => <span style={{ color: '#94a3b8' }}>{value}</span>}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Salary Range */}
                <div className="chart-container salary-summary">
                  <h3>
                    <DollarIcon className="w-5 h-5" />
                    Salary Range Analysis
                  </h3>
                  <div className="salary-grid">
                    <div className="salary-stat">
                      <span className="label">Minimum</span>
                      <span className="value">${(salaryStats.min || 0).toLocaleString()}</span>
                    </div>
                    <div className="salary-stat">
                      <span className="label">Maximum</span>
                      <span className="value">${(salaryStats.max || 0).toLocaleString()}</span>
                    </div>
                    <div className="salary-stat highlight">
                      <span className="label">Median</span>
                      <span className="value">${(salaryStats.median || 0).toLocaleString()}</span>
                    </div>
                    <div className="salary-stat">
                      <span className="label">Postings Tracked</span>
                      <span className="value">{salaryStats.postings_with_salary || 0}</span>
                    </div>
                  </div>
                  {/* Visual salary range bar */}
                  <div className="salary-range-visual">
                    <div className="range-bar">
                      <div className="range-fill" style={{
                        left: '0%',
                        width: '100%',
                        background: 'linear-gradient(90deg, #10b981 0%, #06b6d4 50%, #3b82f6 100%)'
                      }}></div>
                      <div className="range-marker" style={{ left: '50%' }}>
                        <span>Median</span>
                      </div>
                    </div>
                    <div className="range-labels">
                      <span>${(salaryStats.min || 0).toLocaleString()}</span>
                      <span>${(salaryStats.max || 0).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Top Skills Tab */}
          {activeTab === 'skills' && topSkills.length > 0 && (
            <div className="tab-content animate-fade-in">
              <div className="skills-container">
                <div className="chart-container skills-chart">
                  <h3>
                    <FireIcon className="w-5 h-5" />
                    Top Demanded Skills
                  </h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={topSkills}
                      layout="vertical"
                      margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={true}
                        vertical={false}
                        stroke="rgba(148, 163, 184, 0.1)"
                      />
                      <XAxis
                        type="number"
                        stroke="#64748b"
                        fontSize={12}
                      />
                      <YAxis
                        dataKey="skill_name"
                        type="category"
                        stroke="#64748b"
                        fontSize={12}
                        width={90}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar
                        dataKey="market_demand_score"
                        fill="url(#barGradient)"
                        radius={[0, 6, 6, 0]}
                        animationDuration={800}
                      />
                      <defs>
                        <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                          <stop offset="0%" stopColor={CHART_COLORS.primary} />
                          <stop offset="100%" stopColor={CHART_COLORS.secondary} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="chart-container skills-list">
                  <h3>
                    <LayersIcon className="w-5 h-5" />
                    Skill Details
                  </h3>
                  <div className="skills-table">
                    {topSkills.map((skill, idx) => (
                      <div
                        key={idx}
                        className="skill-row"
                        onClick={() => handleSkillClick(skill.skill_id)}
                      >
                        <div className="skill-rank">#{idx + 1}</div>
                        <div className="skill-info">
                          <div className="skill-name">{skill.skill_name}</div>
                          <div className="skill-meta">
                            {skill.postings_count} postings
                            {skill.average_salary > 0 && ` • Avg: $${(skill.average_salary || 0).toLocaleString()}`}
                          </div>
                        </div>
                        <div className="skill-demand">
                          <div className="demand-bar">
                            <div
                              className="demand-fill"
                              style={{
                                width: `${Math.min(skill.market_demand_score, 100)}%`,
                                background: `linear-gradient(90deg, ${CHART_COLORS.primary}, ${CHART_COLORS.secondary})`
                              }}
                            ></div>
                          </div>
                          <span className="demand-score">{skill.market_demand_score.toFixed(1)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Salary Trends for Selected Skill */}
              {selectedSkill && salaryTrends && (
                <div className="chart-container salary-trends animate-slide-in">
                  <h3>
                    <TrendingUpIcon className="w-5 h-5" />
                    Salary Trend: {salaryTrends.skill_name}
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={salaryTrends.monthly_data || []}>
                      <defs>
                        <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={CHART_COLORS.success} stopOpacity={0.3} />
                          <stop offset="100%" stopColor={CHART_COLORS.success} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="rgba(148, 163, 184, 0.1)"
                      />
                      <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                      <YAxis
                        stroke="#64748b"
                        fontSize={12}
                        tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                      />
                      <Tooltip
                        content={<CustomTooltip />}
                        formatter={(value) => `$${(value || 0).toLocaleString()}`}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="average_salary"
                        stroke={CHART_COLORS.success}
                        fill="url(#areaGradient)"
                        strokeWidth={2}
                        name="Average Salary"
                      />
                      <Line
                        type="monotone"
                        dataKey="median_salary"
                        stroke={CHART_COLORS.warning}
                        strokeWidth={2}
                        dot={{ fill: CHART_COLORS.warning, r: 4 }}
                        name="Median Salary"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {/* Industries Tab */}
          {activeTab === 'industries' && jobStats && (
            <div className="tab-content animate-fade-in">
              <div className="chart-container">
                <h3>
                  <BuildingIcon className="w-5 h-5" />
                  Industry Breakdown
                </h3>
              </div>
              <div className="industries-grid">
                {Object.entries(jobStats.industries || {}).map(([industry, count], idx) => (
                  <div key={industry} className="industry-card" style={{ animationDelay: `${idx * 50}ms` }}>
                    <div className="industry-icon" style={{ background: COLORS[idx % COLORS.length] }}>
                      <BuildingIcon className="w-5 h-5" />
                    </div>
                    <div className="industry-content">
                      <h4>{industry}</h4>
                      <div className="industry-stats">
                        <div className="stat">
                          <span className="value">{count}</span>
                          <span className="label">Postings</span>
                        </div>
                        <div className="stat">
                          <span className="value">{((count / (jobStats.total_postings || 1)) * 100).toFixed(1)}%</span>
                          <span className="label">of Total</span>
                        </div>
                      </div>
                      <div className="industry-bar">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${(count / (jobStats.total_postings || 1)) * 100}%`,
                            background: COLORS[idx % COLORS.length]
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Salaries Tab */}
          {activeTab === 'salaries' && jobStats && (
            <div className="tab-content animate-fade-in">
              <div className="chart-container salary-analytics">
                <h3>
                  <DollarIcon className="w-5 h-5" />
                  Salary Analytics
                </h3>
                <div className="salary-distribution">
                  <div className="distribution-visual">
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart
                        data={[
                          { name: 'Min', value: salaryStats.min || 0 },
                          { name: 'Q1', value: (salaryStats.min || 0) + ((salaryStats.max || 0) - (salaryStats.min || 0)) * 0.25 },
                          { name: 'Median', value: salaryStats.median || 0 },
                          { name: 'Q3', value: (salaryStats.min || 0) + ((salaryStats.max || 0) - (salaryStats.min || 0)) * 0.75 },
                          { name: 'Max', value: salaryStats.max || 0 }
                        ]}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                        <YAxis
                          stroke="#64748b"
                          fontSize={12}
                          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                          {[0, 1, 2, 3, 4].map((index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={index === 2 ? CHART_COLORS.success : COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="salary-metrics">
                    <div className="metric-card">
                      <div className="metric-icon" style={{ background: CHART_COLORS.primary }}>
                        <DollarIcon className="w-5 h-5" />
                      </div>
                      <div className="metric-info">
                        <span className="metric-label">Minimum</span>
                        <span className="metric-value">${(salaryStats.min || 0).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="metric-card highlight">
                      <div className="metric-icon" style={{ background: CHART_COLORS.success }}>
                        <DollarIcon className="w-5 h-5" />
                      </div>
                      <div className="metric-info">
                        <span className="metric-label">Median</span>
                        <span className="metric-value">${(salaryStats.median || 0).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-icon" style={{ background: CHART_COLORS.warning }}>
                        <DollarIcon className="w-5 h-5" />
                      </div>
                      <div className="metric-info">
                        <span className="metric-label">Average</span>
                        <span className="metric-value">${(salaryStats.average || 0).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-icon" style={{ background: CHART_COLORS.secondary }}>
                        <DollarIcon className="w-5 h-5" />
                      </div>
                      <div className="metric-info">
                        <span className="metric-label">Maximum</span>
                        <span className="metric-value">${(salaryStats.max || 0).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
