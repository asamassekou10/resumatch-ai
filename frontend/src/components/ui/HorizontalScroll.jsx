import React, { useRef, useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * HorizontalScroll Component
 *
 * A reusable horizontal scroll container with visible navigation arrows
 * and indicators to show there's more content to scroll.
 *
 * Features:
 * - Left/Right arrow buttons
 * - Auto-hide arrows when at start/end
 * - Smooth scroll behavior
 * - Progress dots indicator
 * - Touch/swipe support
 * - Responsive design
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to scroll
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.showDots - Show progress dots (default: false)
 * @param {boolean} props.showArrows - Show navigation arrows (default: true)
 * @param {number} props.scrollAmount - Pixels to scroll per click (default: 300)
 */
const HorizontalScroll = ({
  children,
  className = '',
  showDots = false,
  showArrows = true,
  scrollAmount = 300
}) => {
  const scrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  // Check scroll position and update button states
  const checkScroll = () => {
    const element = scrollRef.current;
    if (!element) return;

    const { scrollLeft, scrollWidth, clientWidth } = element;
    setCanScrollLeft(scrollLeft > 0);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);

    // Calculate scroll progress (0 to 1)
    const progress = scrollWidth > clientWidth
      ? scrollLeft / (scrollWidth - clientWidth)
      : 0;
    setScrollProgress(progress);
  };

  useEffect(() => {
    checkScroll();
    const element = scrollRef.current;
    if (element) {
      element.addEventListener('scroll', checkScroll);
      window.addEventListener('resize', checkScroll);
    }

    return () => {
      if (element) {
        element.removeEventListener('scroll', checkScroll);
      }
      window.removeEventListener('resize', checkScroll);
    };
  }, [children]);

  const scroll = (direction) => {
    const element = scrollRef.current;
    if (!element) return;

    const scrollBy = direction === 'left' ? -scrollAmount : scrollAmount;
    element.scrollBy({ left: scrollBy, behavior: 'smooth' });
  };

  return (
    <div className={`relative group ${className}`}>
      {/* Left Arrow */}
      {showArrows && canScrollLeft && (
        <motion.button
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 10 }}
          onClick={() => scroll('left')}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full p-2 shadow-lg hover:shadow-xl transition-all opacity-90 hover:opacity-100"
          aria-label="Scroll left"
        >
          <ChevronLeft className="w-5 h-5" />
        </motion.button>
      )}

      {/* Scrollable Container */}
      <div
        ref={scrollRef}
        className="overflow-x-auto overflow-y-hidden scrollbar-hide"
        style={{
          scrollbarWidth: 'none', // Firefox
          msOverflowStyle: 'none', // IE/Edge
          WebkitOverflowScrolling: 'touch' // iOS smooth scrolling
        }}
      >
        <div className="flex gap-4 min-w-max">
          {children}
        </div>
      </div>

      {/* Right Arrow */}
      {showArrows && canScrollRight && (
        <motion.button
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          onClick={() => scroll('right')}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full p-2 shadow-lg hover:shadow-xl transition-all opacity-90 hover:opacity-100"
          aria-label="Scroll right"
        >
          <ChevronRight className="w-5 h-5" />
        </motion.button>
      )}

      {/* Progress Dots (optional) */}
      {showDots && (
        <div className="flex justify-center gap-2 mt-4">
          {[...Array(Math.ceil(scrollRef.current?.scrollWidth / scrollRef.current?.clientWidth) || 1)].map((_, i) => {
            const isActive = Math.abs(scrollProgress * (scrollRef.current?.scrollWidth / scrollRef.current?.clientWidth - 1) - i) < 0.5;
            return (
              <button
                key={i}
                onClick={() => {
                  const element = scrollRef.current;
                  if (element) {
                    element.scrollTo({
                      left: i * element.clientWidth,
                      behavior: 'smooth'
                    });
                  }
                }}
                className={`h-2 rounded-full transition-all ${
                  isActive
                    ? 'w-8 bg-gradient-to-r from-blue-500 to-purple-600'
                    : 'w-2 bg-gray-600 hover:bg-gray-500'
                }`}
                aria-label={`Go to section ${i + 1}`}
              />
            );
          })}
        </div>
      )}

      {/* Gradient Fade Indicators */}
      {canScrollLeft && (
        <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-black to-transparent pointer-events-none z-5" />
      )}
      {canScrollRight && (
        <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-black to-transparent pointer-events-none z-5" />
      )}
    </div>
  );
};

export default HorizontalScroll;

// CSS to hide scrollbars (add to your global CSS or component)
/*
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
*/
