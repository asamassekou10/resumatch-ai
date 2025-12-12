import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import ProtectedRoute from './ProtectedRoute';
import MainLayout from '../layouts/MainLayout';
import MarketLayout from '../layouts/MarketLayout';
import LoadingSpinner from '../common/LoadingSpinner';
import { ROUTES } from '../../config/routes';

// ============================================
// LAZY LOAD COMPONENTS (Code Splitting)
// ============================================

// Public Pages
const LandingPageV2 = lazy(() => import('../LandingPageV2'));
const LoginPage = lazy(() => import('../LoginPage'));
const RegisterPage = lazy(() => import('../RegisterPage'));
const GuestAnalyze = lazy(() => import('../GuestAnalyze'));
const PricingPage = lazy(() => import('../PricingPage'));
const HelpPage = lazy(() => import('../HelpPage'));

// Protected Pages
const Dashboard = lazy(() => import('../Dashboard'));
const AnalyzePage = lazy(() => import('../AnalyzePage'));
const ProfilePage = lazy(() => import('../ProfilePage'));
const SettingsPage = lazy(() => import('../SettingsPage'));
const BillingPage = lazy(() => import('../BillingPage'));

// Market Intelligence Pages
const MarketDashboard = lazy(() => import('../MarketDashboard'));
const SkillGap = lazy(() => import('../SkillGap'));
const JobMarketStats = lazy(() => import('../JobMarketStats'));
const SkillRelationships = lazy(() => import('../SkillRelationships'));
const MarketInsights = lazy(() => import('../MarketInsights'));
const InterviewPrep = lazy(() => import('../InterviewPrep'));
const CompanyIntel = lazy(() => import('../CompanyIntel'));
const CareerPath = lazy(() => import('../CareerPath'));

// Admin Pages
const AdminDashboard = lazy(() => import('../AdminDashboard'));

/**
 * AppRoutes Component
 *
 * Central routing configuration for the entire application.
 * Defines all routes with their authentication and authorization requirements.
 *
 * Route Categories:
 * 1. Public Routes - No authentication required
 * 2. Protected Routes - Authentication required
 * 3. Market Routes - Authentication + Subscription required
 * 4. Admin Routes - Authentication + Admin access required
 *
 * Features:
 * - Lazy loading for code splitting
 * - Protected route wrappers
 * - Layout components for consistent UI
 * - Loading states during route transitions
 * - 404 handling
 *
 * @param {Object} props
 * @param {Object} props.userProfile - Current user profile data
 * @param {string} props.token - Authentication token
 * @param {Function} props.handleLogout - Logout callback
 * @param {Function} props.handleLogin - Login callback
 */
