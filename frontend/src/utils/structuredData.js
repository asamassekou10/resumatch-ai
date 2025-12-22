/**
 * Structured Data Utility
 * 
 * Generates JSON-LD structured data for SEO
 */

const SITE_URL = 'https://resumeanalyzerai.com';
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

const structuredData = {
  generateOrganizationSchema,
  generateWebApplicationSchema,
  generateBreadcrumbSchema,
  generateFAQSchema,
  generateProductSchema,
  generateServiceSchema,
};

export default structuredData;

