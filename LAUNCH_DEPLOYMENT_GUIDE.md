# Launch Strategy Deployment Guide

## Quick Summary

✅ **Ready to deploy:** Launch pricing strategy with 10 free credits and Founding Member tier
✅ **All code complete:** Backend migrations, frontend components, and API endpoints ready
✅ **Zero risk:** No existing paying users to disrupt

---

## Pre-Deployment Checklist

### 1. Stripe Setup (30 minutes)

Create the following products in your Stripe Dashboard:

#### Product 1: Pro Founding Member
- Name: `Pro - Founding Member`
- Description: `Limited to first 100 subscribers. Lock in $19.99/month forever.`
- Price: `$19.99/month` recurring
- Copy the **Price ID** (starts with `price_`)

#### Product 2: Elite
- Name: `Elite`
- Description: `For recruiters and career coaches`
- Price: `$49.99/month` recurring
- Copy the **Price ID**

### 2. Environment Variables

Add these to Render.com dashboard (or .env for local):

```bash
# Required for launch
STRIPE_PRO_FOUNDING_PRICE_ID=price_xxxxxxxxxxxxx  # From Stripe Dashboard
STRIPE_ELITE_PRICE_ID=price_xxxxxxxxxxxxx         # From Stripe Dashboard

# Optional (for future phases)
STRIPE_STARTER_PRICE_ID=price_xxxxxxxxxxxxx       # Add in Month 3
STRIPE_PRO_PRICE_ID=price_xxxxxxxxxxxxx           # Add when Founding tier fills
STRIPE_PRO_ANNUAL_PRICE_ID=price_xxxxxxxxxxxxx    # Add in Month 3
```

---

## Deployment Steps

### Step 1: Run Database Migrations (5 minutes)

```bash
cd backend/migrations

# 1. Add subscription tracking fields
python add_subscription_fields.py

# 2. Update pricing tiers (Free: 10 credits, Pro Founding: $19.99, Elite: $49.99)
python update_pricing_tiers.py

# 3. Configure credit costs per operation
python add_credit_costs.py
```

**Expected output:**
```
✅ Subscription fields added
✅ New tiers inserted
✅ Credit costs configured
```

### Step 2: Deploy Backend (10 minutes)

```bash
# Commit all changes
git add .
git commit -m "Launch strategy: 10 free credits, Founding Member tier at $19.99"
git push origin main
```

Render will auto-deploy. Check logs for:
- ✅ `Subscription scheduler initialized (credit reset & trial expiration)`
- ✅ `Database initialized successfully`
- ✅ No errors on startup

### Step 3: Deploy Frontend (5 minutes)

Frontend changes are already committed. Verify pricing page shows:
- Free: 10 analyses
- Pro Founding: $19.99/month (highlighted)
- Elite: $49.99/month

### Step 4: Test End-to-End (15 minutes)

#### Test 1: New User Registration
1. Sign up with test email
2. Verify user gets 10 credits
3. Check dashboard shows credit balance

#### Test 2: Founding Member Upgrade
1. Go to pricing page
2. Click "Join as Founding Member"
3. Complete Stripe checkout (use test card: `4242 4242 4242 4242`)
4. Verify:
   - User gets 50 credits
   - Subscription tier = `pro_founding`
   - Subscription status = `active`

#### Test 3: Credit Deduction
1. Upload resume and analyze
2. Verify 1 credit is deducted
3. Check response includes `credits_remaining`

#### Test 4: Founding Member Limit
1. Create 100 test users with `pro_founding` tier (or manually update DB)
2. Try to subscribe as 101st member
3. Verify error: "Founding Member tier is full"

---

## Post-Deployment Verification

### Check Database

```sql
-- Verify tiers exist
SELECT name, display_name, monthly_credits, price_cents
FROM subscription_tier
WHERE is_active = true;

-- Should show:
-- free | Free | 10 | 0
-- pro_founding | Pro - Founding Member | 50 | 1999
-- elite | Elite | 200 | 4999

-- Verify credit costs
SELECT operation, subscription_tier, cost_in_credits
FROM rate_limit_config
WHERE subscription_tier IN ('free', 'pro_founding');

-- Check no founding members yet
SELECT COUNT(*) FROM users WHERE subscription_tier = 'pro_founding';
-- Should be 0
```

### Check API Endpoints

