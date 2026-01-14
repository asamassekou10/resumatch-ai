import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const StripeCheckout = ({ token, navigate: parentNavigate }) => {
  const [searchParams] = useSearchParams();
  const routerNavigate = useNavigate();
  const navigate = parentNavigate || routerNavigate;
  const tier = searchParams.get('tier') || 'pro_founding';
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const createCheckoutSession = async () => {
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(
          `${API_URL}/payments/create-checkout-session?tier=${tier}`,
          {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to create checkout session');
        }

        const data = await response.json();
        
        if (data.checkout_url) {
          // Redirect to Stripe's hosted checkout page
          window.location.href = data.checkout_url;
        } else {
          throw new Error('No checkout URL received');
        }
      } catch (err) {
        setError(err.message || 'Failed to start checkout. Please try again.');
        setLoading(false);
      }
    };

    createCheckoutSession();
  }, [tier, token, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-cyan-400 mx-auto mb-4" />
          <p className="text-white text-lg font-semibold mb-2">Redirecting to secure checkout...</p>
          <p className="text-slate-400 text-sm">You'll be redirected to Stripe's secure payment page</p>
        </div>
      </div>
    );
    }

  if (error) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => navigate('/pricing')}
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Pricing
          </button>
          <div className="bg-red-900/20 border border-red-700 rounded-xl p-6">
            <h3 className="text-red-400 font-semibold mb-2 text-lg">Checkout Error</h3>
            <p className="text-red-300 text-sm mb-4">{error}</p>
                <button
                  onClick={() => navigate('/pricing')}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold text-sm transition"
                >
              Return to Pricing
                </button>
        </div>
      </div>
    </div>
  );
  }

  return null;
};

export default StripeCheckout;
