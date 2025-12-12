import { Navigate, useLocation } from 'react-router-dom';
import { ROUTES } from '../../config/routes';

/**
 * ProtectedRoute Component
 *
 * Wraps routes that require authentication and/or specific permissions.
 * Handles:
 * - Authentication check (token exists)
 * - Subscription validation (for premium features)
 * - Admin access control
 * - Post-login redirect (returns user to attempted route)
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Component to render if authorized
 * @param {boolean} props.requireAdmin - Whether route requires admin access
 * @param {boolean} props.requireSubscription - Whether route requires active subscription
 */
const ProtectedRoute = ({
  children,
  requireAdmin = false,
  requireSubscription = false
}) => {
  const token = localStorage.getItem('token');
  const location = useLocation();

  // Parse user profile from localStorage
  let userProfile = {};
  try {
    const storedProfile = localStorage.getItem('userProfile');
    if (storedProfile) {
      userProfile = JSON.parse(storedProfile);
    }
  } catch (error) {
    console.error('Error parsing user profile:', error);
  }

  // Check 1: Authentication - must have token
  if (!token) {
    console.log('[ProtectedRoute] No token found, redirecting to login');
    // Save the attempted location for post-login redirect
    return (
      <Navigate
        to={ROUTES.LOGIN}
        state={{ from: location }}
        replace
      />
    );
  }

  // Check 2: Admin Access
  if (requireAdmin && !userProfile.is_admin) {
    console.log('[ProtectedRoute] Admin access required but user is not admin');
    return (
      <Navigate
        to={ROUTES.DASHBOARD}
        state={{
          message: 'Admin access required',
          severity: 'error'
        }}
        replace
      />
    );
  }

  // Check 3: Subscription Access
  const hasSubscription = userProfile.subscription_status === 'active';
  const isAdmin = userProfile.is_admin;

  if (requireSubscription && !hasSubscription && !isAdmin) {
    console.log('[ProtectedRoute] Subscription required but user does not have active subscription');
    return (
      <Navigate
        to={ROUTES.PRICING}
        state={{
          message: 'This feature requires an active subscription',
          severity: 'warning',
          from: location
        }}
        replace
      />
    );
  }

  // All checks passed - render the protected component
  return children;
};

export default ProtectedRoute;
