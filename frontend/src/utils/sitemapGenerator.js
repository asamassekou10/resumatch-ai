/**
 * Sitemap Generator Utility
 * 
 * Generates a dynamic sitemap.xml from route configuration.
 * This ensures all public routes are included with proper SEO metadata.
 */

const SITE_URL = 'https://resumeanalyzerai.com';

/**
 * Route configuration with SEO metadata
 */
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

/**
 * Generate sitemap XML string
 */
export const generateSitemap = () => {
  const urls = ROUTE_CONFIG.map(route => {
    const fullUrl = `${SITE_URL}${route.path}`;
    return `  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${route.lastmod}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
  </url>`;
  }).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">

${urls}

</urlset>`;
};

/**
 * Update sitemap file (for build scripts)
 * This would typically be called during the build process
 */
export const updateSitemapFile = () => {
  const fs = require('fs');
  const path = require('path');
  
  const sitemapContent = generateSitemap();
  const sitemapPath = path.join(__dirname, '../../public/sitemap.xml');
  
  fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');
  console.log('✅ Sitemap updated successfully');
};

export default generateSitemap;

