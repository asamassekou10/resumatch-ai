import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Upload, Mail, Calendar, Award, FileText } from 'lucide-react';
import { ROUTES } from '../config/routes';
import SpotlightCard from './ui/SpotlightCard';
import { getCreditsDisplay } from '../utils/credits';

const ProfilePage = ({ user }) => {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');

  // Don't render if no user
  if (!user) {
    return (
      <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <p className="text-gray-400 relative z-10">Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        {/* Page Header */}
        <div className="mb-8 relative z-10">
          <h1 className="text-3xl font-bold text-white mb-2 font-display relative z-10">My Profile</h1>
          <p className="text-gray-400 relative z-10">Manage your account information and view your activity</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Avatar & Quick Stats */}
          <div className="lg:col-span-1">
            {/* Avatar Card */}
            <SpotlightCard className="rounded-2xl p-6 mb-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10"
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
                <div className="grid grid-cols-2 gap-3 mt-4 relative z-10">
                  <div className="bg-white/5 rounded-lg p-3 relative z-10">
                    <p className="text-gray-400 text-xs mb-1 relative z-10">Credits</p>
                    <p className="text-cyan-400 text-lg font-bold font-display relative z-10">{getCreditsDisplay(user.credits, user.subscription_tier || 'free')}</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 relative z-10">
                    <p className="text-gray-400 text-xs mb-1 relative z-10">Plan</p>
                    <p className="text-purple-400 text-lg font-bold capitalize font-display relative z-10">{user.subscription_tier || 'free'}</p>
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
            </SpotlightCard>
          </div>

          {/* Right Column - Profile Details & History */}
          <div className="lg:col-span-2 space-y-6 relative z-10">
            {/* Profile Information Card */}
            <SpotlightCard className="rounded-2xl p-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="relative z-10"
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
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition relative z-10"
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
                  <p className={`py-3 font-semibold ${user.subscription_tier === 'elite' ? 'text-amber-400' : user.subscription_tier === 'pro' ? 'text-cyan-400' : 'text-slate-400'}`}>
                    {user.credits || 0} / {user.subscription_tier === 'elite' ? 1000 : user.subscription_tier === 'pro' ? 100 : 5}
                  </p>
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
            </SpotlightCard>

            {/* Recent Analyses Card */}
            <SpotlightCard className="rounded-2xl p-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="relative z-10"
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
                onClick={() => navigate(ROUTES.DASHBOARD)}
                className="w-full mt-4 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
              >
                View All Analyses
              </button>
              </motion.div>
            </SpotlightCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
