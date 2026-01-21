/**
 * 404 Not Found Page
 *
 * SEO-friendly 404 page that:
 * - Returns proper 404 status (handled by server)
 * - Provides helpful navigation options
 * - Suggests related content
 * - Maintains brand consistency
 */

import { Link } from 'react-router-dom';
import { Home, Search, FileText, ArrowRight } from 'lucide-react';
import SEO from './common/SEO';
import ShimmerButton from './ui/ShimmerButton';
import SpotlightCard from './ui/SpotlightCard';
import { ROUTES } from '../config/routes';

const NotFound = () => {
  return (
    <>
      <SEO
        title="Page Not Found (404)"
        description="The page you're looking for doesn't exist. Find resume guides, blog posts, and our AI resume analyzer."
        noindex={true}
      />

      <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />

        <div className="relative z-10 max-w-2xl mx-auto px-4 py-16 text-center">
          {/* 404 Display */}
          <div className="mb-8">
            <span className="text-8xl sm:text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-pink-500 font-display">
              404
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
            Page Not Found
          </h1>

          <p className="text-lg text-gray-400 mb-8 max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
            Let's get you back on track.
          </p>

          {/* Primary CTA */}
          <div className="mb-12">
            <Link to={ROUTES.LANDING}>
              <ShimmerButton>
                <Home className="w-4 h-4 mr-2" />
                Back to Home
              </ShimmerButton>
            </Link>
          </div>

          {/* Helpful Links */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link to={ROUTES.GUEST_ANALYZE}>
              <SpotlightCard className="rounded-xl p-5 h-full hover:border-blue-500/50 transition-all group">
                <div className="flex items-center gap-3">
                  <Search className="w-5 h-5 text-blue-400" />
                  <div className="text-left">
                    <h3 className="text-white font-semibold group-hover:text-blue-400 transition-colors">
                      Analyze Your Resume
                    </h3>
                    <p className="text-sm text-gray-400">
                      Free AI-powered analysis
                    </p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 ml-auto" />
                </div>
              </SpotlightCard>
            </Link>

            <Link to="/blog">
              <SpotlightCard className="rounded-xl p-5 h-full hover:border-blue-500/50 transition-all group">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <div className="text-left">
                    <h3 className="text-white font-semibold group-hover:text-blue-400 transition-colors">
                      Resume Guides
                    </h3>
                    <p className="text-sm text-gray-400">
                      Tips and best practices
                    </p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 ml-auto" />
                </div>
              </SpotlightCard>
            </Link>
          </div>

          {/* Popular Resume Guides */}
          <div className="mt-12 text-left">
            <h2 className="text-lg font-semibold text-white mb-4 font-display">
              Popular Resume Guides
            </h2>
            <div className="flex flex-wrap gap-2">
              {[
                { name: 'Software Engineer', slug: 'software-engineer' },
                { name: 'Registered Nurse', slug: 'registered-nurse' },
                { name: 'Project Manager', slug: 'project-manager' },
                { name: 'Data Analyst', slug: 'data-analyst' }
              ].map((role) => (
                <Link
                  key={role.slug}
                  to={`/resume-for/${role.slug}`}
                  className="px-4 py-2 bg-white/5 border border-white/10 rounded-full text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-all"
                >
                  {role.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NotFound;
