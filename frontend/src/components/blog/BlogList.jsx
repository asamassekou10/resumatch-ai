import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, Clock, ArrowRight } from 'lucide-react';
import SEO from '../common/SEO';
import SpotlightCard from '../ui/SpotlightCard';
import { getRecentBlogPosts } from '../../utils/blogContent';

const BlogList = () => {
  const blogPosts = getRecentBlogPosts(100); // Show all blog posts

  return (
    <>
      <SEO
        title="Resume Tips & Career Advice Blog"
        description="Expert resume tips, ATS optimization guides, and career advice to help you land your dream job. Learn how to create a winning resume that gets interviews."
        keywords="resume tips, career advice, resume blog, ATS optimization, job search tips, resume writing"
        url="https://resumeanalyzerai.com/blog"
      />
      <div className="max-w-6xl mx-auto px-4 py-12 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-display">
            Resume Tips & Career Advice
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Expert guides, industry insights, and proven strategies to help you create a resume that gets interviews.
          </p>
        </motion.div>

        {/* Blog Posts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {blogPosts.map((post, index) => (
            <motion.div
              key={post.slug}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <SpotlightCard className="rounded-xl p-6 h-full flex flex-col hover:scale-105 transition-transform">
                <div className="flex-1">
                  <span className="inline-block px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs text-purple-300 mb-3">
                    {post.category}
                  </span>
                  <h2 className="text-xl font-bold text-white mb-3 font-display line-clamp-2">
                    {post.title}
                  </h2>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(post.datePublished).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      <span>{post.readTime}</span>
                    </div>
                  </div>
                </div>
                <Link
                  to={`/blog/${post.slug}`}
                  className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium text-sm transition"
                >
                  Read More <ArrowRight className="w-4 h-4" />
                </Link>
              </SpotlightCard>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <SpotlightCard className="rounded-xl p-8 bg-gradient-to-r from-purple-500/10 to-blue-600/10 border border-purple-500/20 text-center">
            <h2 className="text-2xl font-bold text-white mb-4 font-display">
              Ready to Optimize Your Resume?
            </h2>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              Put these tips into practice. Get instant AI-powered feedback on your resume and see how it performs against ATS systems.
            </p>
            <Link
              to="/guest-analyze"
              className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold rounded-full transition"
            >
              Analyze Your Resume Free <ArrowRight size={16} />
            </Link>
          </SpotlightCard>
        </motion.div>
      </div>
    </>
  );
};

export default BlogList;


