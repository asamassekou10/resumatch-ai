import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Rocket, Bell } from 'lucide-react';
import { ROUTES } from '../config/routes';

const ComingSoon = ({ title = "Market Intelligence", description = "We're working hard to bring you powerful market insights and analytics." }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        {/* Coming Soon Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
            <Rocket className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-blue-300">Coming Soon</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {title}
          </h1>

          <p className="text-xl text-gray-400 mb-8">
            {description}
          </p>

          {/* Feature Preview */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm mb-8">
            <div className="space-y-4">
              <div className="flex items-start gap-3 text-left">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Real-Time Market Data</h3>
                  <p className="text-gray-400 text-sm">Stay ahead with live job market trends and salary insights</p>
                </div>
              </div>

              <div className="flex items-start gap-3 text-left">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Skill Gap Analysis</h3>
                  <p className="text-gray-400 text-sm">Identify in-demand skills and close the gap in your expertise</p>
                </div>
              </div>

              <div className="flex items-start gap-3 text-left">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Career Path Planning</h3>
                  <p className="text-gray-400 text-sm">Map your journey with AI-powered career progression insights</p>
                </div>
              </div>

              <div className="flex items-start gap-3 text-left">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Company Intelligence</h3>
                  <p className="text-gray-400 text-sm">Get insider insights on companies and hiring trends</p>
                </div>
              </div>
            </div>
          </div>

          {/* Notification Sign-up */}
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center gap-2 mb-3">
              <Bell className="w-5 h-5 text-blue-400" />
              <h3 className="text-white font-semibold">Get Notified</h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              We'll notify you as soon as Market Intelligence is available!
            </p>
            <p className="text-gray-400 text-xs">
              As a registered user, you'll be among the first to access these features when they launch.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate(ROUTES.DASHBOARD)}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-lg inline-flex items-center justify-center gap-2 transition-all hover:scale-105 active:scale-95"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </button>

            <button
              onClick={() => navigate(ROUTES.ANALYZE)}
              className="px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-semibold rounded-lg transition-all hover:scale-105 active:scale-95"
            >
              Analyze Resume
            </button>
          </div>
        </div>

        {/* Timeline Hint */}
        <div className="text-center">
          <p className="text-gray-500 text-sm">
            Expected launch: Q1 2026
          </p>
        </div>
      </div>
    </div>
  );
};

export default ComingSoon;
