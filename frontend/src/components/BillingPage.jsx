import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CreditCard, Crown, CheckCircle, Download, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { ROUTES } from '../config/routes';
import SpotlightCard from './ui/SpotlightCard';
import ShimmerButton from './ui/ShimmerButton';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const BillingPage = ({ user }) => {
  const navigate = useNavigate();
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');

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

  // Fetch payment method and billing history
  useEffect(() => {
    const fetchBillingData = async () => {
      if (!token || !user || user.subscription_tier === 'free') {
        setLoading(false);
        return;
      }

      try {
        // Fetch payment method
        const pmResponse = await axios.get(`${API_URL}/billing/payment-method`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setPaymentMethod(pmResponse.data.payment_method);

        // Fetch billing history
        const bhResponse = await axios.get(`${API_URL}/billing/history`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setBillingHistory(bhResponse.data.invoices || []);
      } catch (error) {
        console.error('Error fetching billing data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBillingData();
  }, [token, user]);

  // Show loading if no user data yet
  if (!user) {
    return (
      <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="text-center relative z-10">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-300 text-lg relative z-10">Loading billing information...</p>
        </div>
      </div>
    );
  }

  // Map 'premium' to 'pro' for backwards compatibility
  const normalizedPlan = user.subscription_tier === 'premium' ? 'pro' : (user.subscription_tier || 'free');
  const currentPlan = normalizedPlan;
  const features = planFeatures[currentPlan] || planFeatures.free;

  const handleCancelSubscription = async () => {
    try {
      await axios.post(
        `${API_URL}/billing/cancel-subscription`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Subscription will be canceled at the end of the billing period');
      setShowCancelModal(false);
    } catch (error) {
      console.error('Error canceling subscription:', error);
      alert('Failed to cancel subscription. Please try again.');
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="max-w-5xl mx-auto px-4 py-8 relative z-10">
        <h1 className="text-3xl font-bold text-white mb-2 font-display relative z-10">Billing & Subscription</h1>
        <p className="text-gray-400 mb-8 relative z-10">Manage your subscription and payment methods</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Plan - Large Card */}
          <div className="lg:col-span-2 relative z-10">
            <SpotlightCard className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-2xl p-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10"
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
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Credits remaining</span>
                    <span className="text-cyan-400 font-semibold">{user.credits || 0}</span>
                  </div>
                </div>
              )}

              <div className="flex gap-3 relative z-10">
                {currentPlan === 'free' && (
                  <ShimmerButton
                    onClick={() => navigate(ROUTES.PRICING)}
                    className="flex-1"
                  >
                    Upgrade to Pro
                  </ShimmerButton>
                )}
                {currentPlan === 'pro' && (
                  <>
                    <ShimmerButton
                      onClick={() => navigate(ROUTES.PRICING)}
                      className="flex-1"
                    >
                      Upgrade to Elite
                    </ShimmerButton>
                    <button
                      onClick={() => setShowCancelModal(true)}
                      className="px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition relative z-10"
                    >
                      Cancel Plan
                    </button>
                  </>
                )}
                {currentPlan === 'elite' && (
                  <button
                    onClick={() => setShowCancelModal(true)}
                    className="flex-1 px-6 py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition relative z-10"
                  >
                    Cancel Subscription
                  </button>
                )}
              </div>
              </motion.div>
            </SpotlightCard>
          </div>

          {/* Payment Method & Quick Actions */}
          <div className="space-y-6 relative z-10">
            {/* Payment Method Card */}
            {currentPlan !== 'free' && (
              <SpotlightCard className="rounded-2xl p-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="relative z-10"
                >
                <h3 className="text-lg font-semibold text-white mb-4">Payment Method</h3>

                {loading ? (
                  <div className="text-center py-4">
                    <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  </div>
                ) : paymentMethod ? (
                  <div className="mb-4 p-4 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center gap-3 mb-2">
                      <CreditCard className="w-5 h-5 text-cyan-400" />
                      <span className="text-white font-medium capitalize">
                        {paymentMethod.card.brand} •••• {paymentMethod.card.last4}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm">
                      Expires {paymentMethod.card.exp_month}/{paymentMethod.card.exp_year}
                    </p>
                  </div>
                ) : (
                  <div className="mb-4 p-4 bg-slate-900/50 rounded-lg">
                    <p className="text-slate-400 text-sm">No payment method on file</p>
                  </div>
                )}

                <button
                  onClick={() => navigate(ROUTES.PRICING)}
                  className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-sm"
                >
                  Update Payment Method
                </button>
                </motion.div>
              </SpotlightCard>
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
                  <span className="text-slate-400">Current Balance</span>
                  <span className="text-white font-semibold">{user.credits || 0}</span>
                </div>
              </div>

              <button
                onClick={() => navigate(ROUTES.PRICING)}
                className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition text-sm"
              >
                Get More Credits
              </button>
            </motion.div>
          </div>
        </div>

        {/* Billing History */}
        {currentPlan !== 'free' && (
          <SpotlightCard className="mt-6 rounded-2xl p-6 relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="relative z-10"
            >
            <h3 className="text-lg font-semibold text-white mb-4">Billing History</h3>

            {loading ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : billingHistory.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Date</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Description</th>
                      <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Amount</th>
                      <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                      <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Invoice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingHistory.map((invoice) => (
                      <tr key={invoice.id} className="border-b border-slate-700/50 hover:bg-slate-700/20 transition">
                        <td className="py-3 px-4 text-white">{formatDate(invoice.date)}</td>
                        <td className="py-3 px-4 text-slate-300">{invoice.description}</td>
                        <td className="py-3 px-4 text-right text-white font-semibold">
                          ${invoice.amount.toFixed(2)} {invoice.currency}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className={`px-2 py-1 rounded text-xs ${
                            invoice.status === 'paid' ? 'bg-green-500/20 text-green-400' :
                            invoice.status === 'open' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {invoice.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          {invoice.invoice_pdf && (
                            <a
                              href={invoice.invoice_pdf}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-1 ml-auto justify-end"
                            >
                              <Download className="w-4 h-4" />
                              Download
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 relative z-10">
                <p className="text-gray-400 relative z-10">No billing history available</p>
              </div>
            )}
            </motion.div>
          </SpotlightCard>
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
                  onClick={handleCancelSubscription}
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
