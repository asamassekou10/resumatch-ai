import React from 'react';
import { ArrowRight, GraduationCap, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import SpotlightCard from './SpotlightCard';

/**
 * Promotion Banner Component
 *
 * Displays promotional content for free trial and student plans
 * Used in blog posts and PSEO pages to drive conversions
 *
 * @param {Object} props
 * @param {string} props.variant - 'trial' (default) or 'student'
 * @param {string} props.className - Additional CSS classes
 */
const PromotionBanner = ({ variant = 'trial', className = '' }) => {
  const isTrial = variant === 'trial';

  return (
    <div className={`my-8 ${className}`}>
      <SpotlightCard className="rounded-xl overflow-hidden">
        <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Icon */}
            <div className="flex-shrink-0">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                {isTrial ? (
                  <Sparkles className="w-7 h-7 text-white" />
                ) : (
                  <GraduationCap className="w-7 h-7 text-white" />
                )}
              </div>
            </div>

            {/* Content */}
            <div className="flex-1">
              <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">
                {isTrial ? (
                  <>Try Premium Free for 7 Days</>
                ) : (
                  <>Students Save 50% on Premium</>
                )}
              </h3>
              <p className="text-gray-300 text-sm sm:text-base mb-4">
                {isTrial ? (
                  <>
                    Get unlimited resume analyses, AI-powered insights, cover letter generation,
                    and interview prep. No credit card required.
                  </>
                ) : (
                  <>
                    Special student pricing at just <span className="font-bold text-blue-400">$4.99/month</span> with
                    your .edu email. Includes 30 monthly credits and all premium features.
                  </>
                )}
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <Link
                  to={ROUTES.REGISTER}
                  className="group inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
                >
                  {isTrial ? 'Start Free Trial' : 'Get Student Plan'}
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </Link>
                <Link
                  to={ROUTES.PRICING}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white/10 text-white font-semibold rounded-lg hover:bg-white/20 transition-all border border-white/20"
                >
                  View All Plans
                </Link>
              </div>
            </div>
          </div>

          {/* Features List */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
              <div className="flex items-center gap-2 text-gray-300">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <span>Unlimited AI Analysis</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <span>Cover Letter Generator</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <span>Interview Prep</span>
              </div>
            </div>
          </div>
        </div>
      </SpotlightCard>
    </div>
  );
};

export default PromotionBanner;
