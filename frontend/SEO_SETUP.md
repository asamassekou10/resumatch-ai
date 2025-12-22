# SEO Setup Guide

This document outlines the SEO improvements implemented and how to complete the setup.

## Implemented Features

### ✅ Technical SEO
- **Dynamic Sitemap Generation**: Automatic sitemap.xml generation with all public routes
- **Enhanced robots.txt**: Proper crawl directives for search engines
- **SEO Component**: Reusable SEO component with meta tags, Open Graph, and Twitter Cards
- **Structured Data**: JSON-LD schemas for Organization, WebApplication, FAQPage

### ✅ Performance Optimization
- **Resource Hints**: DNS prefetch and preconnect for faster resource loading
- **Nginx Enhancements**: Optimized compression, caching headers, and static file serving
- **Service Worker**: PWA caching for offline support and faster page loads
- **Web Vitals Tracking**: Core Web Vitals sent to Google Analytics

### ✅ Analytics & Tracking
- **Google Analytics 4**: Integrated with page view and event tracking
- **Route Tracking**: Automatic page view tracking on route changes
- **Conversion Events**: Ready-to-use event tracking functions

## Required Setup

### 1. Google Analytics Setup

1. Create a Google Analytics 4 property at https://analytics.google.com
2. Get your Measurement ID (format: `G-XXXXXXXXXX`)
3. Add to your `.env` file:
   ```env
   REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   REACT_APP_ENABLE_ANALYTICS=true
   ```
4. Verify tracking in Google Analytics Real-Time reports

### 2. Open Graph Image

Create an Open Graph image (`og-image.png`) at `frontend/public/og-image.png`:

- **Dimensions**: 1200x630px
- **Format**: PNG or JPG
- **Content**: Should include your logo, app name, and tagline
- **File size**: Keep under 300KB for fast loading

You can use tools like:
- Canva (https://www.canva.com)
- Figma
- Photoshop

**Note**: The image is referenced in meta tags. If you don't create it, social shares will not display an image.

### 3. Favicon Icons

Ensure you have all favicon sizes in `frontend/public/`:
- `favicon.ico` (16x16, 32x32, 48x48)
- `favicon-16x16.png`
- `favicon-32x32.png`
- `apple-touch-icon.png` (180x180)
- `logo192.png` (192x192) - already exists
- `logo512.png` (512x512) - already exists

### 4. Google Search Console

1. Go to https://search.google.com/search-console
2. Add your property: `https://resumeanalyzerai.com`
3. Verify ownership (HTML tag or DNS)
4. Submit your sitemap: `https://resumeanalyzerai.com/sitemap.xml`
5. Monitor indexing status and fix any crawl errors

### 5. Environment Variables

Create/update `frontend/.env`:
```env
REACT_APP_API_URL=https://resumatch-backend-7qdb.onrender.com/api
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

## Testing SEO

### Validate Structured Data
- Google Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org/

### Check Meta Tags
- Open Graph Debugger: https://developers.facebook.com/tools/debug/
- Twitter Card Validator: https://cards-dev.twitter.com/validator

### Performance Testing
- Google PageSpeed Insights: https://pagespeed.web.dev/
- Lighthouse (Chrome DevTools)
- WebPageTest: https://www.webpagetest.org/

### Mobile Testing
- Google Mobile-Friendly Test: https://search.google.com/test/mobile-friendly

## Usage

### Tracking Custom Events

```javascript
import { trackEvent, trackResumeUpload, trackSubscription } from './utils/analytics';

// Track custom events
trackEvent('button_click', { button_name: 'Get Started', location: 'hero' });

// Track resume upload
trackResumeUpload('pdf');

// Track subscription
trackSubscription('pro', 29.99);
```

### Adding SEO to New Pages

```javascript
import SEO from './components/common/SEO';

function MyPage() {
  return (
    <>
      <SEO
        title="My Page Title"
        description="Page description for search engines"
        keywords="keyword1, keyword2, keyword3"
        url="https://resumeanalyzerai.com/my-page"
      />
      {/* Page content */}
    </>
  );
}
```

### Adding Structured Data

```javascript
import SEO from './components/common/SEO';
import { generateFAQSchema } from './utils/structuredData';

const faqs = [
  { question: 'Question 1?', answer: 'Answer 1' },
  { question: 'Question 2?', answer: 'Answer 2' },
];

function FAQPage() {
  return (
    <>
      <SEO
        title="FAQ"
        description="Frequently asked questions"
        structuredData={[generateFAQSchema(faqs)]}
      />
      {/* Page content */}
    </>
  );
}
```

## Build Process

The sitemap is automatically generated during build:

```bash
npm run build
```

Or manually:
```bash
npm run generate:sitemap
```

## Monitoring

### Weekly
- Check Google Search Console for indexing issues
- Review Google Analytics for traffic trends

### Monthly
- Review search performance in Search Console
- Check Core Web Vitals in Analytics
- Update sitemap if new pages are added

### Quarterly
- Full SEO audit
- Performance optimization review
- Content updates based on search trends

## Troubleshooting

### Analytics Not Tracking
1. Check `REACT_APP_ENABLE_ANALYTICS=true` in environment
2. Verify `REACT_APP_GOOGLE_ANALYTICS_ID` is set
3. Check browser console for errors
4. Verify Google Analytics property is active

### Sitemap Not Updating
- Run `npm run generate:sitemap` manually
- Check file permissions
- Verify routes are added to `scripts/generate-sitemap.js`

### Service Worker Not Working
- Check browser console for errors
- Clear browser cache and reload
- Verify service worker is registered (Application tab in DevTools)

## Additional Resources

- [Google Search Central](https://developers.google.com/search)
- [Schema.org Documentation](https://schema.org/)
- [Web.dev SEO Guide](https://web.dev/lighthouse-seo/)
- [Core Web Vitals](https://web.dev/vitals/)

