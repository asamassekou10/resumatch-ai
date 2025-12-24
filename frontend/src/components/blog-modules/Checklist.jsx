import React from 'react';
import { CheckCircle } from 'lucide-react';

/**
 * Checklist component for quick, scannable items
 */
const Checklist = ({ title, items = [] }) => {
  return (
    <div className="space-y-3 rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm my-6">
      {title && <h3 className="text-lg font-bold text-white font-display">{title}</h3>}
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-3 text-gray-200">
            <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5" />
            <span className="leading-relaxed text-sm md:text-base">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Checklist;


