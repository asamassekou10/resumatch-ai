import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CreditCard, Crown, CheckCircle, Download, AlertCircle } from 'lucide-react';
import { ROUTES } from '../config/routes';

const BillingPage = ({ user }) => {
  const navigate = useNavigate();
  const [showCancelModal, setShowCancelModal] = useState(false);

  // Don't render if no user
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <p className="text-slate-400">Please log in to view billing information.</p>
      </div>
    );
  }

  const planFeatures = {
    free: [
      '5 resume analyses per month',
      'Basic AI analysis',
      'Community support',
    ],
    pro: [
      '100 resume analyses per month',
      'Priority AI processing',
      'Advanced market intelligence',
      'Job match recommendations',
      'Interview preparation tools',
      'Email support',
    ],
    elite: [
      '1000 resume analyses per month',
      'Priority AI processing',
      'Advanced market intelligence',
      'Unlimited job matches',
      'Premium interview tools',
      'Dedicated account manager',
      'API access',
      'Priority support',
    ],
  };

  const planPrices = {
    free: 0,
    pro: 9.99,
    elite: 49.99,
  };

  const currentPlan = user.subscription_tier || 'free';
  const features = planFeatures[currentPlan] || planFeatures.free;

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
                    {currentPlan !== 'free' && <Crown className="w-6 h-6 text-yellow-400" />}
                    {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} Plan
                  </h2>
                  <p className="text-3xl font-bold text-cyan-400">
                    ${planPrices[currentPlan].toFixed(2)}
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
                  {features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2 text-slate-300">
                      <CheckCircle className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {currentPlan !== 'free' && (
                <div className="border-t border-slate-700 pt-4 mb-6">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-400">Next billing date</span>
                    <span className="text-white">
                      {user.subscription_end_date
                        ? new Date(user.subscription_end_date).toLocaleDateString()
                        : 'January 8, 2025'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Credits remaining</span>
                    <span className="text-cyan-400 font-semibold">{user.credits || 0}/100</span>
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                {currentPlan === 'free' && (
                  <button
                    onClick={() => navigate(ROUTES.PRICING)}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition"
                  >
                    Upgrade to Pro
                  </button>
                )}
                {currentPlan === 'pro' && (
                  <>
                    <button
                      onClick={() => navigate(ROUTES.PRICING)}
                      className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition"
                    >
                      Upgrade to Elite
                    </button>
                    <button
                      onClick={() => setShowCancelModal(true)}
                      className="px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition"
                    >
                      Cancel Plan
                    </button>
                  </>
                )}
                {currentPlan === 'elite' && (
                  <button
                    onClick={() => setShowCancelModal(true)}
                    className="flex-1 px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition"
                  >
                    Cancel Subscription
                  </button>
                )}
              </div>
            </motion.div>
          </div>

          {/* Payment Method & Quick Actions */}
          <div className="space-y-6">
            {/* Payment Method Card */}
            {currentPlan !== 'free' && (
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
            )}

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
                  <span className="text-white">{100 - (user.credits || 0)}/100</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${((100 - (user.credits || 0)) / 100) * 100}%` }}
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
        {currentPlan !== 'free' && (
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
                    { date: 'Dec 8, 2024', desc: `${currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} Plan Renewal`, amount: `$${planPrices[currentPlan].toFixed(2)}` },
                    { date: 'Nov 8, 2024', desc: `${currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} Plan Renewal`, amount: `$${planPrices[currentPlan].toFixed(2)}` },
                    { date: 'Oct 8, 2024', desc: `${currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} Plan Renewal`, amount: `$${planPrices[currentPlan].toFixed(2)}` },
                  ].map((item, index) => (
                    <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/20 transition">
                      <td className="py-3 px-4 text-white">{item.date}</td>
                      <td className="py-3 px-4 text-slate-300">{item.desc}</td>
                      <td className="py-3 px-4 text-right text-white font-semibold">{item.amount}</td>
                      <td className="py-3 px-4 text-right">
                        <button className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-1 ml-auto">
                          <Download className="w-4 h-4" />
                          Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Cancel Subscription Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-400" />
                </div>
                <h3 className="text-xl font-bold text-white">Cancel Subscription?</h3>
              </div>

              <p className="text-slate-300 mb-6">
                Are you sure you want to cancel your {currentPlan} subscription? You'll lose access to:
              </p>

              <ul className="space-y-2 mb-6">
                {features.slice(0, 3).map((feature, index) => (
                  <li key={index} className="flex items-center gap-2 text-slate-400">
                    <span className="text-red-400">✗</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
                >
                  Keep Subscription
                </button>
                <button
                  onClick={() => {
                    setShowCancelModal(false);
                    // Handle cancellation
                  }}
                  className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
                >
                  Cancel Plan
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingPage;
