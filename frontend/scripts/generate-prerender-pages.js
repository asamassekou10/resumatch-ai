/**
 * Pre-render Pages Generator for SEO
 *
 * Generates static HTML files with ACTUAL CONTENT for search engine crawlers.
 * This is critical because Google needs to see real text content, not just meta tags.
 *
 * The generated pages include:
 * - Full meta tags (title, description, OG, Twitter)
 * - Structured data (JSON-LD)
 * - ACTUAL page content (headings, paragraphs, lists)
 * - Internal links for crawling
 *
 * This works on Vercel without Puppeteer by generating content-rich HTML.
 */

const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://www.resumeanalyzerai.com';
const SITE_NAME = 'ResumeAnalyzer AI';

// Read job roles with full data
let JOB_ROLES = [];
try {
  const jobRolesPath = path.join(__dirname, '../src/utils/jobRoles.js');
  if (fs.existsSync(jobRolesPath)) {
    const content = fs.readFileSync(jobRolesPath, 'utf8');

    // Extract full job role objects
    const roleMatches = content.matchAll(/{\s*slug:\s*['"]([^'"]+)['"],\s*name:\s*['"]([^'"]+)['"],\s*industry:\s*['"]([^'"]+)['"],\s*keywords:\s*\[([\s\S]*?)\],\s*skills:\s*\[([\s\S]*?)\],\s*description:\s*['"]([^'"]+)['"],\s*tips:\s*\[([\s\S]*?)\],\s*commonMistakes:\s*\[([\s\S]*?)\]/g);

    for (const match of roleMatches) {
      const extractArray = (str) => {
        const items = str.match(/['"]([^'"]+)['"]/g);
        return items ? items.map(s => s.replace(/['"]/g, '')) : [];
      };

      JOB_ROLES.push({
        slug: match[1],
        name: match[2],
        industry: match[3],
        keywords: extractArray(match[4]),
        skills: extractArray(match[5]),
        description: match[6],
        tips: extractArray(match[7]),
        commonMistakes: extractArray(match[8])
      });
    }
    console.log(`Found ${JOB_ROLES.length} job roles with full data`);
  }
} catch (err) {
  console.log('Could not load job roles:', err.message);
}

// Read blog posts with full data
let BLOG_POSTS = [];
try {
  const blogPath = path.join(__dirname, '../src/utils/blogContent.js');
  if (fs.existsSync(blogPath)) {
    const content = fs.readFileSync(blogPath, 'utf8');

    // Extract blog post metadata
    const postPattern = /slug:\s*['"]([^'"]+)['"][\s\S]*?title:\s*['"]([^'"]+)['"][\s\S]*?description:\s*['"]([^'"]+)['"][\s\S]*?keywords:\s*['"]([^'"]+)['"][\s\S]*?category:\s*['"]([^'"]+)['"][\s\S]*?readTime:\s*['"]([^'"]+)['"][\s\S]*?excerpt:\s*['"]([^'"]+)['"]/g;

    let match;
    while ((match = postPattern.exec(content)) !== null) {
      BLOG_POSTS.push({
        slug: match[1],
        title: match[2],
        description: match[3],
        keywords: match[4],
        category: match[5],
        readTime: match[6],
        excerpt: match[7]
      });
    }
    console.log(`Found ${BLOG_POSTS.length} blog posts`);
  }
} catch (err) {
  console.log('Could not load blog posts:', err.message);
}

/**
 * Generate FAQ content for a job role
 */
function generateFAQs(role) {
  return [
    {
      question: `What are the most important keywords for a ${role.name} resume?`,
      answer: `The most important keywords for a ${role.name} resume include: ${role.keywords.slice(0, 5).join(', ')}. These keywords are commonly searched by ATS systems and recruiters in the ${role.industry} industry.`
    },
    {
      question: `What skills should I highlight on my ${role.name} resume?`,
      answer: `Essential skills for a ${role.name} resume include: ${role.skills.join(', ')}. Quantify these skills with specific achievements whenever possible.`
    },
    {
      question: `How do I write a ${role.name} resume with no experience?`,
      answer: `For an entry-level ${role.name} resume: 1) Highlight relevant coursework and projects. 2) Emphasize transferable skills. 3) Include certifications or training. 4) Add volunteer work demonstrating ${role.industry.toLowerCase()} skills.`
    },
    {
      question: `What format works best for a ${role.name} resume?`,
      answer: `For ${role.name} positions, use a reverse-chronological format. Include: Contact Information, Professional Summary, Skills (${role.keywords.slice(0, 3).join(', ')}), Work Experience, and Education.`
    },
    {
      question: `How can I make my ${role.name} resume stand out?`,
      answer: `To stand out: 1) Start with a compelling summary. 2) Use action verbs and quantify results. 3) Include industry certifications. 4) Tailor to each job using keywords like ${role.keywords.slice(0, 3).join(', ')}. 5) Use our free AI resume analyzer.`
    }
  ];
}

/**
 * Generate structured data for job role page
 */
function generateJobRoleStructuredData(role) {
  const faqs = generateFAQs(role);
  const url = `${SITE_URL}/resume-for/${role.slug}`;

  return [
    {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqs.map(faq => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer
        }
      }))
    },
    {
      '@context': 'https://schema.org',
      '@type': 'HowTo',
      name: `How to Write a ${role.name} Resume`,
      description: `Step-by-step guide to creating an ATS-optimized ${role.name} resume.`,
      totalTime: 'PT30M',
      step: [
        { '@type': 'HowToStep', position: 1, name: 'Choose the right format', text: `Use a reverse-chronological format for ${role.name} positions.` },
        { '@type': 'HowToStep', position: 2, name: 'Write a professional summary', text: `Include years of experience and key skills like ${role.skills.slice(0, 2).join(' and ')}.` },
        { '@type': 'HowToStep', position: 3, name: 'Add relevant keywords', text: `Include keywords like ${role.keywords.slice(0, 3).join(', ')} throughout your resume.` },
        { '@type': 'HowToStep', position: 4, name: 'Quantify achievements', text: 'Use numbers and percentages to demonstrate impact.' },
        { '@type': 'HowToStep', position: 5, name: 'Optimize for ATS', text: 'Use standard section headers and test with an ATS scanner.' }
      ]
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL },
        { '@type': 'ListItem', position: 2, name: 'Resume Guides', item: `${SITE_URL}/resume-for` },
        { '@type': 'ListItem', position: 3, name: `${role.name} Resume`, item: url }
      ]
    }
  ];
}

