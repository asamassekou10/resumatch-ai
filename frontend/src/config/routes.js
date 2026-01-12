/**
 * Route Configuration
 *
 * Centralized route definitions for the application.
 * Use these constants throughout the app for consistency and maintainability.
 */

// Route path constants
export const ROUTES = {
  // ============================================
  // PUBLIC ROUTES (No Authentication Required)
  // ============================================
  LANDING: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  GUEST_ANALYZE: '/guest-analyze',
  PRICING: '/pricing',
  CHECKOUT: '/checkout',
  HELP: '/help',
  HELP_TERMS: '/help/terms',
  HELP_PRIVACY: '/help/privacy',

  // ============================================
  // PROTECTED ROUTES (Authentication Required)
  // ============================================
  DASHBOARD: '/dashboard',
  ANALYZE: '/analyze',
  RESULT: '/result/:id',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  BILLING: '/billing',

  // ============================================
  // MARKET INTELLIGENCE ROUTES
  // ============================================
  MARKET: '/market',
  MARKET_DASHBOARD: '/market/dashboard',
  MARKET_SKILL_GAP: '/market/skill-gap',
  MARKET_JOB_STATS: '/market/job-stats',
  MARKET_SKILL_RELATIONSHIPS: '/market/skill-relationships',
  MARKET_INSIGHTS: '/market/insights',
  MARKET_INTERVIEW_PREP: '/market/interview-prep',
  MARKET_COMPANY_INTEL: '/market/company-intel',
  MARKET_CAREER_PATH: '/market/career-path',

  // ============================================
  // ADMIN ROUTES (Admin Access Required)
  // ============================================
  ADMIN: '/admin',
  ADMIN_USERS: '/admin/users',
  ADMIN_ANALYTICS: '/admin/analytics',
  ADMIN_JOBS: '/admin/jobs',
};

/**
 * View name to route mapping
 * Used during migration to map old view state values to new routes
 *
 * @deprecated Use ROUTES constants directly after migration
 */
export const VIEW_TO_ROUTE = {
  // Public views
  'landing': ROUTES.LANDING,
  'login': ROUTES.LOGIN,
  'register': ROUTES.REGISTER,
  'guest-analyze': ROUTES.GUEST_ANALYZE,
  'pricing': ROUTES.PRICING,
  'help': ROUTES.HELP,

  // Protected views
  'dashboard': ROUTES.DASHBOARD,
  'analyze': ROUTES.ANALYZE,
  'profile': ROUTES.PROFILE,
  'settings': ROUTES.SETTINGS,
  'billing': ROUTES.BILLING,

  // Market Intelligence views
  'market-dashboard': ROUTES.MARKET_DASHBOARD,
  'skill-gap': ROUTES.MARKET_SKILL_GAP,
  'job-stats': ROUTES.MARKET_JOB_STATS,
  'skill-relationships': ROUTES.MARKET_SKILL_RELATIONSHIPS,
  'market-insights': ROUTES.MARKET_INSIGHTS,
  'interview-prep': ROUTES.MARKET_INTERVIEW_PREP,
  'company-intel': ROUTES.MARKET_COMPANY_INTEL,
  'career-path': ROUTES.MARKET_CAREER_PATH,

  // Admin views
  'admin': ROUTES.ADMIN,
  'admin-users': ROUTES.ADMIN_USERS,
  'admin-analytics': ROUTES.ADMIN_ANALYTICS,
  'admin-jobs': ROUTES.ADMIN_JOBS,
};

/**
 * Route to view name mapping (reverse of VIEW_TO_ROUTE)
 * Useful for migration and debugging
 *
 * @deprecated Use ROUTES constants directly after migration
 */
export const ROUTE_TO_VIEW = Object.entries(VIEW_TO_ROUTE).reduce(
  (acc, [view, route]) => ({ ...acc, [route]: view }),
  {}
);

/**
 * Check if a route requires authentication
 */
export const isProtectedRoute = (path) => {
  const publicRoutes = [
    ROUTES.LANDING,
    ROUTES.LOGIN,
    ROUTES.REGISTER,
    ROUTES.GUEST_ANALYZE,
    ROUTES.PRICING,
    ROUTES.HELP,
    ROUTES.HELP_TERMS,
    ROUTES.HELP_PRIVACY,
  ];

  return !publicRoutes.includes(path);
};

/**
 * Check if a route requires subscription
 */
export const requiresSubscription = (path) => {
  return path.startsWith('/market');
};

/**
 * Check if a route requires admin access
 */
export const requiresAdmin = (path) => {
  return path.startsWith('/admin');
};

/**
 * Get route metadata
 */
export const getRouteMetadata = (path) => {
  return {
    isProtected: isProtectedRoute(path),
    requiresSubscription: requiresSubscription(path),
    requiresAdmin: requiresAdmin(path),
  };
};

/**
 * Navigation groups for menus
 */
export const NAV_GROUPS = {
  main: [
    { label: 'Dashboard', route: ROUTES.DASHBOARD, icon: 'Home' },
    { label: 'Analyze Resume', route: ROUTES.ANALYZE, icon: 'FileText' },
    { label: 'Pricing', route: ROUTES.PRICING, icon: 'CreditCard' },
    { label: 'Settings', route: ROUTES.SETTINGS, icon: 'Settings' },
    { label: 'Help & Support', route: ROUTES.HELP, icon: 'HelpCircle' },
  ],
  market: [
    { label: 'Overview', route: ROUTES.MARKET_DASHBOARD },
    { label: 'Interview Prep', route: ROUTES.MARKET_INTERVIEW_PREP },
    { label: 'Company Intel', route: ROUTES.MARKET_COMPANY_INTEL },
    { label: 'Career Path', route: ROUTES.MARKET_CAREER_PATH },
    { label: 'Skill Gap', route: ROUTES.MARKET_SKILL_GAP },
    { label: 'Job Stats', route: ROUTES.MARKET_JOB_STATS },
    { label: 'Skill Relationships', route: ROUTES.MARKET_SKILL_RELATIONSHIPS },
    { label: 'Market Insights', route: ROUTES.MARKET_INSIGHTS },
  ],
  admin: [
    { label: 'Dashboard', route: ROUTES.ADMIN },
    { label: 'Users', route: ROUTES.ADMIN_USERS },
    { label: 'Analytics', route: ROUTES.ADMIN_ANALYTICS },
    { label: 'Jobs', route: ROUTES.ADMIN_JOBS },
  ],
  public: [
    { label: 'Home', route: ROUTES.LANDING, icon: 'Home' },
    { label: 'Try Free', route: ROUTES.GUEST_ANALYZE, icon: 'FileText' },
    { label: 'Pricing', route: ROUTES.PRICING, icon: 'CreditCard' },
    { label: 'Login', route: ROUTES.LOGIN, icon: 'LogIn' },
    { label: 'Sign Up', route: ROUTES.REGISTER, icon: 'UserPlus' },
  ],
};

export default ROUTES;
