import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Award, Copy, Check, ExternalLink } from 'lucide-react';

/**
 * ResumeScoreBadge - Embeddable badge component for external websites
 *
 * This component can be used:
 * 1. On the user's dashboard to show their score
 * 2. As an embeddable widget users can add to their portfolio/LinkedIn
 *
 * @param {Object} props
 * @param {number} props.score - The resume score (0-100)
 * @param {string} props.userName - User's name for personalization
 * @param {string} props.variant - 'light' | 'dark' | 'minimal'
 * @param {boolean} props.showEmbed - Show embed code option
 */
const ResumeScoreBadge = ({
  score = 85,
  userName = "Your Name",
  variant = 'dark',
  showEmbed = false
}) => {
  const [copied, setCopied] = useState(false);

  // Determine score color
  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-400 to-emerald-500';
    if (score >= 60) return 'from-yellow-400 to-orange-500';
    return 'from-red-400 to-pink-500';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Work';
  };

  // Generate embed code
  const embedCode = `<a href="https://resumeanalyzerai.com/guest-analyze?ref=badge" target="_blank" rel="noopener noreferrer" style="display:inline-block;text-decoration:none;">
  <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:12px;padding:16px 24px;display:flex;align-items:center;gap:12px;border:1px solid rgba(139,92,246,0.3);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
    <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#22c55e,#10b981);display:flex;align-items:center;justify-content:center;">
      <span style="color:white;font-weight:bold;font-size:14px;">${score}</span>
    </div>
    <div>
      <div style="color:white;font-weight:600;font-size:14px;">ATS Score: ${score}/100</div>
      <div style="color:#a78bfa;font-size:12px;">Verified by ResumeAnalyzer AI</div>
    </div>
  </div>
</a>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(embedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const variantStyles = {
    dark: 'bg-gradient-to-br from-slate-900 to-purple-900/50 border-purple-500/30',
    light: 'bg-gradient-to-br from-white to-purple-50 border-purple-200',
    minimal: 'bg-transparent border-gray-300'
  };

  const textStyles = {
    dark: 'text-white',
    light: 'text-gray-900',
    minimal: 'text-gray-700'
  };

  return (
    <div className="space-y-6">
      {/* Badge Preview */}
      <motion.div
        className={`inline-flex items-center gap-4 p-4 rounded-xl border ${variantStyles[variant]}`}
        whileHover={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        {/* Score Circle */}
        <div className={`relative w-14 h-14 rounded-full bg-gradient-to-br ${getScoreColor(score)} flex items-center justify-center shadow-lg`}>
          <span className="text-white font-bold text-lg">{score}</span>
        </div>

        {/* Text Content */}
        <div>
          <div className={`font-semibold ${textStyles[variant]}`}>
            ATS Score: {score}/100
          </div>
          <div className="text-purple-400 text-sm flex items-center gap-1">
            <Award className="w-3 h-3" />
            <span>Verified by ResumeAnalyzer AI</span>
          </div>
          <div className="text-gray-500 text-xs mt-1">
            {getScoreLabel(score)}
          </div>
        </div>

        {/* External Link Icon */}
        <ExternalLink className="w-4 h-4 text-gray-400" />
      </motion.div>

      {/* Embed Code Section */}
      {showEmbed && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-white font-semibold text-sm">Embed This Badge</h4>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium rounded-lg transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  Copy Code
                </>
              )}
            </button>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 overflow-x-auto">
            <pre className="text-xs text-gray-400 whitespace-pre-wrap break-all">
              {embedCode}
            </pre>
          </div>

          <p className="text-gray-500 text-xs">
            Add this code to your portfolio, blog, or LinkedIn to showcase your verified ATS score.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResumeScoreBadge;
