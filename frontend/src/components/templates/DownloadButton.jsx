/**
 * DownloadButton Component
 * Handles PDF download with progress indicator
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import config from '../../config';

const API_URL = config.api.baseURL;

const DownloadButton = ({ analysisId, documentType, templateId, token, disabled }) => {
  const [downloading, setDownloading] = useState(false);
  const [status, setStatus] = useState(null); // 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('');

  const handleDownload = async () => {
    if (disabled || downloading) return;

    try {
      setDownloading(true);
      setStatus(null);
      setErrorMessage('');

      const response = await fetch(`${API_URL}/analyze/${analysisId}/download-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          document_type: documentType,
          template_id: templateId
        })
      });

      if (!response.ok) {
        // Try to get error message from response
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Download failed');
        }
        throw new Error('Failed to generate PDF');
      }

      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = documentType === 'resume' ? 'resume.pdf' : 'cover_letter.pdf';

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Get the blob
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setStatus('success');
      setTimeout(() => setStatus(null), 3000);

    } catch (err) {
      console.error('Download error:', err);
      setStatus('error');
      setErrorMessage(err.message || 'Download failed');
    } finally {
      setDownloading(false);
    }
  };

  const getButtonContent = () => {
    if (downloading) {
      return (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Generating PDF...</span>
        </>
      );
    }

    if (status === 'success') {
      return (
        <>
          <CheckCircle className="w-5 h-5" />
          <span>Downloaded!</span>
        </>
      );
    }

    if (status === 'error') {
      return (
        <>
          <AlertCircle className="w-5 h-5" />
          <span>Try Again</span>
        </>
      );
    }

    return (
      <>
        <Download className="w-5 h-5" />
        <span>Download {documentType === 'resume' ? 'Resume' : 'Cover Letter'} PDF</span>
      </>
    );
  };

  const getButtonClasses = () => {
    const baseClasses = 'w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition';

    if (disabled) {
      return `${baseClasses} bg-gray-700 text-gray-400 cursor-not-allowed`;
    }

    if (downloading) {
      return `${baseClasses} bg-blue-600 text-white cursor-wait`;
    }

    if (status === 'success') {
      return `${baseClasses} bg-green-500 text-white`;
    }

    if (status === 'error') {
      return `${baseClasses} bg-red-500 text-white hover:bg-red-600`;
    }

    return `${baseClasses} bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 shadow-lg shadow-green-500/25`;
  };

  return (
    <div>
      <motion.button
        onClick={handleDownload}
        disabled={disabled || downloading}
        className={getButtonClasses()}
        whileHover={!disabled && !downloading ? { scale: 1.02 } : {}}
        whileTap={!disabled && !downloading ? { scale: 0.98 } : {}}
      >
        {getButtonContent()}
      </motion.button>

      {status === 'error' && errorMessage && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-red-400 mt-2 text-center"
        >
          {errorMessage}
        </motion.p>
      )}

      {status === 'success' && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-green-400 mt-2 text-center"
        >
          Your PDF has been downloaded!
        </motion.p>
      )}
    </div>
  );
};

export default DownloadButton;
