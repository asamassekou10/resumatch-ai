/**
 * Postbuild script - runs react-snap for prerendering
 * Skips on Vercel and CI environments since Puppeteer requires system libraries
 * and can have port conflicts in CI
 */

if (process.env.VERCEL) {
  console.log('Skipping react-snap on Vercel (Puppeteer not supported)');
  process.exit(0);
}

if (process.env.CI) {
  console.log('Skipping react-snap on CI environment (port conflicts and resource limitations)');
  process.exit(0);
}

const { execSync } = require('child_process');

try {
  console.log('Running react-snap for prerendering...');
  execSync('npx react-snap', { stdio: 'inherit' });
} catch (error) {
  console.error('react-snap failed:', error.message);
  process.exit(1);
}
