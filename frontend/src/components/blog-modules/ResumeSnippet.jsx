import { CheckCircle2, XCircle } from 'lucide-react';

/**
 * ResumeSnippet Component
 * 
 * Displays "Good" vs "Bad" resume examples visually.
 * Designed to look like a mini piece of paper with a drop shadow.
 * 
 * @param {Object} props
 * @param {'good' | 'bad'} props.type - Type of snippet (good or bad)
 * @param {string} props.content - The resume bullet point text
 */
const ResumeSnippet = ({ type, content }) => {
  const isGood = type === 'good';
  
  const baseStyles = 'relative bg-white/5 backdrop-blur-sm rounded-lg p-5 my-6 shadow-lg border';
  const typeStyles = isGood
    ? 'border-green-500/30 bg-green-900/10 shadow-green-500/10'
    : 'border-red-500/30 bg-red-900/10 shadow-red-500/10';
  
  const Icon = isGood ? CheckCircle2 : XCircle;
  const iconColor = isGood ? 'text-green-400' : 'text-red-400';
  const textColor = isGood ? 'text-gray-200' : 'text-gray-400';
  const labelColor = isGood ? 'text-green-300' : 'text-red-300';
  
  return (
    <div className={`${baseStyles} ${typeStyles}`}>
      {/* Icon and Label */}
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`w-5 h-5 ${iconColor} flex-shrink-0`} />
        <span className={`text-xs font-bold uppercase tracking-wide ${labelColor}`}>
          {isGood ? 'Strong Example' : 'Weak Example'}
        </span>
      </div>
      
      {/* Resume Content */}
      <p className={`${textColor} leading-relaxed font-mono text-sm italic`}>
        "{content}"
      </p>
      
      {/* Subtle paper texture effect */}
      <div className="absolute inset-0 rounded-lg opacity-5 pointer-events-none" 
           style={{
             backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)'
           }}
      />
    </div>
  );
};

export default ResumeSnippet;



