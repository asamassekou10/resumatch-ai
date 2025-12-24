import React from 'react';

const toneStyles = {
  info: 'bg-blue-500/10 border-blue-500/30 text-blue-100',
  warning: 'bg-amber-500/10 border-amber-500/30 text-amber-100',
  success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-100',
  neutral: 'bg-white/5 border-white/10 text-gray-100',
};

const CalloutCard = ({ title, body, tone = 'info', children }) => {
  const toneClass = toneStyles[tone] || toneStyles.info;

  return (
    <div className={`rounded-xl border ${toneClass} p-5 backdrop-blur-sm my-6`}>
      {title && <h3 className="text-lg font-bold font-display mb-2">{title}</h3>}
      {body && <p className="text-sm md:text-base leading-relaxed">{body}</p>}
      {children}
    </div>
  );
};

export default CalloutCard;