/**
 * Generate HTML content for job role page
 */
function generateJobRoleHTML(role) {
  const url = `${SITE_URL}/resume-for/${role.slug}`;
  const title = `${role.name} Resume Examples & Guide [2026] | Free Templates`;
  const description = `Create a winning ${role.name} resume with our expert guide. Includes ${role.industry} keywords, ATS tips, and free AI-powered analysis.`;
  const faqs = generateFAQs(role);
  const structuredData = generateJobRoleStructuredData(role);

  // Generate related roles links
  const relatedRoles = JOB_ROLES.filter(r => r.slug !== role.slug).slice(0, 4);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <meta name="description" content="${description}">
  <meta name="keywords" content="${role.name.toLowerCase()} resume, ${role.industry.toLowerCase()} resume, ${role.keywords.join(', ').toLowerCase()}, resume tips, ATS optimization">
  <meta name="author" content="${SITE_NAME}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="${url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="${url}">
  <meta property="og:title" content="${title}">
  <meta property="og:description" content="${description}">
  <meta property="og:image" content="${SITE_URL}/og-image.png">
  <meta property="og:site_name" content="${SITE_NAME}">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${title}">
  <meta name="twitter:description" content="${description}">
  <meta name="twitter:image" content="${SITE_URL}/og-image.png">

  <!-- Structured Data -->
  ${structuredData.map(sd => `<script type="application/ld+json">${JSON.stringify(sd)}</script>`).join('\n  ')}

  <!-- Icons -->
  <link rel="icon" type="image/png" href="/favicon-96x96.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; color: #e5e7eb; background: #000; margin: 0; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { font-size: 2.5rem; color: #fff; margin-bottom: 1rem; }
    h2 { font-size: 1.5rem; color: #60a5fa; margin-top: 2rem; }
    h3 { font-size: 1.25rem; color: #fff; }
    p { margin: 1rem 0; }
    ul, ol { padding-left: 1.5rem; }
    li { margin: 0.5rem 0; }
    a { color: #60a5fa; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .badge { display: inline-block; background: rgba(59,130,246,0.2); border: 1px solid rgba(59,130,246,0.3); padding: 4px 12px; border-radius: 9999px; font-size: 0.875rem; color: #93c5fd; margin-right: 8px; margin-bottom: 8px; }
    .cta { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: #fff; padding: 12px 24px; border-radius: 9999px; font-weight: 600; margin: 1rem 0; }
    .faq-item { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; margin: 1rem 0; }
    .faq-q { font-weight: 600; color: #fff; }
    .faq-a { color: #9ca3af; margin-top: 0.5rem; }
    .related { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .related a { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; display: block; }
    nav { margin-bottom: 2rem; font-size: 0.875rem; color: #6b7280; }
    nav a { color: #9ca3af; }
  </style>
</head>
<body>
  <div class="container">
    <nav>
      <a href="/">Home</a> &gt; <a href="/resume-for">Resume Guides</a> &gt; ${role.name} Resume
    </nav>

    <span class="badge">${role.industry} Industry</span>

    <h1>How to Write a ${role.name} Resume</h1>

    <p>${role.description}</p>

    <a href="/guest-analyze" class="cta">Analyze Your ${role.name} Resume Free</a>

    <h2>ATS Keywords to Include</h2>
    <p>These keywords appear frequently in ${role.name} job descriptions:</p>
    <div>
      ${role.keywords.map(k => `<span class="badge">${k}</span>`).join('')}
    </div>

    <h2>Essential Skills for ${role.name}</h2>
    <ul>
      ${role.skills.map(s => `<li>${s}</li>`).join('\n      ')}
    </ul>

    <h2>How to Write Your ${role.name} Resume</h2>
    <ol>
      <li><strong>Choose the right format</strong> - Use a reverse-chronological format for ${role.name} positions.</li>
      <li><strong>Write a professional summary</strong> - Include your years of experience and key skills like ${role.skills.slice(0, 2).join(' and ')}.</li>
      <li><strong>Add relevant keywords</strong> - Include keywords like ${role.keywords.slice(0, 3).join(', ')} throughout your resume.</li>
      <li><strong>Quantify your achievements</strong> - Use numbers and percentages to demonstrate your impact.</li>
      <li><strong>Optimize for ATS</strong> - Use standard headers and test with our free ATS scanner.</li>
    </ol>

    <h2>Expert Tips for ${role.name} Resumes</h2>
    <ul>
      ${role.tips.map(t => `<li>${t}</li>`).join('\n      ')}
    </ul>

    <h2>Common ${role.name} Resume Mistakes</h2>
    <ul>
      ${role.commonMistakes.map(m => `<li>${m}</li>`).join('\n      ')}
    </ul>

    <h2>${role.name} Resume FAQ</h2>
    ${faqs.map(faq => `
    <div class="faq-item">
      <div class="faq-q">${faq.question}</div>
      <div class="faq-a">${faq.answer}</div>
    </div>`).join('')}

    <h2>Ready to Optimize Your Resume?</h2>
    <p>Get instant AI-powered feedback on your ${role.name} resume. Our analysis will help you highlight the right keywords and skills.</p>
    <a href="/guest-analyze" class="cta">Analyze Your Resume Free</a>

    <h2>Related Career Paths</h2>
    <div class="related">
      ${relatedRoles.map(r => `<a href="/resume-for/${r.slug}">${r.name} Resume Guide</a>`).join('\n      ')}
    </div>

    <h2>More Resources</h2>
    <ul>
      <li><a href="/blog">Resume Tips Blog</a></li>
      <li><a href="/pricing">View Pricing Plans</a></li>
      <li><a href="/resources/for-students">Student Resources</a></li>
    </ul>
  </div>
  <div id="root"></div>
</body>
</html>`;
}

/**
 * Generate HTML content for blog post
 */
function generateBlogPostHTML(post) {
  const url = `${SITE_URL}/blog/${post.slug}`;

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.description,
    author: { '@type': 'Organization', name: SITE_NAME },
    publisher: { '@type': 'Organization', name: SITE_NAME, logo: { '@type': 'ImageObject', url: `${SITE_URL}/logo512.png` } },
    url: url,
    image: `${SITE_URL}/og-image.png`
  };

  // Get related posts
  const relatedPosts = BLOG_POSTS.filter(p => p.slug !== post.slug).slice(0, 3);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${post.title}</title>
  <meta name="description" content="${post.description}">
  <meta name="keywords" content="${post.keywords}">
  <meta name="author" content="${SITE_NAME}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="${url}">

  <meta property="og:type" content="article">
  <meta property="og:url" content="${url}">
  <meta property="og:title" content="${post.title}">
  <meta property="og:description" content="${post.description}">
  <meta property="og:image" content="${SITE_URL}/og-image.png">
  <meta property="og:site_name" content="${SITE_NAME}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${post.title}">
  <meta name="twitter:description" content="${post.description}">

  <script type="application/ld+json">${JSON.stringify(structuredData)}</script>

  <link rel="icon" type="image/png" href="/favicon-96x96.png">

  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; color: #e5e7eb; background: #000; margin: 0; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { font-size: 2.5rem; color: #fff; }
    p { margin: 1rem 0; }
    a { color: #60a5fa; }
    .meta { color: #6b7280; font-size: 0.875rem; margin-bottom: 2rem; }
    .badge { display: inline-block; background: rgba(59,130,246,0.2); padding: 4px 12px; border-radius: 9999px; font-size: 0.875rem; color: #93c5fd; }
    .cta { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: #fff; padding: 12px 24px; border-radius: 9999px; font-weight: 600; margin: 1rem 0; text-decoration: none; }
    nav { margin-bottom: 2rem; font-size: 0.875rem; }
    nav a { color: #9ca3af; }
    .related { margin-top: 2rem; }
    .related a { display: block; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; margin: 0.5rem 0; }
  </style>
</head>
<body>
  <div class="container">
    <nav>
      <a href="/">Home</a> &gt; <a href="/blog">Blog</a> &gt; ${post.title.substring(0, 30)}...
    </nav>

    <span class="badge">${post.category}</span>
    <span class="meta">${post.readTime}</span>

    <h1>${post.title}</h1>

    <p>${post.excerpt}</p>

    <p>${post.description}</p>

    <a href="/guest-analyze" class="cta">Try Free Resume Analysis</a>

    <div class="related">
      <h2>Related Articles</h2>
      ${relatedPosts.map(p => `<a href="/blog/${p.slug}">${p.title}</a>`).join('\n      ')}
    </div>

    <h2>Resume Guides by Role</h2>
    <ul>
      ${JOB_ROLES.slice(0, 5).map(r => `<li><a href="/resume-for/${r.slug}">${r.name} Resume Guide</a></li>`).join('\n      ')}
    </ul>
  </div>
  <div id="root"></div>
</body>
</html>`;
}

/**
 * Generate hub page for all resume guides
 */
function generateResumeGuidesHubHTML() {
  const url = `${SITE_URL}/resume-for`;
  const title = 'Resume Guides by Job Role | Expert Tips for Every Career';
  const description = 'Browse our comprehensive collection of resume guides for every job role. Get industry-specific keywords, skills, and expert tips.';

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Resume Writing Guides by Job Role',
    numberOfItems: JOB_ROLES.length,
    itemListElement: JOB_ROLES.map((role, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: `${role.name} Resume Guide`,
      url: `${SITE_URL}/resume-for/${role.slug}`
    }))
  };

  // Group by industry
  const industries = {};
  JOB_ROLES.forEach(role => {
    if (!industries[role.industry]) industries[role.industry] = [];
    industries[role.industry].push(role);
  });

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <meta name="description" content="${description}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="${url}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="${url}">
  <meta property="og:title" content="${title}">
  <meta property="og:description" content="${description}">
  <meta property="og:image" content="${SITE_URL}/og-image.png">

  <script type="application/ld+json">${JSON.stringify(structuredData)}</script>

  <link rel="icon" type="image/png" href="/favicon-96x96.png">

  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; color: #e5e7eb; background: #000; margin: 0; padding: 20px; }
    .container { max-width: 1000px; margin: 0 auto; }
    h1 { font-size: 2.5rem; color: #fff; text-align: center; }
    h2 { color: #60a5fa; margin-top: 2rem; }
    p { text-align: center; color: #9ca3af; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; }
    .card a { color: #fff; text-decoration: none; font-weight: 600; }
    .card a:hover { color: #60a5fa; }
    .card small { color: #6b7280; display: block; margin-top: 0.5rem; }
    .cta { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: #fff; padding: 12px 24px; border-radius: 9999px; font-weight: 600; margin: 1rem auto; text-decoration: none; }
    .cta-wrap { text-align: center; margin: 2rem 0; }
    nav { margin-bottom: 2rem; font-size: 0.875rem; }
    nav a { color: #9ca3af; }
  </style>
</head>
<body>
  <div class="container">
    <nav>
      <a href="/">Home</a> &gt; Resume Guides
    </nav>

    <h1>Resume Guides for Every Career</h1>
    <p>Industry-specific resume guides with keywords, skills, and expert tips. ${JOB_ROLES.length} guides available.</p>

    <div class="cta-wrap">
      <a href="/guest-analyze" class="cta">Analyze Your Resume Free</a>
    </div>

    ${Object.entries(industries).map(([industry, roles]) => `
    <h2>${industry}</h2>
    <div class="grid">
      ${roles.map(role => `
      <div class="card">
        <a href="/resume-for/${role.slug}">${role.name} Resume Guide</a>
        <small>${role.keywords.slice(0, 3).join(', ')}</small>
      </div>`).join('')}
    </div>`).join('')}

    <h2>More Resources</h2>
    <ul>
      <li><a href="/blog">Resume Tips Blog</a></li>
      <li><a href="/guest-analyze">Free Resume Analysis</a></li>
      <li><a href="/pricing">View Pricing</a></li>
    </ul>
  </div>
  <div id="root"></div>
</body>
</html>`;
}

/**
 * Generate blog index page
 */
function generateBlogIndexHTML() {
  const url = `${SITE_URL}/blog`;
  const title = 'Resume Tips & Career Advice Blog | ResumeAnalyzer AI';
  const description = 'Expert resume tips, ATS optimization guides, and career advice. Learn how to beat applicant tracking systems and land your dream job.';

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Blog',
    name: title,
    description: description,
    url: url,
    publisher: { '@type': 'Organization', name: SITE_NAME }
  };

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <meta name="description" content="${description}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="${url}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="${url}">
  <meta property="og:title" content="${title}">
  <meta property="og:description" content="${description}">

  <script type="application/ld+json">${JSON.stringify(structuredData)}</script>

  <link rel="icon" type="image/png" href="/favicon-96x96.png">

  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; color: #e5e7eb; background: #000; margin: 0; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { font-size: 2.5rem; color: #fff; }
    .grid { display: grid; gap: 1rem; margin-top: 2rem; }
    .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 8px; }
    .card h2 { font-size: 1.25rem; margin: 0 0 0.5rem; }
    .card h2 a { color: #fff; text-decoration: none; }
    .card h2 a:hover { color: #60a5fa; }
    .card p { color: #9ca3af; margin: 0; font-size: 0.9rem; }
    .badge { display: inline-block; background: rgba(59,130,246,0.2); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; color: #93c5fd; margin-bottom: 0.5rem; }
    nav a { color: #9ca3af; }
  </style>
</head>
<body>
  <div class="container">
    <nav><a href="/">Home</a> &gt; Blog</nav>

    <h1>Resume Tips & Career Advice</h1>
    <p>${BLOG_POSTS.length} expert guides to help you land your dream job.</p>

    <div class="grid">
      ${BLOG_POSTS.map(post => `
      <div class="card">
        <span class="badge">${post.category}</span>
        <h2><a href="/blog/${post.slug}">${post.title}</a></h2>
        <p>${post.excerpt.substring(0, 150)}...</p>
      </div>`).join('')}
    </div>

    <h2>Resume Guides</h2>
    <ul>
      ${JOB_ROLES.slice(0, 6).map(r => `<li><a href="/resume-for/${r.slug}">${r.name} Resume</a></li>`).join('\n      ')}
      <li><a href="/resume-for">View All Resume Guides</a></li>
    </ul>
  </div>
  <div id="root"></div>
</body>
</html>`;
}

/**
 * Generate static page HTML
 */
function generateStaticPageHTML(page) {
  const url = `${SITE_URL}${page.path}`;
  const pageTitle = page.title.includes('ResumeAnalyzer') ? page.title : `${page.title} | ${SITE_NAME}`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${pageTitle}</title>
  <meta name="description" content="${page.description}">
  <meta name="keywords" content="${page.keywords}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="${url}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="${url}">
  <meta property="og:title" content="${pageTitle}">
  <meta property="og:description" content="${page.description}">
  <meta property="og:image" content="${SITE_URL}/og-image.png">

  <link rel="icon" type="image/png" href="/favicon-96x96.png">

  <style>
    body { font-family: system-ui, sans-serif; color: #e5e7eb; background: #000; margin: 0; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; text-align: center; padding: 4rem 1rem; }
    h1 { font-size: 2.5rem; color: #fff; }
    p { color: #9ca3af; font-size: 1.1rem; }
    .cta { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: #fff; padding: 12px 24px; border-radius: 9999px; font-weight: 600; margin: 1rem; text-decoration: none; }
    ul { list-style: none; padding: 0; margin: 2rem 0; }
    li { margin: 0.5rem 0; }
    a { color: #60a5fa; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${page.heading || page.title.split('|')[0].trim()}</h1>
    <p>${page.description}</p>
    ${page.cta ? `<a href="${page.cta.url}" class="cta">${page.cta.text}</a>` : ''}
    ${page.content || ''}
    <ul>
      <li><a href="/guest-analyze">Free Resume Analysis</a></li>
      <li><a href="/blog">Resume Tips Blog</a></li>
      <li><a href="/resume-for">Resume Guides</a></li>
      <li><a href="/pricing">Pricing</a></li>
    </ul>
  </div>
  <div id="root"></div>
</body>
</html>`;
}

// Static pages configuration
const STATIC_PAGES = [
  {
    path: '/guest-analyze',
    title: 'Free Resume Analysis | ATS Resume Scanner',
    description: 'Get instant AI-powered resume analysis. Upload your resume and receive ATS scores, keyword optimization tips, and personalized recommendations. No sign-up required.',
    keywords: 'free resume analysis, resume scanner, ATS checker, resume feedback',
    heading: 'Free AI Resume Analysis',
    cta: { text: 'Start Free Analysis', url: '/guest-analyze' }
  },
  {
    path: '/pricing',
    title: 'Pricing Plans',
    description: 'Start free with 1 scan, then get unlimited scans for 7 days at $6.99 or subscribe monthly. AI-powered resume analysis with ATS scoring.',
    keywords: 'pricing, resume analyzer pricing, affordable resume analysis',
    heading: 'Simple, Transparent Pricing',
    content: '<p>Free: 1 scan | 7-Day Pass: $6.99 unlimited | Pro: $19.99/mo</p>'
  },
  {
    path: '/help',
    title: 'Help Center',
    description: 'Get help with ResumeAnalyzer AI. Find answers about resume analysis, ATS optimization, and our features.',
    keywords: 'help, FAQ, support',
    heading: 'How Can We Help?'
  },
  {
    path: '/login',
    title: 'Sign In',
    description: 'Sign in to your ResumeAnalyzer AI account to access your resume analyses and premium features.',
    keywords: 'login, sign in',
    heading: 'Sign In to Your Account'
  },
  {
    path: '/register',
    title: 'Create Free Account',
    description: 'Create your free ResumeAnalyzer AI account. Get AI-powered resume analysis, ATS scoring, and job matching.',
    keywords: 'sign up, register, free trial',
    heading: 'Create Your Free Account',
    cta: { text: 'Get Started Free', url: '/register' }
  },
  {
    path: '/resources/for-students',
    title: 'Resume Tips for Students',
    description: 'Expert resume writing tips for students and recent graduates. Learn how to create an entry-level resume that stands out.',
    keywords: 'student resume, entry level resume, college resume',
    heading: 'Resume Resources for Students'
  }
];

/**
 * Main generator function
 */
function generatePrerenderedPages() {
  const buildDir = path.join(__dirname, '../build');

  if (!fs.existsSync(buildDir)) {
    console.log('Build directory not found. Run after build.');
    return;
  }

  let generated = 0;

  // Generate job role pages
  JOB_ROLES.forEach(role => {
    const dirPath = path.join(buildDir, 'resume-for', role.slug);
    fs.mkdirSync(dirPath, { recursive: true });
    fs.writeFileSync(path.join(dirPath, 'index.html'), generateJobRoleHTML(role));
    generated++;
  });

  // Generate resume guides hub page
  const hubDir = path.join(buildDir, 'resume-for');
  fs.mkdirSync(hubDir, { recursive: true });
  fs.writeFileSync(path.join(hubDir, 'index.html'), generateResumeGuidesHubHTML());
  generated++;

  // Generate blog posts
  BLOG_POSTS.forEach(post => {
    const dirPath = path.join(buildDir, 'blog', post.slug);
    fs.mkdirSync(dirPath, { recursive: true });
    fs.writeFileSync(path.join(dirPath, 'index.html'), generateBlogPostHTML(post));
    generated++;
  });

  // Generate blog index
  const blogDir = path.join(buildDir, 'blog');
  fs.mkdirSync(blogDir, { recursive: true });
  fs.writeFileSync(path.join(blogDir, 'index.html'), generateBlogIndexHTML());
  generated++;

  // Generate static pages
  STATIC_PAGES.forEach(page => {
    const dirPath = path.join(buildDir, page.path);
    fs.mkdirSync(dirPath, { recursive: true });
    fs.writeFileSync(path.join(dirPath, 'index.html'), generateStaticPageHTML(page));
    generated++;
  });

  console.log(`\n✅ Pre-rendered ${generated} pages with FULL CONTENT for SEO`);
  console.log(`   Job role pages: ${JOB_ROLES.length}`);
  console.log(`   Blog posts: ${BLOG_POSTS.length}`);
  console.log(`   Static pages: ${STATIC_PAGES.length + 2}`);
}

generatePrerenderedPages();
