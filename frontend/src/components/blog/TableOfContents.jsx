import { useEffect, useState } from 'react';
import { Hash } from 'lucide-react';

/**
 * TableOfContents Component
 * 
 * Automatically generates a table of contents from h2 headings in the article
 */
const TableOfContents = ({ content }) => {
  const [headings, setHeadings] = useState([]);
  const [activeId, setActiveId] = useState('');

  useEffect(() => {
    // Wait for content to be rendered, then find headings in the actual DOM
    const findHeadings = () => {
      // Find the article content container
      const articleContent = document.querySelector('.prose');
      if (!articleContent) return;

      const h2Elements = Array.from(articleContent.querySelectorAll('h2'));
      
      const extractedHeadings = h2Elements.map((h2, index) => {
        // Generate a safe ID from the heading text
        const text = h2.textContent || '';
        const id = `heading-${index}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 30)}`;
        
        // Add ID to the actual DOM element if it doesn't have one
        if (!h2.id) {
          h2.id = id;
        }
        
        return { id: h2.id, text };
      });

      setHeadings(extractedHeadings);

      // Intersection Observer for active heading
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setActiveId(entry.target.id);
            }
          });
        },
        { rootMargin: '-20% 0% -35% 0%' }
      );

      h2Elements.forEach((h2) => observer.observe(h2));

      return () => {
        h2Elements.forEach((h2) => observer.unobserve(h2));
      };
    };

    // Use a small delay to ensure content is rendered
    const timeoutId = setTimeout(findHeadings, 100);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [content]);

  const scrollToHeading = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (headings.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4">
        <Hash className="w-4 h-4 text-purple-400" />
        <h3 className="font-bold text-white text-sm uppercase tracking-wide font-display">Table of Contents</h3>
      </div>
      <nav className="space-y-2">
        {headings.map((heading) => (
          <button
            key={heading.id}
            onClick={() => scrollToHeading(heading.id)}
            className={`block w-full text-left text-sm py-2 px-3 rounded transition-all ${
              activeId === heading.id
                ? 'bg-purple-500/20 text-purple-300 border-l-2 border-purple-500'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            {heading.text}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default TableOfContents;



