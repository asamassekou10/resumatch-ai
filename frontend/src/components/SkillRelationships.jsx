import { useState } from 'react';
import ApiService, { handleApiError } from '../services/api';
import { TargetIcon, CheckIcon, LoadingIcon, LayersIcon } from './Icons';
import RepersonalizeButton from './RepersonalizeButton';
import '../styles/SkillRelationships.css';

const POPULAR_SKILLS = ['Python', 'JavaScript', 'React', 'Docker', 'PostgreSQL', 'AWS', 'Kubernetes', 'Django'];

// Link icon component
const LinkIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
);

export default function SkillRelationships({ userProfile, onRepersonalize }) {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSkillToggle = (skill) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    );
  };

  const getRecommendations = async () => {
    if (selectedSkills.length === 0) {
      setError('Please select at least one skill');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await ApiService.getRecommendedSkills(selectedSkills, 10);
      setRecommendations(result.recommendations || []);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="skill-relationships">
      <div className="rel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="header-icon">
            <LinkIcon className="w-8 h-8" />
          </div>
          <div>
            <h1>Skill Relationships & Recommendations</h1>
            <p>Discover which skills complement your current expertise</p>
          </div>
        </div>
        {userProfile?.preferences_completed && onRepersonalize && (
          <RepersonalizeButton onClick={onRepersonalize} />
        )}
      </div>

      <div className="rel-container">
        {/* Input Panel */}
        <div className="input-panel">
          <h3>
            <LayersIcon className="w-5 h-5" />
            Select Your Skills
          </h3>
          <div className="skills-selector">
            {POPULAR_SKILLS.map(skill => (
              <button
                key={skill}
                className={`skill-chip ${selectedSkills.includes(skill) ? 'active' : ''}`}
                onClick={() => handleSkillToggle(skill)}
              >
                {selectedSkills.includes(skill) && <CheckIcon className="w-4 h-4" />}
                {skill}
              </button>
            ))}
          </div>

          {error && <div className="error-alert">{error}</div>}

          <button
            className="btn btn-primary btn-block"
            onClick={getRecommendations}
            disabled={loading || selectedSkills.length === 0}
          >
            {loading ? (
              <>
                <LoadingIcon className="w-4 h-4" />
                <span>Finding Recommendations...</span>
              </>
            ) : (
              <>
                <TargetIcon className="w-4 h-4" />
                <span>Get Recommendations</span>
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="results-panel">
          {recommendations.length > 0 ? (
            <div>
              <h3>
                <TargetIcon className="w-5 h-5" />
                Recommended Skills
              </h3>
              <div className="recommendations-list">
                {recommendations.map((skill, idx) => (
                  <div key={idx} className="recommendation-item">
                    <div className="rank">#{idx + 1}</div>
                    <div className="skill-info">
                      <div className="skill-name">{skill.skill_name}</div>
                      <div className="skill-category">{skill.category}</div>
                    </div>
                    <div className="score-badge">
                      {skill.recommendation_score.toFixed(1)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-message">
              <TargetIcon className="w-12 h-12" />
              <p>Select skills to see complementary recommendations</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
