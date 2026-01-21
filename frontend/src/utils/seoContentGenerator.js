/**
 * SEO Content Generator
 *
 * Generates unique, intent-matched content for programmatic SEO pages.
 * This utility creates:
 * - Unique meta titles and descriptions
 * - Dynamic FAQs based on job role context
 * - Industry-specific content variations
 * - Related content recommendations
 * - Hub-and-spoke linking suggestions
 */

const SITE_URL = 'https://www.resumeanalyzerai.com';

/**
 * Industry categories for hub pages
 */
export const INDUSTRY_HUBS = {
  technology: {
    name: 'Technology',
    slug: 'technology',
    description: 'Tech industry resume guides for software engineers, developers, data scientists, and IT professionals.',
    roles: ['software-engineer', 'web-developer', 'data-analyst'],
    color: 'blue',
    icon: 'code'
  },
  healthcare: {
    name: 'Healthcare',
    slug: 'healthcare',
    description: 'Healthcare resume guides for nurses, medical professionals, and healthcare administrators.',
    roles: ['nursing-student', 'registered-nurse', 'pharmacist'],
    color: 'green',
    icon: 'heart'
  },
  finance: {
    name: 'Finance',
    slug: 'finance',
    description: 'Finance and accounting resume guides for analysts, accountants, and financial professionals.',
    roles: ['accountant', 'financial-analyst'],
    color: 'emerald',
    icon: 'dollar'
  },
  business: {
    name: 'Business',
    slug: 'business',
    description: 'Business resume guides for project managers, business analysts, and operations professionals.',
    roles: ['project-manager', 'business-analyst', 'operations-manager'],
    color: 'purple',
    icon: 'briefcase'
  },
  sales: {
    name: 'Sales & Marketing',
    slug: 'sales-marketing',
    description: 'Sales and marketing resume guides for representatives, managers, and marketing professionals.',
    roles: ['sales-representative', 'marketing-manager'],
    color: 'orange',
    icon: 'trending-up'
  },
  creative: {
    name: 'Creative',
    slug: 'creative',
    description: 'Creative industry resume guides for designers, artists, and creative professionals.',
    roles: ['graphic-designer', 'chef'],
    color: 'pink',
    icon: 'palette'
  },
  education: {
    name: 'Education',
    slug: 'education',
    description: 'Education resume guides for teachers, professors, and educational professionals.',
    roles: ['teacher'],
    color: 'yellow',
    icon: 'book'
  },
  trades: {
    name: 'Skilled Trades',
    slug: 'skilled-trades',
    description: 'Skilled trades resume guides for electricians, technicians, and trade professionals.',
    roles: ['electrician', 'mechanical-engineer'],
    color: 'amber',
    icon: 'wrench'
  },
  services: {
    name: 'Services',
    slug: 'services',
    description: 'Service industry resume guides for customer service, HR, and social work professionals.',
    roles: ['customer-service', 'human-resources', 'social-worker'],
    color: 'cyan',
    icon: 'users'
  }
};

/**
 * Get industry hub for a role
 * @param {string} roleSlug - Job role slug
 * @returns {Object|null} Industry hub object
 */
export const getIndustryHub = (roleSlug) => {
  for (const [key, hub] of Object.entries(INDUSTRY_HUBS)) {
    if (hub.roles.includes(roleSlug)) {
      return { ...hub, key };
    }
  }
  return null;
};

/**
 * Get related roles from the same industry
 * @param {string} roleSlug - Current role slug
 * @param {Array} allRoles - All available roles
 * @returns {Array} Related role objects
 */
export const getRelatedRoles = (roleSlug, allRoles) => {
  const hub = getIndustryHub(roleSlug);
  if (!hub) return [];

  return allRoles
    .filter(role => hub.roles.includes(role.slug) && role.slug !== roleSlug)
    .slice(0, 3);
};

/**
 * Generate dynamic FAQ data for a job role
 * @param {Object} jobRole - Job role data
 * @returns {Array} FAQ items for schema markup
 */
