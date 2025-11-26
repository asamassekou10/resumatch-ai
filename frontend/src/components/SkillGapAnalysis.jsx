import React, { useState } from 'react';
import API from '../services/api';
import RepersonalizeButton from './RepersonalizeButton';
import '../styles/SkillGap.css';

const skillCategories = {
  'Backend Development': ['Python', 'Java', 'C#', 'Node.js', 'Go', 'Rust'],
  'Frontend Development': ['React', 'Vue', 'Angular', 'TypeScript', 'CSS', 'HTML'],
  'DevOps & Infrastructure': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Jenkins', 'Terraform'],
  'Data Science': ['Machine Learning', 'TensorFlow', 'Pandas', 'SQL', 'Scala', 'Spark'],
  'Cloud & Databases': ['PostgreSQL', 'MongoDB', 'Redis', 'Firebase', 'DynamoDB', 'Azure'],
  'Mobile Development': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'iOS', 'Android']
};

const SkillGapAnalysis = ({ userProfile, onRepersonalize }) => {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [customSkill, setCustomSkill] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [gapScore, setGapScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);

  const handleAddSkill = (skill) => {
    if (!selectedSkills.includes(skill)) {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleAddCustomSkill = () => {
    if (customSkill.trim() && !selectedSkills.includes(customSkill)) {
      setSelectedSkills([...selectedSkills, customSkill]);
      setCustomSkill('');
    }
  };

  const handleRemoveSkill = (skill) => {
    setSelectedSkills(selectedSkills.filter(s => s !== skill));
  };

  const analyzeGap = async () => {
    setLoading(true);
    try {
      const result = await API.getSkillGapAnalysis(selectedSkills, jobTitle);
      const gap = result?.gap_score || 50;
      setGapScore(gap);
    } catch (err) {
      console.error('Error analyzing gap:', err);
    }
    setLoading(false);
  };

  const getGapColor = (score) => {
    if (score < 20) return '#22c55e';
    if (score < 40) return '#3b82f6';
    if (score < 60) return '#eab308';
    if (score < 80) return '#f97316';
    return '#ef4444';
  };

  const getGapLabel = (score) => {
    if (score < 20) return 'Excellent Match';
    if (score < 40) return 'Good Match';
    if (score < 60) return 'Moderate Gap';
    if (score < 80) return 'Significant Gap';
    return 'Large Gap';
  };

  return (
    <div className="skill-gap min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-8">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold mb-2">Skill Gap Analysis</h1>
          <p className="text-slate-400">Compare your skills against market demand</p>
        </div>
        {userProfile?.preferences_completed && onRepersonalize && (
          <RepersonalizeButton onClick={onRepersonalize} />
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Skill Selection */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Your Skills</h2>
          
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Target Job Title (Optional)</label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g., Full Stack Developer"
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Add Custom Skill</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customSkill}
                onChange={(e) => setCustomSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddCustomSkill()}
                placeholder="Enter skill name..."
                className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400"
              />
              <button onClick={handleAddCustomSkill} className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium">
                Add
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {Object.entries(skillCategories).map(([category, skills]) => (
              <div key={category} className="bg-slate-800/50 rounded-lg border border-slate-700">
                <button
                  onClick={() => setExpandedCategory(expandedCategory === category ? null : category)}
                  className="w-full px-4 py-3 font-medium text-left hover:bg-slate-700/50 transition"
                >
                  {category} →
                </button>
                {expandedCategory === category && (
                  <div className="px-4 pb-3 space-y-2">
                    {skills.map(skill => (
                      <button
                        key={skill}
                        onClick={() => handleAddSkill(skill)}
                        className="block w-full text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-600 rounded-lg transition text-sm"
                      >
                        + {skill}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - Analysis Results */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 mb-6">
            <h3 className="text-sm font-medium text-slate-300 mb-4">Selected Skills ({selectedSkills.length})</h3>
            <div className="flex flex-wrap gap-2">
              {selectedSkills.map(skill => (
                <div key={skill} className="px-3 py-1 bg-cyan-500/20 border border-cyan-400 rounded-full text-sm flex items-center gap-2">
                  {skill}
                  <button onClick={() => handleRemoveSkill(skill)} className="text-cyan-400 hover:text-cyan-300">
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          {selectedSkills.length > 0 && (
            <button
              onClick={analyzeGap}
              disabled={loading}
              className="w-full px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-600 text-white rounded-lg font-medium mb-6"
            >
              {loading ? 'Analyzing...' : 'Analyze Gap'}
            </button>
          )}

          {gapScore !== null && (
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
              <div className="text-center">
                <div className="text-6xl font-bold mb-2" style={{ color: getGapColor(gapScore) }}>
                  {gapScore}
                </div>
                <div className="text-xl font-medium mb-4">{getGapLabel(gapScore)}</div>
                <div className="w-full bg-slate-700 rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full transition-all"
                    style={{
                      width: `${gapScore}%`,
                      backgroundColor: getGapColor(gapScore)
                    }}
                  ></div>
                </div>
              </div>
              <div className="mt-6 space-y-2 text-sm text-slate-300">
                <div>Your Skills: {selectedSkills.length}</div>
                <div>Match: {Math.round(100 - gapScore)}%</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillGapAnalysis;
