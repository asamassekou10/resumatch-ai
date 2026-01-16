/**
 * Postbuild script - handles prerendering for SEO
 *
 * On Vercel/CI: Runs lightweight static HTML generator (no Puppeteer required)
 * Locally: Runs react-snap for full prerendering with Puppeteer
 */

const { execSync } = require('child_process');
const path = require('path');

// Always run the SEO prerender generator (works everywhere)
console.log('Generating SEO-optimized static pages...');
try {
  execSync('node scripts/generate-prerender-pages.js', {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
  });
} catch (error) {
  console.error('SEO page generation failed:', error.message);
  // Don't exit - this is a non-critical enhancement
}

// On Vercel or CI, we're done (Puppeteer not supported)
if (process.env.VERCEL) {
  console.log('Vercel build complete - using static SEO pages');
  process.exit(0);
}

if (process.env.CI) {
  console.log('CI build complete - using static SEO pages');
  process.exit(0);
}

// Locally, also try react-snap for full client-side rendering
try {
  console.log('Running react-snap for full prerendering...');
  execSync('npx react-snap', { stdio: 'inherit' });
} catch (error) {
  console.error('react-snap failed (non-critical):', error.message);
  // Don't exit with error - SEO pages are already generated
}
