/**
 * Structured Data Utility
 * 
 * Generates JSON-LD structured data for SEO
 */

const SITE_URL = 'https://www.resumeanalyzerai.com';
const SITE_NAME = 'ResumeAnalyzer AI';

/**
 * Generate Organization schema
 */
export const generateOrganizationSchema = () => ({
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: SITE_NAME,
  url: SITE_URL,
  logo: `${SITE_URL}/logo512.png`,
  description: 'AI-powered resume optimization and job matching platform',
  contactPoint: {
    '@type': 'ContactPoint',
    email: 'support@resumeanalyzerai.com',
    contactType: 'Customer Service',
  },
  sameAs: [
    // Add social media profiles when available
    // 'https://twitter.com/resumatchai',
    // 'https://linkedin.com/company/resumeanalyzerai',
  ],
});

/**
 * Generate WebApplication schema
 */
export const generateWebApplicationSchema = () => ({
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: SITE_NAME,
  description: 'AI-powered resume optimization and job matching platform that helps job seekers create ATS-friendly resumes and find the perfect job matches',
  url: SITE_URL,
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  offers: {
    '@type': 'AggregateOffer',
    lowPrice: '0',
    highPrice: '49.99',
    priceCurrency: 'USD',
    offerCount: '3',
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.8',
    ratingCount: '1250',
    bestRating: '5',
    worstRating: '1',
  },
  featureList: [
    'AI-powered resume analysis',
    'ATS keyword optimization',
    'Job match scoring',
    'Skill extraction and verification',
    'Career path recommendations',
    'Interview preparation',
  ],
});

/**
 * Generate BreadcrumbList schema
 * @param {Array} items - Array of {name, url} objects
 */
export const generateBreadcrumbSchema = (items) => ({
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: items.map((item, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: item.name,
    item: item.url,
  })),
});

/**
 * Generate FAQPage schema
 * @param {Array} faqs - Array of {question, answer} objects
 */
export const generateFAQSchema = (faqs) => ({
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map((faq) => ({
    '@type': 'Question',
    name: faq.question,
    acceptedAnswer: {
      '@type': 'Answer',
      text: faq.answer,
    },
  })),
});

/**
 * Generate Product schema for pricing tiers
 * @param {Object} product - Product information
 */
export const generateProductSchema = (product) => ({
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: product.name,
  description: product.description,
  offers: {
    '@type': 'Offer',
    price: product.price,
    priceCurrency: 'USD',
    availability: 'https://schema.org/InStock',
    url: `${SITE_URL}/pricing`,
  },
  category: 'Software',
});

/**
 * Generate Service schema
 */
export const generateServiceSchema = () => ({
  '@context': 'https://schema.org',
  '@type': 'Service',
  serviceType: 'Resume Analysis and Job Matching',
  provider: {
    '@type': 'Organization',
    name: SITE_NAME,
  },
  areaServed: 'Worldwide',
  description: 'AI-powered resume optimization, ATS scoring, skill gap analysis, and intelligent job matching services',
});

/**
 * Generate JobPosting schema for role pages
 * @param {Object} jobData - Job information
 */
export const generateJobPostingSchema = (jobData) => ({
  '@context': 'https://schema.org',
  '@type': 'JobPosting',
  title: jobData.title,
  description: jobData.description || `Resume optimization and analysis services for ${jobData.title} positions`,
  industry: jobData.industry,
  skills: jobData.skills || [],
  employmentType: 'FULL_TIME',
  jobLocation: {
    '@type': 'Place',
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'US',
    },
  },
  baseSalary: {
    '@type': 'MonetaryAmount',
    currency: 'USD',
  },
  datePosted: new Date().toISOString(),
  validThrough: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), // 90 days from now
  hiringOrganization: {
    '@type': 'Organization',
    name: SITE_NAME,
    sameAs: SITE_URL,
  },
});

/**
 * Generate Article schema for blog posts
 * @param {Object} articleData - Article information
 */
export const generateArticleSchema = (articleData) => ({
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: articleData.headline,
  description: articleData.description,
  author: {
    '@type': 'Organization',
    name: SITE_NAME,
    url: SITE_URL,
  },
  publisher: {
    '@type': 'Organization',
    name: SITE_NAME,
    logo: {
      '@type': 'ImageObject',
      url: `${SITE_URL}/logo512.png`,
    },
  },
  datePublished: articleData.datePublished,
  dateModified: articleData.dateModified || articleData.datePublished,
  image: articleData.image || `${SITE_URL}/og-image.png`,
  mainEntityOfPage: {
    '@type': 'WebPage',
    '@id': articleData.url,
  },
});

const structuredData = {
  generateOrganizationSchema,
  generateWebApplicationSchema,
  generateBreadcrumbSchema,
  generateFAQSchema,
  generateProductSchema,
  generateServiceSchema,
  generateJobPostingSchema,
  generateArticleSchema,
};

export default structuredData;

