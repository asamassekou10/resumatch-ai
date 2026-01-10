import React, { useState } from 'react';
import { Link2, FileText, Loader } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * JobDescriptionInput Component
 *
 * Dual-mode input for job descriptions:
 * 1. Paste Mode: Traditional textarea for pasting job description text
 * 2. Link Mode: URL input that fetches and extracts job description from URL
 *
 * @param {Object} props
 * @param {string} props.value - Current job description text
 * @param {Function} props.onChange - Callback when description changes
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.label - Label text
 */
const JobDescriptionInput = ({
  value = '',
  onChange,
  placeholder = '',
  className = '',
  label = '2. Enter Job Description'
}) => {
  const [mode, setMode] = useState('paste'); // 'paste' or 'link'
  const [jobUrl, setJobUrl] = useState('');
  const [fetching, setFetching] = useState(false);
  const [fetchError, setFetchError] = useState('');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const handleFetchFromLink = async () => {
    if (!jobUrl.trim()) {
      setFetchError('Please enter a job posting URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(jobUrl);
    } catch (e) {
      setFetchError('Please enter a valid URL');
      return;
    }

    setFetching(true);
    setFetchError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/v1/jobs/fetch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ url: jobUrl })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Failed to fetch job description');
      }

      // Success - populate the description
      onChange(data.data.description || data.description || '');
      setFetchError('');

      // Optionally switch to paste mode to show the extracted text
      setMode('paste');
    } catch (error) {
      console.error('Error fetching job description:', error);
      setFetchError(
        error.message ||
        'Unable to fetch from this URL. Supported sites: LinkedIn, Indeed, Glassdoor. Please paste the job description manually.'
      );
    } finally {
      setFetching(false);
    }
  };

  return (
    <div className={className}>
      {/* Label */}
      <label className="block text-white font-semibold mb-3 text-lg">{label}</label>

      {/* Tab Switcher */}
      <div className="flex gap-2 mb-4 bg-white/5 p-1 rounded-lg border border-white/10">
        <button
          type="button"
          onClick={() => setMode('paste')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-all ${
            mode === 'paste'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span className="font-medium">Paste Description</span>
        </button>
        <button
          type="button"
          onClick={() => setMode('link')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-all ${
            mode === 'link'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Link2 className="w-4 h-4" />
          <span className="font-medium">Enter Job Link</span>
        </button>
      </div>

      {/* Content Area */}
      <AnimatePresence mode="wait">
        {mode === 'paste' ? (
          <motion.div
            key="paste"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <textarea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder={placeholder || 'Paste the job description here...\n\nInclude:\n- Job responsibilities\n- Required qualifications\n- Preferred skills\n- Company information'}
              className="w-full min-h-[250px] p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-y"
              required
            />
            <p className="text-gray-400 text-sm mt-2">
              💡 Tip: The more detailed the job description, the better your match analysis
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="link"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="space-y-4"
          >
            {/* URL Input */}
            <div>
              <div className="flex gap-2">
                <input
                  type="url"
                  value={jobUrl}
                  onChange={(e) => {
                    setJobUrl(e.target.value);
                    setFetchError('');
                  }}
                  placeholder="https://www.linkedin.com/jobs/view/..."
                  className="flex-1 p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  disabled={fetching}
                />
                <button
                  type="button"
                  onClick={handleFetchFromLink}
                  disabled={fetching || !jobUrl.trim()}
                  className="px-6 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {fetching ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Fetching...
                    </>
                  ) : (
                    'Fetch'
                  )}
                </button>
              </div>

              {/* Error Message */}
              {fetchError && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-2 p-3 bg-red-900/20 border border-red-700/50 rounded-lg text-red-300 text-sm"
                >
                  {fetchError}
                </motion.div>
              )}

              {/* Success hint */}
              {value && mode === 'link' && !fetchError && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-2 p-3 bg-green-900/20 border border-green-700/50 rounded-lg text-green-300 text-sm"
                >
                  ✓ Job description fetched successfully! Switch to "Paste Description" tab to view/edit.
                </motion.div>
              )}
            </div>

            {/* Supported Sites */}
            <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
              <p className="text-gray-300 text-sm font-medium mb-2">Supported Job Boards:</p>
              <div className="flex flex-wrap gap-2">
                {['LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter'].map(site => (
                  <span
                    key={site}
                    className="px-3 py-1 bg-white/10 text-gray-400 text-xs rounded-full"
                  >
                    {site}
                  </span>
                ))}
              </div>
              <p className="text-gray-400 text-xs mt-3">
                💡 Copy the job posting URL from your browser and paste it above. We'll automatically extract the job description.
              </p>
            </div>

            {/* Fallback Instructions */}
            <div className="p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
              <p className="text-blue-300 text-sm">
                <strong>Can't fetch from URL?</strong> No problem! Just copy the job description text and switch to the "Paste Description" tab.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default JobDescriptionInput;
