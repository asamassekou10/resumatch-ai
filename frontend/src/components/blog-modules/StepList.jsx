import React from 'react';

const toneClasses = {
  default: 'bg-white/5 border-white/10',
  success: 'bg-emerald-500/10 border-emerald-500/30',
  info: 'bg-blue-500/10 border-blue-500/30',
};

const StepList = ({ title, steps = [], tone = 'default' }) => {
  const toneClass = toneClasses[tone] || toneClasses.default;

  return (
    <div className={`rounded-xl border ${toneClass} p-6 space-y-4 backdrop-blur-sm my-8`}>
      {title && <h3 className="text-xl font-bold text-white font-display">{title}</h3>}
      <ol className="space-y-3">
        {steps.map((step, index) => (
          <li key={index} className="flex gap-4">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500/20 text-blue-200 font-semibold">
              {index + 1}
            </div>
            <div className="space-y-1">
              <div className="text-white font-semibold">{step.title}</div>
              <p className="text-gray-300 leading-relaxed text-sm md:text-base">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
};

export default StepList;

