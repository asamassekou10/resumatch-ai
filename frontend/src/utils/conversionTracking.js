/**
 * Conversion Tracking Utility
 * Tracks user events throughout the conversion funnel for analytics
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Event types
export const CONVERSION_EVENTS = {
  LANDING_PAGE_VIEW: 'landing_page_view',
  SIGNUP_STARTED: 'signup_started',
  SIGNUP_COMPLETED: 'signup_completed',
  FIRST_ANALYSIS_STARTED: 'first_analysis_started',
  FIRST_ANALYSIS_COMPLETED: 'first_analysis_completed',
  PRICING_PAGE_VIEW: 'pricing_page_view',
  CHECKOUT_STARTED: 'checkout_started',
  PAYMENT_COMPLETED: 'payment_completed',
  EXIT_INTENT: 'exit_intent',
  PRICING_MODAL_OPENED: 'pricing_modal_opened',
  PAYMENT_MODAL_OPENED: 'payment_modal_opened',
  UPGRADE_CLICKED: 'upgrade_clicked',
  TRIAL_BANNER_CLICKED: 'trial_banner_clicked',
};

/**
 * Track a conversion event
 * @param {string} eventType - Type of event (from CONVERSION_EVENTS)
 * @param {object} metadata - Additional event data
 */
export const trackEvent = async (eventType, metadata = {}) => {
  try {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    
    const eventData = {
      event_type: eventType,
      metadata: {
        ...metadata,
        timestamp: new Date().toISOString(),
        user_id: userId || null,
        session_id: getSessionId(),
        page_url: window.location.href,
        referrer: document.referrer || null,
      }
    };

    // Send to backend analytics
    if (token) {
      try {
        await fetch(`${API_URL}/analytics/track-event`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(eventData)
        });
      } catch (err) {
        console.warn('Failed to track event to backend:', err);
      }
    }

    // Also track in Google Analytics if available
    if (window.gtag) {
      window.gtag('event', eventType, {
        event_category: 'conversion',
        event_label: eventType,
        value: metadata.value || 0,
        ...metadata
      });
    }

    // Track in localStorage for offline analytics
    const events = JSON.parse(localStorage.getItem('conversion_events') || '[]');
    events.push(eventData);
    // Keep only last 50 events
    if (events.length > 50) {
      events.shift();
    }
    localStorage.setItem('conversion_events', JSON.stringify(events));

  } catch (error) {
    console.error('Error tracking conversion event:', error);
  }
};

/**
 * Get or create session ID
 */
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

/**
 * Track page view
 */
export const trackPageView = (pageName) => {
  trackEvent(CONVERSION_EVENTS.LANDING_PAGE_VIEW, {
    page_name: pageName
  });
};

/**
 * Track signup start
 */
export const trackSignupStarted = () => {
  trackEvent(CONVERSION_EVENTS.SIGNUP_STARTED);
};

/**
 * Track signup completion
 */
export const trackSignupCompleted = (userId) => {
  trackEvent(CONVERSION_EVENTS.SIGNUP_COMPLETED, {
    user_id: userId
  });
  if (userId) {
    localStorage.setItem('userId', userId.toString());
  }
};

/**
 * Track analysis start
 */
export const trackAnalysisStarted = (isFirst = false) => {
  trackEvent(
    isFirst ? CONVERSION_EVENTS.FIRST_ANALYSIS_STARTED : 'analysis_started',
    { is_first: isFirst }
  );
};

/**
 * Track analysis completion
 */
export const trackAnalysisCompleted = (isFirst = false, score = null) => {
  trackEvent(
    isFirst ? CONVERSION_EVENTS.FIRST_ANALYSIS_COMPLETED : 'analysis_completed',
    { 
      is_first: isFirst,
      score: score
    }
  );
};

/**
 * Track pricing page view
 */
export const trackPricingPageView = () => {
  trackEvent(CONVERSION_EVENTS.PRICING_PAGE_VIEW);
};

/**
 * Track checkout start
 */
export const trackCheckoutStarted = (planType, price) => {
  trackEvent(CONVERSION_EVENTS.CHECKOUT_STARTED, {
    plan_type: planType,
    price: price
  });
};

/**
 * Track payment completion
 */
export const trackPaymentCompleted = (planType, price, transactionId) => {
  trackEvent(CONVERSION_EVENTS.PAYMENT_COMPLETED, {
    plan_type: planType,
    price: price,
    transaction_id: transactionId
  });
};

/**
 * Track exit intent
 */
export const trackExitIntent = (pageName) => {
  trackEvent(CONVERSION_EVENTS.EXIT_INTENT, {
    page_name: pageName
  });
};

/**
 * Track pricing modal opened
 */
export const trackPricingModalOpened = (trigger) => {
  trackEvent(CONVERSION_EVENTS.PRICING_MODAL_OPENED, {
    trigger: trigger
  });
};

/**
 * Track payment modal opened
 */
export const trackPaymentModalOpened = (planType) => {
  trackEvent(CONVERSION_EVENTS.PAYMENT_MODAL_OPENED, {
    plan_type: planType
  });
};

/**
 * Track upgrade button click
 */
export const trackUpgradeClicked = (source, planType) => {
  trackEvent(CONVERSION_EVENTS.UPGRADE_CLICKED, {
    source: source,
    plan_type: planType
  });
};

/**
 * Track trial banner click
 */
export const trackTrialBannerClicked = (bannerType) => {
  trackEvent(CONVERSION_EVENTS.TRIAL_BANNER_CLICKED, {
    banner_type: bannerType
  });
};

/**
 * Get conversion funnel data (for admin dashboard)
 */
export const getConversionFunnel = async (days = 30) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return null;

    const response = await fetch(`${API_URL}/analytics/conversion-funnel?days=${days}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch conversion funnel');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching conversion funnel:', error);
    return null;
  }
};

export default {
  trackEvent,
  trackPageView,
  trackSignupStarted,
  trackSignupCompleted,
  trackAnalysisStarted,
  trackAnalysisCompleted,
  trackPricingPageView,
  trackCheckoutStarted,
  trackPaymentCompleted,
  trackExitIntent,
  trackPricingModalOpened,
  trackPaymentModalOpened,
  trackUpgradeClicked,
  trackTrialBannerClicked,
  getConversionFunnel,
  CONVERSION_EVENTS
};
