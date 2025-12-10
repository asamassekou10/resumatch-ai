# User Pages Implementation Plan
## Profile, Settings, Billing & Help Pages

## 🎯 Overview

This plan covers the implementation of 4 essential user-facing pages that are currently missing but referenced in the navigation:

1. **Profile Page** - User profile management
2. **Settings Page** - Application preferences and account settings
3. **Billing & Subscription Page** - Payment and subscription management
4. **Help & Documentation Page** - Support and guides

All pages will follow the existing design system:
- **Colors**: Cyan (#06b6d4), Purple (#a855f7), Slate dark theme
- **Style**: Glass morphism, modern SaaS aesthetic
- **Framework**: React, Tailwind CSS, Framer Motion

---

## 1. 👤 PROFILE PAGE

### Purpose
Allow users to view and edit their personal information, upload profile picture, and manage their resume history.

### Design Specifications

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│  Navigation (sticky)                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌─────────────────────────────────┐   │
│  │                │  │  Profile Information            │   │
│  │   Avatar       │  │  ─────────────────────────────  │   │
│  │   Upload       │  │  Name: [Input Field]            │   │
│  │                │  │  Email: email@example.com       │   │
│  │   [Change]     │  │  Member Since: Jan 2024         │   │
│  │                │  │  Plan: Pro                      │   │
│  └────────────────┘  │                                 │   │
│                      │  ─────────────────────────────  │   │
│                      │  [Update Profile]               │   │
│                      └─────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Resume Analysis History                              │  │
│  │  ──────────────────────────────────────────────────── │  │
│  │  📄 Resume_v3.pdf          Score: 87%   Dec 8, 2024  │  │
│  │  📄 Resume_final.docx       Score: 92%   Dec 4, 2024  │  │
│  │  📄 Resume_updated.pdf      Score: 85%   Nov 30, 2024 │  │
│  │                                                        │  │
│  │  [View All Analyses]                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Account Statistics                                    │  │
│  │  ──────────────────────────────────────────────────── │  │
│  │  Total Analyses: 23    Credits Used: 65/100          │  │
│  │  Avg Score: 88%        Job Matches: 45               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Components to Create

**File**: `frontend/src/components/ProfilePage.jsx`

```jsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Upload, Mail, Calendar, Award, FileText, TrendingUp } from 'lucide-react';

const ProfilePage = ({ user, setView }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user.name);
  const [profileImage, setProfileImage] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">My Profile</h1>
          <p className="text-slate-400">Manage your account information and view your activity</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Avatar & Quick Stats */}
          <div className="lg:col-span-1">
            {/* Avatar Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 mb-6"
            >
              <div className="text-center">
                {/* Avatar */}
                <div className="relative inline-block mb-4">
                  <div className="w-32 h-32 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-white text-4xl font-bold">
                    {user.name?.charAt(0).toUpperCase()}
                  </div>
                  <button className="absolute bottom-0 right-0 bg-cyan-500 hover:bg-cyan-600 text-white p-2 rounded-full transition">
                    <Upload className="w-4 h-4" />
                  </button>
                </div>

                <h2 className="text-xl font-semibold text-white mb-1">{user.name}</h2>
                <p className="text-slate-400 text-sm mb-4">{user.email}</p>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <p className="text-slate-400 text-xs mb-1">Credits</p>
                    <p className="text-cyan-400 text-lg font-bold">{user.credits}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <p className="text-slate-400 text-xs mb-1">Plan</p>
                    <p className="text-purple-400 text-lg font-bold capitalize">{user.subscription_tier}</p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Account Info Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-cyan-400" />
                Account Info
              </h3>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Member Since</span>
                  <span className="text-white">{new Date(user.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Analyses</span>
                  <span className="text-white">23</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Average Score</span>
                  <span className="text-cyan-400 font-semibold">88%</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right Column - Profile Details & History */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <User className="w-5 h-5 text-cyan-400" />
                  Profile Information
                </h3>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="px-4 py-2 text-sm bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition"
                >
                  {isEditing ? 'Cancel' : 'Edit Profile'}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Full Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500 transition"
                    />
                  ) : (
                    <p className="text-white py-3">{user.name}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Email Address</label>
                  <p className="text-slate-500 py-3 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {user.email}
                  </p>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Subscription Plan</label>
                  <p className="text-white py-3 capitalize flex items-center gap-2">
                    <Award className="w-4 h-4 text-purple-400" />
                    {user.subscription_tier} Plan
                  </p>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Credits Remaining</label>
                  <p className="text-cyan-400 py-3 font-semibold">{user.credits} / 100</p>
                </div>
              </div>

              {isEditing && (
                <div className="mt-6 flex gap-3">
                  <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition">
                    Save Changes
                  </button>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </motion.div>

            {/* Recent Analyses Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                Recent Resume Analyses
              </h3>

              <div className="space-y-3">
                {[
                  { name: 'Resume_v3.pdf', score: 87, date: 'Dec 8, 2024' },
                  { name: 'Resume_final.docx', score: 92, date: 'Dec 4, 2024' },
                  { name: 'Resume_updated.pdf', score: 85, date: 'Nov 30, 2024' },
                ].map((analysis, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900/70 transition cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-slate-400" />
                      <div>
                        <p className="text-white font-medium">{analysis.name}</p>
                        <p className="text-slate-400 text-sm">{analysis.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm text-slate-400">Score</p>
                        <p className="text-cyan-400 font-bold">{analysis.score}%</p>
                      </div>
                      <button className="text-cyan-400 hover:text-cyan-300">
                        View →
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setView('dashboard')}
                className="w-full mt-4 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
              >
                View All Analyses
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
```

### Features to Implement
- ✅ Avatar upload (with image cropping)
- ✅ Profile information editing
- ✅ Recent resume analyses list
- ✅ Account statistics
- ✅ Responsive design

---

## 2. ⚙️ SETTINGS PAGE

### Purpose
Allow users to configure application preferences, notification settings, privacy options, and account security.

### Design Specifications

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [General] [Notifications] [Privacy] [Security]         │  ← Tabs
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  GENERAL SETTINGS                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Language             [English ▼]                   │ │
│  │ Timezone            [UTC-5 (EST) ▼]                │ │
│  │ Date Format         [MM/DD/YYYY ▼]                 │ │
│  │                                                     │ │
│  │ THEME                                               │ │
│  │ [●] Dark Mode (Recommended)                         │ │
│  │ [ ] Light Mode                                      │ │
│  │ [ ] Auto (System)                                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  NOTIFICATIONS                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ [✓] Email notifications                             │ │
│  │ [✓] Analysis complete alerts                        │ │
│  │ [✓] Job match notifications                         │ │
│  │ [ ] Marketing emails                                │ │
│  │ [✓] Low credit warnings                             │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [Save Changes]                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Component Structure

**File**: `frontend/src/components/SettingsPage.jsx`

```jsx
const SettingsPage = ({ user }) => {
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400 mb-8">Manage your account preferences</p>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition flex items-center gap-2 ${
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
          {activeTab === 'general' && <GeneralSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
          {activeTab === 'privacy' && <PrivacySettings />}
          {activeTab === 'security' && <SecuritySettings />}
        </motion.div>
      </div>
    </div>
  );
};
```

### Settings Sections

#### 1. General Settings
- Language selection
- Timezone
- Date/time format
- Theme (Dark/Light/Auto)
- Default resume format

#### 2. Notification Settings
- Email notifications toggle
- Analysis complete alerts
- Job match notifications
- Low credit warnings
- Marketing emails opt-in/out
- Weekly summary emails

#### 3. Privacy Settings
- Profile visibility
- Resume history privacy
- Data sharing preferences
- Download my data
- Delete account

#### 4. Security Settings
- Change password
- Two-factor authentication (2FA)
- Active sessions
- Login history
- Connected devices

---

## 3. 💳 BILLING & SUBSCRIPTION PAGE

### Purpose
Manage subscription plans, payment methods, billing history, and credits.

### Design Specifications

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│  💳 Billing & Subscription                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CURRENT PLAN                                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  👑 Pro Plan                     $9.99/month       │ │
│  │  ─────────────────────────────────────────────────│ │
│  │  • 100 resume analyses per month                  │ │
│  │  • Priority AI processing                          │ │
│  │  • Advanced market insights                        │ │
│  │  • Email support                                   │ │
│  │                                                     │ │
│  │  Next billing date: Jan 8, 2025                   │ │
│  │  Credits remaining: 85/100                         │ │
│  │                                                     │ │
│  │  [Upgrade to Elite] [Cancel Subscription]          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  PAYMENT METHOD                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  💳 Visa ending in 4242                            │ │
│  │  Expires 12/2026                                   │ │
│  │  [Update Payment Method]                            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  BILLING HISTORY                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Dec 8, 2024  Pro Plan Renewal    $9.99  [Invoice]│ │
│  │  Nov 8, 2024  Pro Plan Renewal    $9.99  [Invoice]│ │
│  │  Oct 8, 2024  Pro Plan Renewal    $9.99  [Invoice]│ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Component Structure

**File**: `frontend/src/components/BillingPage.jsx`

```jsx
const BillingPage = ({ user, setView }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-2">Billing & Subscription</h1>
        <p className="text-slate-400 mb-8">Manage your subscription and payment methods</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Plan - Large Card */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-cyan-500/10 to-purple-600/10 border border-cyan-500/20 rounded-2xl p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-1">
                    <Crown className="w-6 h-6 text-yellow-400" />
                    {user.subscription_tier === 'pro' ? 'Pro Plan' : 'Elite Plan'}
                  </h2>
                  <p className="text-3xl font-bold text-cyan-400">
                    ${user.subscription_tier === 'pro' ? '9.99' : '49.99'}
                    <span className="text-lg text-slate-400">/month</span>
                  </p>
                </div>
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                  Active
                </span>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-semibold text-slate-400 mb-3">Plan Features</h3>
                <ul className="space-y-2">
                  {[
                    '100 resume analyses per month',
                    'Priority AI processing',
                    'Advanced market intelligence',
                    'Job match recommendations',
                    'Interview preparation tools',
                    'Email support',
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-2 text-slate-300">
                      <CheckCircle className="w-4 h-4 text-cyan-400" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="border-t border-slate-700 pt-4 mb-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Next billing date</span>
                  <span className="text-white">January 8, 2025</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Credits remaining</span>
                  <span className="text-cyan-400 font-semibold">{user.credits}/100</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setView('pricing')}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition"
                >
                  Upgrade to Elite
                </button>
                <button className="px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition">
                  Cancel Plan
                </button>
              </div>
            </motion.div>
          </div>

          {/* Payment Method & Quick Actions */}
          <div className="space-y-6">
            {/* Payment Method Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">Payment Method</h3>

              <div className="mb-4 p-4 bg-slate-900/50 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <CreditCard className="w-5 h-5 text-cyan-400" />
                  <span className="text-white font-medium">Visa •••• 4242</span>
                </div>
                <p className="text-slate-400 text-sm">Expires 12/2026</p>
              </div>

              <button className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-sm">
                Update Payment Method
              </button>
            </motion.div>

            {/* Credits Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">Credits</h3>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Used this month</span>
                  <span className="text-white">{100 - user.credits}/100</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-purple-600 h-2 rounded-full"
                    style={{ width: `${((100 - user.credits) / 100) * 100}%` }}
                  ></div>
                </div>
              </div>

              <button className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition text-sm">
                Purchase Credits
              </button>
            </motion.div>
          </div>
        </div>

        {/* Billing History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6 bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Billing History</h3>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Description</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Amount</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Invoice</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { date: 'Dec 8, 2024', desc: 'Pro Plan Renewal', amount: '$9.99' },
                  { date: 'Nov 8, 2024', desc: 'Pro Plan Renewal', amount: '$9.99' },
                  { date: 'Oct 8, 2024', desc: 'Pro Plan Renewal', amount: '$9.99' },
                ].map((item, index) => (
                  <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                    <td className="py-3 px-4 text-white">{item.date}</td>
                    <td className="py-3 px-4 text-slate-300">{item.desc}</td>
                    <td className="py-3 px-4 text-right text-white font-semibold">{item.amount}</td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 text-sm">
                        Download →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
```

### Features
- ✅ Current plan overview with features list
- ✅ Upgrade/downgrade options
- ✅ Cancel subscription
- ✅ Payment method management
- ✅ Credits tracker
- ✅ Billing history with downloadable invoices
- ✅ Purchase additional credits

---

## 4. ❓ HELP & DOCUMENTATION PAGE

### Purpose
Provide comprehensive help, FAQs, guides, and support options.

### Design Specifications

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│  ❓ Help & Documentation                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Search for help...                          🔍]  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  POPULAR TOPICS                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │ 📄 Getting │ │ 💳 Billing │ │ 🎯 Resume  │          │
│  │   Started  │ │  & Plans   │ │  Tips      │          │
│  └────────────┘ └────────────┘ └────────────┘          │
│                                                          │
│  FREQUENTLY ASKED QUESTIONS                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ▼ How do I analyze my resume?                      │ │
│  │   To analyze your resume, click...                 │ │
│  │                                                     │ │
│  │ ▸ What formats are supported?                      │ │
│  │ ▸ How do I get more credits?                       │ │
│  │ ▸ What is the job matching feature?                │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  CONTACT SUPPORT                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 📧 Email: support@resumeanalyzerai.com             │ │
│  │ 💬 Live Chat (Pro/Elite users)                     │ │
│  │ 📚 Documentation                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Component Structure

