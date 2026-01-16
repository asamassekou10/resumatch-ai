/**
 * Pre-render Pages Generator for SEO
 *
 * Generates static HTML files with proper meta tags for search engine crawlers.
 * This runs during build and creates individual HTML files for each route
 * that include page-specific meta tags, structured data, and content hints.
 *
 * This approach works on Vercel without Puppeteer by generating SEO-optimized
 * HTML shells that include all necessary meta information.
 */

const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://www.resumeanalyzerai.com';
const SITE_NAME = 'ResumeAnalyzer AI';

// Read job roles
let JOB_ROLES = [];
try {
  const jobRolesPath = path.join(__dirname, '../src/utils/jobRoles.js');
  if (fs.existsSync(jobRolesPath)) {
    const content = fs.readFileSync(jobRolesPath, 'utf8');
    // Extract slug and name (job roles use 'name' not 'title')
    const slugRegex = /slug:\s*['"]([^'"]+)['"]/g;
    const nameRegex = /name:\s*['"]([^'"]+)['"]/g;

    const slugs = [];
    const names = [];

    let match;
    while ((match = slugRegex.exec(content)) !== null) {
      slugs.push(match[1]);
    }
    while ((match = nameRegex.exec(content)) !== null) {
      names.push(match[1]);
    }

    // Combine them (they should be in order)
    for (let i = 0; i < slugs.length && i < names.length; i++) {
      JOB_ROLES.push({ slug: slugs[i], title: names[i] });
    }
    console.log(`Found ${JOB_ROLES.length} job roles`);
  }
} catch (err) {
  console.log('Could not load job roles:', err.message);
}

