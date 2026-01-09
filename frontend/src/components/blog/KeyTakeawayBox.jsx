import { AlertCircle } from 'lucide-react';

/**
 * KeyTakeawayBox Component
 * 
 * A visually distinct box for highlighting key takeaways, tips, or important information
 * in blog articles. Uses a light background with colored left border.
 */
const KeyTakeawayBox = ({ children, variant = 'default', title }) => {
  const variants = {
    default: 'bg-blue-50/10 border-l-4 border-blue-500',
    warning: 'bg-yellow-50/10 border-l-4 border-yellow-500',
    success: 'bg-green-50/10 border-l-4 border-green-500',
    info: 'bg-blue-50/10 border-l-4 border-blue-500',
  };

  return (
    <div className={`${variants[variant]} rounded-r-lg p-6 my-8 backdrop-blur-sm`}>
      {title && (
        <div className="flex items-center gap-2 mb-3">
          <AlertCircle className="w-5 h-5 text-blue-400" />
          <h3 className="font-bold text-white text-lg font-display">{title}</h3>
        </div>
      )}
      <div className="text-gray-300 leading-relaxed">
        {children}
      </div>
    </div>
  );
};

export default KeyTakeawayBox;











