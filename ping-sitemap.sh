#!/bin/bash
# Ping search engines about sitemap updates
# Run this after deploying new content

SITEMAP_URL="https://resumeanalyzerai.com/sitemap.xml"

echo "🔔 Pinging search engines about sitemap update..."
echo ""

# Ping Google
echo "📍 Pinging Google..."
curl -s "http://www.google.com/ping?sitemap=${SITEMAP_URL}" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Google pinged successfully"
else
  echo "❌ Failed to ping Google"
fi

# Ping Bing
echo "📍 Pinging Bing..."
curl -s "http://www.bing.com/ping?sitemap=${SITEMAP_URL}" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Bing pinged successfully"
else
  echo "❌ Failed to ping Bing"
fi

echo ""
echo "✅ Done! Search engines have been notified."
echo "⏰ Allow 24-48 hours for recrawling."
