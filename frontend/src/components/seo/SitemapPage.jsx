import { Link } from 'react-router-dom';
import SEO from '../common/SEO';
import Footer from '../ui/Footer';
import { JOB_ROLES } from '../../utils/jobRoles';
import BLOG_POSTS from '../../utils/blogContent';
import { generateBreadcrumbSchema, generateItemListSchema } from '../../utils/structuredData';

const SitemapPage = () => {
  const siteUrl = 'https://www.resumeanalyzerai.com';

  const staticPages = [
    { name: 'Home', url: `${siteUrl}/` },
    { name: 'Free Resume Analysis', url: `${siteUrl}/guest-analyze` },
    { name: 'Pricing', url: `${siteUrl}/pricing` },
    { name: 'Blog', url: `${siteUrl}/blog` },
    { name: 'Resume Guides', url: `${siteUrl}/resume-for` },
    { name: 'Student Resources', url: `${siteUrl}/resources/for-students` },
    { name: 'Help & Support', url: `${siteUrl}/help` },
    { name: 'Privacy Policy', url: `${siteUrl}/help/privacy` },
    { name: 'Terms of Service', url: `${siteUrl}/help/terms` },
  ];

  const roleItems = JOB_ROLES.map((role) => ({
    name: `${role.name} Resume Guide`,
    url: `${siteUrl}/resume-for/${role.slug}`,
  }));

  const blogItems = BLOG_POSTS.map((post) => ({
    name: post.title,
    url: `${siteUrl}/blog/${post.slug}`,
  }));

  const structuredData = [
    generateBreadcrumbSchema([
      { name: 'Home', url: `${siteUrl}/` },
      { name: 'Sitemap', url: `${siteUrl}/sitemap` },
    ]),
    generateItemListSchema(
      [...staticPages, ...roleItems, ...blogItems],
      'ResumeAnalyzer AI Sitemap'
    ),
  ];

  return (
    <>
      <SEO
        title="Sitemap | ResumeAnalyzer AI"
        description="Browse all ResumeAnalyzer AI pages including resume guides, blog posts, and resources."
        keywords="sitemap, resume guides, resume tips, blog, resources"
        url={`${siteUrl}/sitemap`}
        structuredData={structuredData}
      />

      <div className="min-h-screen bg-black text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-3xl sm:text-4xl font-bold mb-3 font-display">Sitemap</h1>
          <p className="text-gray-400 mb-10">
            Quick access to all public pages, resume guides, and blog posts.
          </p>

          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-4">Main Pages</h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-gray-300">
              {staticPages.map((page) => (
                <li key={page.url}>
                  <Link to={page.url.replace(siteUrl, '')} className="hover:text-white">
                    {page.name}
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-4">Resume Guides</h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-gray-300">
              {roleItems.map((role) => (
                <li key={role.url}>
                  <Link to={role.url.replace(siteUrl, '')} className="hover:text-white">
                    {role.name}
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-4">Blog Posts</h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-gray-300">
              {blogItems.map((post) => (
                <li key={post.url}>
                  <Link to={post.url.replace(siteUrl, '')} className="hover:text-white">
                    {post.name}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>

      <Footer />
    </>
  );
};

export default SitemapPage;
