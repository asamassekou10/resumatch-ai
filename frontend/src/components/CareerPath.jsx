import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Target, TrendingUp, BookOpen, Award, DollarSign,
  Users, Lightbulb, AlertCircle, CheckCircle, Clock,
  Star, FileText, X, Plus, Save, Edit2, Trash2,
  RefreshCw, ChevronRight, ChevronDown, ExternalLink,
  BarChart3, Briefcase, GraduationCap, Network
} from 'lucide-react';
import '../styles/CareerPath.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const CareerPath = ({ industry, userProfile }) => {
  const [paths, setPaths] = useState([]);
  const [selectedPath, setSelectedPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notesText, setNotesText] = useState('');
  const [expandedSections, setExpandedSections] = useState({
    steps: true,
    skills: true,
    resources: false,
    salary: false,
    alternatives: false,
    networking: false,
    milestones: false
  });

  const [generateForm, setGenerateForm] = useState({
    current_role: '',
    target_role: '',
    industry: industry || '',
    years_of_experience: '',
    current_skills: '',
    refresh: false
  });

  const token = localStorage.getItem('token');

  useEffect(() => {
    if (token) {
      fetchCareerPaths();
    }
  }, [token]);

  useEffect(() => {
    if (selectedPath && selectedPath.notes) {
      setNotesText(selectedPath.notes);
    }
  }, [selectedPath]);

  const fetchCareerPaths = async () => {
    try {
      const response = await axios.get(`${API_URL}/career-path/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPaths(response.data.paths || []);
      if (response.data.paths && response.data.paths.length > 0 && !selectedPath) {
        setSelectedPath(response.data.paths[0]);
      }
    } catch (error) {
      console.error('Error fetching career paths:', error);
    }
  };

  const generateCareerPath = async () => {
    setLoading(true);
    try {
      const payload = {
        ...generateForm,
        current_skills: generateForm.current_skills
          ? generateForm.current_skills.split(',').map(s => s.trim()).filter(s => s)
          : [],
        years_of_experience: generateForm.years_of_experience
          ? parseInt(generateForm.years_of_experience)
          : null
      };

      const response = await axios.post(
        `${API_URL}/career-path/generate`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setPaths(prev => [response.data, ...prev]);
      setSelectedPath(response.data);
      setShowGenerateModal(false);
      setGenerateForm({
        current_role: '',
        target_role: '',
        industry: industry || '',
        years_of_experience: '',
        current_skills: '',
        refresh: false
      });
    } catch (error) {
      console.error('Error generating career path:', error);
      alert('Failed to generate career path. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleSave = async (pathId) => {
    const path = paths.find(p => p.id === pathId);
    if (!path) return;

    const endpoint = path.is_saved ? 'unsave' : 'save';
    try {
      const response = await axios.post(
        `${API_URL}/career-path/${pathId}/${endpoint}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setPaths(prev => prev.map(p => p.id === pathId ? response.data.path : p));
      if (selectedPath && selectedPath.id === pathId) {
        setSelectedPath(response.data.path);
      }
    } catch (error) {
      console.error('Error toggling save:', error);
    }
  };

  const deletePath = async (pathId) => {
    if (!window.confirm('Are you sure you want to delete this career path?')) return;

    try {
      await axios.delete(
        `${API_URL}/career-path/${pathId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setPaths(prev => prev.filter(p => p.id !== pathId));
      if (selectedPath && selectedPath.id === pathId) {
        setSelectedPath(paths[0] || null);
      }
    } catch (error) {
      console.error('Error deleting path:', error);
    }
  };

  const saveNotes = async () => {
    if (!selectedPath) return;

    try {
      const response = await axios.put(
        `${API_URL}/career-path/${selectedPath.id}/notes`,
        { notes: notesText },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSelectedPath(response.data.path);
      setPaths(prev => prev.map(p => p.id === selectedPath.id ? response.data.path : p));
      setEditingNotes(false);
    } catch (error) {
      console.error('Error saving notes:', error);
    }
  };

  const updateStepProgress = async (stepKey, completed) => {
    if (!selectedPath) return;

    try {
      const response = await axios.put(
        `${API_URL}/career-path/${selectedPath.id}/progress`,
        {
          step_key: stepKey,
          completed: completed,
          date: new Date().toISOString().split('T')[0]
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSelectedPath(response.data.path);
      setPaths(prev => prev.map(p => p.id === selectedPath.id ? response.data.path : p));
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const getDifficultyColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'beginner-friendly': return '#10b981';
      case 'moderate': return '#f59e0b';
      case 'challenging': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend?.toLowerCase()) {
      case 'growing': return '#10b981';
      case 'stable': return '#3b82f6';
      case 'declining': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="career-path-container">
      {/* Header */}
      <div className="career-path-header">
        <div>
          <h1 className="career-path-title">
            <Target className="icon" />
            Career Path Roadmaps
          </h1>
          <p className="career-path-subtitle">
            AI-powered career progression strategies from current to dream role
          </p>
        </div>
        <button
          className="btn-generate-path"
          onClick={() => setShowGenerateModal(true)}
        >
          <Plus size={20} />
          Generate Career Path
        </button>
      </div>

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowGenerateModal(false)}
          >
            <motion.div
              className="modal-content"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              onTouchStart={(e) => e.stopPropagation()}
              onTouchEnd={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>Generate Career Roadmap</h2>
                <button
                  className="modal-close"
                  onClick={() => setShowGenerateModal(false)}
                >
                  <X size={24} />
                </button>
              </div>

              <div className="modal-body">
                <div className="form-group">
                  <label>Current Role *</label>
                  <input
                    type="text"
                    value={generateForm.current_role}
                    onChange={(e) => setGenerateForm({ ...generateForm, current_role: e.target.value })}
                    placeholder="e.g., Software Engineer"
                  />
                </div>

                <div className="form-group">
                  <label>Target Role *</label>
                  <input
                    type="text"
                    value={generateForm.target_role}
                    onChange={(e) => setGenerateForm({ ...generateForm, target_role: e.target.value })}
                    placeholder="e.g., Engineering Manager"
                  />
                </div>

                <div className="form-group">
                  <label>Industry</label>
                  <input
                    type="text"
                    value={generateForm.industry}
                    onChange={(e) => setGenerateForm({ ...generateForm, industry: e.target.value })}
                    placeholder="e.g., Technology"
                  />
                </div>

                <div className="form-group">
                  <label>Years of Experience</label>
                  <input
                    type="number"
                    value={generateForm.years_of_experience}
                    onChange={(e) => setGenerateForm({ ...generateForm, years_of_experience: e.target.value })}
                    placeholder="e.g., 5"
                    min="0"
                  />
                </div>

                <div className="form-group">
                  <label>Current Skills (comma-separated)</label>
                  <textarea
                    value={generateForm.current_skills}
                    onChange={(e) => setGenerateForm({ ...generateForm, current_skills: e.target.value })}
                    placeholder="e.g., Python, Leadership, Agile"
                    rows="3"
                  />
                </div>

                <div className="form-checkbox">
                  <input
                    type="checkbox"
                    id="refresh"
                    checked={generateForm.refresh}
                    onChange={(e) => setGenerateForm({ ...generateForm, refresh: e.target.checked })}
                  />
                  <label htmlFor="refresh">Force refresh (ignore cache)</label>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  className="btn-secondary"
                  onClick={() => setShowGenerateModal(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  className="btn-primary"
                  onClick={generateCareerPath}
                  disabled={loading || !generateForm.current_role || !generateForm.target_role}
                >
                  {loading ? (
                    <>
                      <RefreshCw className="spin" size={18} />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Target size={18} />
                      Generate Roadmap
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Layout */}
      <div className="path-layout">
        {/* Sidebar */}
        <div className="path-sidebar">
          <h3 className="sidebar-title">Your Career Paths</h3>
          {paths.length === 0 ? (
            <div className="empty-state">
              <Target size={48} />
              <p>No career paths yet</p>
              <p className="empty-subtitle">Generate your first roadmap</p>
            </div>
          ) : (
            <div className="paths-list">
              {paths.map((path) => (
                <motion.div
                  key={path.id}
                  className={`path-item ${selectedPath?.id === path.id ? 'active' : ''}`}
                  onClick={() => setSelectedPath(path)}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="path-item-header">
                    <div className="path-transition">
                      <div className="path-role current">{path.current_role}</div>
                      <ChevronRight size={16} className="arrow" />
                      <div className="path-role target">{path.target_role}</div>
                    </div>
                    <div className="path-item-actions">
                      <button
                        className="icon-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSave(path.id);
                        }}
                      >
                        <Star
                          size={18}
                          fill={path.is_saved ? '#fbbf24' : 'none'}
                          color={path.is_saved ? '#fbbf24' : '#94a3b8'}
                        />
                      </button>
                      <button
                        className="icon-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          deletePath(path.id);
                        }}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                  <div className="path-item-meta">
                    <span className="meta-item">
                      <Clock size={14} />
                      {path.estimated_duration}
                    </span>
                    {path.completion_percentage > 0 && (
                      <span className="meta-item progress">
                        {Math.round(path.completion_percentage)}% Complete
                      </span>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Main Content */}
        {selectedPath ? (
          <div className="path-content">
            {/* Overview Card */}
            <motion.div
              className="path-overview-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="overview-header">
                <div>
                  <h2 className="path-transition-title">
                    {selectedPath.current_role}
                    <ChevronRight className="arrow-icon" />
                    {selectedPath.target_role}
                  </h2>
                  {selectedPath.industry && (
                    <span className="industry-tag">{selectedPath.industry}</span>
                  )}
                </div>
                <div className="overview-badges">
                  <span
                    className="difficulty-badge"
                    style={{ backgroundColor: getDifficultyColor(selectedPath.difficulty_level) }}
                  >
                    {selectedPath.difficulty_level || 'Moderate'}
                  </span>
                  {selectedPath.demand_trend && (
                    <span
                      className="trend-badge"
                      style={{ backgroundColor: getTrendColor(selectedPath.demand_trend) }}
                    >
                      <TrendingUp size={14} />
                      {selectedPath.demand_trend}
                    </span>
                  )}
                </div>
              </div>

              {selectedPath.ai_recommendations && (
                <div className="ai-recommendations">
                  <Lightbulb className="icon" />
                  <div>
                    <h4>AI Recommendations</h4>
                    <p>{selectedPath.ai_recommendations}</p>
                  </div>
                </div>
              )}

              {selectedPath.path_summary && (
                <div className="path-summary">
                  <p>{selectedPath.path_summary}</p>
                </div>
              )}

              {selectedPath.completion_percentage > 0 && (
                <div className="completion-bar">
                  <div className="completion-label">
                    <span>Progress</span>
                    <span>{Math.round(selectedPath.completion_percentage)}%</span>
                  </div>
                  <div className="progress-track">
                    <motion.div
                      className="progress-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${selectedPath.completion_percentage}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              )}
            </motion.div>

            {/* Career Steps */}
            <Section
              title="Career Roadmap"
              icon={<Target />}
              expanded={expandedSections.steps}
              onToggle={() => toggleSection('steps')}
            >
              {selectedPath.career_steps && selectedPath.career_steps.length > 0 ? (
                <div className="career-steps">
                  {selectedPath.career_steps.map((step, index) => {
                    const stepKey = `step_${step.step_number}`;
                    const progress = selectedPath.progress_tracking?.[stepKey];
                    const isCompleted = progress?.completed || false;

                    return (
                      <motion.div
                        key={index}
                        className={`career-step ${isCompleted ? 'completed' : ''}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <div className="step-header">
                          <div className="step-number">{step.step_number}</div>
                          <div className="step-main">
                            <div className="step-title-row">
                              <h4>{step.title}</h4>
                              <button
                                className={`checkbox-btn ${isCompleted ? 'checked' : ''}`}
                                onClick={() => updateStepProgress(stepKey, !isCompleted)}
                              >
                                {isCompleted && <CheckCircle size={20} />}
                              </button>
                            </div>
                            <span className="step-duration">
                              <Clock size={14} />
                              {step.duration}
                            </span>
                          </div>
                        </div>
                        <p className="step-description">{step.description}</p>

                        {step.skills_to_acquire && step.skills_to_acquire.length > 0 && (
                          <div className="step-skills">
                            <h5>Skills to Acquire:</h5>
                            <div className="skills-tags">
                              {step.skills_to_acquire.map((skill, i) => (
                                <span key={i} className="skill-tag">{skill}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {step.key_actions && step.key_actions.length > 0 && (
                          <div className="step-actions">
                            <h5>Key Actions:</h5>
                            <ul>
                              {step.key_actions.map((action, i) => (
                                <li key={i}>{action}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {step.success_metrics && (
                          <div className="step-metrics">
                            <BarChart3 size={16} />
                            <span>{step.success_metrics}</span>
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <p className="empty-message">No career steps available</p>
              )}
            </Section>

            {/* Skills Gap Analysis */}
            <Section
              title="Skills Gap Analysis"
              icon={<GraduationCap />}
              expanded={expandedSections.skills}
              onToggle={() => toggleSection('skills')}
            >
              <div className="skills-grid">
                {selectedPath.current_skills && selectedPath.current_skills.length > 0 && (
                  <div className="skills-section">
                    <h4>Current Skills</h4>
                    <div className="skills-tags">
                      {selectedPath.current_skills.map((skill, i) => (
                        <span key={i} className="skill-tag current">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedPath.transferable_skills && selectedPath.transferable_skills.length > 0 && (
                  <div className="skills-section">
                    <h4>Transferable Skills</h4>
                    <div className="skills-tags">
                      {selectedPath.transferable_skills.map((skill, i) => (
                        <span key={i} className="skill-tag transferable">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedPath.skills_gap && selectedPath.skills_gap.length > 0 && (
                  <div className="skills-section full-width">
                    <h4>Skills to Acquire</h4>
                    <div className="skills-gap-list">
                      {selectedPath.skills_gap.map((item, i) => (
                        <div key={i} className="gap-item">
                          <div className="gap-header">
                            <span className="gap-skill">{item.skill}</span>
                            <span className={`gap-importance ${item.importance?.toLowerCase()}`}>
                              {item.importance}
                            </span>
                          </div>
                          <p className="gap-how">{item.how_to_acquire}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Section>

            {/* Learning Resources */}
            <Section
              title="Learning Resources"
              icon={<BookOpen />}
              expanded={expandedSections.resources}
              onToggle={() => toggleSection('resources')}
            >
              {selectedPath.learning_resources && selectedPath.learning_resources.length > 0 ? (
                <div className="resources-list">
                  {selectedPath.learning_resources.map((resource, i) => (
                    <div key={i} className="resource-item">
                      <div className="resource-header">
                        <span className="resource-type">{resource.type}</span>
                        <span className={`resource-priority ${resource.priority?.toLowerCase()}`}>
                          {resource.priority}
                        </span>
                      </div>
                      <h4>{resource.title}</h4>
                      {resource.provider && <p className="resource-provider">by {resource.provider}</p>}
                      <p className="resource-description">{resource.description}</p>
                      <div className="resource-footer">
                        {resource.cost && <span className="resource-cost">{resource.cost}</span>}
                        {resource.url && (
                          <a
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="resource-link"
                          >
                            View Resource
                            <ExternalLink size={14} />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-message">No learning resources available</p>
              )}

              {selectedPath.certifications && selectedPath.certifications.length > 0 && (
                <div className="certifications-section">
                  <h4>
                    <Award size={18} />
                    Recommended Certifications
                  </h4>
                  <div className="certifications-list">
                    {selectedPath.certifications.map((cert, i) => (
                      <div key={i} className="cert-item">
                        <div className="cert-header">
                          <h5>{cert.name}</h5>
                          <span className={`cert-priority ${cert.priority?.toLowerCase()}`}>
                            {cert.priority}
                          </span>
                        </div>
                        <p className="cert-provider">{cert.provider}</p>
                        <p className="cert-relevance">{cert.relevance}</p>
                        <div className="cert-footer">
                          {cert.cost && <span>{cert.cost}</span>}
                          {cert.duration && <span>{cert.duration}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Section>

            {/* Salary Expectations */}
            {selectedPath.salary_expectations && selectedPath.salary_expectations.length > 0 && (
              <Section
                title="Salary Progression"
                icon={<DollarSign />}
                expanded={expandedSections.salary}
                onToggle={() => toggleSection('salary')}
              >
                <div className="salary-list">
                  {selectedPath.salary_expectations.map((salary, i) => (
                    <div key={i} className="salary-item">
                      <h4>{salary.role}</h4>
                      <div className="salary-range">
                        <span className="salary-min">${salary.min_salary?.toLocaleString()}</span>
                        <div className="salary-bar">
                          <div className="median-marker" />
                        </div>
                        <span className="salary-max">${salary.max_salary?.toLocaleString()}</span>
                      </div>
                      <p className="salary-median">
                        Median: ${salary.median_salary?.toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Alternative Paths */}
            {selectedPath.alternative_paths && selectedPath.alternative_paths.length > 0 && (
              <Section
                title="Alternative Paths"
                icon={<Network />}
                expanded={expandedSections.alternatives}
                onToggle={() => toggleSection('alternatives')}
              >
                <div className="alternatives-list">
                  {selectedPath.alternative_paths.map((alt, i) => (
                    <div key={i} className="alternative-item">
                      <h4>{alt.path_name}</h4>
                      <p className="alt-duration">
                        <Clock size={14} />
                        {alt.duration}
                      </p>
                      <p className="alt-description">{alt.description}</p>
                      {alt.steps_summary && (
                        <p className="alt-steps">{alt.steps_summary}</p>
                      )}
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Networking & Mentorship */}
            {(selectedPath.networking_tips || selectedPath.mentor_guidance) && (
              <Section
                title="Networking & Mentorship"
                icon={<Users />}
                expanded={expandedSections.networking}
                onToggle={() => toggleSection('networking')}
              >
                {selectedPath.networking_tips && (
                  <div className="networking-section">
                    <h4>Networking Strategy</h4>
                    <p>{selectedPath.networking_tips}</p>
                  </div>
                )}

                {selectedPath.mentor_guidance && (
                  <div className="networking-section">
                    <h4>Finding Mentors</h4>
                    <p>{selectedPath.mentor_guidance}</p>
                  </div>
                )}

                {selectedPath.industry_connections && selectedPath.industry_connections.length > 0 && (
                  <div className="connections-section">
                    <h4>Where to Connect</h4>
                    <div className="connections-list">
                      {selectedPath.industry_connections.map((conn, i) => (
                        <div key={i} className="connection-item">
                          <h5>{conn.platform}</h5>
                          <p className="conn-group">{conn.group_or_event}</p>
                          <p className="conn-why">{conn.why_join}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Section>
            )}

            {/* Key Milestones */}
            {selectedPath.key_milestones && selectedPath.key_milestones.length > 0 && (
              <Section
                title="Key Milestones"
                icon={<Briefcase />}
                expanded={expandedSections.milestones}
                onToggle={() => toggleSection('milestones')}
              >
                <div className="milestones-list">
                  {selectedPath.key_milestones.map((milestone, i) => (
                    <div key={i} className="milestone-item">
                      <div className="milestone-header">
                        <h4>{milestone.milestone}</h4>
                        <span className={`milestone-importance ${milestone.importance?.toLowerCase()}`}>
                          {milestone.importance}
                        </span>
                      </div>
                      <p className="milestone-timeframe">
                        <Clock size={14} />
                        {milestone.timeframe}
                      </p>
                      <p className="milestone-criteria">{milestone.success_criteria}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Risk & Success Factors */}
            {((selectedPath.risk_factors && selectedPath.risk_factors.length > 0) ||
              (selectedPath.success_factors && selectedPath.success_factors.length > 0)) && (
              <div className="factors-grid">
                {selectedPath.risk_factors && selectedPath.risk_factors.length > 0 && (
                  <div className="factors-section risk">
                    <h4>
                      <AlertCircle size={18} />
                      Risk Factors
                    </h4>
                    {selectedPath.risk_factors.map((risk, i) => (
                      <div key={i} className="factor-item">
                        <div className="factor-header">
                          <span className="factor-name">{risk.factor}</span>
                          <span className={`factor-impact ${risk.impact?.toLowerCase()}`}>
                            {risk.impact}
                          </span>
                        </div>
                        <p className="factor-detail">{risk.mitigation}</p>
                      </div>
                    ))}
                  </div>
                )}

                {selectedPath.success_factors && selectedPath.success_factors.length > 0 && (
                  <div className="factors-section success">
                    <h4>
                      <CheckCircle size={18} />
                      Success Factors
                    </h4>
                    {selectedPath.success_factors.map((success, i) => (
                      <div key={i} className="factor-item">
                        <div className="factor-header">
                          <span className="factor-name">{success.factor}</span>
                          <span className={`factor-impact ${success.impact?.toLowerCase()}`}>
                            {success.impact}
                          </span>
                        </div>
                        <p className="factor-detail">{success.how_to_leverage}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Personal Notes */}
            <div className="notes-section">
              <div className="notes-header">
                <h3>
                  <FileText size={20} />
                  Personal Notes
                </h3>
                {!editingNotes ? (
                  <button
                    className="btn-icon"
                    onClick={() => setEditingNotes(true)}
                  >
                    <Edit2 size={18} />
                    Edit
                  </button>
                ) : (
                  <div className="notes-actions">
                    <button
                      className="btn-secondary"
                      onClick={() => {
                        setEditingNotes(false);
                        setNotesText(selectedPath.notes || '');
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      className="btn-primary"
                      onClick={saveNotes}
                    >
                      <Save size={16} />
                      Save
                    </button>
                  </div>
                )}
              </div>

              {editingNotes ? (
                <textarea
                  className="notes-editor"
                  value={notesText}
                  onChange={(e) => setNotesText(e.target.value)}
                  placeholder="Add your career planning notes, goals, and reflections..."
                  rows="6"
                />
              ) : (
                <div className="notes-display">
                  {selectedPath.notes || (
                    <p className="notes-empty">
                      No notes yet. Click "Edit" to add your career planning notes.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="empty-content">
            <Target size={64} />
            <h2>No Career Path Selected</h2>
            <p>Generate a career path or select one from the sidebar</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Collapsible Section Component
const Section = ({ title, icon, expanded, onToggle, children }) => (
  <div className="collapsible-section">
    <button className="section-header" onClick={onToggle}>
      <div className="section-title">
        {icon}
        <h3>{title}</h3>
      </div>
      {expanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
    </button>
    <AnimatePresence>
      {expanded && (
        <motion.div
          className="section-content"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  </div>
);

export default CareerPath;