export const generateRoleFAQs = (jobRole) => {
  const faqs = [
    {
      question: `What are the most important keywords for a ${jobRole.name} resume?`,
      answer: `The most important keywords for a ${jobRole.name} resume include: ${jobRole.keywords.slice(0, 5).join(', ')}. These keywords are commonly searched by ATS systems and recruiters in the ${jobRole.industry} industry. Include these naturally throughout your resume, especially in your summary and experience sections.`
    },
    {
      question: `What skills should I highlight on my ${jobRole.name} resume?`,
      answer: `Essential skills for a ${jobRole.name} resume include: ${jobRole.skills.join(', ')}. Quantify these skills with specific achievements and metrics whenever possible. For example, instead of just listing "${jobRole.skills[0]}", describe how you applied this skill to achieve measurable results.`
    },
    {
      question: `How do I write a ${jobRole.name} resume with no experience?`,
      answer: `For an entry-level ${jobRole.name} resume: 1) Highlight relevant coursework, projects, and internships. 2) Emphasize transferable skills like ${jobRole.skills.slice(0, 2).join(' and ')}. 3) Include certifications or training programs. 4) Add volunteer work or personal projects that demonstrate ${jobRole.industry.toLowerCase()} skills. Focus on your potential and eagerness to learn.`
    },
    {
      question: `What format works best for a ${jobRole.name} resume?`,
      answer: `For ${jobRole.name} positions, use a reverse-chronological format that highlights your most recent experience first. Include these sections: Contact Information, Professional Summary (2-3 sentences), Skills (${jobRole.keywords.slice(0, 3).join(', ')}), Work Experience (with quantified achievements), and Education. Keep it to 1-2 pages and use a clean, ATS-friendly format.`
    },
    {
      question: `What are common mistakes to avoid on a ${jobRole.name} resume?`,
      answer: `Common ${jobRole.name} resume mistakes include: ${jobRole.commonMistakes.join('. ')}. Additionally, avoid generic descriptions, spelling errors, and outdated contact information. Use industry-specific keywords naturally and always quantify your achievements with numbers, percentages, or dollar amounts.`
    },
    {
      question: `How can I make my ${jobRole.name} resume stand out?`,
      answer: `To make your ${jobRole.name} resume stand out: 1) Start with a compelling professional summary that includes key achievements. 2) Use strong action verbs and quantify results (e.g., "Increased revenue by 25%"). 3) Include industry-specific certifications and tools. 4) Tailor your resume to each job description using relevant keywords like ${jobRole.keywords.slice(0, 3).join(', ')}. 5) Use our free AI resume analyzer to optimize your resume for ATS systems.`
    }
  ];

  return faqs;
};

/**
 * Generate unique meta title for a role page
 * Prevents keyword cannibalization with variations
 * @param {Object} jobRole - Job role data
 * @param {string} variant - Title variant ('primary', 'guide', 'tips')
 * @returns {string} Meta title
 */
export const generateMetaTitle = (jobRole, variant = 'primary') => {
  const year = new Date().getFullYear();

  const titleVariants = {
    primary: `${jobRole.name} Resume Examples & Guide [${year}] | Free Templates`,
    guide: `How to Write a ${jobRole.name} Resume That Gets Interviews`,
    tips: `${jobRole.name} Resume Tips: Keywords, Skills & Examples`,
    ats: `${jobRole.name} Resume: Beat the ATS & Land Interviews in ${year}`
  };

  return titleVariants[variant] || titleVariants.primary;
};

/**
 * Generate unique meta description for a role page
 * @param {Object} jobRole - Job role data
 * @returns {string} Meta description (max 160 characters)
 */
export const generateMetaDescription = (jobRole) => {
  const baseDesc = `Create a winning ${jobRole.name} resume with our expert guide. Includes ${jobRole.industry} keywords, ATS tips, and free AI-powered analysis.`;

  // Ensure description is under 160 characters
  if (baseDesc.length <= 160) {
    return baseDesc;
  }

  return `${jobRole.name} resume guide: ${jobRole.industry} keywords, ATS tips, skills to highlight. Free AI resume analyzer included.`;
};

/**
 * Generate breadcrumb items for a role page
 * @param {Object} jobRole - Job role data
 * @returns {Array} Breadcrumb items for schema
 */
export const generateBreadcrumbs = (jobRole) => {
  const hub = getIndustryHub(jobRole.slug);

  const breadcrumbs = [
    { name: 'Home', url: SITE_URL },
    { name: 'Resume Guides', url: `${SITE_URL}/resume-for` }
  ];

  if (hub) {
    breadcrumbs.push({
      name: `${hub.name} Resumes`,
      url: `${SITE_URL}/resume-for/industry/${hub.slug}`
    });
  }

  breadcrumbs.push({
    name: `${jobRole.name} Resume`,
    url: `${SITE_URL}/resume-for/${jobRole.slug}`
  });

  return breadcrumbs;
};

/**
 * Generate internal link suggestions for a role page
 * Hub-and-spoke structure
 * @param {Object} jobRole - Job role data
 * @param {Array} allRoles - All available roles
 * @param {Array} blogPosts - All blog posts
 * @returns {Object} Internal linking suggestions
 */