**File**: `frontend/src/components/HelpPage.jsx`

```jsx
const HelpPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);

  const categories = [
    {
      icon: '📄',
      title: 'Getting Started',
      articles: 5,
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: '💳',
      title: 'Billing & Plans',
      articles: 8,
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: '🎯',
      title: 'Resume Tips',
      articles: 12,
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: '🤖',
      title: 'AI Features',
      articles: 6,
      color: 'from-yellow-500 to-orange-500'
    },
  ];

  const faqs = [
    {
      question: 'How do I analyze my resume?',
      answer: 'To analyze your resume, go to the Dashboard and click "Analyze Resume". Upload your resume file (PDF, DOCX, or TXT), optionally add a job description, and click "Analyze". You\'ll receive detailed feedback within seconds.'
    },
    {
      question: 'What file formats are supported?',
      answer: 'We support PDF (.pdf), Microsoft Word (.docx), and plain text (.txt) files. For best results, we recommend using PDF format.'
    },
    {
      question: 'How do I get more credits?',
      answer: 'Credits are included with your subscription plan. Free users get 5 credits, Pro users get 100 credits per month, and Elite users get 1000 credits. You can also purchase additional credits from the Billing page.'
    },
    {
      question: 'What is the job matching feature?',
      answer: 'Our AI-powered job matching analyzes your resume and finds relevant job opportunities from our database. It scores each match based on your skills, experience, and the job requirements.'
    },
    {
      question: 'How accurate is the AI analysis?',
      answer: 'Our AI is trained on thousands of successful resumes and hiring patterns. It provides industry-standard feedback with 95%+ accuracy. However, we recommend using it as a guide alongside professional resume services.'
    },
    {
      question: 'Can I cancel my subscription anytime?',
      answer: 'Yes! You can cancel your subscription at any time from the Billing page. You\'ll retain access to your plan until the end of your current billing period.'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">How can we help you?</h1>
          <p className="text-slate-400 mb-8">Search our knowledge base or browse categories below</p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <input
              type="text"
              placeholder="Search for help..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-6 py-4 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition pr-12"
            />
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          </div>
        </div>

        {/* Categories */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Browse by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((category, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-cyan-500/50 transition cursor-pointer group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${category.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition`}>
                  {category.icon}
                </div>
                <h3 className="text-white font-semibold mb-2">{category.title}</h3>
                <p className="text-slate-400 text-sm">{category.articles} articles</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                  className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-slate-700/30 transition"
                >
                  <span className="text-white font-medium">{faq.question}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-cyan-400 transition-transform ${
                      expandedFaq === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {expandedFaq === index && (
                  <div className="px-6 pb-4">
                    <p className="text-slate-300 leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Contact Support */}
        <div className="bg-gradient-to-r from-cyan-500/10 to-purple-600/10 border border-cyan-500/20 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Still need help?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Email Support</h3>
              <p className="text-slate-400 text-sm mb-3">We'll respond within 24 hours</p>
              <a href="mailto:support@resumeanalyzerai.com" className="text-cyan-400 hover:text-cyan-300">
                support@resumeanalyzerai.com
              </a>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Live Chat</h3>
              <p className="text-slate-400 text-sm mb-3">Pro & Elite users only</p>
              <button className="text-purple-400 hover:text-purple-300">
                Start Chat →
              </button>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Documentation</h3>
              <p className="text-slate-400 text-sm mb-3">Comprehensive guides</p>
              <button className="text-green-400 hover:text-green-300">
                Browse Docs →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Features
- ✅ Search functionality
- ✅ Category browsing
- ✅ Expandable FAQs
- ✅ Contact support options
- ✅ Links to documentation
- ✅ Live chat (for Pro/Elite users)

---

## 📅 IMPLEMENTATION TIMELINE

### Phase 1: Core Pages (Week 1)
**Days 1-2: Profile Page**
- Create ProfilePage component
- Implement avatar upload
- Profile editing functionality
- Recent analyses list
- Account statistics

**Days 3-4: Settings Page**
- Create SettingsPage component
- Tab navigation
- General settings
- Notification preferences
- Privacy controls
- Security settings

### Phase 2: Billing & Help (Week 2)
**Days 5-6: Billing Page**
- Create BillingPage component
- Current plan display
- Payment method management
- Billing history table
- Upgrade/downgrade flows
- Cancel subscription

**Day 7: Help Page**
- Create HelpPage component
- Search functionality
- Category cards
- FAQ accordion
- Contact support section

### Phase 3: Integration & Testing (Week 2)
**Day 8: Integration**
- Wire up all pages to App.jsx routing
- Connect to backend APIs
- User data fetching

**Day 9: Testing**
- Test all pages on desktop
- Test on mobile devices
- Fix responsive issues
- Test user flows

**Day 10: Polish**
- Add animations
- Loading states
- Error handling
- Final UX improvements

---

## 🔌 BACKEND API REQUIREMENTS

### Profile Endpoints
```python
# Update profile
PUT /api/user/profile
Body: { name, avatar_url }

# Get user statistics
GET /api/user/stats
Response: { total_analyses, avg_score, total_credits_used }

# Upload avatar
POST /api/user/avatar
Body: FormData with image file
```

### Settings Endpoints
```python
# Get user settings
GET /api/user/settings

# Update settings
PUT /api/user/settings
Body: { language, timezone, theme, notifications }

# Update password
POST /api/user/change-password
Body: { current_password, new_password }
```

### Billing Endpoints
```python
# Get subscription details
GET /api/subscription/current

# Get billing history
GET /api/billing/history

# Update payment method (Stripe)
POST /api/billing/update-payment-method
Body: { payment_method_id }

# Cancel subscription
DELETE /api/subscription/cancel
```

---

## 🎨 SHARED COMPONENTS TO CREATE

### 1. PageHeader Component
```jsx
const PageHeader = ({ title, subtitle, icon: Icon }) => (
  <div className="mb-8">
    <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
      {Icon && <Icon className="w-8 h-8 text-cyan-400" />}
      {title}
    </h1>
    <p className="text-slate-400">{subtitle}</p>
  </div>
);
```

### 2. Card Component
```jsx
const Card = ({ children, className = '', gradient = false }) => (
  <div className={`
    ${gradient
      ? 'bg-gradient-to-br from-cyan-500/10 to-purple-600/10 border-cyan-500/20'
      : 'bg-slate-800/50'}
    backdrop-blur-sm border border-slate-700 rounded-2xl p-6
    ${className}
  `}>
    {children}
  </div>
);
```

### 3. ToggleSwitch Component
```jsx
const ToggleSwitch = ({ enabled, onChange, label }) => (
  <div className="flex items-center justify-between">
    <span className="text-white">{label}</span>
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
```

---

## ✅ TESTING CHECKLIST

### Profile Page
- [ ] Avatar upload works
- [ ] Profile editing saves correctly
- [ ] Recent analyses load
- [ ] Statistics display correctly
- [ ] Responsive on mobile

### Settings Page
- [ ] All tabs switch correctly
- [ ] Settings save to backend
- [ ] Toggle switches work
- [ ] Password change works
- [ ] 2FA setup works

### Billing Page
- [ ] Current plan displays correctly
- [ ] Payment method updates
- [ ] Billing history loads
- [ ] Invoices download
- [ ] Subscription cancellation works
- [ ] Upgrade flow works

### Help Page
- [ ] Search returns results
- [ ] FAQs expand/collapse
- [ ] Category links work
- [ ] Contact forms work
- [ ] Live chat initiates

---

## 🚀 DEPLOYMENT

After implementation:

1. **Test locally**: http://localhost:3000
2. **Build**: `npm run build`
3. **Commit & Push**: Git workflow
4. **Deploy to Render**: Automatic deployment
5. **Test in production**: Verify all pages work

---

## 📊 SUCCESS METRICS

- ✅ All 4 pages functional
- ✅ Mobile responsive
- ✅ < 3s page load time
- ✅ No console errors
- ✅ Matches design system
- ✅ User flows complete

---

Ready to implement? This plan provides everything needed to build professional, modern pages that match your current design!
