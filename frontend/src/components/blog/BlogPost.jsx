import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Calendar, Clock, ArrowLeft, ArrowRight, FileText } from 'lucide-react';
import SEO from '../common/SEO';
import SpotlightCard from '../ui/SpotlightCard';
import ShimmerButton from '../ui/ShimmerButton';
import { getBlogPostBySlug, getRecentBlogPosts } from '../../utils/blogContent';
import { generateArticleSchema } from '../../utils/structuredData';
import { ROUTES } from '../../config/routes';
import TableOfContents from './TableOfContents';
import BlogContentRenderer from '../../utils/blogContentRenderer';

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
  const content = post.content || (() => (
    <>
      <p>{post.excerpt}</p>
      <p>This is a placeholder blog post. In production, the full content would be loaded from a markdown file or CMS.</p>
    </>
  ));
  
  // For TableOfContents, we need to handle both HTML strings and JSX functions
  // If content is a function, TableOfContents will parse the rendered DOM
  // If content is a string, pass it directly
  const contentForTOC = typeof content === 'string' ? content : '';

  return (
    <>
      <SEO
        title={post.title}
        description={post.description}
        keywords={post.keywords}
        url={`https://resumeanalyzerai.com/blog/${post.slug}`}
        structuredData={[articleSchema]}
      />
      
      {/* Premium Hero Header */}
      <div className="relative z-10 border-b border-white/10">
        <div className="absolute inset-0 bg-gradient-to-b from-purple-900/20 via-blue-900/20 to-transparent z-0"></div>
        <div className="relative z-10 max-w-3xl mx-auto px-4 pt-16 pb-12">
          {/* Back Button */}
          <Link
            to="/blog"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Blog
          </Link>

          {/* Meta Information - Above Title */}
          <div className="flex flex-wrap items-center gap-4 mb-4 text-xs uppercase tracking-wider text-gray-400">
            <span className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-purple-300">
              {post.category}
            </span>
            <div className="flex items-center gap-2">
              <Calendar className="w-3 h-3" />
              <span>{new Date(post.datePublished).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-3 h-3" />
              <span>{post.readTime}</span>
            </div>
            <span>By {post.author}</span>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-8 leading-tight font-display">
            {post.title}
          </h1>
        </div>
      </div>

      {/* Main Content Area - 2 Column Layout */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Article Content - Left Column */}
          <article className="lg:col-span-8">
            <div className="max-w-3xl mx-auto">
              {/* Article Content */}
              <BlogContentRenderer
                content={content}
                className="prose prose-invert prose-lg max-w-none text-gray-300 leading-relaxed"
                style={{
                  '--tw-prose-headings': '#ffffff',
                  '--tw-prose-links': '#a78bfa',
                  '--tw-prose-bold': '#ffffff',
                  '--tw-prose-code': '#a78bfa',
                  '--tw-prose-pre-code': '#ffffff',
                  '--tw-prose-pre-bg': '#1a1a1a',
                }}
              />

              {/* Bottom CTA Section */}
              <SpotlightCard className="rounded-xl p-8 bg-gradient-to-r from-purple-500/10 to-blue-600/10 border border-purple-500/20 mt-12">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-white mb-4 font-display">
                    Ready to Optimize Your Resume?
                  </h2>
                  <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                    Put these tips into practice. Get instant AI-powered feedback on your resume and see how it performs against ATS systems.
                  </p>
                  <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                    Analyze Your Resume Free <ArrowRight size={16} />
                  </ShimmerButton>
                </div>
              </SpotlightCard>

              {/* Related Posts */}
              {recentPosts.filter(p => p.slug !== post.slug).length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold text-white mb-6 font-display">Related Articles</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recentPosts
                      .filter(p => p.slug !== post.slug)
                      .slice(0, 2)
                      .map((relatedPost) => (
                        <Link key={relatedPost.slug} to={`/blog/${relatedPost.slug}`}>
                          <SpotlightCard className="rounded-xl p-6 h-full hover:scale-105 transition-transform">
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
          </article>

          {/* Sticky Sidebar - Right Column */}
          <aside className="lg:col-span-4">
            <div className="sticky top-8 space-y-6">
              {/* Table of Contents */}
              <TableOfContents content={contentForTOC} />

              {/* Sticky CTA Card */}
              <SpotlightCard className="rounded-xl p-6 bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30">
                <div className="text-center">
                  <FileText className="w-10 h-10 text-purple-400 mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-white mb-2 font-display">
                    Analyze Your Resume
                  </h3>
                  <p className="text-gray-300 text-sm mb-4">
                    Get instant AI-powered feedback and see how your resume performs.
                  </p>
                  <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)} className="w-full">
                    Try Free Analysis <ArrowRight size={16} />
                  </ShimmerButton>
                </div>
              </SpotlightCard>
            </div>
          </aside>
        </div>
      </div>
    </>
  );
};

export default BlogPost;
