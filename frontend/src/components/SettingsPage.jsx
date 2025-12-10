import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Bell, Shield, Lock, Globe, Palette, Mail, Smartphone, Download, Trash2, Eye } from 'lucide-react';

const SettingsPage = ({ user }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    // General
    language: 'en',
    timezone: 'America/New_York',
    dateFormat: 'MM/DD/YYYY',
    theme: 'dark',

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

    // Security
    twoFactorEnabled: false,
  });

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400 mb-8">Manage your account preferences and security</p>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-700 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition flex items-center gap-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
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

              <div className="border-t border-slate-700 pt-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Palette className="w-5 h-5 text-cyan-400" />
                  Appearance
                </h3>

                <div className="space-y-3">
                  <label className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900/70 transition">
                    <input
                      type="radio"
                      name="theme"
                      value="dark"
                      checked={settings.theme === 'dark'}
                      onChange={(e) => updateSetting('theme', e.target.value)}
                      className="w-4 h-4 text-cyan-500"
                    />
                    <div className="flex-1">
                      <p className="text-white font-medium">Dark Mode</p>
                      <p className="text-slate-400 text-sm">Recommended for low-light environments</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900/70 transition">
                    <input
                      type="radio"
                      name="theme"
                      value="light"
                      checked={settings.theme === 'light'}
                      onChange={(e) => updateSetting('theme', e.target.value)}
                      className="w-4 h-4 text-cyan-500"
                    />
                    <div className="flex-1">
                      <p className="text-white font-medium">Light Mode</p>
                      <p className="text-slate-400 text-sm">Classic bright interface</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900/70 transition">
                    <input
                      type="radio"
                      name="theme"
                      value="auto"
                      checked={settings.theme === 'auto'}
                      onChange={(e) => updateSetting('theme', e.target.value)}
                      className="w-4 h-4 text-cyan-500"
                    />
                    <div className="flex-1">
                      <p className="text-white font-medium">Auto (System)</p>
                      <p className="text-slate-400 text-sm">Match your system preferences</p>
                    </div>
                  </label>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition">
                  Save Changes
                </button>
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
                    enabled={settings.jobMatches}
                    onChange={(val) => updateSetting('jobMatches', val)}
                    label="Job Match Notifications"
                    description="Receive alerts for new job matches"
                  />
                  <ToggleSwitch
                    enabled={settings.lowCredits}
                    onChange={(val) => updateSetting('lowCredits', val)}
                    label="Low Credit Warnings"
                    description="Alert when credits are running low"
                  />
                  <ToggleSwitch
                    enabled={settings.weeklySummary}
                    onChange={(val) => updateSetting('weeklySummary', val)}
                    label="Weekly Summary"
                    description="Receive weekly activity summary emails"
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

              <div className="flex justify-end pt-4">
                <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition">
                  Save Changes
                </button>
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

              <div className="border-t border-slate-700 pt-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Download className="w-5 h-5 text-cyan-400" />
                  Data Management
                </h3>

                <div className="space-y-3">
                  <button className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition flex items-center justify-center gap-2">
                    <Download className="w-4 h-4" />
                    Download My Data
                  </button>
                  <button className="w-full px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition flex items-center justify-center gap-2">
                    <Trash2 className="w-4 h-4" />
                    Delete Account
                  </button>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition">
                  Save Changes
                </button>
              </div>
            </div>
          )}

          {/* SECURITY SETTINGS */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-cyan-400" />
                  Password & Authentication
                </h3>

                <div className="space-y-4">
                  <button className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-left flex items-center justify-between">
                    <span>Change Password</span>
                    <span className="text-slate-400">→</span>
                  </button>

                  <div className="border-t border-slate-700 pt-4">
                    <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                      <div className="flex-1">
                        <p className="text-white font-medium">Two-Factor Authentication</p>
                        <p className="text-slate-400 text-sm mt-1">Add an extra layer of security to your account</p>
                      </div>
                      <button
                        onClick={() => updateSetting('twoFactorEnabled', !settings.twoFactorEnabled)}
                        className={`px-4 py-2 rounded-lg transition ${
                          settings.twoFactorEnabled
                            ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30'
                            : 'bg-cyan-600 text-white hover:bg-cyan-700'
                        }`}
                      >
                        {settings.twoFactorEnabled ? 'Enabled' : 'Enable'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-700 pt-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Smartphone className="w-5 h-5 text-cyan-400" />
                  Active Sessions
                </h3>

                <div className="space-y-3">
                  <div className="p-4 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">Windows PC • Chrome</p>
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">Current</span>
                    </div>
                    <p className="text-slate-400 text-sm">Last active: Just now</p>
                    <p className="text-slate-400 text-sm">Location: New York, USA</p>
                  </div>

                  <button className="w-full px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition">
                    Sign Out All Other Sessions
                  </button>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;
