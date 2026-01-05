import { X, Check } from 'lucide-react';

/**
 * BeforeAfterExample Component
 * 
 * Visually contrasts a "Weak" example vs. a "Strong" example
 */
const BeforeAfterExample = ({ weak, strong, weakLabel = 'Weak Example', strongLabel = 'Strong Example' }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
      {/* Weak Example */}
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <X className="w-5 h-5 text-red-400" />
          <h4 className="font-bold text-red-400 uppercase text-sm tracking-wide">{weakLabel}</h4>
        </div>
        <p className="text-gray-400 italic leading-relaxed">{weak}</p>
      </div>

      {/* Strong Example */}
      <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Check className="w-5 h-5 text-green-400" />
          <h4 className="font-bold text-green-400 uppercase text-sm tracking-wide">{strongLabel}</h4>
        </div>
        <p className="text-gray-200 leading-relaxed">{strong}</p>
      </div>
    </div>
  );
};

export default BeforeAfterExample;











