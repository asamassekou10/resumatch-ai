import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building, Briefcase, CheckCircle, Bookmark, Trash2, Plus, RefreshCw,
  Target, Users, Clock, BookOpen, Lightbulb, ChevronDown, ChevronUp,
  Sparkles, TrendingUp, Award
} from 'lucide-react';
import axios from 'axios';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';
import '../styles/InterviewPrep.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const InterviewPrep = ({ industry, userProfile }) => {
  const [preps, setPreps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPrep, setSelectedPrep] = useState(null);
  const [expandedQuestions, setExpandedQuestions] = useState(new Set());
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Generate modal state
  const [generateForm, setGenerateForm] = useState({
    company: '',
    job_title: '',
    industry: industry || ''
  });

  useEffect(() => {
    fetchInterviewPreps();
  }, []);

  useEffect(() => {
    // Update industry in generate form when prop changes
    setGenerateForm(prev => ({ ...prev, industry: industry || '' }));
  }, [industry]);

  const fetchInterviewPreps = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/interview-prep/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPreps(response.data.preps || []);

      // Auto-select first prep if available
      if (response.data.preps && response.data.preps.length > 0 && !selectedPrep) {
        setSelectedPrep(response.data.preps[0]);
      }
    } catch (error) {
      console.error('Error fetching interview preps:', error);
      if (error.response?.status === 403) {
        setError('Active subscription required to access interview prep');
      } else {
        setError('Failed to load interview prep. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const generateInterviewPrep = async () => {
    if (!generateForm.company.trim()) {
      alert('Please enter a company name');
      return;
    }

    setGenerating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/interview-prep/generate`,
        generateForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Add new prep to list and select it
      setPreps(prev => [response.data, ...prev]);
      setSelectedPrep(response.data);
      setShowGenerateModal(false);
      setGenerateForm({ company: '', job_title: '', industry: industry || '' });
    } catch (error) {
      console.error('Error generating interview prep:', error);
      alert(error.response?.data?.error || 'Failed to generate interview prep');
    } finally {
      setGenerating(false);
    }
  };

  const savePrep = async (prepId) => {
    try {
      const token = localStorage.getItem('token');
      const prep = preps.find(p => p.id === prepId);

      if (prep.is_saved) {
        await axios.post(
          `${API_URL}/interview-prep/${prepId}/unsave`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        await axios.post(
          `${API_URL}/interview-prep/${prepId}/save`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      // Update local state
      setPreps(preps.map(p =>
        p.id === prepId ? { ...p, is_saved: !p.is_saved } : p
      ));
      if (selectedPrep?.id === prepId) {
        setSelectedPrep({ ...selectedPrep, is_saved: !selectedPrep.is_saved });
      }
    } catch (error) {
      console.error('Error saving prep:', error);
    }
  };

  const deletePrep = async (prepId) => {
    if (!window.confirm('Are you sure you want to delete this interview prep?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${API_URL}/interview-prep/${prepId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Remove from local state
      setPreps(preps.filter(p => p.id !== prepId));
      if (selectedPrep?.id === prepId) {
        setSelectedPrep(preps.find(p => p.id !== prepId) || null);
      }
    } catch (error) {
      console.error('Error deleting prep:', error);
    }
  };

  const markQuestionPracticed = async (prepId, questionIndex) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/interview-prep/${prepId}/practice`,
        { question_index: questionIndex },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update local state with returned prep
      const updatedPrep = response.data.prep;
      setPreps(preps.map(p => p.id === prepId ? updatedPrep : p));
      if (selectedPrep?.id === prepId) {
        setSelectedPrep(updatedPrep);
      }
    } catch (error) {
      console.error('Error marking question practiced:', error);
    }
  };

  const toggleQuestionExpand = (questionIndex) => {
    const newExpanded = new Set(expandedQuestions);
    if (newExpanded.has(questionIndex)) {
      newExpanded.delete(questionIndex);
    } else {
      newExpanded.add(questionIndex);
    }
    setExpandedQuestions(newExpanded);
  };

  const getQuestionTypeIcon = (type) => {
    switch (type) {
      case 'technical':
        return <Target className="w-4 h-4" />;
      case 'behavioral':
        return <Users className="w-4 h-4" />;
      case 'company-specific':
        return <Building className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  const getQuestionTypeColor = (type) => {
    switch (type) {
      case 'technical':
        return '#06b6d4'; // cyan
      case 'behavioral':
        return '#8b5cf6'; // purple
      case 'company-specific':
        return '#10b981'; // green
      default:
        return '#94a3b8'; // gray
    }
  };

  if (loading && preps.length === 0) {
    return (
      <div className="interview-prep-loading">
        <div className="spinner-large"></div>
        <p>Loading interview preparation...</p>
        <p className="loading-subtext">Analyzing your background</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="interview-prep-error">
        <div className="error-icon">⚠️</div>
        <h3>Unable to Load Interview Prep</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => fetchInterviewPreps()}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="interview-prep-container min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="relative z-10">
      {/* Header */}
      <div className="interview-prep-header relative z-10">
        <div className="header-left relative z-10">
          <h2 className="font-display">AI Interview Preparation</h2>
          <p className="subtitle text-gray-400">
            {preps.length > 0
              ? `${preps.length} ${preps.length === 1 ? 'company' : 'companies'} prepared`
              : 'No interview preps yet'}
          </p>
        </div>
        <div className="header-right relative z-10">
          <ShimmerButton
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Generate Prep
          </ShimmerButton>
        </div>
      </div>

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => !generating && setShowGenerateModal(false)}
          >
            <SpotlightCard className="modal-content relative z-50">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="relative z-10"
              >
              <h3>
                <Sparkles className="w-5 h-5" />
                Generate Interview Prep
              </h3>
              <p className="modal-description">
                Get AI-powered interview preparation for any company
              </p>

              <div className="form-group">
                <label>Company Name *</label>
                <input
                  type="text"
                  placeholder="e.g., Google, Amazon, Microsoft"
                  value={generateForm.company}
                  onChange={(e) => setGenerateForm({ ...generateForm, company: e.target.value })}
                  disabled={generating}
                />
              </div>

              <div className="form-group">
                <label>Job Title (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g., Software Engineer, Product Manager"
                  value={generateForm.job_title}
                  onChange={(e) => setGenerateForm({ ...generateForm, job_title: e.target.value })}
                  disabled={generating}
                />
              </div>

              <div className="form-group">
                <label>Industry (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g., Technology, Finance, Healthcare"
                  value={generateForm.industry}
                  onChange={(e) => setGenerateForm({ ...generateForm, industry: e.target.value })}
                  disabled={generating}
                />
              </div>

              <div className="modal-actions">
                <button
                  className="btn-secondary"
                  onClick={() => setShowGenerateModal(false)}
                  disabled={generating}
                >
                  Cancel
                </button>
                <ShimmerButton
                  onClick={generateInterviewPrep}
                  disabled={generating || !generateForm.company.trim()}
                  className="flex items-center gap-2"
                >
                  {generating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Prep
                    </>
                  )}
                </ShimmerButton>
              </div>
              </motion.div>
            </SpotlightCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      {preps.length === 0 ? (
        <SpotlightCard className="empty-state relative z-10">
          <Building className="w-20 h-20 text-gray-400 relative z-10" />
          <h3 className="font-display relative z-10">No Interview Prep Yet</h3>
          <p className="text-gray-400 relative z-10">Generate AI-powered interview preparation for any company</p>
          <ShimmerButton onClick={() => setShowGenerateModal(true)} className="flex items-center gap-2 relative z-10">
            <Plus className="w-4 h-4" />
            Generate Your First Prep
          </ShimmerButton>
        </SpotlightCard>
      ) : (
        <div className="prep-layout relative z-10">
          {/* Sidebar - Company List */}
          <SpotlightCard className="prep-sidebar relative z-10">
            <h3>Your Preps</h3>
            <div className="company-list">
              {preps.map((prep) => (
                <motion.div
                  key={prep.id}
                  className={`company-item ${selectedPrep?.id === prep.id ? 'active' : ''}`}
                  onClick={() => setSelectedPrep(prep)}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="company-item-header">
                    <Building className="w-5 h-5" />
                    <h4>{prep.company}</h4>
                    {prep.is_saved && (
                      <Bookmark className="w-4 h-4 saved-icon" fill="currentColor" />
                    )}
                  </div>
                  {prep.job_title && (
                    <p className="job-title">{prep.job_title}</p>
                  )}
                  <div className="company-item-footer">
                    <span className="question-count">
                      {prep.questions?.length || 0} questions
                    </span>
                    <span className="prep-date">
                      {new Date(prep.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </SpotlightCard>

          {/* Main Content - Prep Details */}
          {selectedPrep && (
            <SpotlightCard className="prep-main relative z-10">
              {/* Prep Header */}
              <div className="prep-details-header">
                <div className="prep-title-section">
                  <h2>{selectedPrep.company}</h2>
                  {selectedPrep.job_title && (
                    <div className="job-info">
                      <Briefcase className="w-4 h-4" />
                      <span>{selectedPrep.job_title}</span>
                    </div>
                  )}
                  {selectedPrep.industry && (
                    <div className="industry-tag">{selectedPrep.industry}</div>
                  )}
                </div>
                <div className="prep-actions">
                  <button
                    className={`btn-icon ${selectedPrep.is_saved ? 'saved' : ''}`}
                    onClick={() => savePrep(selectedPrep.id)}
                    title={selectedPrep.is_saved ? 'Remove from saved' : 'Save for later'}
                  >
                    <Bookmark
                      className="w-5 h-5"
                      fill={selectedPrep.is_saved ? 'currentColor' : 'none'}
                    />
                  </button>
                  <button
                    className="btn-icon btn-delete"
                    onClick={() => deletePrep(selectedPrep.id)}
                    title="Delete prep"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Practice Progress */}
              {selectedPrep.questions && selectedPrep.questions.length > 0 && (
                <div className="practice-progress">
                  <div className="progress-header">
                    <Award className="w-5 h-5" />
                    <span>Practice Progress</span>
                  </div>
                  <div className="progress-stats">
                    <span className="stat">
                      <strong>{selectedPrep.practiced_questions?.length || 0}</strong>
                      {' / '}
                      {selectedPrep.questions.length} questions practiced
                    </span>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${((selectedPrep.practiced_questions?.length || 0) / selectedPrep.questions.length) * 100}%`,
                          background: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)'
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Interview Questions */}
              <div className="prep-section">
                <div className="section-header">
                  <BookOpen className="w-5 h-5" />
                  <h3>Interview Questions</h3>
                  <span className="badge">{selectedPrep.questions?.length || 0} questions</span>
                </div>

                <div className="questions-list">
                  {selectedPrep.questions && selectedPrep.questions.map((question, index) => {
                    const isPracticed = selectedPrep.practiced_questions?.includes(index);
                    const isExpanded = expandedQuestions.has(index);

                    return (
                      <motion.div
                        key={index}
                        className={`question-card ${isPracticed ? 'practiced' : ''}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.03 }}
                      >
                        <div className="question-header" onClick={() => toggleQuestionExpand(index)}>
                          <div className="question-info">
                            <div
                              className="question-type-badge"
                              style={{ background: getQuestionTypeColor(question.type) }}
                            >
                              {getQuestionTypeIcon(question.type)}
                              <span>{question.type || 'General'}</span>
                            </div>
                            <p className="question-text">{question.question}</p>
                          </div>
                          <div className="question-actions">
                            {isPracticed && (
                              <CheckCircle className="w-5 h-5 text-green-500" fill="currentColor" />
                            )}
                            {isExpanded ? (
                              <ChevronUp className="w-5 h-5" />
                            ) : (
                              <ChevronDown className="w-5 h-5" />
                            )}
                          </div>
                        </div>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              className="question-details"
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                            >
                              {question.answer_framework && (
                                <div className="answer-framework">
                                  <h4>
                                    <Target className="w-4 h-4" />
                                    Answer Framework
                                  </h4>
                                  <p>{question.answer_framework}</p>
                                </div>
                              )}

                              {question.tips && (
                                <div className="question-tips">
                                  <h4>
                                    <Lightbulb className="w-4 h-4" />
                                    Tips
                                  </h4>
                                  <p>{question.tips}</p>
                                </div>
                              )}

                              <button
                                className={`btn-practice ${isPracticed ? 'btn-practiced' : 'btn-primary'}`}
                                onClick={() => markQuestionPracticed(selectedPrep.id, index)}
                              >
                                {isPracticed ? (
                                  <>
                                    <CheckCircle className="w-4 h-4" />
                                    Practiced
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle className="w-4 h-4" />
                                    Mark as Practiced
                                  </>
                                )}
                              </button>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Company Culture */}
              {selectedPrep.company_culture && (
                <div className="prep-section">
                  <div className="section-header">
                    <Users className="w-5 h-5" />
                    <h3>Company Culture</h3>
                  </div>
                  <div className="section-content">
                    <p>{selectedPrep.company_culture}</p>
                  </div>
                </div>
              )}

              {/* Interview Process */}
              {selectedPrep.interview_process && (
                <div className="prep-section">
                  <div className="section-header">
                    <Clock className="w-5 h-5" />
                    <h3>Interview Process</h3>
                  </div>
                  <div className="section-content">
                    <div className="process-details">
                      <div className="process-stat">
                        <span className="label">Typical Rounds:</span>
                        <span className="value">{selectedPrep.interview_process.rounds || 'N/A'}</span>
                      </div>
                      <div className="process-stat">
                        <span className="label">Duration:</span>
                        <span className="value">{selectedPrep.interview_process.duration || 'N/A'}</span>
                      </div>
                    </div>
                    {selectedPrep.interview_process.stages && (
                      <div className="process-stages">
                        <h4>Interview Stages:</h4>
                        <ol>
                          {selectedPrep.interview_process.stages.map((stage, index) => (
                            <li key={index}>{stage}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Interview Tips */}
              {selectedPrep.interview_tips && selectedPrep.interview_tips.length > 0 && (
                <div className="prep-section">
                  <div className="section-header">
                    <Lightbulb className="w-5 h-5" />
                    <h3>Interview Tips</h3>
                  </div>
                  <div className="section-content">
                    <ul className="tips-list">
                      {selectedPrep.interview_tips.map((tip, index) => (
                        <li key={index}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Common Topics */}
              {selectedPrep.common_topics && selectedPrep.common_topics.length > 0 && (
                <div className="prep-section">
                  <div className="section-header">
                    <TrendingUp className="w-5 h-5" />
                    <h3>Common Topics</h3>
                  </div>
                  <div className="section-content">
                    <div className="topics-tags">
                      {selectedPrep.common_topics.map((topic, index) => (
                        <span key={index} className="topic-tag">{topic}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </SpotlightCard>
          )}
        </div>
      )}
      </div>
    </div>
  );
};

export default InterviewPrep;
