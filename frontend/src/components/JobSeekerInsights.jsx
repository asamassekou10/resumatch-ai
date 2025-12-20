import { useState, useEffect } from 'react';
import ApiService, { handleApiError } from '../services/api';
import {
  TrendingUpIcon, TargetIcon, BookOpenIcon, MapPinIcon,
  AlertIcon, LoadingIcon, RefreshIcon,
  ArrowUpIcon, ArrowDownIcon, BriefcaseIcon, FireIcon
} from './Icons';
import RepersonalizeButton from './RepersonalizeButton';
import '../styles/theme.css';
import '../styles/JobSeekerInsights.css';

// Insight Card Component
const InsightCard = ({ icon: Icon, title, value, description, color = 'primary', actionButton = null }) => (
  <div className={`insight-card insight-${color}`}>
    <div className="insight-header">
      <div className={`insight-icon insight-icon-${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <h3>{title}</h3>
    </div>
    <div className="insight-body">
      <div className="insight-value">{value}</div>
      {description && <p className="insight-description">{description}</p>}
      {actionButton && (
        <button className="insight-action-btn">
          {actionButton}
        </button>
      )}
    </div>
  </div>
);

// Skill Row Component
const SkillRow = ({ skill, index, isNewSkill = false, highlight = false }) => (
  <div className={`skill-row ${highlight ? 'highlight' : ''} ${isNewSkill ? 'new-skill' : ''}`}>
    <div className="skill-rank">{index + 1}</div>
    <div className="skill-info">
      <div className="skill-name">{skill.skill_name || skill.skill}</div>
      {skill.category && <div className="skill-category">{skill.category}</div>}
    </div>
    <div className="skill-metrics">
      {(skill.demand_percentage || skill.demand_score) && (
        <div className="metric">
          <span className="metric-label">Demand:</span>
          <span className="metric-value">
            {skill.demand_percentage || skill.demand_score}
            {skill.demand_percentage ? '%' : ''}
          </span>
        </div>
      )}
      {skill.average_salary && (
        <div className="metric">
          <span className="metric-label">Avg Salary:</span>
          <span className="metric-value">${skill.average_salary.toLocaleString()}</span>
        </div>
      )}
      {skill.change_percentage !== undefined && (
        <div className={`metric trend ${skill.change_percentage >= 0 ? 'positive' : 'negative'}`}>
          <span className="metric-label">Change:</span>
          <span className="metric-value">
            {skill.change_percentage >= 0 ? '+' : ''}{skill.change_percentage}%
          </span>
        </div>
      )}
      {skill.priority && (
        <div className={`priority-badge priority-${skill.priority.toLowerCase()}`}>
          {skill.priority}
        </div>
      )}
    </div>
  </div>
);

export default function JobSeekerInsights({ userProfile, onRepersonalize }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboard, setDashboard] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [competitiveness, setCompetitiveness] = useState(null);
  const [salary, setSalary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [locations, setLocations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadAllInsights();
  }, []);

  const loadAllInsights = async () => {
    setLoading(true);
    setError('');
    try {
      // Load all insights in parallel
      const [dashboardData, roadmapData, competitivenessData, salaryData, trendsData, locationsData] = await Promise.all([
        ApiService.getInsightsDashboard().catch(() => null),
        ApiService.getInsightsLearningRoadmap().catch(() => null),
        ApiService.getInsightsCompetitiveness().catch(() => null),
        ApiService.getInsightsSalaryEstimate().catch(() => null),
        ApiService.getInsightsTrendingSkills().catch(() => null),
        ApiService.getInsightsLocation().catch(() => null)
      ]);

      setDashboard(dashboardData);
      setRoadmap(roadmapData);
      setCompetitiveness(competitivenessData);
      setSalary(salaryData);
      setTrends(trendsData);
      setLocations(locationsData);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMsg = handleApiError(err);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const renderDashboardTab = () => (
    <div className="insights-tab dashboard-tab">
      <div className="tab-header">
        <h2>Your Insights Dashboard</h2>
        <button className="refresh-btn" onClick={loadAllInsights} disabled={loading}>
          <RefreshIcon className="w-4 h-4" />
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {dashboard && (
        <div className="dashboard-grid">
          <InsightCard
            icon={TargetIcon}
            title="Your Skills"
            value={dashboard.quick_stats?.your_skills || 0}
            description="Skills extracted from your resume"
            color="primary"
          />
          <InsightCard
            icon={BriefcaseIcon}
            title="Matching Jobs"
            value={dashboard.quick_stats?.matching_jobs || 0}
            description={`of ${dashboard.quick_stats?.total_jobs_in_market || 0} total jobs`}
            color="secondary"
          />
          <InsightCard
            icon={TrendingUpIcon}
            title="Market Coverage"
            value={`${dashboard.competitiveness_score || 0}%`}
            description="Your skills vs market demand"
            color="success"
          />
          <InsightCard
            icon={BookOpenIcon}
            title="Next Skill"
            value={dashboard.top_skill_to_learn?.skill || 'N/A'}
            description={dashboard.top_skill_to_learn ? `${dashboard.top_skill_to_learn.demand} job postings` : 'Upload resume'}
            color="warning"
          />
        </div>
      )}

      {!dashboard && !loading && (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>Upload a resume to see your insights</p>
        </div>
      )}
    </div>
  );

  const renderRoadmapTab = () => (
    <div className="insights-tab roadmap-tab">
      <div className="tab-header">
        <h2>Learning Roadmap</h2>
        <p className="tab-subtitle">Prioritized skills based on real market demand</p>
      </div>

      {roadmap && roadmap.roadmap?.length > 0 ? (
        <div className="roadmap-container">
          <div className="roadmap-stats">
            <div className="stat">
              <div className="stat-label">Market Coverage</div>
              <div className="stat-value">{roadmap.market_coverage}%</div>
              <div className="stat-bar">
                <div className="stat-fill" style={{ width: `${roadmap.market_coverage}%` }}></div>
              </div>
            </div>
          </div>

          <div className="skills-list">
            {roadmap.roadmap.slice(0, 15).map((skill, index) => (
              <SkillRow key={index} skill={skill} index={index} />
            ))}
          </div>

          <div className="roadmap-info">
            <p><strong>Industry Focus:</strong> {roadmap.industry_focus || 'All Industries'}</p>
            <p><strong>Total Market Skills:</strong> {roadmap.market_skills_analyzed}</p>
            <p><strong>Last Updated:</strong> {new Date(roadmap.data_freshness?.generated_at).toLocaleDateString()}</p>
          </div>
        </div>
      ) : loading ? (
        <div className="loading-state">
          <LoadingIcon className="w-8 h-8 animate-spin" />
          <p>Loading roadmap...</p>
        </div>
      ) : (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>Upload a resume to generate your learning roadmap</p>
        </div>
      )}
    </div>
  );

  const renderCompetitivenessTab = () => (
    <div className="insights-tab competitiveness-tab">
      <div className="tab-header">
        <h2>Competitiveness Score</h2>
        <p className="tab-subtitle">How competitive are you in your target market?</p>
      </div>

      {competitiveness && (
        <div className="competitiveness-container">
          <div className="score-display">
            <div className={`score-circle score-${competitiveness.level}`}>
              <div className="score-value">{competitiveness.score}</div>
              <div className="score-label">out of 100</div>
            </div>
            <div className="score-info">
              <div className="score-level">{competitiveness.level_description}</div>
              <div className="score-reach">
                Can reach {competitiveness.job_reach_percentage}% of job postings
              </div>
            </div>
          </div>

          <div className="competitiveness-metrics">
            <div className="metric-box">
              <div className="metric-title">Skills Matched</div>
              <div className="metric-content">
                <div className="metric-number">{competitiveness.matched_skills?.length || 0}</div>
                <p>from {competitiveness.market_skills_total} market skills</p>
              </div>
            </div>
            <div className="metric-box">
              <div className="metric-title">Job Postings</div>
              <div className="metric-content">
                <div className="metric-number">{competitiveness.qualifying_job_postings}</div>
                <p>of {competitiveness.total_job_postings} total</p>
              </div>
            </div>
          </div>

          {competitiveness.matched_skills?.length > 0 && (
            <div className="skills-breakdown">
              <h4>Your Top Matched Skills</h4>
              <div className="skills-list">
                {competitiveness.matched_skills.slice(0, 8).map((skill, index) => (
                  <SkillRow key={index} skill={skill} index={index} highlight={true} />
                ))}
              </div>
            </div>
          )}

          {competitiveness.missing_high_demand?.length > 0 && (
            <div className="skills-breakdown">
              <h4>High-Demand Skills You're Missing</h4>
              <div className="skills-list">
                {competitiveness.missing_high_demand.slice(0, 5).map((skill, index) => (
                  <SkillRow key={index} skill={skill} index={index} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!competitiveness && !loading && (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>Upload a resume to calculate your competitiveness score</p>
        </div>
      )}
    </div>
  );

  const renderSalaryTab = () => (
    <div className="insights-tab salary-tab">
      <div className="tab-header">
        <h2>Salary Estimator</h2>
        <p className="tab-subtitle">Based on your skill combination and real market data</p>
      </div>

      {salary && salary.estimated_range ? (
        <div className="salary-container">
          <div className="salary-display">
            <div className="salary-range">
              <div className="range-item">
                <span className="range-label">Minimum</span>
                <span className="range-value">
                  ${salary.estimated_range.min?.toLocaleString() || 'N/A'}
                </span>
              </div>
              <div className="range-divider"></div>
              <div className="range-item">
                <span className="range-label">Maximum</span>
                <span className="range-value">
                  ${salary.estimated_range.max?.toLocaleString() || 'N/A'}
                </span>
              </div>
            </div>

            {salary.premium_vs_market !== undefined && (
              <div className={`premium-badge ${salary.premium_vs_market >= 0 ? 'positive' : 'negative'}`}>
                {salary.premium_vs_market >= 0 ? '+' : ''}{salary.premium_vs_market}% vs market
              </div>
            )}
          </div>

          {salary.market_average && (
            <div className="market-comparison">
              <h4>Market Average</h4>
              <div className="comparison-range">
                <span>${salary.market_average.min?.toLocaleString()}</span>
                <span>-</span>
                <span>${salary.market_average.max?.toLocaleString()}</span>
              </div>
            </div>
          )}

          {salary.skill_salary_impact?.length > 0 && (
            <div className="skill-impact">
              <h4>Skills Contributing to Your Salary</h4>
              <div className="impact-list">
                {salary.skill_salary_impact.slice(0, 10).map((skill, index) => (
                  <div key={index} className="impact-item">
                    <div className="impact-skill">
                      <div className="impact-name">{skill.skill}</div>
                      <div className="impact-data">{skill.weight}% weight</div>
                    </div>
                    <div className="impact-salary">
                      ${skill.avg_salary_min?.toLocaleString()} - ${skill.avg_salary_max?.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="salary-info">
            <p><strong>Data Points:</strong> {salary.data_quality?.total_data_points || 'N/A'} from job postings</p>
            {salary.filters_applied?.industry && <p><strong>Industry:</strong> {salary.filters_applied.industry}</p>}
            {salary.filters_applied?.location && <p><strong>Location:</strong> {salary.filters_applied.location}</p>}
          </div>
        </div>
      ) : loading ? (
        <div className="loading-state">
          <LoadingIcon className="w-8 h-8 animate-spin" />
          <p>Loading salary data...</p>
        </div>
      ) : (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>Upload a resume to estimate your salary range</p>
        </div>
      )}
    </div>
  );

  const renderTrendsTab = () => (
    <div className="insights-tab trends-tab">
      <div className="tab-header">
        <h2>Trending Skills</h2>
        <p className="tab-subtitle">Growing and declining skills in the last 30 days</p>
      </div>

      {trends ? (
        <div className="trends-container">
          <div className="market-velocity">
            <h4>Market Velocity</h4>
            <div className="velocity-indicator">
              <div className="velocity-value">{trends.market_velocity}%</div>
              <p>{trends.market_velocity_description}</p>
            </div>
          </div>

          {trends.growing_skills?.length > 0 && (
            <div className="trend-section growing">
              <div className="section-header">
                <ArrowUpIcon className="w-5 h-5 trend-icon-up" />
                <h4>Growing Skills</h4>
              </div>
              <div className="skills-list">
                {trends.growing_skills.slice(0, 8).map((skill, index) => (
                  <SkillRow
                    key={index}
                    skill={skill}
                    index={index}
                    highlight={skill.user_has_skill}
                  />
                ))}
              </div>
            </div>
          )}

          {trends.emerging_skills?.length > 0 && (
            <div className="trend-section emerging">
              <div className="section-header">
                <FireIcon className="w-5 h-5 trend-icon-new" />
                <h4>Emerging Skills (New)</h4>
              </div>
              <div className="skills-list">
                {trends.emerging_skills.slice(0, 8).map((skill, index) => (
                  <SkillRow
                    key={index}
                    skill={skill}
                    index={index}
                    isNewSkill={true}
                    highlight={skill.user_has_skill}
                  />
                ))}
              </div>
            </div>
          )}

          {trends.declining_skills?.length > 0 && (
            <div className="trend-section declining">
              <div className="section-header">
                <ArrowDownIcon className="w-5 h-5 trend-icon-down" />
                <h4>Declining Skills</h4>
              </div>
              <div className="skills-list">
                {trends.declining_skills.slice(0, 8).map((skill, index) => (
                  <SkillRow key={index} skill={skill} index={index} />
                ))}
              </div>
            </div>
          )}

          {trends.your_skills_affected && (
            <div className="skills-affected">
              <p>
                <strong>Skills Affecting You:</strong> {trends.your_skills_affected.growing} growing,
                {trends.your_skills_affected.declining} declining
              </p>
            </div>
          )}
        </div>
      ) : loading ? (
        <div className="loading-state">
          <LoadingIcon className="w-8 h-8 animate-spin" />
          <p>Loading trends...</p>
        </div>
      ) : (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>No trend data available yet</p>
        </div>
      )}
    </div>
  );

  const renderLocationsTab = () => (
    <div className="insights-tab locations-tab">
      <div className="tab-header">
        <h2>Location Intelligence</h2>
        <p className="tab-subtitle">Best locations for your skills based on real job data</p>
      </div>

      {locations && locations.top_locations?.length > 0 ? (
        <div className="locations-container">
          <div className="locations-list">
            {locations.top_locations.map((location, index) => (
              <div key={index} className="location-card">
                <div className="location-header">
                  <div className="location-info">
                    <h4 className="location-name">
                      <MapPinIcon className="w-4 h-4" />
                      {location.location}
                    </h4>
                    <div className="location-jobs">{location.job_count} job postings</div>
                  </div>
                  <div className="location-score">
                    <div className="score">{location.opportunity_score}%</div>
                    <div className="score-label">opportunity</div>
                  </div>
                </div>

                <div className="location-metrics">
                  <div className="metric">
                    <span className="metric-label">Avg Salary:</span>
                    <span className="metric-value">
                      ${location.average_salary?.toLocaleString() || 'N/A'}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Unique Roles:</span>
                    <span className="metric-value">{location.unique_roles}</span>
                  </div>
                  {location.salary_vs_average !== undefined && (
                    <div className={`metric ${location.salary_vs_average >= 0 ? 'positive' : 'negative'}`}>
                      <span className="metric-label">vs Average:</span>
                      <span className="metric-value">
                        {location.salary_vs_average >= 0 ? '+' : ''}{location.salary_vs_average}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {locations.remote_opportunities?.length > 0 && (
            <div className="remote-section">
              <h4>Remote Opportunities</h4>
              <div className="remote-list">
                {locations.remote_opportunities.map((loc, index) => (
                  <div key={index} className="remote-item">
                    <span>{loc.location}</span>
                    <span className="job-count">{loc.job_count} jobs</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : loading ? (
        <div className="loading-state">
          <LoadingIcon className="w-8 h-8 animate-spin" />
          <p>Loading location data...</p>
        </div>
      ) : (
        <div className="empty-state">
          <AlertIcon className="w-12 h-12" />
          <p>No location data available yet</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="job-seeker-insights">
      <div className="insights-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Your Job Market Insights</h1>
          <p className="insights-subtitle">
            Data-driven insights to guide your career growth
          </p>
        </div>
        {userProfile?.preferences_completed && onRepersonalize && (
          <RepersonalizeButton onClick={onRepersonalize} />
        )}
      </div>

      {error && (
        <div className="error-banner">
          <AlertIcon className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      <div className="insights-tabs">
        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`tab-btn ${activeTab === 'roadmap' ? 'active' : ''}`}
            onClick={() => setActiveTab('roadmap')}
          >
            Learning Roadmap
          </button>
          <button
            className={`tab-btn ${activeTab === 'competitiveness' ? 'active' : ''}`}
            onClick={() => setActiveTab('competitiveness')}
          >
            Competitiveness
          </button>
          <button
            className={`tab-btn ${activeTab === 'salary' ? 'active' : ''}`}
            onClick={() => setActiveTab('salary')}
          >
            Salary
          </button>
          <button
            className={`tab-btn ${activeTab === 'trends' ? 'active' : ''}`}
            onClick={() => setActiveTab('trends')}
          >
            Trends
          </button>
          <button
            className={`tab-btn ${activeTab === 'locations' ? 'active' : ''}`}
            onClick={() => setActiveTab('locations')}
          >
            Locations
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'dashboard' && renderDashboardTab()}
          {activeTab === 'roadmap' && renderRoadmapTab()}
          {activeTab === 'competitiveness' && renderCompetitivenessTab()}
          {activeTab === 'salary' && renderSalaryTab()}
          {activeTab === 'trends' && renderTrendsTab()}
          {activeTab === 'locations' && renderLocationsTab()}
        </div>
      </div>

      {lastUpdated && (
        <div className="insights-footer">
          <p>Last updated: {lastUpdated.toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}