```bash
# Get founding member count (public)
curl https://your-backend.onrender.com/api/analytics/founding-members-count

# Expected response:
# {"count": 0, "remaining": 100, "total": 100, "percentage_claimed": 0.0}

# Create checkout session (requires auth token)
curl -X POST \
  https://your-backend.onrender.com/api/payments/create-checkout-session?tier=pro_founding \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: {"checkout_url": "https://checkout.stripe.com/..."}
```

### Check Logs

```bash
# In Render dashboard, check logs for:
✅ "Subscription scheduler initialized"
✅ "Email automation scheduler initialized"
✅ No webhook errors
✅ No database errors
```

---

## Launch Marketing Setup

### 1. Update Homepage

Add these elements to your homepage:

```jsx
import FoundingMemberBanner from './components/ui/FoundingMemberBanner';

// In Hero section
<h1>Analyze Your Resume Against Any Job in Seconds</h1>
<p>10 Free Analyses • No Credit Card Required • See Results Instantly</p>

// Above features section
<FoundingMemberBanner className="mb-8" />
```

### 2. Dashboard Integration

Add trial offer banner for users running low on credits:

```jsx
import TrialOfferBanner from './components/ui/TrialOfferBanner';
import CreditBalance from './components/ui/CreditBalance';

function Dashboard({ userProfile }) {
  const handleStartTrial = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/subscription/start-mega-trial`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Show success message, refresh user profile
    } catch (error) {
      console.error('Failed to start trial:', error);
    }
  };

  return (
    <div>
      <CreditBalance credits={userProfile.credits} tier={userProfile.subscription_tier} />

      {userProfile.credits <= 3 && !userProfile.is_trial_active && (
        <TrialOfferBanner
          credits={userProfile.credits}
          onStartTrial={handleStartTrial}
          className="mt-4"
        />
      )}

      {/* Rest of dashboard */}
    </div>
  );
}
```

### 3. Email Sequence (Optional, can add later)

Set up automated emails:

**Day 1: Welcome Email**
```
Subject: Welcome to AI Resume Analyzer! 🎉

You've got 10 free analyses to get started.
Upload your first resume and see how you match against your target job.

[Analyze Your First Resume]
```

**Day 3: Engagement Email**
```
Subject: You've improved 3 resumes! 7 credits left.

Great progress! You're seeing real improvements in your resume scores.

Want unlimited analyses? Try Pro for 30 days free.
[Start Free Trial]
```

**Day 7: Trial Offer**
```
Subject: Special offer: 30-day Pro trial + 30 credits 🚀

Almost out of credits? We've got you covered.

Get 30 days of Pro features + 30 analyses completely free.
No credit card required.

[Claim Your Free Trial]
```

---

## Monitoring & Metrics

### Key Metrics to Track Daily

| Metric | Where to Check | Target (Week 1) |
|--------|----------------|-----------------|
| New signups | `/api/analytics/overview` | 10+ |
| Founding Members | `/api/analytics/founding-members-count` | 2-5 |
| Free → Trial | Check `is_trial_active` count | 30% |
| Trial → Paid | Check `subscription_status='active'` | 20% |

### SQL Queries for Metrics

```sql
-- Daily signups
SELECT DATE(created_at) as date, COUNT(*) as signups
FROM users
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Founding Members
SELECT COUNT(*) as founding_members
FROM users
WHERE subscription_tier = 'pro_founding';

-- Active trials
SELECT COUNT(*) as active_trials
FROM users
WHERE is_trial_active = true;

-- Credit utilization
SELECT
  AVG(10 - credits) as avg_credits_used,
  COUNT(CASE WHEN credits = 0 THEN 1 END) as users_out_of_credits
FROM users
WHERE subscription_tier = 'free';
```

---

## Troubleshooting

### Issue: Users not getting 10 credits on signup

**Check:**
```sql
SELECT email, credits, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

**Fix:** If credits = 0, manually update:
```sql
UPDATE users
SET credits = 10
WHERE subscription_tier = 'free' AND credits = 0;
```

### Issue: Founding Member checkout fails

**Check Logs:**
```bash
# Look for Stripe errors in Render logs
grep "Stripe" /var/log/app.log
```

**Common causes:**
- Price ID not set in environment variables
- Stripe webhook secret incorrect
- Test mode vs live mode mismatch

**Fix:**
1. Verify `STRIPE_PRO_FOUNDING_PRICE_ID` is set
2. Check Stripe Dashboard → API keys (test vs live)
3. Restart backend service

