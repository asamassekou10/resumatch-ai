import { Helmet } from 'react-helmet-async';

/**
 * SEO Component
 *
 * Manages page-specific meta tags for SEO optimization.
 * Handles:
 * - Page titles
 * - Meta descriptions
 * - Open Graph tags (social media sharing)
 * - Twitter Card tags
 * - Canonical URLs
 * - Keywords (optional)
 *
 * @param {Object} props
 * @param {string} props.title - Page title (will be appended with " | ResumeAnalyzer AI")
 * @param {string} props.description - Page meta description
 * @param {string} props.keywords - Comma-separated keywords (optional)
 * @param {string} props.image - Social media share image URL (optional)
 * @param {string} props.url - Canonical URL for this page (optional)
 * @param {string} props.type - Open Graph type (default: "website")
 */
const SEO = ({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website'
}) => {
  // Default values
  const siteUrl = 'https://resumeanalyzerai.com';
  const defaultTitle = 'ResumeAnalyzer AI - AI-Powered Resume Analysis & Job Matching';
  const defaultDescription = 'Optimize your resume with AI-powered analysis, ATS scoring, skill gap analysis, and personalized job matching. Get hired faster with ResumeAnalyzer AI.';
  const defaultImage = `${siteUrl}/og-image.png`; // You'll need to add this image
  const siteName = 'ResumeAnalyzer AI';

  // Construct final values
  const pageTitle = title ? `${title} | ${siteName}` : defaultTitle;
  const pageDescription = description || defaultDescription;
  const pageUrl = url || siteUrl;
  const pageImage = image || defaultImage;

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
      <meta property="og:locale" content="en_US" />

      {/* Twitter Card Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={pageTitle} />
      <meta name="twitter:description" content={pageDescription} />
      <meta name="twitter:image" content={pageImage} />
      <meta name="twitter:site" content="@resumatchai" />
      <meta name="twitter:creator" content="@resumatchai" />

      {/* Canonical URL */}
      <link rel="canonical" href={pageUrl} />

      {/* Additional Meta Tags */}
      <meta name="robots" content="index, follow" />
      <meta name="author" content="ResumeAnalyzer AI" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />

      {/* Theme Color for Mobile Browsers */}
      <meta name="theme-color" content="#0f172a" />
    </Helmet>
  );
};

export default SEO;
