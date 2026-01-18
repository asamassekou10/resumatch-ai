/**
 * TemplateSelector Component
 * Grid of template cards for selection
 */

import { motion } from 'framer-motion';
import { Check, FileText, Star } from 'lucide-react';

const TemplateSelector = ({ templates, selectedTemplate, onSelect, documentType }) => {
  if (!templates || templates.length === 0) {
    return (
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Select Template</h3>
        <p className="text-gray-400 text-sm">No templates available</p>
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-blue-400" />
        {documentType === 'resume' ? 'Resume' : 'Cover Letter'} Template
      </h3>

      <div className="space-y-3">
        {templates.map((template) => {
          const isSelected = selectedTemplate === template.id;

          return (
            <motion.button
              key={template.id}
              onClick={() => onSelect(template.id)}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              className={`w-full p-4 rounded-xl border transition text-left ${
                isSelected
                  ? 'bg-blue-500/20 border-blue-500/50 ring-2 ring-blue-500/30'
                  : 'bg-white/5 border-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Selection indicator */}
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 transition ${
                    isSelected
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-500'
                  }`}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-white">{template.name}</span>
                    {template.ats_score && template.ats_score >= 100 && (
                      <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded">
                        <Star className="w-3 h-3" />
                        ATS Best
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-400 mb-2 line-clamp-2">
                    {template.description}
                  </p>

                  {/* Features */}
                  <div className="flex flex-wrap gap-1.5">
                    {template.features?.slice(0, 3).map((feature, idx) => (
                      <span
                        key={idx}
                        className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>

                  {/* ATS Score */}
                  {template.ats_score && (
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            template.ats_score >= 95
                              ? 'bg-green-500'
                              : template.ats_score >= 85
                                ? 'bg-yellow-500'
                                : 'bg-orange-500'
                          }`}
                          style={{ width: `${template.ats_score}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">
                        {template.ats_score}% ATS
                      </span>
                    </div>
                  )}

                  {/* Recommended for */}
                  {template.recommended_for?.length > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      Best for: {template.recommended_for.slice(0, 3).join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};

export default TemplateSelector;
