import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Bell, Shield, Lock, Globe, Mail, Eye, CreditCard, X, AlertCircle } from 'lucide-react';
import SpotlightCard from './ui/SpotlightCard';
import { ROUTES } from '../config/routes';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const SettingsPage = ({ user }) => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const [activeTab, setActiveTab] = useState('general');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [canceling, setCanceling] = useState(false);
  const [settings, setSettings] = useState({
    // General
    language: 'en',
    timezone: 'America/New_York',
    dateFormat: 'MM/DD/YYYY',

    // Notifications
    emailNotifications: true,
    analysisComplete: true,
    jobMatches: true,
    marketingEmails: false,
    lowCredits: true,
    weeklySummary: true,

    // Privacy
    profileVisibility: 'private',
    resumeHistory: 'private',
    dataSharing: false,
  });

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'subscription', label: 'Subscription', icon: CreditCard },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleCancelSubscription = async () => {
    setCanceling(true);
    try {
      const response = await fetch(`${API_URL}/billing/cancel-subscription`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        alert('Subscription will be canceled at the end of the billing period. You will retain access until then.');
        setShowCancelModal(false);
        // Refresh page to update user data
        window.location.reload();
      } else {
        alert(data.error || 'Failed to cancel subscription. Please try again.');
      }
    } catch (error) {
      console.error('Error canceling subscription:', error);
      alert('Failed to cancel subscription. Please try again.');
    } finally {
      setCanceling(false);
    }
  };

  // Normalize subscription tier
  const normalizedTier = user?.subscription_tier === 'premium' ? 'pro' : (user?.subscription_tier || 'free');
  const hasActiveSubscription = normalizedTier !== 'free' && normalizedTier !== 'weekly_pass' && user?.subscription_status === 'active';
  const isTrialing = user?.subscription_status === 'trialing' || user?.is_trial_active;
  const hasActivePass = user?.weekly_pass?.is_active === true;
  const passInfo = user?.weekly_pass;

  // Toggle Switch Component
  const ToggleSwitch = ({ enabled, onChange, label, description }) => (
    <div className="flex items-center justify-between py-3">
      <div className="flex-1">
        <p className="text-white font-medium">{label}</p>
        {description && <p className="text-slate-400 text-sm mt-1">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
          enabled ? 'bg-cyan-500' : 'bg-slate-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
            enabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="max-w-4xl mx-auto px-4 py-8 relative z-10">
        <h1 className="text-3xl font-bold text-white mb-2 font-display relative z-10">Settings</h1>
        <p className="text-gray-400 mb-8 relative z-10">Manage your account preferences and security</p>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-white/10 overflow-x-auto relative z-10">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition flex items-center gap-2 whitespace-nowrap relative z-10 ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <SpotlightCard className="rounded-2xl p-6 relative z-10">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative z-10"
          >
          {/* GENERAL SETTINGS */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-cyan-400" />
                  Language & Region
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Language</label>
                    <select
                      value={settings.language}
                      onChange={(e) => updateSetting('language', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      <option value="en">English</option>
                      <option value="es">Español</option>
                      <option value="fr">Français</option>
                      <option value="de">Deutsch</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Timezone</label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => updateSetting('timezone', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="UTC">UTC</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Date Format</label>
                    <select
                      value={settings.dateFormat}
                      onChange={(e) => updateSetting('dateFormat', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                </div>
              </div>

            </div>
          )}

          {/* NOTIFICATION SETTINGS */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Mail className="w-5 h-5 text-cyan-400" />
                  Email Notifications
                </h3>

                <div className="space-y-2">
                  <ToggleSwitch
                    enabled={settings.emailNotifications}
                    onChange={(val) => updateSetting('emailNotifications', val)}
                    label="Email Notifications"
                    description="Receive email updates about your account"
                  />
                  <div className="border-t border-slate-700 my-2"></div>
                  <ToggleSwitch
                    enabled={settings.analysisComplete}
                    onChange={(val) => updateSetting('analysisComplete', val)}
                    label="Analysis Complete Alerts"
                    description="Get notified when resume analysis is complete"
                  />
                  <ToggleSwitch
                    enabled={settings.lowCredits}
                    onChange={(val) => updateSetting('lowCredits', val)}
                    label="Low Credit Warnings"
                    description="Alert when credits are running low"
                  />
                  <div className="border-t border-slate-700 my-2"></div>
                  <ToggleSwitch
                    enabled={settings.marketingEmails}
                    onChange={(val) => updateSetting('marketingEmails', val)}
                    label="Marketing Emails"
                    description="Receive product updates and promotions"
                  />
                </div>
              </div>
            </div>
          )}

          {/* PRIVACY SETTINGS */}
          {activeTab === 'privacy' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Eye className="w-5 h-5 text-cyan-400" />
                  Privacy Controls
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Profile Visibility</label>
                    <select
                      value={settings.profileVisibility}
                      onChange={(e) => updateSetting('profileVisibility', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      <option value="public">Public</option>
                      <option value="private">Private</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Resume History Visibility</label>
                    <select
                      value={settings.resumeHistory}
                      onChange={(e) => updateSetting('resumeHistory', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    >
                      <option value="public">Public</option>
                      <option value="private">Private</option>
                    </select>
                  </div>

                  <div className="border-t border-slate-700 pt-4">
                    <ToggleSwitch
                      enabled={settings.dataSharing}
                      onChange={(val) => updateSetting('dataSharing', val)}
                      label="Data Sharing for Improvement"
                      description="Help us improve by sharing anonymized usage data"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SUBSCRIPTION SETTINGS */}
          {activeTab === 'subscription' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-cyan-400" />
                  Subscription & Billing
                </h3>

                <div className="space-y-4">
                  {/* Active 7-Day Pass Banner */}
                  {hasActivePass && passInfo && (
                    <div className="bg-gradient-to-r from-cyan-500/20 to-blue-600/20 rounded-lg p-4 border border-cyan-500/30">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-white font-semibold flex items-center gap-2">
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            7-Day Pass Active
                          </p>
                          <p className="text-cyan-300 text-sm mt-1">
                            {passInfo.days_remaining > 0
                              ? `${passInfo.days_remaining} day${passInfo.days_remaining !== 1 ? 's' : ''} remaining`
                              : `${passInfo.hours_remaining} hour${passInfo.hours_remaining !== 1 ? 's' : ''} remaining`
                            }
                          </p>
                          <p className="text-slate-400 text-xs mt-1">
                            Expires: {new Date(passInfo.expires_at).toLocaleString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-cyan-400 font-bold text-lg">Unlimited Scans</p>
                          <p className="text-slate-400 text-xs">During pass period</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Current Plan */}
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="text-white font-semibold capitalize">
                          {normalizedTier === 'pro_founding' ? 'Pro Founding Member' : normalizedTier === 'weekly_pass' ? '7-Day Pass' : normalizedTier} Plan
                        </p>
                        {isTrialing && (
                          <p className="text-blue-400 text-sm mt-1">
                            Free Trial Active {user?.trial_end_date && `- Ends ${new Date(user.trial_end_date).toLocaleDateString()}`}
                          </p>
                        )}
                        {hasActiveSubscription && !isTrialing && (
                          <p className="text-green-400 text-sm mt-1">Active Subscription</p>
                        )}
                        {normalizedTier === 'free' && !hasActivePass && (
                          <p className="text-slate-400 text-sm mt-1">Free tier with {user?.credits || 0} credits</p>
                        )}
                        {normalizedTier === 'free' && hasActivePass && (
                          <p className="text-green-400 text-sm mt-1">7-Day Pass Active - Unlimited scans!</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-white font-bold">
                          {normalizedTier === 'free' ? '$0' : normalizedTier === 'weekly_pass' ? '$6.99' : normalizedTier === 'pro_founding' ? '$19.99' : normalizedTier === 'pro' ? '$24.99' : '$49.99'}
                          {normalizedTier !== 'free' && normalizedTier !== 'weekly_pass' && <span className="text-slate-400 text-sm font-normal">/month</span>}
                          {normalizedTier === 'weekly_pass' && <span className="text-slate-400 text-sm font-normal">/week</span>}
                        </p>
                      </div>
                    </div>

                    {normalizedTier !== 'free' && (
                      <div className="mt-4 pt-4 border-t border-slate-700">
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-slate-400">Credits Remaining</span>
                          <span className="text-cyan-400 font-semibold">{user?.credits || 0}</span>
                        </div>
                      </div>
                    )}

                    <div className="mt-4 flex flex-wrap gap-3">
                      {normalizedTier === 'free' && !hasActivePass && (
                        <>
                          <button
                            onClick={() => navigate(ROUTES.PRICING)}
                            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold rounded-lg transition"
                          >
                            Get 7-Day Pass - $6.99
                          </button>
                          <button
                            onClick={() => navigate(ROUTES.PRICING)}
                            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition"
                          >
                            View All Plans
                          </button>
                        </>
                      )}
                      {normalizedTier === 'free' && hasActivePass && (
                        <button
                          onClick={() => navigate(ROUTES.ANALYZE)}
                          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold rounded-lg transition"
                        >
                          Start Analyzing
                        </button>
                      )}
                      {(hasActiveSubscription || isTrialing) && (
                        <button
                          onClick={() => setShowCancelModal(true)}
                          className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 font-semibold rounded-lg transition border border-red-600/30"
                        >
                          Cancel Subscription
                        </button>
                      )}
                      <button
                        onClick={() => navigate(ROUTES.BILLING)}
                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition"
                      >
                        View Billing Details
                      </button>
                    </div>
                  </div>

                  {/* Subscription Info */}
                  {normalizedTier !== 'free' && (
                    <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                      <p className="text-slate-400 text-sm mb-2">
                        {isTrialing ? (
                          <>
                            Your 7-day free trial includes 10 credits. After the trial ends on{' '}
                            {user?.trial_end_date ? new Date(user.trial_end_date).toLocaleDateString() : 'the end of your trial period'},
                            {' '}your subscription will automatically begin and you'll be charged monthly.
                          </>
                        ) : (
                          <>
                            Your subscription is active and will automatically renew each month.
                            {user?.subscription_start_date && ` Started on ${new Date(user.subscription_start_date).toLocaleDateString()}.`}
                          </>
                        )}
                      </p>
                      <p className="text-slate-500 text-xs mt-2">
                        You can cancel anytime and retain access until the end of your billing period.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SECURITY SETTINGS */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-cyan-400" />
                  Security
                </h3>
                <p className="text-slate-400">
                  Security features are coming soon. You can currently manage your password through your profile settings.
                </p>
              </div>
            </div>
          )}
          </motion.div>
        </SpotlightCard>

        {/* Cancel Subscription Modal */}
        <AnimatePresence>
          {showCancelModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-slate-800 rounded-xl p-6 max-w-md w-full mx-4 border border-slate-700"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">Cancel Subscription</h3>
                  <button
                    onClick={() => setShowCancelModal(false)}
                    className="p-1 hover:bg-slate-700 rounded-lg transition"
                  >
                    <X className="w-5 h-5 text-slate-400" />
                  </button>
                </div>

                <div className="mb-6">
                  <div className="flex items-start gap-3 mb-4">
                    <AlertCircle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-white font-medium mb-2">Are you sure you want to cancel?</p>
                      <p className="text-slate-400 text-sm">
                        Your subscription will remain active until the end of your current billing period.
                        {isTrialing && user?.trial_end_date && (
                          <> Your trial ends on {new Date(user.trial_end_date).toLocaleDateString()}.</>
                        )}
                        {' '}After that, you'll be downgraded to the free plan.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowCancelModal(false)}
                    className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition"
                  >
                    Keep Subscription
                  </button>
                  <button
                    onClick={handleCancelSubscription}
                    disabled={canceling}
                    className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {canceling ? 'Canceling...' : 'Cancel Subscription'}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SettingsPage;