// Read blog posts
let BLOG_POSTS = [];
try {
  const blogPath = path.join(__dirname, '../src/utils/blogContent.js');
  if (fs.existsSync(blogPath)) {
    const content = fs.readFileSync(blogPath, 'utf8');

    // Split by blog post objects (each starts with { and has slug:)
    const postBlocks = content.split(/\n\s*{\s*\n?\s*slug:/).slice(1);

    postBlocks.forEach(block => {
      // Extract slug
      const slugMatch = block.match(/^\s*['"]([^'"]+)['"]/);
      // Extract title
      const titleMatch = block.match(/title:\s*['"]([^'"]+)['"]/);
      // Extract description (for meta)
      const descMatch = block.match(/description:\s*['"]([^'"]+)['"]/);

      if (slugMatch && titleMatch) {
        BLOG_POSTS.push({
          slug: slugMatch[1],
          title: titleMatch[1],
          excerpt: descMatch ? descMatch[1] : titleMatch[1]
        });
      }
    });
    console.log(`Found ${BLOG_POSTS.length} blog posts`);
  }
} catch (err) {
  console.log('Could not load blog posts:', err.message);
}

// Define all pages with their SEO metadata
const PAGES = [
  {
    path: '/',
    title: 'ResumeAnalyzer AI | Free ATS Resume Scanner & Optimizer',
    description: 'Optimize your resume with AI-powered analysis, ATS scoring, skill gap analysis, and personalized job matching. Get hired faster with ResumeAnalyzer AI. First scan free.',
    keywords: 'resume analyzer, AI resume, ATS score, job matching, career tools, resume optimization, free resume scanner, ATS checker'
  },
  {
    path: '/guest-analyze',
    title: 'Free Resume Analysis | ResumeAnalyzer AI',
    description: 'Get instant AI-powered resume analysis. Upload your resume and receive ATS scores, keyword optimization tips, and personalized recommendations. No sign-up required.',
    keywords: 'free resume analysis, resume scanner, ATS checker, resume feedback, resume tips'
  },
  {
    path: '/pricing',
    title: 'Pricing Plans | ResumeAnalyzer AI',
    description: 'Start free, then get unlimited scans for 7 days at $6.99 or subscribe monthly. No long-term commitments required. AI-powered resume analysis with ATS scoring.',
    keywords: 'pricing, resume analyzer pricing, AI career tools pricing, affordable resume analysis, 7-day pass'
  },
  {
    path: '/blog',
    title: 'Resume Tips & Career Advice Blog | ResumeAnalyzer AI',
    description: 'Expert resume tips, ATS optimization guides, and career advice to help you land your dream job. Learn how to beat applicant tracking systems.',
    keywords: 'resume tips, career advice, ATS tips, job search tips, resume writing guide'
  },
  {
    path: '/help',
    title: 'Help Center | ResumeAnalyzer AI',
    description: 'Get help with ResumeAnalyzer AI. Find answers to frequently asked questions about resume analysis, ATS optimization, and our features.',
    keywords: 'help, FAQ, support, resume analyzer help'
  },
  {
    path: '/login',
    title: 'Sign In | ResumeAnalyzer AI',
    description: 'Sign in to your ResumeAnalyzer AI account to access your resume analyses, saved results, and premium features.',
    keywords: 'login, sign in, account'
  },
  {
    path: '/register',
    title: 'Create Account | ResumeAnalyzer AI',
    description: 'Create your free ResumeAnalyzer AI account. Get AI-powered resume analysis, ATS scoring, and personalized job matching.',
    keywords: 'sign up, register, create account, free trial'
  },
  {
    path: '/resources/for-students',
    title: 'Resume Tips for Students | ResumeAnalyzer AI',
    description: 'Expert resume writing tips and resources specifically for students and recent graduates. Learn how to create an entry-level resume that stands out.',
    keywords: 'student resume, entry level resume, recent graduate resume, college resume tips'
  },
  // Add job role pages
  ...JOB_ROLES.map(role => ({
    path: `/resume-for/${role.slug}`,
    title: `${role.title} Resume Tips & Keywords | ResumeAnalyzer AI`,
    description: `Expert resume tips, keywords, and examples for ${role.title} positions. Optimize your resume with AI-powered analysis and land more interviews.`,
    keywords: `${role.title} resume, ${role.slug} resume tips, ${role.title} keywords, ${role.title} resume example`
  })),
  // Add blog post pages
  ...BLOG_POSTS.map(post => ({
    path: `/blog/${post.slug}`,
    title: post.title,
    description: post.excerpt,
    keywords: `resume tips, ${post.slug.replace(/-/g, ' ')}, career advice`
  }))
];

/**
 * Generate HTML template with proper meta tags
 */
function generateHTML(page) {
  const fullUrl = `${SITE_URL}${page.path}`;
  const pageTitle = page.title.includes('ResumeAnalyzer') ? page.title : `${page.title} | ${SITE_NAME}`;

  // Generate structured data for this page
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': page.path.includes('/blog/') ? 'Article' : 'WebPage',
    name: pageTitle,
    description: page.description,
    url: fullUrl,
    publisher: {
      '@type': 'Organization',
      name: SITE_NAME,
      url: SITE_URL
    }
  };

  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" type="image/png" href="/favicon-96x96.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
    <meta name="theme-color" content="#0891b2" />

    <!-- Page-Specific Meta Tags -->
    <title>${pageTitle}</title>
    <meta name="title" content="${pageTitle}" />
    <meta name="description" content="${page.description}" />
    <meta name="keywords" content="${page.keywords}" />
    <meta name="author" content="${SITE_NAME}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="${fullUrl}" />

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="${page.path.includes('/blog/') ? 'article' : 'website'}" />
    <meta property="og:url" content="${fullUrl}" />
    <meta property="og:title" content="${pageTitle}" />
    <meta property="og:description" content="${page.description}" />
    <meta property="og:image" content="${SITE_URL}/og-image.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:site_name" content="${SITE_NAME}" />
    <meta property="og:locale" content="en_US" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="${fullUrl}" />
    <meta name="twitter:title" content="${pageTitle}" />
    <meta name="twitter:description" content="${page.description}" />
    <meta name="twitter:image" content="${SITE_URL}/og-image.png" />

    <!-- Structured Data -->
    <script type="application/ld+json">
    ${JSON.stringify(structuredData, null, 2)}
    </script>

    <!-- App Icons -->
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/manifest.json" />

    <!-- Preconnect -->
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  </head>
  <body>
    <noscript>
      <div style="text-align: center; padding: 40px; font-family: sans-serif;">
        <h1>${pageTitle}</h1>
        <p>${page.description}</p>
        <p>JavaScript is required for full functionality. Please enable JavaScript.</p>
        <a href="${SITE_URL}">Visit ${SITE_NAME}</a>
      </div>
    </noscript>
    <div id="root"></div>
  </body>
</html>`;
}

/**
 * Main function to generate all pre-rendered pages
 */
function generatePrerenderedPages() {
  const buildDir = path.join(__dirname, '../build');

  // Only run if build directory exists (post-build)
  if (!fs.existsSync(buildDir)) {
    console.log('Build directory not found. Run this script after build.');
    return;
  }

  let generated = 0;
  let skipped = 0;

  PAGES.forEach(page => {
    // Skip root path (handled by main index.html)
    if (page.path === '/') {
      skipped++;
      return;
    }

    // Create directory structure
    const pagePath = page.path.endsWith('/') ? page.path.slice(0, -1) : page.path;
    const dirPath = path.join(buildDir, pagePath);
    const htmlPath = path.join(dirPath, 'index.html');

    // Create directory if it doesn't exist
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }

    // Generate and write HTML
    const html = generateHTML(page);
    fs.writeFileSync(htmlPath, html, 'utf8');
    generated++;
  });

  console.log(`\n✅ Pre-rendered ${generated} pages for SEO`);
  console.log(`   Skipped ${skipped} pages (root handled by main index.html)`);
  console.log(`   Total routes: ${PAGES.length}`);
}

// Run the generator
generatePrerenderedPages();
