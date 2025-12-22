/**
 * RouteTracker Component
 * 
 * Tracks page views for analytics when routes change
 */
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackPageView } from '../../utils/analytics';

const RouteTracker = () => {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    const pageTitle = document.title || 'ResumeAnalyzer AI';
    trackPageView(location.pathname + location.search, pageTitle);
  }, [location]);

  return null;
};

export default RouteTracker;

