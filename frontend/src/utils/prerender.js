/**
 * Prerendering detection utility
 * Helps components detect if they're being prerendered by react-snap
 */

/**
 * Check if code is running in prerender/SSR environment
 * @returns {boolean} True if prerendering, false if client-side
 */
export const isPrerendering = () => {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return true;
  }

  // Check for react-snap's navigator.userAgent
  if (navigator.userAgent === 'ReactSnap') {
    return true;
  }

  // Check if window.__REACT_SNAP__ is set
  if (window.__REACT_SNAP__) {
    return true;
  }

  return false;
};

/**
 * Only execute function if NOT prerendering
 * Useful for preventing API calls during SSR
 */
export const skipDuringPrerender = (fn) => {
  if (!isPrerendering()) {
    return fn();
  }
  return null;
};

const prerenderUtils = {
  isPrerendering,
  skipDuringPrerender,
};

export default prerenderUtils;
