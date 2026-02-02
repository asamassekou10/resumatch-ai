/**
 * Structured Data Utility
 *
 * Generates JSON-LD structured data for SEO
 * Supports: Organization, WebApplication, BreadcrumbList, FAQPage,
 * Product, Service, Article, HowTo, WebPage, and more.
 *
 * Usage:
 * import { generateFAQSchema, generateHowToSchema } from './structuredData';
 * const schemas = [generateFAQSchema(faqs), generateHowToSchema(steps)];
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
  foundingDate: '2024',
  contactPoint: {
    '@type': 'ContactPoint',
    email: 'support@resumeanalyzerai.com',
    contactType: 'Customer Service',
    availableLanguage: ['English'],
  },
  sameAs: [
    'https://twitter.com/resumatchai',
    'https://linkedin.com/company/resumeanalyzerai',
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
 * Generate HowTo schema for resume writing guides
 * Better suited for programmatic SEO pages than JobPosting
 * @param {Object} howToData - HowTo information
 */
export const generateHowToSchema = (howToData) => ({
  '@context': 'https://schema.org',
  '@type': 'HowTo',
  name: howToData.name || `How to Write a ${howToData.role} Resume`,
  description: howToData.description || `Step-by-step guide to creating a professional ${howToData.role} resume that passes ATS screening and impresses hiring managers.`,
  totalTime: 'PT30M',
  estimatedCost: {
    '@type': 'MonetaryAmount',
    currency: 'USD',
    value: '0'
  },
  supply: howToData.supplies || [
    { '@type': 'HowToSupply', name: 'Your work experience details' },
    { '@type': 'HowToSupply', name: 'Education and certifications' },
    { '@type': 'HowToSupply', name: 'Skills and achievements' }
  ],
  tool: [
    { '@type': 'HowToTool', name: 'ResumeAnalyzer AI (free)' },
    { '@type': 'HowToTool', name: 'Word processor or resume builder' }
  ],
  step: (howToData.steps || []).map((step, index) => ({
    '@type': 'HowToStep',
    position: index + 1,
    name: step.name,
    text: step.text,
    url: `${SITE_URL}/resume-for/${howToData.slug}#step-${index + 1}`
  }))
});

/**
 * Generate WebPage schema for programmatic SEO pages
 * @param {Object} pageData - Page information
 */
export const generateWebPageSchema = (pageData) => ({
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  name: pageData.name,
  description: pageData.description,
  url: pageData.url,
  isPartOf: {
    '@type': 'WebSite',
    name: SITE_NAME,
    url: SITE_URL
  },
  about: {
    '@type': 'Thing',
    name: pageData.about || pageData.name
  },
  mainEntity: pageData.mainEntity || undefined,
  breadcrumb: pageData.breadcrumb || undefined,
  speakable: {
    '@type': 'SpeakableSpecification',
    cssSelector: ['h1', '.article-prose']
  },
  datePublished: pageData.datePublished || new Date().toISOString().split('T')[0],
  dateModified: pageData.dateModified || new Date().toISOString().split('T')[0]
});

/**
 * Generate Occupation schema for role pages (alternative to JobPosting)
 * More appropriate for resume guide pages
 * @param {Object} occupationData - Occupation information
 */
export const generateOccupationSchema = (occupationData) => ({
  '@context': 'https://schema.org',
  '@type': 'Occupation',
  name: occupationData.name,
  description: occupationData.description,
  occupationLocation: {
    '@type': 'Country',
    name: 'United States'
  },
  skills: occupationData.skills?.join(', ') || '',
  qualifications: occupationData.qualifications || `Experience in ${occupationData.industry}`,
  responsibilities: occupationData.responsibilities || occupationData.description,
  occupationalCategory: occupationData.industry
});

/**
 * Generate ItemList schema for listing pages (blog index, role index)
 * @param {Array} items - Array of items with name and url
 * @param {string} listName - Name of the list
 */
export const generateItemListSchema = (items, listName) => ({
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: listName,
  numberOfItems: items.length,
  itemListElement: items.map((item, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: item.name || item.title,
    url: item.url
  }))
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

/**
 * Generate VideoObject schema for demo videos
 * @param {Object} videoData - Video information
 */
export const generateVideoSchema = (videoData) => ({
  '@context': 'https://schema.org',
  '@type': 'VideoObject',
  name: videoData.name || 'How to Use ResumeAnalyzer AI - Demo Video',
  description: videoData.description || 'Watch how ResumeAnalyzer AI analyzes your resume, provides ATS optimization tips, and helps you land more interviews.',
  thumbnailUrl: videoData.thumbnailUrl || `${SITE_URL}/demo-video-cover.png`,
  uploadDate: videoData.uploadDate || '2026-01-01',
  duration: videoData.duration || 'PT2M30S', // ISO 8601 duration format
  contentUrl: videoData.contentUrl || `${SITE_URL}/demo-video.mp4`,
  embedUrl: videoData.embedUrl || `${SITE_URL}/demo-video.mp4`,
  publisher: {
    '@type': 'Organization',
    name: SITE_NAME,
    logo: {
      '@type': 'ImageObject',
      url: `${SITE_URL}/logo512.png`,
    },
  },
  potentialAction: {
    '@type': 'WatchAction',
    target: `${SITE_URL}/#demo-video`,
  },
});

/**
 * Generate Review schema for testimonials
 * @param {Object} reviewData - Review information
 */
export const generateReviewSchema = (reviewData) => ({
  '@context': 'https://schema.org',
  '@type': 'Review',
  itemReviewed: {
    '@type': 'SoftwareApplication',
    name: SITE_NAME,
    applicationCategory: 'BusinessApplication',
  },
  reviewRating: {
    '@type': 'Rating',
    ratingValue: reviewData.rating || '5',
    bestRating: '5',
    worstRating: '1',
  },
  author: {
    '@type': 'Person',
    name: reviewData.authorName,
    jobTitle: reviewData.authorTitle || undefined,
  },
  reviewBody: reviewData.reviewText,
  datePublished: reviewData.datePublished || new Date().toISOString().split('T')[0],
});

/**
 * Generate multiple reviews as an array
 * @param {Array} reviews - Array of review objects
 */
export const generateReviewsSchema = (reviews) => 
  reviews.map(review => generateReviewSchema(review));

/**
 * Generate SoftwareApplication schema with reviews
 * Combines app info with aggregate rating and individual reviews
 */
export const generateSoftwareAppWithReviewsSchema = (reviews = []) => ({
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: SITE_NAME,
  description: 'AI-powered resume optimization and job matching platform that helps job seekers create ATS-friendly resumes and find the perfect job matches',
  url: SITE_URL,
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web Browser',
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
    reviewCount: '500',
    ratingCount: '1250',
    bestRating: '5',
    worstRating: '1',
  },
  review: reviews.length > 0 ? reviews.map(review => ({
    '@type': 'Review',
    reviewRating: {
      '@type': 'Rating',
      ratingValue: review.rating || '5',
      bestRating: '5',
    },
    author: {
      '@type': 'Person',
      name: review.authorName,
    },
    reviewBody: review.reviewText,
  })) : undefined,
});

const structuredData = {
  generateOrganizationSchema,
  generateWebApplicationSchema,
  generateBreadcrumbSchema,
  generateFAQSchema,
  generateProductSchema,
  generateServiceSchema,
  generateHowToSchema,
  generateWebPageSchema,
  generateOccupationSchema,
  generateItemListSchema,
  generateArticleSchema,
  generateVideoSchema,
  generateReviewSchema,
  generateReviewsSchema,
  generateSoftwareAppWithReviewsSchema,
};

export default structuredData;

