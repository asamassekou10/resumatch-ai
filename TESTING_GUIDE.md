# React Router Migration - Testing Guide

**Purpose:** Verify that the React Router migration works correctly across all features
**Priority:** High - Must complete before merging to main
**Estimated Time:** 2-3 hours

---

## Quick Start

```bash
# Run the application locally
cd frontend
npm start

# Open in browser
http://localhost:3000
```

---

## Critical Path Testing (30 minutes)

### Test 1: Landing Page & Navigation
1. Open `http://localhost:3000/`
2. ✅ Verify landing page loads
3. ✅ Click "Try Free (5 Credits)" → Should go to `/guest-analyze`
4. ✅ Click "View Pricing" → Should go to `/pricing`
5. ✅ Click browser back button → Should return to landing
6. ✅ Refresh page → Should stay on current page (not return to landing)

### Test 2: Guest Analysis Flow
1. Go to `http://localhost:3000/guest-analyze`
2. ✅ Verify page loads
3. ✅ Upload a resume file
4. ✅ Click "Analyze Resume"
5. ✅ Verify analysis completes
6. ✅ Click "Sign In" button → Should navigate somewhere
7. ✅ Click "View Pricing" button → Should go to `/pricing`

### Test 3: Pricing Page
1. Go to `http://localhost:3000/pricing`
2. ✅ Verify page loads with 3 plans (Free, Pro, Elite)
3. ✅ Verify page title in browser tab: "Pricing Plans | ResuMatch AI"
4. ✅ Click toggle between Monthly/Yearly
5. ✅ Verify prices update correctly
6. ✅ Test plan selection buttons

