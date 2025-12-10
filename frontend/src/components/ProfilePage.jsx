import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Upload, Mail, Calendar, Award, FileText } from 'lucide-react';

const ProfilePage = ({ user, setView }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');

  // Don't render if no user
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <p className="text-slate-400">Please log in to view your profile.</p>
      </div>
    );
  }

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
                    {user.name?.charAt(0).toUpperCase() || 'U'}
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
                    <p className="text-cyan-400 text-lg font-bold">{user.credits || 0}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <p className="text-slate-400 text-xs mb-1">Plan</p>
                    <p className="text-purple-400 text-lg font-bold capitalize">{user.subscription_tier || 'free'}</p>
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
                    {user.subscription_tier || 'free'} Plan
                  </p>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Credits Remaining</label>
                  <p className="text-cyan-400 py-3 font-semibold">{user.credits || 0} / 100</p>
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