### Issue: Credits not deducting after analysis

**Check:**
```sql
SELECT user_id, COUNT(*) as analysis_count
FROM analysis
WHERE created_at >= NOW() - INTERVAL '1 day'
GROUP BY user_id;
```

**Compare with user credits:**
```sql
SELECT id, email, credits
FROM users
WHERE id IN (SELECT DISTINCT user_id FROM analysis WHERE created_at >= NOW() - INTERVAL '1 day');
```

**Fix:** If credits not deducting, check `SubscriptionService.deduct_credits()` is being called in analysis route.

### Issue: Scheduler not running

**Check logs for:**
```
Subscription scheduler initialized (credit reset & trial expiration)
```

**If missing:**
1. Check if APScheduler is installed: `pip list | grep APScheduler`
2. Verify imports in [app.py](backend/app.py#L2811-L2816)
3. Restart backend service

---

## Rollback Plan (If Needed)

If critical issues arise:

### 1. Immediate (5 minutes)

Disable Founding Member tier:

```sql
UPDATE subscription_tier
SET is_active = false
WHERE name = 'pro_founding';
```

### 2. Short-term (30 minutes)

Revert to old pricing:

```sql
-- Revert free tier to 5 credits
UPDATE subscription_tier
SET monthly_credits = 5
WHERE name = 'free';

-- Update existing users
UPDATE users
SET credits = 5
WHERE subscription_tier = 'free' AND credits > 5;
```

### 3. Full rollback (1 hour)

```bash
git revert HEAD
git push origin main
```

Then run old migrations to restore previous tier structure.

---

## Success Criteria (Week 1)

✅ **Technical:**
- [ ] 0 production errors
- [ ] All new users get 10 credits
- [ ] Founding Member checkout works
- [ ] Credit deduction accurate
- [ ] Scheduler running daily

✅ **Business:**
- [ ] 10+ signups
- [ ] 2+ Founding Members
- [ ] 3+ active trials
- [ ] 0 support tickets about pricing confusion

---

## Next Steps After Launch

### Week 2-4: Iterate

- Monitor conversion funnel
- Collect user feedback
- A/B test messaging
- Adjust free tier if abuse detected (10 → 7 → 5)

### Month 2: Add Features

- Implement email automation
- Add mega trial button to dashboard
- Create usage reports
- Build referral system

### Month 3: Scale

- Close Founding Member tier at 100 users
- Launch Starter tier at $9.99
- Add Pro annual at $199/year
- Reduce free tier to 5 credits

---

## Support & Questions

### Common User Questions

**Q: "How do credits work?"**
A: Each resume analysis costs 1 credit. Free users get 10/month, Pro Founding gets 50/month.

**Q: "What's the difference between Founding Member and regular Pro?"**
A: Founding Members lock in $19.99/month forever (limited to 100). Regular Pro is $24.99/month.

**Q: "Can I upgrade my free account later?"**
A: Yes! You can upgrade anytime. Founding Member tier available only while spots last.

**Q: "Do unused credits roll over?"**
A: Credits reset monthly on your billing anniversary. Use them or lose them.

### Technical Support

For deployment issues:
1. Check Render logs
2. Verify environment variables
3. Test Stripe webhooks in Dashboard
4. Review database migrations

For code issues:
- Backend: [services/subscription_service.py](backend/services/subscription_service.py)
- Frontend: [components/PricingPageV2.jsx](frontend/src/components/PricingPageV2.jsx)
- Stripe: [app.py:2268-2470](backend/app.py#L2268-L2470)

---

## Launch Checklist

Print this and check off as you go:

- [ ] Created Stripe products (Pro Founding, Elite)
- [ ] Added Price IDs to Render environment variables
- [ ] Ran `add_subscription_fields.py`
- [ ] Ran `update_pricing_tiers.py`
- [ ] Ran `add_credit_costs.py`
- [ ] Committed and pushed code
- [ ] Verified backend deployment (check logs)
- [ ] Tested new user signup (10 credits granted)
- [ ] Tested Founding Member checkout
- [ ] Tested credit deduction
- [ ] Verified founding member counter works
- [ ] Added FoundingMemberBanner to homepage
- [ ] Added TrialOfferBanner to dashboard
- [ ] Set up monitoring for key metrics
- [ ] Prepared email sequences (optional)
- [ ] Announced launch on social media

**You're ready to launch! 🚀**
