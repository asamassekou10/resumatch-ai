/**
 * Google Analytics 4 Utility
 * 
 * Handles page views and event tracking for SEO and marketing analytics
 */

const GA_MEASUREMENT_ID = process.env.REACT_APP_GOOGLE_ANALYTICS_ID;
const ENABLE_ANALYTICS = process.env.REACT_APP_ENABLE_ANALYTICS === 'true';

/**
 * Initialize Google Analytics
 */
export const initAnalytics = () => {
  if (!ENABLE_ANALYTICS || !GA_MEASUREMENT_ID) {
    return;
  }

  // Load gtag.js script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', GA_MEASUREMENT_ID, {
    page_path: window.location.pathname,
    send_page_view: false // We'll track page views manually
  });
};

/**
 * Track page view
 * @param {string} path - Page path
 * @param {string} title - Page title
 */
export const trackPageView = (path, title) => {
  if (!ENABLE_ANALYTICS || !GA_MEASUREMENT_ID || !window.gtag) {
    return;
  }

  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: path,
    page_title: title,
  });

  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title,
  });
};

/**
 * Track custom event
 * @param {string} eventName - Event name
 * @param {Object} eventParams - Event parameters
 */
export const trackEvent = (eventName, eventParams = {}) => {
  if (!ENABLE_ANALYTICS || !GA_MEASUREMENT_ID || !window.gtag) {
    return;
  }

  window.gtag('event', eventName, eventParams);
};

/**
 * Track resume upload
 * @param {string} fileType - File type (pdf, docx, txt)
 */
export const trackResumeUpload = (fileType) => {
  trackEvent('resume_upload', {
    file_type: fileType,
  });
};

/**
 * Track job match
 * @param {number} matchScore - Match score (0-100)
 */
export const trackJobMatch = (matchScore) => {
  trackEvent('job_match', {
    match_score: matchScore,
  });
};

/**
 * Track subscription conversion
 * @param {string} tier - Subscription tier (pro, elite)
 * @param {number} value - Subscription value
 */
export const trackSubscription = (tier, value) => {
  trackEvent('purchase', {
    currency: 'USD',
    value: value,
    items: [{
      item_id: tier,
      item_name: `${tier} Subscription`,
      price: value,
      quantity: 1,
    }],
  });
};

/**
 * Track button click
 * @param {string} buttonName - Button identifier
 * @param {string} location - Location on page
 */
export const trackButtonClick = (buttonName, location) => {
  trackEvent('button_click', {
    button_name: buttonName,
    location: location,
  });
};

/**
 * Track search
 * @param {string} searchTerm - Search query
 * @param {string} category - Search category
 */
export const trackSearch = (searchTerm, category) => {
  trackEvent('search', {
    search_term: searchTerm,
    category: category,
  });
};

export default {
  initAnalytics,
  trackPageView,
  trackEvent,
  trackResumeUpload,
  trackJobMatch,
  trackSubscription,
  trackButtonClick,
  trackSearch,
};

