/**
 * Build script to generate sitemap.xml
 * 
 * Run this script during the build process to ensure sitemap is up-to-date
 * Usage: node scripts/generate-sitemap.js
 */

const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://resumeanalyzerai.com';

const ROUTE_CONFIG = [
  {
    path: '/',
    priority: '1.0',
    changefreq: 'daily',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/pricing',
    priority: '0.9',
    changefreq: 'weekly',
    lastmod: new Date().toISOString().split('T')[0]
  },
  {
    path: '/guest-analyze',
    priority: '0.9',
    changefreq: 'monthly',
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
  }
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