const AppRoutes = ({ userProfile, token, handleLogout, handleLogin }) => {
  return (
    <Suspense fallback={<LoadingSpinner message="Loading page..." />}>
      <Routes>
        {/* ============================================ */}
        {/* PUBLIC ROUTES (No Authentication Required) */}
        {/* ============================================ */}

        <Route path={ROUTES.LANDING} element={<LandingPageV2 token={token} />} />

        <Route
          path={ROUTES.LOGIN}
          element={<LoginPage onLogin={handleLogin} />}
        />

        <Route
          path={ROUTES.REGISTER}
          element={<RegisterPage onRegister={handleLogin} />}
        />

        <Route
          path={ROUTES.GUEST_ANALYZE}
          element={<GuestAnalyze />}
        />

        <Route
          path={ROUTES.PRICING}
          element={<PricingPage userProfile={userProfile} />}
        />

        <Route path={ROUTES.HELP} element={<HelpPage />} />

        <Route
          path={ROUTES.HELP_TERMS}
          element={<HelpPage defaultTab="terms" />}
        />

        <Route
          path={ROUTES.HELP_PRIVACY}
          element={<HelpPage defaultTab="privacy" />}
        />

        {/* ============================================ */}
        {/* PROTECTED ROUTES (Main Application)         */}
        {/* Uses MainLayout for consistent navigation   */}
        {/* ============================================ */}

        <Route
          element={
            <MainLayout
              userProfile={userProfile}
              token={token}
              handleLogout={handleLogout}
            />
          }
        >
          <Route
            path={ROUTES.DASHBOARD}
            element={
              <ProtectedRoute>
                <Dashboard userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.ANALYZE}
            element={
              <ProtectedRoute>
                <AnalyzePage userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.PROFILE}
            element={
              <ProtectedRoute>
                <ProfilePage user={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.SETTINGS}
            element={
              <ProtectedRoute>
                <SettingsPage user={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.BILLING}
            element={
              <ProtectedRoute>
                <BillingPage user={userProfile} />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* ============================================ */}
        {/* MARKET INTELLIGENCE ROUTES                  */}
        {/* Uses MarketLayout + Subscription Required   */}
        {/* ============================================ */}

        {/* Redirect /market to /market/dashboard */}
        <Route
          path={ROUTES.MARKET}
          element={<Navigate to={ROUTES.MARKET_DASHBOARD} replace />}
        />

        <Route
          element={
            <MarketLayout
              userProfile={userProfile}
              token={token}
              handleLogout={handleLogout}
            />
          }
        >
          <Route
            path={ROUTES.MARKET_DASHBOARD}
            element={
              <ProtectedRoute requireSubscription={true}>
                <MarketDashboard userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_SKILL_GAP}
            element={
              <ProtectedRoute requireSubscription={true}>
                <SkillGap userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_JOB_STATS}
            element={
              <ProtectedRoute requireSubscription={true}>
                <JobMarketStats userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_SKILL_RELATIONSHIPS}
            element={
              <ProtectedRoute requireSubscription={true}>
                <SkillRelationships userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_INSIGHTS}
            element={
              <ProtectedRoute requireSubscription={true}>
                <MarketInsights userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_INTERVIEW_PREP}
            element={
              <ProtectedRoute requireSubscription={true}>
                <InterviewPrep userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_COMPANY_INTEL}
            element={
              <ProtectedRoute requireSubscription={true}>
                <CompanyIntel userProfile={userProfile} />
              </ProtectedRoute>
            }
          />

          <Route
            path={ROUTES.MARKET_CAREER_PATH}
            element={
              <ProtectedRoute requireSubscription={true}>
                <CareerPath userProfile={userProfile} />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* ============================================ */}
        {/* ADMIN ROUTES (Admin Access Required)        */}
        {/* ============================================ */}

        <Route
          path={ROUTES.ADMIN}
          element={
            <ProtectedRoute requireAdmin={true}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path={ROUTES.ADMIN_USERS}
          element={
            <ProtectedRoute requireAdmin={true}>
              {/* TODO: Create AdminUsers component */}
              <div className="min-h-screen flex items-center justify-center bg-slate-900">
                <div className="text-white">Admin Users - Coming Soon</div>
              </div>
            </ProtectedRoute>
          }
        />

        <Route
          path={ROUTES.ADMIN_ANALYTICS}
          element={
            <ProtectedRoute requireAdmin={true}>
              {/* TODO: Create AdminAnalytics component */}
              <div className="min-h-screen flex items-center justify-center bg-slate-900">
                <div className="text-white">Admin Analytics - Coming Soon</div>
              </div>
            </ProtectedRoute>
          }
        />

        <Route
          path={ROUTES.ADMIN_JOBS}
          element={
            <ProtectedRoute requireAdmin={true}>
              {/* TODO: Create AdminJobs component */}
              <div className="min-h-screen flex items-center justify-center bg-slate-900">
                <div className="text-white">Admin Jobs - Coming Soon</div>
              </div>
            </ProtectedRoute>
          }
        />

        {/* ============================================ */}
        {/* 404 NOT FOUND - Redirect to Landing         */}
        {/* ============================================ */}

        <Route
          path="*"
          element={<Navigate to={ROUTES.LANDING} replace />}
        />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
