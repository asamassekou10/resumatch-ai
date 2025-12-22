import React from 'react';

/**
 * BlogContentRenderer Component
 * 
 * Renders blog content that can be either:
 * - HTML string (backward compatible with existing posts)
 * - JSX function (new format allowing React components)
 * 
 * @param {Object} props
 * @param {string | Function} props.content - HTML string or function returning JSX
 * @param {string} props.className - Additional CSS classes for the container
 * @param {Object} props.style - Inline styles for the container
 */
const BlogContentRenderer = ({ content, className = '', style = {} }) => {
  // If content is a function, it's JSX - render it directly
  if (typeof content === 'function') {
    return (
      <div className={className} style={style}>
        {content()}
      </div>
    );
  }
  
  // If content is a string, it's HTML - use dangerouslySetInnerHTML (backward compatibility)
  if (typeof content === 'string') {
    return (
      <div
        className={className}
        style={style}
        dangerouslySetInnerHTML={{ __html: content }}
      />
    );
  }
  
  // Fallback for null/undefined
  return null;
};

export default BlogContentRenderer;



