/**
 * Breadcrumbs Component
 *
 * Provides navigational breadcrumbs for SEO and user experience.
 * Features:
 * - Semantic HTML with proper schema markup support
 * - Responsive design (collapses on mobile)
 * - Accessible navigation
 * - Integrates with structured data generator
 */

import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

/**
 * Breadcrumbs navigation component
 * @param {Object} props
 * @param {Array} props.items - Array of {name, url} breadcrumb items
 * @param {string} props.className - Additional CSS classes
 */
const Breadcrumbs = ({ items = [], className = '' }) => {
  if (!items || items.length === 0) return null;

  return (
    <nav
      aria-label="Breadcrumb"
      className={`flex items-center text-sm text-gray-400 mb-6 overflow-x-auto scrollbar-hide ${className}`}
    >
      <ol
        className="flex items-center space-x-1 sm:space-x-2 whitespace-nowrap"
        itemScope
        itemType="https://schema.org/BreadcrumbList"
      >
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const isFirst = index === 0;

          return (
            <li
              key={item.url || index}
              className="flex items-center"
              itemProp="itemListElement"
              itemScope
              itemType="https://schema.org/ListItem"
            >
              {index > 0 && (
                <ChevronRight className="w-4 h-4 mx-1 sm:mx-2 text-gray-600 flex-shrink-0" />
              )}

              {isLast ? (
                // Current page - not a link
                <span
                  className="text-gray-300 font-medium truncate max-w-[200px] sm:max-w-none"
                  itemProp="name"
                  aria-current="page"
                >
                  {item.name}
                </span>
              ) : (
                // Clickable link
                <Link
                  to={item.url.replace('https://www.resumeanalyzerai.com', '')}
                  className="hover:text-white transition-colors flex items-center gap-1"
                  itemProp="item"
                >
                  {isFirst && <Home className="w-4 h-4 flex-shrink-0" />}
                  <span itemProp="name" className="hidden sm:inline">
                    {item.name}
                  </span>
                  {isFirst && (
                    <span itemProp="name" className="sm:hidden">
                      {item.name}
                    </span>
                  )}
                </Link>
              )}

              <meta itemProp="position" content={String(index + 1)} />
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