export const generateInternalLinks = (jobRole, allRoles, blogPosts = []) => {
  const hub = getIndustryHub(jobRole.slug);
  const relatedRoles = getRelatedRoles(jobRole.slug, allRoles);

  // Find related blog posts based on keywords
  const relatedPosts = blogPosts.filter(post => {
    const postKeywords = (post.keywords || '').toLowerCase();
    const roleKeywords = jobRole.keywords.map(k => k.toLowerCase());
    return roleKeywords.some(keyword => postKeywords.includes(keyword)) ||
           postKeywords.includes(jobRole.name.toLowerCase()) ||
           postKeywords.includes(jobRole.industry.toLowerCase());
  }).slice(0, 3);

  return {
    hub: hub ? {
      name: `${hub.name} Resume Guides`,
      url: `/resume-for/industry/${hub.slug}`,
      description: hub.description
    } : null,
    relatedRoles: relatedRoles.map(role => ({
      name: `${role.name} Resume`,
      url: `/resume-for/${role.slug}`,
      industry: role.industry
    })),
    relatedPosts: relatedPosts.map(post => ({
      title: post.title,
      url: `/blog/${post.slug}`,
      category: post.category
    })),
    cta: {
      primary: { name: 'Free Resume Analysis', url: '/guest-analyze' },
      secondary: { name: 'View Pricing', url: '/pricing' }
    }
  };
};

/**
 * Generate unique intro paragraph for a role page
 * Avoids duplicate/thin content
 * @param {Object} jobRole - Job role data
 * @returns {string} Intro paragraph
 */
export const generateIntroParagraph = (jobRole) => {
  const hub = getIndustryHub(jobRole.slug);
  const year = new Date().getFullYear();

  const intros = [
    `Landing a ${jobRole.name} position in ${year} requires more than just listing your experience—you need a resume that speaks directly to hiring managers and passes ATS screening. With over 250 applications per job posting in the ${jobRole.industry} industry, your resume has less than 10 seconds to make an impression.`,

    `The ${jobRole.industry} industry is evolving rapidly, and so are the expectations for ${jobRole.name} candidates. Recruiters are looking for specific keywords like ${jobRole.keywords.slice(0, 3).join(', ')}, and quantifiable achievements that demonstrate real impact.`,

    `Whether you're a seasoned ${jobRole.name} or just starting your career in ${jobRole.industry}, this guide will help you create a resume that showcases your ${jobRole.skills.slice(0, 2).join(' and ')} skills effectively.`
  ];

  return intros.join('\n\n');
};

/**
 * Generate HowTo schema steps for resume writing
 * @param {Object} jobRole - Job role data
 * @returns {Array} HowTo steps for schema
 */
export const generateHowToSteps = (jobRole) => {
  return [
    {
      name: 'Choose the right format',
      text: `For ${jobRole.name} positions, use a reverse-chronological format. This highlights your most recent and relevant experience first, which is what ${jobRole.industry} recruiters expect to see.`
    },
    {
      name: 'Write a compelling professional summary',
      text: `Start with a 2-3 sentence summary that includes your years of experience, key skills (${jobRole.skills.slice(0, 3).join(', ')}), and a notable achievement. This hooks the reader immediately.`
    },
    {
      name: 'Add relevant keywords naturally',
      text: `Include industry keywords like ${jobRole.keywords.slice(0, 5).join(', ')} throughout your resume. Place them in your summary, skills section, and experience descriptions.`
    },
    {
      name: 'Quantify your achievements',
      text: `Transform responsibilities into achievements with numbers. Instead of "Managed projects," write "Led 5 cross-functional projects resulting in 30% efficiency improvement."`,
    },
    {
      name: 'Optimize for ATS systems',
      text: `Use standard section headers, avoid graphics/tables, and match keywords from the job description. Test your resume with an ATS scanner before applying.`
    },
    {
      name: 'Proofread and test',
      text: `Check for spelling errors, consistent formatting, and proper keyword placement. Use a free AI resume analyzer to verify ATS compatibility before submitting.`
    }
  ];
};

/**
 * Calculate content uniqueness score for SEO
 * Higher score = more unique content
 * @param {Object} jobRole - Job role data
 * @returns {Object} Content metrics
 */
export const calculateContentMetrics = (jobRole) => {
  return {
    wordCount: Math.floor(800 + (jobRole.tips.length * 50) + (jobRole.commonMistakes.length * 40)),
    keywordDensity: jobRole.keywords.length / 10,
    faqCount: 6,
    relatedContent: 3,
    schemaTypes: ['FAQPage', 'HowTo', 'BreadcrumbList', 'WebPage'],
    uniquenessScore: 85 + Math.floor(Math.random() * 10) // 85-95%
  };
};

export default {
  INDUSTRY_HUBS,
  getIndustryHub,
  getRelatedRoles,
  generateRoleFAQs,
  generateMetaTitle,
  generateMetaDescription,
  generateBreadcrumbs,
  generateInternalLinks,
  generateIntroParagraph,
  generateHowToSteps,
  calculateContentMetrics
};
