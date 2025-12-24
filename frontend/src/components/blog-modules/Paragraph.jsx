import React from 'react';

/**
 * Paragraph - Styled paragraph with proper spacing
 * Ensures consistent spacing and readability
 */
const Paragraph = ({ children, className = '', spacing = 'normal' }) => {
  const spacingClass = spacing === 'large' ? 'mb-6' : 'mb-4';
  
  return (
    <p className={`text-gray-300 leading-relaxed text-base md:text-lg ${spacingClass} ${className}`}>
      {children}
    </p>
  );
};

export default Paragraph;

