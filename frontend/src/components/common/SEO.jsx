import { Helmet } from 'react-helmet-async';
import {
  generateOrganizationSchema,
  generateWebApplicationSchema,
} from '../../utils/structuredData';

/**
 * SEO Component
 *
 * Manages page-specific meta tags for SEO optimization.
 * Features:
 * - Dynamic page titles with brand suffix
 * - Meta descriptions (max 160 chars recommended)
 * - Open Graph tags (Facebook, LinkedIn)
 * - Twitter Card tags
 * - Canonical URL management (duplicate prevention)
 * - Keywords (optional, for legacy support)
 * - Structured data (JSON-LD)
 * - Robots directives
 *
 * @param {Object} props
 * @param {string} props.title - Page title (will be appended with " | ResumeAnalyzer AI")
 * @param {string} props.description - Page meta description (max 160 chars)
 * @param {string} props.keywords - Comma-separated keywords (optional)
 * @param {string} props.image - Social media share image URL (optional)
 * @param {string} props.url - Canonical URL for this page (required for proper SEO)
 * @param {string} props.type - Open Graph type (default: "website", use "article" for blog)
 * @param {Object} props.structuredData - Additional structured data schemas (optional)
 * @param {boolean} props.noindex - Set to true to prevent indexing (default: false)
 * @param {string} props.publishedTime - ISO date string for article published time
 * @param {string} props.modifiedTime - ISO date string for article modified time
 */
const SEO = ({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website',
  structuredData = null,
  noindex = false,
  publishedTime,
  modifiedTime
}) => {
  // Default values
  const siteUrl = 'https://www.resumeanalyzerai.com';
  const defaultTitle = 'ResumeAnalyzer AI - AI-Powered Resume Analysis & Job Matching';
  const defaultDescription = 'Optimize your resume with AI-powered analysis, ATS scoring, skill gap analysis, and personalized job matching. Get hired faster with ResumeAnalyzer AI.';
  const defaultImage = `${siteUrl}/og-image.png`;
  const siteName = 'ResumeAnalyzer AI';

  // Construct final values
  const pageTitle = title ? `${title} | ${siteName}` : defaultTitle;
  const pageDescription = description || defaultDescription;
  const pageImage = image || defaultImage;

  // Canonical URL handling - normalize to prevent duplicates
  // Always use www version and remove trailing slashes (except for root)
  const normalizeUrl = (inputUrl) => {
    if (!inputUrl) return siteUrl;

    let normalized = inputUrl;

    // Ensure https://www. prefix
    if (normalized.startsWith('https://resumeanalyzerai.com')) {
      normalized = normalized.replace('https://resumeanalyzerai.com', 'https://www.resumeanalyzerai.com');
    }

    // Remove trailing slash except for homepage
    if (normalized !== siteUrl && normalized.endsWith('/')) {
      normalized = normalized.slice(0, -1);
    }

    // Remove query parameters and hash for canonical
    const urlObj = new URL(normalized);
    normalized = `${urlObj.origin}${urlObj.pathname}`;

    return normalized;
  };

  const pageUrl = normalizeUrl(url);

  // Robots directive
  const robotsContent = noindex
    ? 'noindex, nofollow'
    : 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1';

  // Generate default structured data
  const defaultStructuredData = [
    generateOrganizationSchema(),
    generateWebApplicationSchema(),
  ];

  // Merge with custom structured data if provided
  const allStructuredData = structuredData
    ? [...defaultStructuredData, ...(Array.isArray(structuredData) ? structuredData : [structuredData])]
    : defaultStructuredData;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{pageTitle}</title>
      <meta name="description" content={pageDescription} />
      {keywords && <meta name="keywords" content={keywords} />}

      {/* Open Graph Tags (Facebook, LinkedIn) */}
      <meta property="og:site_name" content={siteName} />
      <meta property="og:title" content={pageTitle} />
      <meta property="og:description" content={pageDescription} />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:image" content={pageImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={pageTitle} />
      <meta property="og:locale" content="en_US" />

      {/* Twitter Card Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={pageTitle} />
      <meta name="twitter:description" content={pageDescription} />
      <meta name="twitter:image" content={pageImage} />
      <meta name="twitter:image:alt" content={pageTitle} />
      <meta name="twitter:site" content="@resumatchai" />
      <meta name="twitter:creator" content="@resumatchai" />

      {/* Canonical URL - Critical for duplicate prevention */}
      <link rel="canonical" href={pageUrl} />

      {/* Robots directive with enhanced settings */}
      <meta name="robots" content={robotsContent} />
      <meta name="googlebot" content={robotsContent} />

      {/* Additional Meta Tags */}
      <meta name="author" content="ResumeAnalyzer AI" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="format-detection" content="telephone=no" />

      {/* Article timestamps for blog posts */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && (
        <meta property="article:author" content="ResumeAnalyzer AI" />
      )}

      {/* Theme Color for Mobile Browsers */}
      <meta name="theme-color" content="#0f172a" />

      {/* Structured Data (JSON-LD) */}
      {allStructuredData.map((data, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
        />
      ))}
    </Helmet>
  );
};

export default SEO;
