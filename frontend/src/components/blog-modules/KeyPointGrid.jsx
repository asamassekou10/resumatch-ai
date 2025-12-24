import React from 'react';

const KeyPointGrid = ({ title, items = [] }) => {
  return (
    <div className="space-y-4 my-8">
      {title && <h3 className="text-xl font-bold text-white font-display mb-4">{title}</h3>}
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((item, index) => (
          <div
            key={index}
            className="border border-white/10 rounded-xl p-5 bg-white/5 backdrop-blur-sm h-full"
          >
            <div className="text-white font-semibold mb-2">{item.title}</div>
            <p className="text-gray-300 leading-relaxed text-sm md:text-base">{item.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KeyPointGrid;

