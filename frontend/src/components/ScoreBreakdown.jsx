import React, { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronUp, Info } from 'lucide-react';

/**
 * ScoreBreakdown Component
 * 
 * Displays transparent breakdown of how resume score was calculated.
 * Shows factor-by-factor analysis with color-coded indicators.
 */
const ScoreBreakdown = ({ scoreBreakdown, overallScore }) => {
  const [expandedFactors, setExpandedFactors] = useState({});
  const [showFullBreakdown, setShowFullBreakdown] = useState(false);

  if (!scoreBreakdown || !scoreBreakdown.score_calculation) {
    return null;
  }

  const calc = scoreBreakdown.score_calculation;
  const factors = [
    {
      key: 'keyword_matching',
      label: 'Keyword Matching',
      data: calc.keyword_matching,
      color: 'purple'
    },
    {
      key: 'experience_qualifications',
      label: 'Experience & Qualifications',
      data: calc.experience_qualifications,
      color: 'blue'
    },
    {
      key: 'ats_readability',
      label: 'ATS Readability',
      data: calc.ats_readability,
      color: 'cyan'
    },
    {
      key: 'content_quality',
      label: 'Content Quality',
      data: calc.content_quality,
      color: 'green'
    },
    {
      key: 'job_specific_match',
      label: 'Job-Specific Match',
      data: calc.job_specific_match,
      color: 'yellow'
    }
  ];

  const toggleFactor = (key) => {
    setExpandedFactors(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getStatusColor = (status, severity) => {
    if (status === 'found') return 'text-green-400';
    if (status === 'missing') {
      if (severity === 'required' || severity === 'critical') return 'text-red-400';
      return 'text-yellow-400';
    }
    return 'text-gray-400';
  };

  const getStatusIcon = (status, severity) => {
    if (status === 'found') {
      return <CheckCircle className="w-4 h-4 text-green-400" />;
    }
    if (status === 'missing') {
      if (severity === 'required' || severity === 'critical') {
        return <XCircle className="w-4 h-4 text-red-400" />;
      }
      return <AlertCircle className="w-4 h-4 text-yellow-400" />;
    }
    return <Info className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Summary */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-700 border border-slate-600 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold text-white font-display">Score Breakdown</h3>
          <button
            onClick={() => setShowFullBreakdown(!showFullBreakdown)}
            className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1"
          >
            {showFullBreakdown ? (
              <>Hide Details <ChevronUp className="w-4 h-4" /></>
            ) : (
              <>Show Details <ChevronDown className="w-4 h-4" /></>
            )}
          </button>
        </div>

        {/* Factor Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
          {factors.map((factor) => (
            <div
              key={factor.key}
              className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 cursor-pointer hover:border-purple-500/50 transition-colors"
              onClick={() => toggleFactor(factor.key)}
            >
              <div className="text-xs text-slate-400 mb-2">{factor.label}</div>
              <div className="text-2xl font-bold text-white mb-1">
                {factor.data?.score || 0}%
              </div>
              <div className="text-xs text-slate-400">
                Weight: {(factor.data?.weight * 100).toFixed(0)}% | 
                Contribution: {factor.data?.weighted_contribution?.toFixed(1) || 0}%
              </div>
              <div className="mt-2 w-full bg-slate-600 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    factor.color === 'purple' ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
                    factor.color === 'blue' ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                    factor.color === 'cyan' ? 'bg-gradient-to-r from-cyan-500 to-cyan-600' :
                    factor.color === 'green' ? 'bg-gradient-to-r from-green-500 to-green-600' :
                    'bg-gradient-to-r from-yellow-500 to-yellow-600'
                  }`}
                  style={{ width: `${factor.data?.score || 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Hard Filter Alert */}
        {calc.hard_filters?.applied && (
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-red-400 font-semibold mb-2">Hard Filter Applied</h4>
                <p className="text-red-300 text-sm mb-2">
                  Your score was reduced by a {((1 - calc.hard_filters.multiplier) * 100).toFixed(0)}% multiplier due to critical gaps.
                </p>
                <ul className="text-red-300 text-sm space-y-1">
                  {calc.hard_filters.reasons?.map((reason, idx) => (
                    <li key={idx}>• {reason.explanation}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Final Formula */}
        {calc.final_formula && (
          <div className="bg-slate-700/30 rounded-lg p-3 text-sm font-mono text-slate-300">
            {calc.final_formula}
          </div>
        )}
      </div>

      {/* Detailed Breakdown */}
      {showFullBreakdown && (
        <div className="space-y-4">
            {factors.map((factor) => (
              <div
                key={factor.key}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
              >
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleFactor(factor.key)}
                >
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-1">{factor.label}</h4>
                    <p className="text-sm text-slate-400">{factor.data?.explanation}</p>
                  </div>
                  {expandedFactors[factor.key] ? (
                    <ChevronUp className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  )}
                </div>

                {expandedFactors[factor.key] && (
                  <div className="mt-4 space-y-4">
                      {/* Matches */}
                      {factor.data?.matches && factor.data.matches.length > 0 && (
                        <div>
                          <h5 className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
                            Matches Found
                          </h5>
                          <div className="space-y-1">
                            {factor.data.matches.map((match, idx) => (
                              <div key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                                {getStatusIcon(match.status, match.severity)}
                                <span className={getStatusColor(match.status, match.severity)}>
                                  {match.item} {match.location && `(${match.location})`}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Gaps */}
                      {factor.data?.gaps && factor.data.gaps.length > 0 && (
                        <div>
                          <h5 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2">
                            <XCircle className="w-4 h-4" />
                            Missing Items
                          </h5>
                          <div className="space-y-1">
                            {factor.data.gaps.map((gap, idx) => (
                              <div key={idx} className="flex items-start gap-2 text-sm">
                                {getStatusIcon(gap.status, gap.severity)}
                                <div className="flex-1">
                                  <span className={getStatusColor(gap.status, gap.severity)}>
                                    {gap.item}
                                  </span>
                                  {gap.penalty && (
                                    <span className="text-red-400 ml-2">
                                      (Penalty: {gap.penalty} points)
                                    </span>
                                  )}
                                  {gap.why_matters && (
                                    <p className="text-xs text-slate-400 mt-0.5">{gap.why_matters}</p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Details */}
                      {factor.data?.details && (
                        <div className="bg-slate-700/30 rounded-lg p-3">
                          <h5 className="text-sm font-semibold text-slate-300 mb-2">Details</h5>
                          <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
                            {Object.entries(factor.data.details).map(([key, value]) => (
                              <div key={key}>
                                <span className="capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
                                <span className="text-slate-300">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                )}
              </div>
            ))}

            {/* Penalties & Bonuses */}
            {(calc.penalties?.length > 0 || calc.bonuses?.length > 0) && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-white mb-4">Penalties & Bonuses</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {calc.penalties?.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-red-400 mb-2">Penalties Applied</h5>
                      <ul className="space-y-1">
                        {calc.penalties.map((penalty, idx) => (
                          <li key={idx} className="text-sm text-red-300 flex items-center gap-2">
                            <XCircle className="w-4 h-4" />
                            {penalty.reason} ({penalty.points} points)
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {calc.bonuses?.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-green-400 mb-2">Bonuses Applied</h5>
                      <ul className="space-y-1">
                        {calc.bonuses.map((bonus, idx) => (
                          <li key={idx} className="text-sm text-green-300 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
                            {bonus.reason} (+{bonus.points} points)
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
};

export default ScoreBreakdown;

