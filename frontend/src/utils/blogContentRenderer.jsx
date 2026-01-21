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
  // Handle null/undefined content
  if (!content) {
    return (
      <div className={className} style={style}>
        <p className="text-gray-400">Content not available.</p>
      </div>
    );
  }

  // If content is a function, it's JSX - render it directly
  if (typeof content === 'function') {
    try {
      const renderedContent = content();
      return (
        <div className={className} style={style}>
          {renderedContent}
        </div>
      );
    } catch (error) {
      console.error('Error rendering blog content:', error);
      return (
        <div className={className} style={style}>
          <p className="text-red-400">Error loading content. Please try refreshing the page.</p>
        </div>
      );
    }
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
  
  // Fallback for unexpected types
  console.warn('BlogContentRenderer received unexpected content type:', typeof content);
  return (
    <div className={className} style={style}>
      <p className="text-gray-400">Unable to render content.</p>
    </div>
  );
};

export default BlogContentRenderer;









