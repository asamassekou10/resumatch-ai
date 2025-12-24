import React from 'react';

/**
 * SectionDivider - Visual separator between major sections
 * Provides breathing room and clear section breaks
 */
const SectionDivider = ({ className = '' }) => {
  return (
    <div className={`my-12 border-t border-white/10 ${className}`} />
  );
};

export default SectionDivider;

