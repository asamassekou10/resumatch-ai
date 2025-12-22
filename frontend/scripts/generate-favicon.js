/**
 * Favicon Generator Script
 * 
 * Generates a multi-resolution favicon.ico file from PNG files
 * 
 * Usage: node scripts/generate-favicon.js
 * 
 * Note: This script uses the 'to-ico' package. If not installed:
 * npm install --save-dev to-ico
 * 
 * Alternative: Use online tools like:
 * - https://www.favicon-generator.org/
 * - https://realfavicongenerator.net/
 * - ImageMagick: convert favicon-16x16.png favicon-32x32.png favicon-48x48.png favicon.ico
 */

const fs = require('fs');
const path = require('path');

// Check if to-ico is available
let toIco;
try {
  toIco = require('to-ico');
} catch (err) {
  console.log('⚠️  to-ico package not found.');
  console.log('📦 Install it with: npm install --save-dev to-ico');
  console.log('🔄 Alternatively, use an online tool:');
  console.log('   - https://www.favicon-generator.org/');
  console.log('   - https://realfavicongenerator.net/');
  console.log('   - Or use ImageMagick: convert favicon-*.png favicon.ico');
  process.exit(1);
}

const publicDir = path.join(__dirname, '../public');
const faviconSizes = [
  { file: 'favicon-16x16.png', size: 16 },
  { file: 'favicon-32x32.png', size: 32 },
  { file: 'favicon-48x48.png', size: 48 },
];

async function generateFavicon() {
  console.log('🎨 Generating favicon.ico from PNG files...\n');

  // Read all PNG files
  const images = [];
  const missingFiles = [];

  for (const { file, size } of faviconSizes) {
    const filePath = path.join(publicDir, file);
    if (fs.existsSync(filePath)) {
      const buffer = fs.readFileSync(filePath);
      images.push(buffer);
      console.log(`✅ Found ${file} (${size}x${size})`);
    } else {
      missingFiles.push(file);
      console.log(`❌ Missing ${file}`);
    }
  }

  if (missingFiles.length > 0) {
    console.log(`\n⚠️  Missing files: ${missingFiles.join(', ')}`);
    console.log('Please ensure all favicon PNG files exist before generating favicon.ico\n');
    return;
  }

  if (images.length === 0) {
    console.log('❌ No favicon images found!');
    return;
  }

  try {
    // Generate ICO file
    const ico = await toIco(images);
    const outputPath = path.join(publicDir, 'favicon.ico');
    fs.writeFileSync(outputPath, ico);
    
    console.log(`\n✅ favicon.ico generated successfully!`);
    console.log(`📁 Location: ${outputPath}`);
    console.log(`📊 Size: ${(ico.length / 1024).toFixed(2)} KB`);
  } catch (error) {
    console.error('❌ Error generating favicon.ico:', error.message);
    console.log('\n💡 Alternative: Use an online tool to generate favicon.ico');
  }
}

generateFavicon();

