/**
 * Build script to generate sitemap.xml
 * 
 * Run this script during the build process to ensure sitemap is up-to-date
 * Usage: node scripts/generate-sitemap.js
 */

const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://www.resumeanalyzerai.com';

// Import job roles for dynamic pages
let JOB_ROLES = [];
try {
  // Use require to load the module (Node.js can handle ES modules with proper setup)
  // For MVP, we'll use a simpler approach: read the file and extract slugs
  const jobRolesPath = path.join(__dirname, '../src/utils/jobRoles.js');
  if (fs.existsSync(jobRolesPath)) {
    const jobRolesContent = fs.readFileSync(jobRolesPath, 'utf8');
    // Extract all slug values from the JOB_ROLES array
    const slugRegex = /slug:\s*['"]([^'"]+)['"]/g;
    let match;
    while ((match = slugRegex.exec(jobRolesContent)) !== null) {
      const slug = match[1];
      JOB_ROLES.push({
        path: `/resume-for/${slug}`,
        priority: '0.8',
        changefreq: 'monthly',
        lastmod: new Date().toISOString().split('T')[0]
      });
    }
    console.log(`✅ Found ${JOB_ROLES.length} job role pages for sitemap`);
  }
} catch (err) {
  console.log('⚠️  Could not load job roles for sitemap:', err.message);
}

// Import blog posts for dynamic pages
let BLOG_POSTS = [];
try {
  const blogContentPath = path.join(__dirname, '../src/utils/blogContent.js');
  if (fs.existsSync(blogContentPath)) {
    const blogContent = fs.readFileSync(blogContentPath, 'utf8');
    // Extract all slug values from the BLOG_POSTS array
    const slugRegex = /slug:\s*['"]([^'"]+)['"]/g;
    let match;
    while ((match = slugRegex.exec(blogContent)) !== null) {
      const slug = match[1];
      BLOG_POSTS.push({
        path: `/blog/${slug}`,
        priority: '0.6',  // Lower priority than tool pages
        changefreq: 'monthly',
        lastmod: new Date().toISOString().split('T')[0]
      });
    }
    console.log(`✅ Found ${BLOG_POSTS.length} blog posts for sitemap`);
  }
} catch (err) {
  // Blog content may not exist yet, that's okay
  console.log('⚠️  Could not load blog posts for sitemap:', err.message);
}

const ROUTE_CONFIG = [
  {
    path: '/',
    priority: '1.0',
    changefreq: 'daily',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/guest-analyze',
    priority: '1.0',  // Main tool - highest priority
    changefreq: 'weekly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/pricing',
    priority: '0.9',
    changefreq: 'weekly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/help',
    priority: '0.7',
    changefreq: 'monthly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/help/terms',
    priority: '0.5',
    changefreq: 'yearly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/help/privacy',
    priority: '0.5',
    changefreq: 'yearly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/login',
    priority: '0.5',
    changefreq: 'yearly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/register',
    priority: '0.7',
    changefreq: 'yearly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/blog',
    priority: '0.8',
    changefreq: 'weekly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/resources/for-students',
    priority: '0.8',
    changefreq: 'monthly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  // Add job role pages
  ...JOB_ROLES,
  // Add blog post pages
  ...BLOG_POSTS,
];

function generateSitemap() {
  const urls = ROUTE_CONFIG.map(route => {
    const fullUrl = `${SITE_URL}${route.path}`;
    return `  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${route.lastmod}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
  </url>`;
  }).join('\n');

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">

${urls}

</urlset>`;

  return sitemap;
}

// Generate and write sitemap
const sitemapContent = generateSitemap();
const publicPath = path.join(__dirname, '../public');
const sitemapPath = path.join(publicPath, 'sitemap.xml');

// Ensure public directory exists
if (!fs.existsSync(publicPath)) {
  fs.mkdirSync(publicPath, { recursive: true });
}

fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');
console.log('✅ Sitemap generated successfully at:', sitemapPath);

