import React from 'react';
import { RefreshIcon } from './Icons';

const RepersonalizeButton = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:shadow-lg transition-all duration-200 font-medium text-sm"
      title="Update your market preferences and insights"
    >
      <RefreshIcon className="w-4 h-4" />
      <span>Repersonalize Insights</span>
    </button>
  );
};

export default RepersonalizeButton;
