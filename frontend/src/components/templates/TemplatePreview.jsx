/**
 * TemplatePreview Component
 * Shows a live preview of the resume/cover letter in the selected template
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Eye, Loader2, AlertCircle, Maximize2, X } from 'lucide-react';
import config from '../../config';

const API_URL = config.api.baseURL;

const TemplatePreview = ({
  analysisId,
  documentType,
  templateId,
  token,
  structuredResume,
  disabled
}) => {
  const [html, setHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Fetch preview when template or data changes
  useEffect(() => {
    if (disabled || !templateId) return;

    const fetchPreview = async () => {
      try {
        setLoading(true);
        setError('');

        const response = await fetch(`${API_URL}/analyze/${analysisId}/preview-html`, {
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
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to load preview');
        }

        const data = await response.json();
        setHtml(data.data.html);

      } catch (err) {
        setError(err.message || 'Failed to load preview');
        console.error('Preview error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPreview();
  }, [analysisId, documentType, templateId, token, disabled, structuredResume]);

  if (disabled) {
    return (
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Eye className="w-5 h-5 text-purple-400" />
          Preview
        </h3>
        <div className="aspect-[8.5/11] bg-white/5 rounded-lg flex items-center justify-center">
          <p className="text-gray-500 text-sm text-center px-4">
            Parse your resume to see a preview
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-purple-400" />
            Preview
          </h3>
          {html && !loading && (
            <button
              onClick={() => setIsFullscreen(true)}
              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition"
              title="Fullscreen preview"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="aspect-[8.5/11] bg-white/5 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Loading preview...</p>
            </div>
          </div>
        ) : error ? (
          <div className="aspect-[8.5/11] bg-white/5 rounded-lg flex items-center justify-center">
            <div className="text-center px-4">
              <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          </div>
        ) : html ? (
          <div className="aspect-[8.5/11] bg-white rounded-lg overflow-hidden shadow-xl relative">
            <div className="absolute inset-0 overflow-auto">
              <iframe
                srcDoc={`
                  <!DOCTYPE html>
                  <html>
                  <head>
                    <style>
                      body {
                        margin: 0;
                        padding: 0;
                        transform: scale(0.4);
                        transform-origin: top left;
                        width: 250%;
                      }
                    </style>
                  </head>
                  <body>${html}</body>
                  </html>
                `}
                title="Resume Preview"
                className="w-full border-0"
                style={{ height: '250%' }}
                sandbox="allow-same-origin"
              />
            </div>
          </div>
        ) : (
          <div className="aspect-[8.5/11] bg-white/5 rounded-lg flex items-center justify-center">
            <p className="text-gray-500 text-sm">No preview available</p>
          </div>
        )}

        <p className="text-xs text-gray-500 mt-3 text-center">
          This is how your {documentType === 'resume' ? 'resume' : 'cover letter'} will look
        </p>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setIsFullscreen(false)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="relative w-full max-w-4xl h-[90vh] bg-white rounded-xl overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setIsFullscreen(false)}
              className="absolute top-4 right-4 z-10 p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
            <iframe
              srcDoc={html}
              title="Resume Preview Fullscreen"
              className="w-full h-full border-0"
              sandbox="allow-same-origin"
            />
          </motion.div>
        </motion.div>
      )}
    </>
  );
};

export default TemplatePreview;
