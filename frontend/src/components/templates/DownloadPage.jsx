/**
 * DownloadPage Component
 * Main page for viewing, editing, and downloading resume/cover letter PDFs
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, FileText, Mail, Download, RefreshCw,
  CheckCircle, AlertCircle, Loader2
} from 'lucide-react';
import config from '../../config';
import ResumeEditor from './ResumeEditor';
import TemplateSelector from './TemplateSelector';
import TemplatePreview from './TemplatePreview';
import DownloadButton from './DownloadButton';
import SEO from '../common/SEO';

const API_URL = config.api.baseURL;

const DownloadPage = ({ token }) => {
  const { analysisId } = useParams();
  const navigate = useNavigate();

  // Data state
  const [analysis, setAnalysis] = useState(null);
  const [structuredResume, setStructuredResume] = useState(null);
  const [templates, setTemplates] = useState({ resume: [], coverLetter: [] });

  // UI state
  const [activeTab, setActiveTab] = useState('resume'); // 'resume' or 'coverLetter'
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [selectedCLTemplate, setSelectedCLTemplate] = useState('professional');

  // Loading states
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch analysis data and templates
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch analysis data with structured resume
      const analysisRes = await fetch(`${API_URL}/analyze/${analysisId}/structured-resume`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!analysisRes.ok) {
        if (analysisRes.status === 404) {
          throw new Error('Analysis not found');
        }
        throw new Error('Failed to load analysis');
      }

      const analysisData = await analysisRes.json();
      setAnalysis(analysisData.data);
      setStructuredResume(analysisData.data.structured_resume);
      setCurrentFormData(analysisData.data.structured_resume);

      if (analysisData.data.selected_resume_template) {
        setSelectedTemplate(analysisData.data.selected_resume_template);
      }
      if (analysisData.data.selected_cover_letter_template) {
        setSelectedCLTemplate(analysisData.data.selected_cover_letter_template);
      }

      // Fetch templates
      const [resumeTemplatesRes, clTemplatesRes] = await Promise.all([
        fetch(`${API_URL}/templates/resume`),
        fetch(`${API_URL}/templates/cover-letter`)
      ]);

      if (resumeTemplatesRes.ok) {
        const resumeData = await resumeTemplatesRes.json();
        setTemplates(prev => ({ ...prev, resume: resumeData.data.templates }));
      }

      if (clTemplatesRes.ok) {
        const clData = await clTemplatesRes.json();
        setTemplates(prev => ({ ...prev, coverLetter: clData.data.templates }));
      }

    } catch (err) {
      setError(err.message || 'Failed to load data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  }, [analysisId, token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Parse resume function wrapped in useCallback for stable reference
  const handleParseResume = useCallback(async () => {
    try {
      setParsing(true);
      setError('');

      const response = await fetch(`${API_URL}/analyze/${analysisId}/parse-resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to parse resume');
      }

      const data = await response.json();
      setStructuredResume(data.data.structured_resume);
      setSuccessMessage('Resume parsed successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (err) {
      setError(err.message || 'Failed to parse resume');
      console.error('Error parsing resume:', err);
    } finally {
      setParsing(false);
    }
  }, [analysisId, token]);

  // Auto-parse resume if optimized resume exists but not yet parsed
  useEffect(() => {
    if (!loading && analysis?.has_optimized_resume && !structuredResume && !parsing) {
      handleParseResume();
    }
  }, [loading, analysis, structuredResume, parsing, handleParseResume]);

  // Track current form data for real-time preview updates
  const [currentFormData, setCurrentFormData] = useState(null);

  // Save edited resume data
  const handleSaveResume = async (updatedData) => {
    try {
      setSaving(true);
      setError('');

      const response = await fetch(`${API_URL}/analyze/${analysisId}/structured-resume`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          structured_resume: updatedData,
          selected_resume_template: selectedTemplate,
          selected_cover_letter_template: selectedCLTemplate
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save changes');
      }

      setStructuredResume(updatedData);
      setCurrentFormData(updatedData);
      setSuccessMessage('Changes saved!');
      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (err) {
      setError(err.message || 'Failed to save changes');
      console.error('Error saving resume:', err);
    } finally {
      setSaving(false);
    }
  };

  // Update current form data for real-time preview
  const handleFormDataChange = (updatedData) => {
    setCurrentFormData(updatedData);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading your documents...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !analysis) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const hasOptimizedResume = analysis?.has_optimized_resume;
  const hasCoverLetter = analysis?.has_cover_letter;

  return (
    <>
      <SEO
        title="Download Documents"
        description="Download your optimized resume and cover letter as professional PDFs"
      />

      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />

        <div className="max-w-6xl mx-auto px-4 py-8 relative z-10">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <button
              onClick={() => navigate(-1)}
              className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white font-display">Download Documents</h1>
              <p className="text-gray-400 text-sm">
                {analysis?.job_title && analysis?.company_name
                  ? `${analysis.job_title} at ${analysis.company_name}`
                  : 'Edit and download your professional documents'}
              </p>
            </div>
          </div>

          {/* Success/Error Messages */}
          {successMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl flex items-center gap-3"
            >
              <CheckCircle className="w-5 h-5 text-green-400" />
              <p className="text-green-400">{successMessage}</p>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400" />
              <p className="text-red-400">{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-red-400 hover:text-red-300"
              >
                Dismiss
              </button>
            </motion.div>
          )}

          {/* Tab Navigation */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setActiveTab('resume')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                activeTab === 'resume'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              <FileText className="w-5 h-5" />
              Resume
            </button>
            <button
              onClick={() => setActiveTab('coverLetter')}
              disabled={!hasCoverLetter}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                activeTab === 'coverLetter'
                  ? 'bg-blue-500 text-white'
                  : hasCoverLetter
                    ? 'text-gray-400 hover:text-white hover:bg-white/10'
                    : 'text-gray-600 cursor-not-allowed'
              }`}
            >
              <Mail className="w-5 h-5" />
              Cover Letter
              {!hasCoverLetter && <span className="text-xs">(Not generated)</span>}
            </button>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Editor / Content */}
            <div className="lg:col-span-2">
              {activeTab === 'resume' ? (
                <>
                  {!hasOptimizedResume ? (
                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-8 text-center">
                      <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-white mb-2">No Optimized Resume</h3>
                      <p className="text-gray-400 mb-6">
                        Generate an optimized resume from your analysis first.
                      </p>
                      <button
                        onClick={() => navigate(`/analyze/${analysisId}`)}
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                      >
                        Go to Analysis
                      </button>
                    </div>
                  ) : !structuredResume ? (
                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-8 text-center">
                      <RefreshCw className={`w-16 h-16 mx-auto mb-4 ${parsing ? 'animate-spin text-blue-500' : 'text-gray-600'}`} />
                      <h3 className="text-xl font-semibold text-white mb-2">Parse Your Resume</h3>
                      <p className="text-gray-400 mb-6">
                        We need to analyze your resume structure to enable template formatting.
                        This uses AI to extract your contact info, experience, education, and skills.
                      </p>
                      <button
                        onClick={handleParseResume}
                        disabled={parsing}
                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2 mx-auto"
                      >
                        {parsing ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Parsing...
                          </>
                        ) : (
                          <>
                            <RefreshCw className="w-5 h-5" />
                            Parse Resume
                          </>
                        )}
                      </button>
                    </div>
                  ) : (
                    <ResumeEditor
                      data={structuredResume}
                      onSave={handleSaveResume}
                      onDataChange={handleFormDataChange}
                      saving={saving}
                    />
                  )}
                </>
              ) : (
                <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Cover Letter Preview</h3>
                  <div className="bg-white/5 rounded-lg p-6 prose prose-invert max-w-none">
                    <p className="text-gray-300 whitespace-pre-wrap">
                      {analysis?.cover_letter || 'No cover letter content available.'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Template Selection & Download */}
            <div className="space-y-6">
              {/* Template Selector */}
              <TemplateSelector
                templates={activeTab === 'resume' ? templates.resume : templates.coverLetter}
                selectedTemplate={activeTab === 'resume' ? selectedTemplate : selectedCLTemplate}
                onSelect={activeTab === 'resume' ? setSelectedTemplate : setSelectedCLTemplate}
                documentType={activeTab}
              />

              {/* Live Preview */}
              <TemplatePreview
                analysisId={analysisId}
                documentType={activeTab === 'resume' ? 'resume' : 'cover_letter'}
                templateId={activeTab === 'resume' ? selectedTemplate : selectedCLTemplate}
                token={token}
                structuredResume={currentFormData || structuredResume}
                disabled={activeTab === 'resume' && !structuredResume}
              />

              {/* Download Section */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Download className="w-5 h-5 text-green-400" />
                  Download PDF
                </h3>

                {activeTab === 'resume' && !structuredResume ? (
                  <p className="text-gray-400 text-sm">
                    Parse your resume first to enable PDF download.
                  </p>
                ) : (
                  <DownloadButton
                    analysisId={analysisId}
                    documentType={activeTab === 'resume' ? 'resume' : 'cover_letter'}
                    templateId={activeTab === 'resume' ? selectedTemplate : selectedCLTemplate}
                    token={token}
                    disabled={activeTab === 'resume' && !structuredResume}
                  />
                )}
              </div>

              {/* Tips */}
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-blue-400 mb-2">Tips</h4>
                <ul className="text-sm text-gray-400 space-y-1">
                  <li>• Review and edit your information before downloading</li>
                  <li>• Classic template has 100% ATS compatibility</li>
                  <li>• Modern template works great for tech roles</li>
                  <li>• PDF text is fully selectable for ATS systems</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DownloadPage;