### Test 4: Direct URL Access
1. Open a new tab
2. Go directly to `http://localhost:3000/pricing`
3. ✅ Page loads correctly (doesn't redirect to landing)
4. Go directly to `http://localhost:3000/guest-analyze`
5. ✅ Page loads correctly
6. Go to `http://localhost:3000/nonexistent-page`
7. ✅ Should redirect to landing page

### Test 5: Browser Navigation
1. Navigate through several pages (landing → pricing → guest-analyze)
2. ✅ Click browser back button multiple times
3. ✅ Verify it goes through history correctly
4. ✅ Click browser forward button
5. ✅ Verify it goes forward through history

---

## Protected Routes Testing (If Logged In)

### Test 6: Authentication Flow
1. Log in to the application
2. ✅ Should redirect to `/dashboard` after login
3. ✅ Verify Navigation menu shows user-specific items
4. ✅ Test User Menu dropdown (click user avatar/name)
5. ✅ Click "Profile" → Should go to `/profile`
6. ✅ Click "Billing" → Should go to `/billing`
7. ✅ Logout → Should return to landing page

### Test 7: Profile Page
1. Navigate to `/profile`
2. ✅ Verify profile page loads
3. ✅ Click "View All Analyses" button → Should navigate to dashboard
4. ✅ Test "Edit Profile" functionality
5. ✅ Refresh page → Should stay on profile page

### Test 8: Billing Page
1. Navigate to `/billing`
2. ✅ Verify billing page loads
3. If on Free plan:
   - ✅ Click "Upgrade to Pro" → Should go to `/pricing`
4. If on Pro plan:
   - ✅ Click "Upgrade to Elite" → Should go to `/pricing`
5. ✅ Refresh page → Should stay on billing page

### Test 9: Market Intelligence Routes
1. Click "Market Intelligence" in navigation
2. ✅ Should show dropdown menu
3. ✅ Click "Overview" → Should go to `/market/dashboard`
4. ✅ Click "Interview Prep" → Should go to `/market/interview-prep`
5. ✅ Click "Company Intel" → Should go to `/market/company-intel`
6. ✅ Click "Career Path" → Should go to `/market/career-path`
7. ✅ Verify each page loads correctly
8. ✅ Refresh on any market page → Should stay on that page

### Test 10: Subscription Required Flow
1. If not subscribed, try to access `/market/dashboard`
2. ✅ Should show SubscriptionRequired page OR redirect to pricing
3. ✅ Click "View Pricing Plans" → Should go to `/pricing`
4. ✅ Click "Back to Dashboard" → Should go to `/dashboard`

---

## Mobile Testing (30 minutes)

### Test 11: Mobile Navigation
1. Open DevTools and switch to mobile view (iPhone/Android)
2. ✅ Click hamburger menu icon
3. ✅ Mobile menu opens
4. ✅ Click "Dashboard" → Should navigate and close menu
5. ✅ Click "Market Intelligence" → Should expand sub-menu
6. ✅ Click a market item → Should navigate and close menu
7. ✅ Click user menu items → Should navigate and close menu
8. ✅ Click outside menu → Should close menu

### Test 12: Mobile Browser Features
1. On mobile device/simulator
2. ✅ Test pull-to-refresh → Should not break navigation
3. ✅ Test landscape/portrait orientation changes
4. ✅ Test iOS "swipe back" gesture (if iOS)
5. ✅ Test Android back button

---

## SEO & Meta Tags Testing (15 minutes)

### Test 13: Page Titles
1. Navigate to different pages and check browser tab title:
   - `/` → "ResuMatch AI - AI-Powered Resume Analysis & Job Matching"
   - `/pricing` → "Pricing Plans | ResuMatch AI"
   - `/guest-analyze` → "Free Resume Analysis | ResuMatch AI"
2. ✅ Each page has unique title

### Test 14: Meta Tags (View Page Source)
1. Right-click → "View Page Source" on different pages
2. ✅ Look for `<meta name="description">`
3. ✅ Look for `<meta property="og:title">`
4. ✅ Look for `<meta name="twitter:card">`
5. ✅ Look for `<link rel="canonical">`

### Test 15: Social Media Sharing
1. Optional: Use Facebook Debugger (https://developers.facebook.com/tools/debug/)
2. Enter your staging URL
3. ✅ Verify Open Graph tags load correctly
4. Optional: Use Twitter Card Validator
5. ✅ Verify Twitter Card tags load correctly

---

## Cross-Browser Testing (30 minutes)

### Test 16: Desktop Browsers
Test the critical path in each browser:
- [ ] **Chrome** (latest)
  - Landing → Pricing → Guest Analyze → Back button
- [ ] **Firefox** (latest)
  - Landing → Pricing → Guest Analyze → Back button
- [ ] **Safari** (latest - Mac only)
  - Landing → Pricing → Guest Analyze → Back button
- [ ] **Edge** (latest)
  - Landing → Pricing → Guest Analyze → Back button

### Test 17: Mobile Browsers
- [ ] **Mobile Safari** (iOS)
  - Test critical path + mobile menu
- [ ] **Chrome Mobile** (Android)
  - Test critical path + mobile menu

---

## Performance Testing (15 minutes)

### Test 18: Lighthouse Audit
1. Open Chrome DevTools → Lighthouse tab
2. Run audit on `/` (landing page)
3. ✅ Performance score > 80
4. ✅ Best Practices score > 90
5. ✅ SEO score > 90
6. ✅ Accessibility score > 80

### Test 19: Network Performance
1. Open DevTools → Network tab
2. Throttle to "Fast 3G"
3. Navigate through pages
4. ✅ Pages load within 5 seconds
5. ✅ Loading spinner shows during lazy loading
6. ✅ No infinite loading states

### Test 20: Bundle Size
1. Run `npm run build`
2. Check output:
   - ✅ Main bundle < 150KB (gzipped)
   - ✅ Code splitting working (multiple chunks)
   - ✅ Lazy loaded routes don't load on initial page

---

## Edge Cases & Error Handling (20 minutes)

### Test 21: Invalid URLs
1. Go to `http://localhost:3000/invalid-route-12345`
2. ✅ Redirects to landing page (or shows 404 page)
3. ✅ No console errors

### Test 22: Protected Route Without Auth
1. Log out (or clear localStorage)
2. Try to access `http://localhost:3000/dashboard`
3. ✅ Redirects to login page or landing
4. Try to access `http://localhost:3000/profile`
5. ✅ Redirects to login page or landing

### Test 23: Rapid Navigation
1. Quickly click through multiple pages
2. ✅ No broken states
3. ✅ No console errors
4. ✅ Active page highlighting stays correct

### Test 24: Page Refresh Scenarios
1. Navigate to `/pricing`
2. Refresh page (F5)
3. ✅ Stays on `/pricing`
4. Navigate to `/guest-analyze`
5. Hard refresh (Ctrl+Shift+R)
6. ✅ Stays on `/guest-analyze` and loads correctly

---

## Console Error Check (Throughout Testing)

Keep DevTools Console open during ALL testing:
- ✅ No React errors (red text)
- ✅ No 404 errors for assets
- ✅ No undefined/null errors
- ✅ Warnings are acceptable (ESLint warnings already known)

---

## Testing Completion Checklist

### Must Pass (P0)
- [ ] Landing page loads
- [ ] Navigation between pages works
- [ ] Browser back/forward buttons work
- [ ] Page refresh works on all pages
- [ ] Direct URL access works
- [ ] Mobile menu works
- [ ] No critical console errors

### Should Pass (P1)
- [ ] All protected routes work
- [ ] Authentication flow works (if implemented)
- [ ] SEO meta tags present
- [ ] Lighthouse score > 80
- [ ] Cross-browser compatibility
- [ ] Mobile responsive

### Nice to Have (P2)
- [ ] Social media sharing previews work
- [ ] Performance < 3s on Fast 3G
- [ ] All ESLint warnings addressed
- [ ] Accessibility score > 90

---

## Reporting Issues

If you find any issues during testing:

1. **Document the Issue:**
   - What page were you on?
   - What action did you take?
   - What happened (actual behavior)?
   - What should have happened (expected behavior)?
   - Browser and device used
   - Console errors (if any)

2. **Priority Classification:**
   - **P0 (Critical):** Breaks core functionality, blocks testing
   - **P1 (High):** Major feature doesn't work, workaround exists
   - **P2 (Medium):** Minor issue, doesn't block users
   - **P3 (Low):** Cosmetic issue, nice-to-fix

3. **Report Location:**
   - Add to GitHub Issues
   - Or create `TESTING_ISSUES.md` file
   - Or notify the team directly

---

## Sign-Off

**Tester Name:** _________________
**Date:** _________________
**Overall Status:** [ ] Pass  [ ] Pass with Issues  [ ] Fail
**Ready for Production:** [ ] Yes  [ ] No  [ ] Pending Fixes

**Notes:**
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

## Quick Troubleshooting

**Issue:** Page redirects to landing instead of staying on route
- **Fix:** Check server configuration (_redirects or vercel.json)
- **Fix:** Ensure SPA routing configured on deployment platform

**Issue:** Console error "Cannot read property of undefined"
- **Fix:** Check component props - likely missing userProfile or token
- **Fix:** Ensure ProtectedRoute wraps the component correctly

**Issue:** Images/assets not loading
- **Fix:** Check relative paths in code
- **Fix:** Ensure public folder assets copied to build

**Issue:** Lazy loaded components not loading
- **Fix:** Check import paths in AppRoutes.jsx
- **Fix:** Ensure components export default

---

**Happy Testing! 🚀**
