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
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold text-white font-display">Score Breakdown</h3>
          <button
            onClick={() => setShowFullBreakdown(!showFullBreakdown)}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
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
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 cursor-pointer hover:border-cyan-400/50 transition-colors"
              onClick={() => toggleFactor(factor.key)}
            >
              <div className="text-xs text-gray-400 mb-2">{factor.label}</div>
              <div className="text-2xl font-bold text-white mb-1">
                {factor.data?.score || 0}%
              </div>
              <div className="text-xs text-gray-400">
                Weight: {(factor.data?.weight * 100).toFixed(0)}% | 
                Contribution: {Math.max(0, factor.data?.weighted_contribution || 0).toFixed(1)}%
              </div>
              <div className="mt-2 w-full bg-white/10 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    factor.color === 'purple' ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                    factor.color === 'blue' ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                    factor.color === 'cyan' ? 'bg-gradient-to-r from-cyan-500 to-cyan-600' :
                    factor.color === 'green' ? 'bg-gradient-to-r from-green-500 to-green-600' :
                    'bg-gradient-to-r from-yellow-500 to-yellow-600'
                  }`}
                  style={{ width: `${Math.max(0, Math.min(100, factor.data?.score || 0))}%` }}
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

        {/* Final Formula - Improved Display */}
        {calc.final_formula && (
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-white mb-2">Score Calculation</h4>
            <div className="text-xs font-mono text-gray-300 space-y-1">
              {(() => {
                // Parse and format the formula string for better display
                const formula = calc.final_formula;
                // If it contains negative values, show them more clearly
                if (formula.includes('Base weighted score:') && formula.includes('-')) {
                  const parts = formula.split('|');
                  return (
                    <div className="space-y-1">
                      {parts.map((part, idx) => (
                        <div key={idx} className={part.includes('-') && !part.includes('Penalties') ? 'text-amber-400' : 'text-gray-300'}>
                          {part.trim()}
                        </div>
                      ))}
                    </div>
                  );
                }
                return <div>{formula}</div>;
              })()}
            </div>
          </div>
        )}
      </div>

      {/* Detailed Breakdown */}
      {showFullBreakdown && (
        <div className="space-y-4">
            {factors.map((factor) => (
              <div
                key={factor.key}
                className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6"
              >
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleFactor(factor.key)}
                >
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-1">{factor.label}</h4>
                    <p className="text-sm text-gray-400">{factor.data?.explanation}</p>
                  </div>
                  {expandedFactors[factor.key] ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
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
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                          <h5 className="text-sm font-semibold text-gray-300 mb-2">Details</h5>
                          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                            {Object.entries(factor.data.details).map(([key, value]) => (
                              <div key={key}>
                                <span className="capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
                                <span className="text-gray-300">{String(value)}</span>
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
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
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

