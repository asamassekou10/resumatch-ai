import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building, Briefcase, Users, TrendingUp, DollarSign, MapPin, Globe,
  Calendar, Award, Target, Code, Lightbulb, BookOpen, FileText,
  Bookmark, Trash2, Plus, RefreshCw, Sparkles, Edit3, Save, X,
  CheckCircle, AlertCircle, Info, ThumbsUp, ThumbsDown
} from 'lucide-react';
import axios from 'axios';
import '../styles/CompanyIntel.css';

const CompanyIntel = ({ industry, userProfile }) => {
  const [intels, setIntels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIntel, setSelectedIntel] = useState(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notesText, setNotesText] = useState('');

  // Generate modal state
  const [generateForm, setGenerateForm] = useState({
    company: '',
    industry: industry || ''
  });

  useEffect(() => {
    fetchCompanyIntels();
  }, []);

  useEffect(() => {
    setGenerateForm(prev => ({ ...prev, industry: industry || '' }));
  }, [industry]);

  const fetchCompanyIntels = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        'http://localhost:5000/api/company-intel/',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setIntels(response.data.intels || []);

      if (response.data.intels && response.data.intels.length > 0 && !selectedIntel) {
        setSelectedIntel(response.data.intels[0]);
        setNotesText(response.data.intels[0].notes || '');
      }
    } catch (error) {
      console.error('Error fetching company intels:', error);
      if (error.response?.status === 403) {
        setError('Active subscription required to access company intelligence');
      } else {
        setError('Failed to load company intelligence. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const generateCompanyIntel = async () => {
    if (!generateForm.company.trim()) {
      alert('Please enter a company name');
      return;
    }

    setGenerating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:5000/api/company-intel/generate',
        generateForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setIntels(prev => [response.data, ...prev]);
      setSelectedIntel(response.data);
      setNotesText(response.data.notes || '');
      setShowGenerateModal(false);
      setGenerateForm({ company: '', industry: industry || '' });
    } catch (error) {
      console.error('Error generating company intel:', error);
      alert(error.response?.data?.error || 'Failed to generate company intelligence');
    } finally {
      setGenerating(false);
    }
  };

  const saveIntel = async (intelId) => {
    try {
      const token = localStorage.getItem('token');
      const intel = intels.find(i => i.id === intelId);

      if (intel.is_saved) {
        await axios.post(
          `http://localhost:5000/api/company-intel/${intelId}/unsave`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        await axios.post(
          `http://localhost:5000/api/company-intel/${intelId}/save`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      setIntels(intels.map(i => i.id === intelId ? { ...i, is_saved: !i.is_saved } : i));
      if (selectedIntel?.id === intelId) {
        setSelectedIntel({ ...selectedIntel, is_saved: !selectedIntel.is_saved });
      }
    } catch (error) {
      console.error('Error saving intel:', error);
    }
  };

  const deleteIntel = async (intelId) => {
    if (!window.confirm('Are you sure you want to delete this company intelligence?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `http://localhost:5000/api/company-intel/${intelId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setIntels(intels.filter(i => i.id !== intelId));
      if (selectedIntel?.id === intelId) {
        setSelectedIntel(intels.find(i => i.id !== intelId) || null);
      }
    } catch (error) {
      console.error('Error deleting intel:', error);
    }
  };

  const saveNotes = async () => {
    if (!selectedIntel) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:5000/api/company-intel/${selectedIntel.id}/notes`,
        { notes: notesText },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setIntels(intels.map(i => i.id === selectedIntel.id ? response.data.intel : i));
      setSelectedIntel(response.data.intel);
      setEditingNotes(false);
    } catch (error) {
      console.error('Error saving notes:', error);
    }
  };

  if (loading && intels.length === 0) {
    return (
      <div className="company-intel-loading">
        <div className="spinner-large"></div>
        <p>Loading company intelligence...</p>
        <p className="loading-subtext">Gathering insights</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="company-intel-error">
        <div className="error-icon">⚠️</div>
        <h3>Unable to Load Company Intelligence</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => fetchCompanyIntels()}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="company-intel-container">
      {/* Header */}
      <div className="company-intel-header">
        <div className="header-left">
          <h2>Company Intelligence Hub</h2>
          <p className="subtitle">
            {intels.length > 0
              ? `${intels.length} ${intels.length === 1 ? 'company' : 'companies'} researched`
              : 'No companies researched yet'}
          </p>
        </div>
        <div className="header-right">
          <button
            className="btn-primary btn-generate"
            onClick={() => setShowGenerateModal(true)}
          >
            <Plus className="w-4 h-4" />
            Research Company
          </button>
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
            <motion.div
              className="modal-content"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3>
                <Sparkles className="w-5 h-5" />
                Research Company
              </h3>
              <p className="modal-description">
                Get AI-powered intelligence for any company
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
                <button
                  className="btn-primary"
                  onClick={generateCompanyIntel}
                  disabled={generating || !generateForm.company.trim()}
                >
                  {generating ? (
                    <>
                      <RefreshCw className="w-4 h-4 spinning" />
                      Researching...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Intelligence
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      {intels.length === 0 ? (
        <div className="empty-state">
          <Building className="w-20 h-20 text-slate-400" />
          <h3>No Company Research Yet</h3>
          <p>Generate AI-powered intelligence for any company you're interested in</p>
          <button className="btn-primary" onClick={() => setShowGenerateModal(true)}>
            <Plus className="w-4 h-4" />
            Research Your First Company
          </button>
        </div>
      ) : (
        <div className="intel-layout">
          {/* Sidebar */}
          <div className="intel-sidebar">
            <h3>Your Research</h3>
            <div className="company-list">
              {intels.map((intel) => (
                <motion.div
                  key={intel.id}
                  className={`company-item ${selectedIntel?.id === intel.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedIntel(intel);
                    setNotesText(intel.notes || '');
                    setEditingNotes(false);
                  }}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="company-item-header">
                    <Building className="w-5 h-5" />
                    <h4>{intel.company}</h4>
                    {intel.is_saved && (
                      <Bookmark className="w-4 h-4 saved-icon" fill="currentColor" />
                    )}
                  </div>
                  {intel.industry && (
                    <p className="industry">{intel.industry}</p>
                  )}
                  <div className="company-item-footer">
                    <span className="research-date">
                      {new Date(intel.created_at).toLocaleDateString()}
                    </span>
                    {intel.has_notes && (
                      <FileText className="w-3 h-3 text-cyan-400" />
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Main Intelligence View */}
          {selectedIntel && (
            <div className="intel-main">
              {/* Intel Header */}
              <div className="intel-header">
                <div className="intel-title-section">
                  <h2>{selectedIntel.company}</h2>
                  <div className="intel-meta">
                    {selectedIntel.industry && (
                      <div className="meta-item">
                        <Briefcase className="w-4 h-4" />
                        <span>{selectedIntel.industry}</span>
                      </div>
                    )}
                    {selectedIntel.headquarters && (
                      <div className="meta-item">
                        <MapPin className="w-4 h-4" />
                        <span>{selectedIntel.headquarters}</span>
                      </div>
                    )}
                    {selectedIntel.website && (
                      <div className="meta-item">
                        <Globe className="w-4 h-4" />
                        <a href={selectedIntel.website} target="_blank" rel="noopener noreferrer">
                          Website
                        </a>
                      </div>
                    )}
                  </div>
                </div>
                <div className="intel-actions">
                  <button
                    className={`btn-icon ${selectedIntel.is_saved ? 'saved' : ''}`}
                    onClick={() => saveIntel(selectedIntel.id)}
                  >
                    <Bookmark
                      className="w-5 h-5"
                      fill={selectedIntel.is_saved ? 'currentColor' : 'none'}
                    />
                  </button>
                  <button
                    className="btn-icon btn-delete"
                    onClick={() => deleteIntel(selectedIntel.id)}
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* AI Summary */}
              {selectedIntel.ai_summary && (
                <div className="ai-summary-card">
                  <div className="summary-header">
                    <Sparkles className="w-5 h-5" />
                    <h3>AI Executive Summary</h3>
                  </div>
                  <p>{selectedIntel.ai_summary}</p>
                </div>
              )}

              {/* Company Overview */}
              {selectedIntel.overview && (
                <div className="intel-section">
                  <div className="section-header">
                    <Info className="w-5 h-5" />
                    <h3>Company Overview</h3>
                  </div>
                  <div className="section-content">
                    <p>{selectedIntel.overview}</p>
                    {(selectedIntel.founded_year || selectedIntel.company_size) && (
                      <div className="overview-stats">
                        {selectedIntel.founded_year && (
                          <div className="stat">
                            <Calendar className="w-4 h-4" />
                            <span>Founded: {selectedIntel.founded_year}</span>
                          </div>
                        )}
                        {selectedIntel.company_size && (
                          <div className="stat">
                            <Users className="w-4 h-4" />
                            <span>{selectedIntel.company_size} employees</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Products & Services */}
              {selectedIntel.products_services && selectedIntel.products_services.length > 0 && (
                <div className="intel-section">
                  <div className="section-header">
                    <Target className="w-5 h-5" />
                    <h3>Products & Services</h3>
                  </div>
                  <div className="section-content">
                    <div className="products-grid">
                      {selectedIntel.products_services.map((product, index) => (
                        <div key={index} className="product-card">
                          <h4>{product.name}</h4>
                          <p>{product.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Culture & Values */}
              {(selectedIntel.company_culture || selectedIntel.core_values) && (
                <div className="intel-section">
                  <div className="section-header">
                    <Users className="w-5 h-5" />
                    <h3>Culture & Values</h3>
                  </div>
                  <div className="section-content">
                    {selectedIntel.company_culture && (
                      <p className="culture-text">{selectedIntel.company_culture}</p>
                    )}
                    {selectedIntel.core_values && selectedIntel.core_values.length > 0 && (
                      <div className="values-list">
                        <h4>Core Values:</h4>
                        <div className="values-tags">
                          {selectedIntel.core_values.map((value, index) => (
                            <span key={index} className="value-tag">{value}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Financial & Growth */}
              {(selectedIntel.financial_health || selectedIntel.growth_metrics) && (
                <div className="intel-section">
                  <div className="section-header">
                    <TrendingUp className="w-5 h-5" />
                    <h3>Financial Health & Growth</h3>
                  </div>
                  <div className="section-content">
                    <div className="metrics-grid">
                      {selectedIntel.financial_health && (
                        <div className="metric-group">
                          <h4>Financial Health</h4>
                          {Object.entries(selectedIntel.financial_health).map(([key, value]) => (
                            value && (
                              <div key={key} className="metric-item">
                                <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                                <span className="metric-value">{value}</span>
                              </div>
                            )
                          ))}
                        </div>
                      )}
                      {selectedIntel.growth_metrics && (
                        <div className="metric-group">
                          <h4>Growth Metrics</h4>
                          {Object.entries(selectedIntel.growth_metrics).map(([key, value]) => (
                            value && (
                              <div key={key} className="metric-item">
                                <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                                <span className="metric-value">{value}</span>
                              </div>
                            )
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Pros & Cons */}
              {selectedIntel.pros_cons && (
                <div className="intel-section">
                  <div className="section-header">
                    <Award className="w-5 h-5" />
                    <h3>Pros & Cons</h3>
                  </div>
                  <div className="section-content">
                    <div className="pros-cons-grid">
                      {selectedIntel.pros_cons.pros && selectedIntel.pros_cons.pros.length > 0 && (
                        <div className="pros-section">
                          <h4 className="pros-title">
                            <ThumbsUp className="w-4 h-4" />
                            Pros
                          </h4>
                          <ul>
                            {selectedIntel.pros_cons.pros.map((pro, index) => (
                              <li key={index}>
                                <CheckCircle className="w-4 h-4" />
                                {pro}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedIntel.pros_cons.cons && selectedIntel.pros_cons.cons.length > 0 && (
                        <div className="cons-section">
                          <h4 className="cons-title">
                            <ThumbsDown className="w-4 h-4" />
                            Cons
                          </h4>
                          <ul>
                            {selectedIntel.pros_cons.cons.map((con, index) => (
                              <li key={index}>
                                <AlertCircle className="w-4 h-4" />
                                {con}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tech Stack */}
              {selectedIntel.tech_stack && (
                <div className="intel-section">
                  <div className="section-header">
                    <Code className="w-5 h-5" />
                    <h3>Technology Stack</h3>
                  </div>
                  <div className="section-content">
                    <div className="tech-stack-grid">
                      {selectedIntel.tech_stack.languages && selectedIntel.tech_stack.languages.length > 0 && (
                        <div className="tech-category">
                          <h4>Languages</h4>
                          <div className="tech-tags">
                            {selectedIntel.tech_stack.languages.map((tech, index) => (
                              <span key={index} className="tech-tag">{tech}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedIntel.tech_stack.frameworks && selectedIntel.tech_stack.frameworks.length > 0 && (
                        <div className="tech-category">
                          <h4>Frameworks</h4>
                          <div className="tech-tags">
                            {selectedIntel.tech_stack.frameworks.map((tech, index) => (
                              <span key={index} className="tech-tag">{tech}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedIntel.tech_stack.tools && selectedIntel.tech_stack.tools.length > 0 && (
                        <div className="tech-category">
                          <h4>Tools</h4>
                          <div className="tech-tags">
                            {selectedIntel.tech_stack.tools.map((tech, index) => (
                              <span key={index} className="tech-tag">{tech}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Key Insights */}
              {selectedIntel.key_insights && selectedIntel.key_insights.length > 0 && (
                <div className="intel-section">
                  <div className="section-header">
                    <Lightbulb className="w-5 h-5" />
                    <h3>Key Insights</h3>
                  </div>
                  <div className="section-content">
                    <ul className="insights-list">
                      {selectedIntel.key_insights.map((insight, index) => (
                        <li key={index}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selectedIntel.recommendations && selectedIntel.recommendations.length > 0 && (
                <div className="intel-section">
                  <div className="section-header">
                    <Target className="w-5 h-5" />
                    <h3>Recommendations</h3>
                  </div>
                  <div className="section-content">
                    <ul className="recommendations-list">
                      {selectedIntel.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Personal Notes */}
              <div className="intel-section">
                <div className="section-header">
                  <FileText className="w-5 h-5" />
                  <h3>Personal Notes</h3>
                  {!editingNotes && (
                    <button
                      className="btn-edit"
                      onClick={() => setEditingNotes(true)}
                    >
                      <Edit3 className="w-4 h-4" />
                      Edit
                    </button>
                  )}
                </div>
                <div className="section-content">
                  {editingNotes ? (
                    <div className="notes-editor">
                      <textarea
                        value={notesText}
                        onChange={(e) => setNotesText(e.target.value)}
                        placeholder="Add your personal notes about this company..."
                        rows={6}
                      />
                      <div className="notes-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => {
                            setEditingNotes(false);
                            setNotesText(selectedIntel.notes || '');
                          }}
                        >
                          <X className="w-4 h-4" />
                          Cancel
                        </button>
                        <button
                          className="btn-primary"
                          onClick={saveNotes}
                        >
                          <Save className="w-4 h-4" />
                          Save Notes
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="notes-display">
                      {selectedIntel.notes ? (
                        <p>{selectedIntel.notes}</p>
                      ) : (
                        <p className="no-notes">No notes yet. Click Edit to add your thoughts.</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompanyIntel;
