/**
 * Internal Links Component
 *
 * Implements hub-and-spoke internal linking structure for SEO.
 * Features:
 * - Related roles from same industry (spoke-to-spoke)
 * - Industry hub link (spoke-to-hub)
 * - Related blog content
 * - Strategic anchor text optimization
 */

import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Briefcase, ExternalLink } from 'lucide-react';
import SpotlightCard from '../ui/SpotlightCard';

/**
 * Related Roles Section
 * Links to other roles in the same industry
 */
export const RelatedRolesSection = ({ roles = [], currentRole = '' }) => {
  if (!roles || roles.length === 0) return null;

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-white mb-6 font-display">
        Related Career Paths
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {roles.map((role) => (
          <Link
            key={role.url}
            to={role.url}
            className="group"
          >
            <SpotlightCard className="rounded-xl p-5 h-full hover:border-blue-500/50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors font-display">
                    {role.name}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    {role.industry} Industry
                  </p>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all flex-shrink-0" />
              </div>
            </SpotlightCard>
          </Link>
        ))}
      </div>
    </div>
  );
};

/**
 * Industry Hub Link
 * Links back to the industry category page
 */
export const IndustryHubLink = ({ hub }) => {
  if (!hub) return null;

  return (
    <Link
      to={hub.url}
      className="group inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full text-blue-300 hover:bg-blue-500/20 transition-all mb-6"
    >
      <Briefcase className="w-4 h-4" />
      <span>Browse all {hub.name}</span>
      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
    </Link>
  );
};

/**
 * Related Blog Posts Section
 * Contextual links to relevant blog content
 */
export const RelatedBlogSection = ({ posts = [] }) => {
  if (!posts || posts.length === 0) return null;

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-white mb-6 font-display flex items-center gap-2">
        <BookOpen className="w-6 h-6 text-blue-400" />
        Related Guides & Articles
      </h2>
      <div className="space-y-4">
        {posts.map((post) => (
          <Link
            key={post.url}
            to={post.url}
            className="group block"
          >
            <SpotlightCard className="rounded-xl p-5 hover:border-blue-500/50 transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-blue-400 uppercase tracking-wider">
                    {post.category}
                  </span>
                  <h3 className="text-white font-semibold group-hover:text-blue-400 transition-colors mt-1">
                    {post.title}
                  </h3>
                </div>
                <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-blue-400 flex-shrink-0" />
              </div>
            </SpotlightCard>
          </Link>
        ))}
      </div>
    </div>
  );
};

/**
 * Complete Internal Links Section
 * Combines all internal linking elements
 */
const InternalLinks = ({
  hub = null,
  relatedRoles = [],
  relatedPosts = [],
  currentRole = ''
}) => {
  const hasContent = hub || relatedRoles.length > 0 || relatedPosts.length > 0;

  if (!hasContent) return null;

  return (
    <div className="border-t border-white/10 pt-12 mt-12">
      {hub && <IndustryHubLink hub={hub} />}
      {relatedRoles.length > 0 && (
        <RelatedRolesSection roles={relatedRoles} currentRole={currentRole} />
      )}
      {relatedPosts.length > 0 && (
        <RelatedBlogSection posts={relatedPosts} />
      )}
    </div>
  );
};

export default InternalLinks;
