import { Lightbulb } from 'lucide-react';

/**
 * InsiderTip Component
 * 
 * Highlights "Insider Strategy" sections with a distinctive yellow/gold design.
 * 
 * @param {Object} props
 * @param {string} props.title - The tip title/heading
 * @param {React.ReactNode} props.children - The tip content
 */
const InsiderTip = ({ title, children }) => {
  return (
    <div className="bg-amber-900/20 border-l-4 border-amber-500/30 rounded-r-lg p-6 my-8 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <h3 className="font-bold text-white text-lg font-display">{title}</h3>
      </div>
      <div className="text-gray-300 leading-relaxed">
        {children}
      </div>
    </div>
  );
};

export default InsiderTip;



