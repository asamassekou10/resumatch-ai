/**
 * Blog Content Data
 * 
 * Contains blog post metadata and content for SEO blog pages.
 * Content is stored as markdown files in frontend/src/content/blog/
 */

export const BLOG_POSTS = [
  {
    slug: 'how-to-beat-ats-2025',
    title: 'How to Beat the ATS in 2025: Complete Guide',
    description: 'Learn proven strategies to optimize your resume for Applicant Tracking Systems (ATS) and increase your chances of getting past automated screening in 2025.',
    keywords: 'ATS optimization, resume keywords, applicant tracking system, ATS resume, beat ATS, resume screening',
    author: 'ResumeAnalyzer AI Team',
    datePublished: '2025-01-15',
    dateModified: '2025-01-15',
    image: 'https://resumeanalyzerai.com/og-image.png',
    category: 'Resume Tips',
    readTime: '8 min read',
    excerpt: 'Applicant Tracking Systems (ATS) are used by 99% of Fortune 500 companies to screen resumes. Learn how to optimize your resume to pass these automated filters and land more interviews.',
  },
  {
    slug: 'why-not-getting-interviews',
    title: 'Why Am I Not Getting Interviews? 7 Common Resume Mistakes',
    description: 'Discover the 7 most common resume mistakes that prevent you from getting interviews and learn how to fix them to increase your response rate.',
    keywords: 'resume mistakes, not getting interviews, resume errors, job search tips, resume problems',
    author: 'ResumeAnalyzer AI Team',
    datePublished: '2025-01-15',
    dateModified: '2025-01-15',
    image: 'https://resumeanalyzerai.com/og-image.png',
    category: 'Resume Tips',
    readTime: '6 min read',
    excerpt: 'If you\'re sending out resumes but not getting interviews, these 7 common mistakes might be the reason. Learn how to identify and fix them.',
  },
  {
    slug: 'resume-keywords-project-managers',
    title: 'Resume Keywords for Project Managers: ATS Optimization Guide',
    description: 'Discover the essential resume keywords and phrases that project managers need to include to pass ATS screening and get noticed by hiring managers.',
    keywords: 'project manager resume, PM resume keywords, project manager ATS, resume keywords, project management resume',
    author: 'ResumeAnalyzer AI Team',
    datePublished: '2025-01-15',
    dateModified: '2025-01-15',
    image: 'https://resumeanalyzerai.com/og-image.png',
    category: 'Industry Guides',
    readTime: '7 min read',
    excerpt: 'Project managers need specific keywords to pass ATS filters. This guide shows you exactly which terms to include in your resume.',
  },
  {
    slug: 'software-engineer-resume-hiring-managers',
    title: 'Software Engineer Resume: What Hiring Managers Really Look For',
    description: 'Learn what tech hiring managers actually look for in software engineer resumes, including the skills, projects, and achievements that get you interviews.',
    keywords: 'software engineer resume, tech resume, developer resume, engineering resume, software developer resume',
    author: 'ResumeAnalyzer AI Team',
    datePublished: '2025-01-15',
    dateModified: '2025-01-15',
    image: 'https://resumeanalyzerai.com/og-image.png',
    category: 'Industry Guides',
    readTime: '9 min read',
    excerpt: 'Tech hiring managers see hundreds of resumes. Learn what makes a software engineer resume stand out and get you the interview.',
  },
  {
    slug: 'nursing-resume-tips-healthcare',
    title: 'Nursing Resume Tips: Stand Out in Healthcare Applications',
    description: 'Essential tips for creating a standout nursing resume that highlights your clinical experience, certifications, and patient care skills.',
    keywords: 'nursing resume, nurse resume, healthcare resume, nursing student resume, RN resume',
    author: 'ResumeAnalyzer AI Team',
    datePublished: '2025-01-15',
    dateModified: '2025-01-15',
    image: 'https://resumeanalyzerai.com/og-image.png',
    category: 'Industry Guides',
    readTime: '6 min read',
    excerpt: 'Healthcare hiring is competitive. Learn how to create a nursing resume that showcases your clinical expertise and gets you noticed.',
  },
];

/**
 * Get blog post by slug
 * @param {string} slug - Blog post slug
 * @returns {Object|null} Blog post object or null if not found
 */
export const getBlogPostBySlug = (slug) => {
  return BLOG_POSTS.find(post => post.slug === slug) || null;
};

/**
 * Get all blog post slugs (for sitemap generation)
 * @returns {Array<string>} Array of blog post slugs
 */
export const getAllBlogPostSlugs = () => {
  return BLOG_POSTS.map(post => post.slug);
};

/**
 * Get recent blog posts
 * @param {number} count - Number of posts to return
 * @returns {Array<Object>} Array of blog post objects
 */
export const getRecentBlogPosts = (count = 5) => {
  return BLOG_POSTS.slice(0, count).sort((a, b) => 
    new Date(b.datePublished) - new Date(a.datePublished)
  );
};

export default BLOG_POSTS;


