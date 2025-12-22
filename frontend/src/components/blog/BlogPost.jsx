import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, Clock, ArrowLeft, ArrowRight } from 'lucide-react';
import SEO from '../common/SEO';
import SpotlightCard from '../ui/SpotlightCard';
import { getBlogPostBySlug, getRecentBlogPosts } from '../../utils/blogContent';
import { generateArticleSchema } from '../../utils/structuredData';
import { ROUTES } from '../../config/routes';

const BlogPost = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const post = getBlogPostBySlug(slug);
  const recentPosts = getRecentBlogPosts(3);

  // Redirect if post not found
  useEffect(() => {
    if (!post) {
      navigate('/blog', { replace: true });
    }
  }, [post, navigate]);

  if (!post) {
    return null;
  }

  // Generate Article schema
  const articleSchema = generateArticleSchema({
    headline: post.title,
    description: post.description,
    datePublished: post.datePublished,
    dateModified: post.dateModified,
    url: `https://resumeanalyzerai.com/blog/${post.slug}`,
    image: post.image,
  });

  // Use full content if available, otherwise use placeholder
  const content = post.content || `
    <p>${post.excerpt}</p>
    <p>This is a placeholder blog post. In production, the full content would be loaded from a markdown file or CMS.</p>
    <h2>Key Takeaways</h2>
    <ul>
      <li>Optimize your resume for ATS systems</li>
      <li>Include relevant keywords for your industry</li>
      <li>Quantify your achievements</li>
      <li>Keep your resume format clean and scannable</li>
    </ul>
    <p>Ready to test your resume? <a href="/guest-analyze" class="text-purple-400 hover:text-purple-300">Try our free resume analyzer</a> to see how your resume performs.</p>
  `;

  return (
    <>
      <SEO
        title={post.title}
        description={post.description}
        keywords={post.keywords}
        url={`https://resumeanalyzerai.com/blog/${post.slug}`}
        structuredData={[articleSchema]}
      />
      <div className="max-w-4xl mx-auto px-4 py-12 relative z-10">
        {/* Back Button */}
        <Link
          to="/blog"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Blog
        </Link>

        {/* Article Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <span className="inline-block px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs text-purple-300 mb-4">
            {post.category}
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-display">
            {post.title}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-400 mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>{new Date(post.datePublished).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{post.readTime}</span>
            </div>
            <span>By {post.author}</span>
          </div>
        </motion.div>

        {/* Article Content */}
        <SpotlightCard className="rounded-xl p-8 mb-8">
          <div
            className="prose prose-invert max-w-none text-gray-300"
            dangerouslySetInnerHTML={{ __html: content }}
            style={{
              '--tw-prose-headings': '#ffffff',
              '--tw-prose-links': '#a78bfa',
            }}
          />
        </SpotlightCard>

        {/* CTA Section */}
        <SpotlightCard className="rounded-xl p-8 bg-gradient-to-r from-purple-500/10 to-blue-600/10 border border-purple-500/20 mb-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4 font-display">
              Ready to Optimize Your Resume?
            </h2>
            <p className="text-gray-400 mb-6">
              Put these tips into practice. Get instant AI-powered feedback on your resume.
            </p>
            <Link
              to={ROUTES.GUEST_ANALYZE}
              className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold rounded-full transition"
            >
              Analyze Your Resume Free <ArrowRight size={16} />
            </Link>
          </div>
        </SpotlightCard>

        {/* Related Posts */}
        {recentPosts.filter(p => p.slug !== post.slug).length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6 font-display">Related Articles</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recentPosts
                .filter(p => p.slug !== post.slug)
                .slice(0, 2)
                .map((relatedPost) => (
                  <Link key={relatedPost.slug} to={`/blog/${relatedPost.slug}`}>
                    <SpotlightCard className="rounded-xl p-6 hover:scale-105 transition-transform">
                      <h3 className="text-lg font-bold text-white mb-2 font-display line-clamp-2">
                        {relatedPost.title}
                      </h3>
                      <p className="text-gray-400 text-sm line-clamp-2">
                        {relatedPost.excerpt}
                      </p>
                    </SpotlightCard>
                  </Link>
                ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default BlogPost;


