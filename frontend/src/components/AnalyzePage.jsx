import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUp, ArrowRight, AlertCircle, CheckCircle, Loader, ArrowLeft, Mail, Sparkles, FileText } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';
import ScoreBreakdown from './ScoreBreakdown';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * AnalyzePage Component
 *
 * Resume analysis page for authenticated users.
 * Allows users to upload resume and job description for AI analysis.
 * Can also display analysis results when in viewMode="result".
 */
const AnalyzePage = ({ userProfile, viewMode = 'analyze' }) => {
  const navigate = useNavigate();
  const { id } = useParams();
  const token = localStorage.getItem('token');

  // Analysis mode state
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('Analyzing resume...');
  const [error, setError] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');

  // Result view mode state
  const [analysisData, setAnalysisData] = useState(null);
  const [resultLoading, setResultLoading] = useState(false);

  // AI Features state
  const [aiFeatureLoading, setAiFeatureLoading] = useState(null); // 'feedback', 'optimize', 'cover-letter'
  const [aiFeatureProgress, setAiFeatureProgress] = useState(0);
  const [aiFeatureMessage, setAiFeatureMessage] = useState('');
  const [aiFeedback, setAiFeedback] = useState(null);
  const [optimizedResume, setOptimizedResume] = useState(null);
  const [coverLetter, setCoverLetter] = useState(null);

  // Email state
  const [sendingEmail, setSendingEmail] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const fetchAnalysisResult = useCallback(async () => {
    setResultLoading(true);
    try {
      const response = await fetch(`${API_URL}/analyses/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to load analysis');
      }

      const data = await response.json();
      setAnalysisData(data);
      // Load existing AI content if available
      if (data.ai_feedback) setAiFeedback(data.ai_feedback);
    } catch (err) {
      setError(err.message || 'Failed to load analysis results');
    } finally {
      setResultLoading(false);
    }
  }, [id, token]);

  // Fetch analysis result if in view mode
  useEffect(() => {
    if (viewMode === 'result' && id && token) {
      fetchAnalysisResult();
    }
  }, [viewMode, id, token, fetchAnalysisResult]);

  const handleGenerateFeedback = async () => {
    setAiFeatureLoading('feedback');
    setAiFeatureProgress(0);
    setAiFeatureMessage('Generating AI feedback...');
    setError('');

    // Simulate progress
    const progressInterval = setInterval(() => {
      setAiFeatureProgress((prev) => {
        if (prev < 80) return prev + Math.random() * 20;
        return prev;
      });
    }, 500);

    try {
      const response = await fetch(`${API_URL}/analyze/feedback/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate feedback');
      }

      clearInterval(progressInterval);
      setAiFeatureProgress(100);
      setAiFeedback(data.feedback);

      setTimeout(() => {
        setAiFeatureLoading(null);
        setAiFeatureProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'Failed to generate AI feedback');
      setAiFeatureLoading(null);
    }
  };

  const handleOptimizeResume = async () => {
    setAiFeatureLoading('optimize');
    setAiFeatureProgress(0);
    setAiFeatureMessage('Optimizing resume...');
    setError('');

    const progressInterval = setInterval(() => {
      setAiFeatureProgress((prev) => {
        if (prev < 80) return prev + Math.random() * 20;
        return prev;
      });
    }, 500);

    try {
      const response = await fetch(`${API_URL}/analyze/optimize/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to optimize resume');
      }

      clearInterval(progressInterval);
      setAiFeatureProgress(100);
      setOptimizedResume(data.optimized_resume);

      setTimeout(() => {
        setAiFeatureLoading(null);
        setAiFeatureProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'Failed to optimize resume');
      setAiFeatureLoading(null);
    }
  };

  const handleGenerateCoverLetter = async () => {
    setAiFeatureLoading('cover-letter');
    setAiFeatureProgress(0);
    setAiFeatureMessage('Generating cover letter...');
    setError('');

    const progressInterval = setInterval(() => {
      setAiFeatureProgress((prev) => {
        if (prev < 80) return prev + Math.random() * 20;
        return prev;
      });
    }, 500);

    try {
      const response = await fetch(`${API_URL}/analyze/cover-letter/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate cover letter');
      }

      clearInterval(progressInterval);
      setAiFeatureProgress(100);
      setCoverLetter(data.cover_letter);

      setTimeout(() => {
        setAiFeatureLoading(null);
        setAiFeatureProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'Failed to generate cover letter');
      setAiFeatureLoading(null);
    }
  };

  const handleSendEmail = async () => {
    if (!id) {
      setError('Analysis ID not found');
      return;
    }

    setSendingEmail(true);
    setError('');
    setEmailSent(false);

    try {
      const response = await fetch(`${API_URL}/email-analysis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ analysis_id: parseInt(id) })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send email');
      }

      setEmailSent(true);
      // Show success message for 5 seconds
      setTimeout(() => setEmailSent(false), 5000);
    } catch (err) {
      setError(err.message || 'Failed to send email');
      setEmailSent(false);
    } finally {
      setSendingEmail(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setResumeFile(file);
    }
  };

  const handleAnalyze = async () => {
    if (!resumeFile || !jobDescription) {
      setError('Please upload a resume and enter a job description');
      return;
    }

    // Check credits
    if (userProfile && userProfile.credits <= 0) {
      setError('You have no credits remaining. Please upgrade your plan.');
      return;
    }

    setLoading(true);
    setLoadingProgress(0);
    setLoadingMessage('Analyzing resume...');
    setError('');

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setLoadingProgress((prev) => {
        if (prev < 80) return prev + Math.random() * 30;
        return prev;
      });
    }, 500);

    const messageSequence = [
      'Analyzing resume...',
      'Extracting keywords...',
      'Matching with job description...',
      'Calculating match score...',
      'Generating insights...',
    ];
    let messageIndex = 0;
    const messageInterval = setInterval(() => {
      if (messageIndex < messageSequence.length - 1) {
        messageIndex++;
        setLoadingMessage(messageSequence[messageIndex]);
      }
    }, 1500);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);
      if (jobTitle) formData.append('job_title', jobTitle);
      if (companyName) formData.append('company_name', companyName);

      // Try streaming endpoint first, fallback to regular if not available
      const useStreaming = true; // Enable streaming by default
      
      if (useStreaming) {
        // Use SSE streaming for progressive updates
        const streamResponse = await fetch(`${API_URL}/analyze/stream`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (!streamResponse.ok) {
          const errorData = await streamResponse.json().catch(() => ({}));
          throw new Error(errorData.error || 'Analysis failed');
        }

        // Read SSE stream
        const reader = streamResponse.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;

        clearInterval(progressInterval);
        clearInterval(messageInterval);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.stage) {
                  setLoadingProgress(data.progress || 0);
                  setLoadingMessage(data.message || 'Processing...');
                  
                  if (data.stage === 'score_ready' && data.data) {
                    // Score is ready - could show it in UI
                  } else if (data.stage === 'complete') {
                    finalResult = data.data;
                  } else if (data.stage === 'error') {
                    throw new Error(data.message || data.error || 'Analysis failed');
                  }
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, line);
              }
            }
          }
        }

        if (finalResult && finalResult.analysis_id) {
          setLoadingProgress(100);
          setLoadingMessage('Complete!');
          setTimeout(() => {
            navigate(`/result/${finalResult.analysis_id}`);
          }, 500);
        } else {
          throw new Error('Analysis completed but no result received');
        }
      } else {
        // Fallback to regular endpoint
        const response = await fetch(`${API_URL}/analyze`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        const data = await response.json();

        clearInterval(progressInterval);
        clearInterval(messageInterval);
        setLoadingProgress(100);
        setLoadingMessage('Complete!');

        if (!response.ok) {
          throw new Error(data.error || 'Analysis failed');
        }

        setTimeout(() => {
          navigate(`/result/${data.analysis_id || data.id}`);
        }, 500);
      }
    } catch (err) {
      clearInterval(progressInterval);
      clearInterval(messageInterval);
      setError(err.message || 'Analysis failed. Please try again.');
      setLoading(false);
    }
  };

  // If in result view mode, show results
  if (viewMode === 'result') {
    if (resultLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <Loader className="w-12 h-12 text-cyan-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-300">Loading analysis results...</p>
          </div>
        </div>
      );
    }

    if (!analysisData) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-400 mb-4">{error || 'Analysis not found'}</p>
            <button
              onClick={() => navigate(ROUTES.DASHBOARD)}
              className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      );
    }

    // Display analysis results - matching guest-analyze design
    return (
      <div className="min-h-screen bg-black relative overflow-hidden py-12 px-4">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-5xl mx-auto space-y-6 relative z-10"
        >
          {/* Back Button */}
          <button
            onClick={() => navigate(ROUTES.DASHBOARD)}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </button>

          {/* Results Header */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-2 font-display">AI-Powered Analysis Complete</h1>
            <p className="text-gray-400 text-sm sm:text-base">Comprehensive resume evaluation & ATS optimization</p>
          </motion.div>

          {/* Overall Score Card */}
          <SpotlightCard
            className="rounded-2xl p-4 sm:p-6 md:p-8 shadow-2xl"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative z-10"
            >
            <div className="flex flex-col sm:grid sm:grid-cols-2 gap-6">
              <div className="text-center">
                <div className="text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
                  {analysisData.match_score || 0}%
                </div>
                <p className="text-gray-300 font-semibold text-sm sm:text-base font-display">Overall Match Score</p>
                <p className="text-gray-400 text-xs sm:text-sm mt-2">
                  {analysisData.match_score >= 80 ? 'Excellent Match' :
                   analysisData.match_score >= 60 ? 'Good Match' :
                   analysisData.match_score >= 40 ? 'Fair Match' : 'Needs Improvement'}
                </p>
              </div>
              <div className="flex flex-col justify-center gap-3 text-center sm:text-left">
                <div>
                  <p className="text-gray-400 text-xs sm:text-sm mb-1">Job Title</p>
                  <p className="text-white font-semibold text-sm sm:text-base truncate font-display">{analysisData.job_title || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs sm:text-sm mb-1">Company</p>
                  <p className="text-white font-semibold text-sm sm:text-base truncate font-display">{analysisData.company_name || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs sm:text-sm mb-1">Resume</p>
                  <p className="text-purple-400 font-semibold text-sm sm:text-base truncate font-display">{analysisData.resume_filename || 'Unknown'}</p>
                </div>
              </div>
            </div>
            </motion.div>
          </SpotlightCard>

          {/* Score Breakdown - Transparent Calculation */}
          {analysisData.ai_feedback && (() => {
            try {
              const aiFeedback = typeof analysisData.ai_feedback === 'string' 
                ? JSON.parse(analysisData.ai_feedback) 
                : analysisData.ai_feedback;
              if (aiFeedback.score_breakdown) {
                return (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <ScoreBreakdown
                      scoreBreakdown={aiFeedback.score_breakdown}
                      overallScore={analysisData.match_score}
                    />
                  </motion.div>
                );
              }
            } catch (e) {
              // Ignore parsing errors
            }
            return null;
          })()}

          {/* Error Message */}
          {error && (
            <motion.div
              className="bg-red-500/10 backdrop-blur-xl border border-red-500/30 rounded-xl p-4 flex items-start gap-3"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-300 text-sm">{error}</p>
            </motion.div>
          )}

          {/* Success Toast - Email Sent */}
          <AnimatePresence>
            {emailSent && (
              <motion.div
                className="bg-green-500/10 backdrop-blur-xl border border-green-500/30 rounded-xl p-4 flex items-start gap-3"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-green-300 text-sm font-semibold">Email sent successfully!</p>
                  <p className="text-green-400/80 text-xs mt-1">Your analysis report has been sent to your email address.</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* AI Feature Progress */}
          <AnimatePresence>
            {aiFeatureLoading && (
              <motion.div
                className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-white font-semibold flex items-center gap-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Loader className="w-4 h-4 text-cyan-400" />
                      </motion.div>
                      {aiFeatureMessage}
                    </span>
                    <span className="text-gray-400 text-sm">{Math.round(aiFeatureProgress)}%</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-cyan-500 to-purple-600"
                      initial={{ width: '0%' }}
                      animate={{ width: `${aiFeatureProgress}%` }}
                      transition={{ ease: 'easeOut', duration: 0.3 }}
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* AI Feedback Display */}
          {aiFeedback && (
            <motion.div
              className="bg-gradient-to-br from-purple-900/20 to-cyan-900/20 border border-purple-700/50 rounded-lg p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="text-white font-semibold">AI-Generated Feedback</h3>
              </div>
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{aiFeedback}</div>
              </div>
            </motion.div>
          )}

          {/* Optimized Resume Display */}
          {optimizedResume && (
            <motion.div
              className="bg-gradient-to-br from-cyan-900/20 to-blue-900/20 border border-cyan-700/50 rounded-lg p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-cyan-400" />
                <h3 className="text-white font-semibold">AI-Optimized Resume</h3>
              </div>
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{optimizedResume}</div>
              </div>
            </motion.div>
          )}

          {/* Cover Letter Display */}
          {coverLetter && (
            <motion.div
              className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 border border-amber-700/50 rounded-lg p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <FileUp className="w-5 h-5 text-amber-400" />
                <h3 className="text-white font-semibold">AI-Generated Cover Letter</h3>
              </div>
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{coverLetter}</div>
              </div>
            </motion.div>
          )}

          {/* Match Breakdown - Progress Bars */}
          <motion.div
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <h3 className="text-white font-semibold mb-4 font-display">Match Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Skills Match */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">Skills Match</span>
                  <span className="text-cyan-400 font-semibold font-display">
                    {analysisData.keywords_found ?
                      Math.round((analysisData.keywords_found.length / (analysisData.keywords_found.length + (analysisData.keywords_missing?.length || 0))) * 100) :
                      analysisData.match_score}%
                  </span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{
                      width: `${analysisData.keywords_found ?
                        Math.round((analysisData.keywords_found.length / (analysisData.keywords_found.length + (analysisData.keywords_missing?.length || 0))) * 100) :
                        analysisData.match_score}%`
                    }}
                    transition={{ delay: 0.3, duration: 1 }}
                  />
                </div>
              </div>

              {/* Experience Match */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">Experience Match</span>
                  <span className="text-cyan-400 font-semibold">{Math.max(0, analysisData.match_score - 5)}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: `${Math.max(0, analysisData.match_score - 5)}%` }}
                    transition={{ delay: 0.4, duration: 1 }}
                  />
                </div>
              </div>

              {/* Keywords Match */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">Keywords Match</span>
                  <span className="text-cyan-400 font-semibold">{analysisData.match_score}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: `${analysisData.match_score}%` }}
                    transition={{ delay: 0.5, duration: 1 }}
                  />
                </div>
              </div>

              {/* ATS Compatibility */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">ATS Compatibility</span>
                  <span className="text-cyan-400 font-semibold">{Math.min(100, analysisData.match_score + 10)}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: `${Math.min(100, analysisData.match_score + 10)}%` }}
                    transition={{ delay: 0.6, duration: 1 }}
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Keywords Found */}
          {analysisData.keywords_found && analysisData.keywords_found.length > 0 && (
            <motion.div
              className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.17 }}
            >
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Keywords Found ({analysisData.keywords_found.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysisData.keywords_found.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-green-900/30 text-green-300 rounded-full text-sm border border-green-700/50"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </motion.div>
          )}

          {/* Keywords Missing */}
          {analysisData.keywords_missing && analysisData.keywords_missing.length > 0 && (
            <motion.div
              className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.19 }}
            >
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-400" />
                Keywords to Add ({analysisData.keywords_missing.length})
              </h3>
              <p className="text-gray-400 text-sm mb-3">
                Adding these keywords could improve your match score
              </p>
              <div className="flex flex-wrap gap-2">
                {analysisData.keywords_missing.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-amber-900/30 text-amber-300 rounded-full text-sm border border-amber-700/50"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </motion.div>
          )}

          {/* Priority Improvements */}
          <motion.div
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.17 }}
          >
            <h3 className="text-white font-semibold mb-4">Priority Improvements</h3>
            <div className="space-y-3">
              {/* Generate improvements based on missing keywords */}
              {analysisData.keywords_missing && analysisData.keywords_missing.length > 0 && (
                <div className="bg-white/10/50 rounded-lg p-4 border border-white/20">
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-white font-semibold">Add Missing Keywords</p>
                    <span className="text-amber-400 text-sm">+{Math.min(15, analysisData.keywords_missing.length * 2)}%</span>
                  </div>
                  <p className="text-gray-400 text-sm mb-2">
                    Include {analysisData.keywords_missing.slice(0, 3).join(', ')}
                    {analysisData.keywords_missing.length > 3 && ` and ${analysisData.keywords_missing.length - 3} more`} in your resume.
                  </p>
                  <p className="text-slate-500 text-sm italic">
                    Example: Add these skills to your work experience or skills section naturally.
                  </p>
                </div>
              )}

              {/* Improvement based on match score */}
              {analysisData.match_score < 80 && (
                <div className="bg-white/10/50 rounded-lg p-4 border border-white/20">
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-white font-semibold">Optimize Resume Format</p>
                    <span className="text-amber-400 text-sm">+8%</span>
                  </div>
                  <p className="text-gray-400 text-sm mb-2">
                    Use clear section headings and bullet points to improve ATS readability.
                  </p>
                  <p className="text-slate-500 text-sm italic">
                    Example: Use standard section titles like "Work Experience", "Education", "Skills".
                  </p>
                </div>
              )}

              {/* Third improvement */}
              <div className="bg-white/10/50 rounded-lg p-4 border border-white/20">
                <div className="flex justify-between items-start mb-2">
                  <p className="text-white font-semibold">Quantify Achievements</p>
                  <span className="text-amber-400 text-sm">+10%</span>
                </div>
                <p className="text-gray-400 text-sm mb-2">
                  Add specific numbers and metrics to demonstrate your impact.
                </p>
                <p className="text-slate-500 text-sm italic">
                  Example: "Increased sales by 35%" instead of "Improved sales performance".
                </p>
              </div>
            </div>
          </motion.div>

          {/* ATS Optimization Tips */}
          <motion.div
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.19 }}
          >
            <h3 className="text-white font-semibold mb-3">ATS Optimization Tips</h3>
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-gray-400 text-sm">Expected ATS Pass Rate</span>
                <span className="text-cyan-400 font-semibold">
                  {analysisData.match_score >= 70 ? 'High' : analysisData.match_score >= 50 ? 'Medium' : 'Low'}
                </span>
              </div>
            </div>
            <ul className="space-y-2">
              <li className="text-gray-300 text-sm flex gap-2">
                <span className="text-cyan-400">✓</span>
                Use standard section headings (Experience, Education, Skills)
              </li>
              <li className="text-gray-300 text-sm flex gap-2">
                <span className="text-cyan-400">✓</span>
                Include exact keywords from the job description
              </li>
              <li className="text-gray-300 text-sm flex gap-2">
                <span className="text-cyan-400">✓</span>
                Avoid tables, graphics, and complex formatting
              </li>
              <li className="text-gray-300 text-sm flex gap-2">
                <span className="text-cyan-400">✓</span>
                Use common file formats (PDF or DOCX)
              </li>
            </ul>
          </motion.div>

          {/* AI Suggestions */}
          {analysisData.suggestions && (
            <motion.div
              className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.21 }}
            >
              <h3 className="text-white font-semibold mb-4">AI Feedback & Suggestions</h3>
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{analysisData.suggestions}</div>
              </div>
            </motion.div>
          )}

          {/* AI Features Buttons */}
          <motion.div
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.23 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold">AI-Powered Features</h3>
              <button
                onClick={handleSendEmail}
                disabled={sendingEmail || emailSent}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-600/20 to-purple-600/20 hover:from-cyan-600/30 hover:to-purple-600/30 border border-cyan-400/30 hover:border-cyan-400/60 disabled:opacity-50 text-white text-sm rounded-lg transition-all"
              >
                {sendingEmail ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : emailSent ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    Email Sent!
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4" />
                    Email me this Report
                  </>
                )}
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={handleGenerateFeedback}
                disabled={!!aiFeatureLoading || !!aiFeedback}
                className="p-4 bg-gradient-to-br from-purple-600/20 to-cyan-600/20 border border-purple-400/30 rounded-lg hover:border-purple-400/60 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex flex-col items-center text-center gap-2">
                  <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center group-hover:bg-purple-500/30 transition">
                    {aiFeedback ? (
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    ) : (
                      <Sparkles className="w-6 h-6 text-purple-400" />
                    )}
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">
                      {aiFeedback ? 'Generated ✓' : 'Generate AI Feedback'}
                    </p>
                    <p className="text-gray-400 text-xs mt-1">
                      {aiFeedback ? 'See below' : 'Get detailed improvement suggestions'}
                    </p>
                  </div>
                </div>
              </button>
              <button
                onClick={handleOptimizeResume}
                disabled={!!aiFeatureLoading || !!optimizedResume}
                className="p-4 bg-gradient-to-br from-cyan-600/20 to-blue-600/20 border border-cyan-400/30 rounded-lg hover:border-cyan-400/60 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex flex-col items-center text-center gap-2">
                  <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center group-hover:bg-cyan-500/30 transition">
                    {optimizedResume ? (
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    ) : (
                      <FileText className="w-6 h-6 text-cyan-400" />
                    )}
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">
                      {optimizedResume ? 'Optimized ✓' : 'Optimize Resume'}
                    </p>
                    <p className="text-gray-400 text-xs mt-1">
                      {optimizedResume ? 'See below' : 'AI-enhanced resume version'}
                    </p>
                  </div>
                </div>
              </button>
              <button
                onClick={handleGenerateCoverLetter}
                disabled={!!aiFeatureLoading || !!coverLetter}
                className="p-4 bg-gradient-to-br from-amber-600/20 to-orange-600/20 border border-amber-400/30 rounded-lg hover:border-amber-400/60 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex flex-col items-center text-center gap-2">
                  <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center group-hover:bg-amber-500/30 transition">
                    {coverLetter ? (
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    ) : (
                      <FileUp className="w-6 h-6 text-amber-400" />
                    )}
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">
                      {coverLetter ? 'Generated ✓' : 'Generate Cover Letter'}
                    </p>
                    <p className="text-gray-400 text-xs mt-1">
                      {coverLetter ? 'See below' : 'Tailored to this job posting'}
                    </p>
                  </div>
                </div>
              </button>
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            className="flex gap-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <ShimmerButton
              onClick={() => navigate(ROUTES.ANALYZE)}
              className="flex-1"
            >
              Analyze Another Resume
              <ArrowRight className="w-5 h-5" />
            </ShimmerButton>
            <motion.button
              onClick={() => navigate(ROUTES.DASHBOARD)}
              className="px-6 py-3 bg-white/10 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Back to Dashboard
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    );
  }

  // Default: Analyze mode
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Analyze Your Resume</h1>
        <p className="text-gray-400">Upload your resume and job description to get AI-powered insights</p>
        {userProfile && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-gray-400">Credits remaining:</span>
            <span className={`font-semibold ${userProfile.credits > 0 ? 'text-cyan-400' : 'text-red-400'}`}>
              {userProfile.credits}
            </span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6 flex items-start gap-3 relative z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-400 text-sm relative z-10">{error}</p>
        </motion.div>
      )}

      {/* Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 relative z-10">
        {/* Resume Upload */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <label className="block text-white font-semibold mb-3">Resume File</label>
          <div className="relative">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileUpload}
              className="hidden"
              id="resume-upload"
            />
            <label
              htmlFor="resume-upload"
              className="flex items-center justify-center w-full px-4 py-8 border-2 border-dashed border-white/20 rounded-lg cursor-pointer hover:border-purple-500 transition-colors bg-white/5 backdrop-blur-sm"
            >
              {resumeFile ? (
                <div className="text-center">
                  <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                  <p className="text-white font-semibold text-sm">{resumeFile.name}</p>
                  <p className="text-gray-400 text-xs mt-1">Click to change</p>
                </div>
              ) : (
                <div className="text-center">
                  <FileUp className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-white font-semibold text-sm">Upload Your Resume</p>
                  <p className="text-gray-400 text-xs mt-1">PDF, DOCX, or TXT</p>
                </div>
              )}
            </label>
          </div>
        </motion.div>

        {/* Job Details */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <label className="block text-white font-semibold mb-3">Job Details</label>
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Company (optional)"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full px-4 py-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
            />
            <input
              type="text"
              placeholder="Job Title (optional)"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              className="w-full px-4 py-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
            />
            <textarea
              placeholder="Paste job description here (required)"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full px-4 py-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none h-32 resize-none"
            />
          </div>
        </motion.div>
      </div>

      {/* Progress Section */}
      {loading && (
        <motion.div
          className="mt-6 space-y-4 relative z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="space-y-2">
            <div className="flex items-center justify-between relative z-10">
              <span className="text-white font-semibold flex items-center gap-2 relative z-10">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                >
                  <Loader className="w-4 h-4 text-purple-400" />
                </motion.div>
                {loadingMessage}
              </span>
              <span className="text-gray-400 text-sm relative z-10">{Math.round(loadingProgress)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden relative z-10">
              <motion.div
                className="h-full bg-gradient-to-r from-purple-500 to-blue-600"
                initial={{ width: '0%' }}
                animate={{ width: `${loadingProgress}%` }}
                transition={{ ease: 'easeOut', duration: 0.3 }}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Analyze Button */}
      {!loading && (
        <div className="w-full mt-6 relative z-10">
          <ShimmerButton
            onClick={handleAnalyze}
            disabled={loading || !resumeFile || !jobDescription}
            className="w-full"
          >
            Start Analysis
            <ArrowRight className="w-5 h-5" />
          </ShimmerButton>
        </div>
      )}
    </div>
  );
};

export default AnalyzePage;
