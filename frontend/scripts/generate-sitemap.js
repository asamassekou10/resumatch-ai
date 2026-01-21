/**
 * Sitemap Generator for Programmatic SEO
 *
 * Generates sitemap.xml with:
 * - Dynamic job role pages
 * - Blog posts with proper dates
 * - Industry hub pages (future)
 * - Proper priority and changefreq based on page type
 * - Scalable architecture for 1000s of pages
 *
 * Run: node scripts/generate-sitemap.js
 */

const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://www.resumeanalyzerai.com';

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Extract slugs from a JS file using regex
 * @param {string} filePath - Path to the JS file
 * @param {string} pattern - Regex pattern to match slugs
 * @returns {Array} Array of slugs
 */
function extractSlugs(filePath, pattern = /slug:\s*['"]([^'"]+)['"]/g) {
  const slugs = [];
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      let match;
      while ((match = pattern.exec(content)) !== null) {
        slugs.push(match[1]);
      }
    }
  } catch (err) {
    console.error(`Error reading ${filePath}:`, err.message);
  }
  return slugs;
}

/**
 * Extract blog post metadata (slug and date)
 * @param {string} filePath - Path to blogContent.js
 * @returns {Array} Array of {slug, date} objects
 */
function extractBlogPosts(filePath) {
  const posts = [];
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');

      // Match slug and dateModified/datePublished pairs
      const postPattern = /slug:\s*['"]([^'"]+)['"][\s\S]*?date(?:Modified|Published):\s*['"]([^'"]+)['"]/g;
      let match;

      while ((match = postPattern.exec(content)) !== null) {
        posts.push({
          slug: match[1],
          date: match[2]
        });
      }
    }
  } catch (err) {
    console.error('Error extracting blog posts:', err.message);
  }
  return posts;
}

/**
 * Generate XML for a single URL entry
 * @param {Object} config - URL configuration
 * @returns {string} XML string for the URL
 */
function generateUrlEntry({ url, lastmod, changefreq, priority }) {
  return `  <url>
    <loc>${url}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

// ============================================
// ROUTE CONFIGURATIONS
// ============================================

const today = new Date().toISOString().split('T')[0];

// Static routes with fixed configuration
const STATIC_ROUTES = [
  { path: '/', priority: '1.0', changefreq: 'daily', lastmod: today },
  { path: '/guest-analyze', priority: '1.0', changefreq: 'weekly', lastmod: today },
  { path: '/pricing', priority: '0.9', changefreq: 'weekly', lastmod: today },
  { path: '/blog', priority: '0.9', changefreq: 'daily', lastmod: today },
  { path: '/resume-for', priority: '0.9', changefreq: 'weekly', lastmod: today }, // Hub page
  { path: '/help', priority: '0.7', changefreq: 'monthly', lastmod: today },
  { path: '/help/terms', priority: '0.5', changefreq: 'yearly', lastmod: '2026-01-01' },
  { path: '/help/privacy', priority: '0.5', changefreq: 'yearly', lastmod: '2026-01-01' },
  { path: '/login', priority: '0.5', changefreq: 'yearly', lastmod: '2026-01-01' },
  { path: '/register', priority: '0.7', changefreq: 'yearly', lastmod: '2026-01-01' },
  { path: '/resources/for-students', priority: '0.8', changefreq: 'monthly', lastmod: today }
];

// ============================================
// DYNAMIC ROUTE EXTRACTION
// ============================================

// Get job role pages
const jobRolesPath = path.join(__dirname, '../src/utils/jobRoles.js');
const jobRoleSlugs = extractSlugs(jobRolesPath);
console.log(`Found ${jobRoleSlugs.length} job role pages`);

const JOB_ROLE_ROUTES = jobRoleSlugs.map(slug => ({
  path: `/resume-for/${slug}`,
  priority: '0.8',
  changefreq: 'weekly',
  lastmod: today // These pages have dynamic content generation now
}));

// Get blog post pages with their dates
const blogContentPath = path.join(__dirname, '../src/utils/blogContent.js');
const blogPosts = extractBlogPosts(blogContentPath);
console.log(`Found ${blogPosts.length} blog posts`);

const BLOG_ROUTES = blogPosts.map(post => ({
  path: `/blog/${post.slug}`,
  priority: '0.7',
  changefreq: 'monthly',
  lastmod: post.date || today
}));

// If no blog posts found with dates, fallback to slug extraction
if (BLOG_ROUTES.length === 0) {
  const blogSlugs = extractSlugs(blogContentPath);
  console.log(`Fallback: Found ${blogSlugs.length} blog slugs`);

  BLOG_ROUTES.push(...blogSlugs.map(slug => ({
    path: `/blog/${slug}`,
    priority: '0.7',
    changefreq: 'monthly',
    lastmod: today
  })));
}

// ============================================
// INDUSTRY HUB PAGES (Future expansion)
// ============================================

// These can be uncommented when industry hub pages are implemented
// const INDUSTRY_HUBS = [
//   { path: '/resume-for/industry/technology', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/healthcare', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/finance', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/business', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/sales-marketing', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/creative', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/education', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/skilled-trades', priority: '0.8', changefreq: 'weekly', lastmod: today },
//   { path: '/resume-for/industry/services', priority: '0.8', changefreq: 'weekly', lastmod: today }
// ];

// ============================================
// SITEMAP GENERATION
// ============================================

function generateSitemap() {
  // Combine all routes
  const allRoutes = [
    ...STATIC_ROUTES,
    ...JOB_ROLE_ROUTES,
    ...BLOG_ROUTES
    // ...INDUSTRY_HUBS // Uncomment when implemented
  ];

  // Generate XML entries
  const urlEntries = allRoutes.map(route =>
    generateUrlEntry({
      url: `${SITE_URL}${route.path}`,
      lastmod: route.lastmod,
      changefreq: route.changefreq,
      priority: route.priority
    })
  ).join('\n');

  // Create full sitemap XML
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">

${urlEntries}

</urlset>`;

  return sitemap;
}

// ============================================
// WRITE SITEMAP
// ============================================

const sitemapContent = generateSitemap();
const publicPath = path.join(__dirname, '../public');
const sitemapPath = path.join(publicPath, 'sitemap.xml');

// Ensure public directory exists
if (!fs.existsSync(publicPath)) {
  fs.mkdirSync(publicPath, { recursive: true });
}

fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');

// Summary
const totalUrls = STATIC_ROUTES.length + JOB_ROLE_ROUTES.length + BLOG_ROUTES.length;
console.log('');
console.log('='.repeat(50));
console.log('SITEMAP GENERATION COMPLETE');
console.log('='.repeat(50));
console.log(`Static pages: ${STATIC_ROUTES.length}`);
console.log(`Job role pages: ${JOB_ROLE_ROUTES.length}`);
console.log(`Blog posts: ${BLOG_ROUTES.length}`);
console.log(`TOTAL URLs: ${totalUrls}`);
console.log('');
console.log(`Sitemap saved to: ${sitemapPath}`);
