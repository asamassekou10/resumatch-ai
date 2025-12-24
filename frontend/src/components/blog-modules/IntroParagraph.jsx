import React from 'react';

/**
 * IntroParagraph - Large, readable opening paragraph for articles
 * Provides better visual hierarchy and readability
 */
const IntroParagraph = ({ children, className = '' }) => {
  return (
    <p className={`text-lg md:text-xl text-gray-200 leading-relaxed mb-8 font-light ${className}`}>
      {children}
    </p>
  );
};

export default IntroParagraph;

