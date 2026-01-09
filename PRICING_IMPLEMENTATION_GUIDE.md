# Pricing System Implementation Guide

This guide explains how to implement the updated pricing system for the AI Resume Analyzer.

## Overview

The pricing system has been completely redesigned based on market research to:
- ✅ Align with competitor pricing ($9.99-$49.99 range)
- ✅ Fix critical infrastructure gaps (webhooks, credit reset, trial system)
- ✅ Add annual billing support
- ✅ Implement credit-based usage tracking
- ✅ Create upgrade prompts and user flows

## Implementation Steps

### Phase 1: Database Migration

Run these migration scripts in order to update the database schema:

```bash
cd backend/migrations

# 1. Add subscription tracking fields to User model
python add_subscription_fields.py

# 2. Update subscription tiers with new pricing
python update_pricing_tiers.py

# 3. Add credit cost configurations
python add_credit_costs.py
```

**What this does:**
- Adds `subscription_start_date` and `last_credit_reset` fields to users table
- Creates new pricing tiers: Free ($0, 3 credits), Starter ($9.99, 15 credits), Pro ($24.99, 50 credits), Elite ($49.99, 200 credits)
- Configures credit costs for each operation (resume_analysis=1 credit, feedback=2 credits, optimization=3 credits)

### Phase 2: Stripe Configuration

Update your Stripe Price IDs in environment variables:

```bash
# In Render.com Dashboard or .env file:

STRIPE_STARTER_PRICE_ID=price_xxxxxxxxxxxxx  # Create in Stripe Dashboard
STRIPE_PRO_PRICE_ID=price_xxxxxxxxxxxxx      # Update existing
STRIPE_ELITE_PRICE_ID=price_xxxxxxxxxxxxx    # Update existing
STRIPE_PRO_ANNUAL_PRICE_ID=price_xxxxxxxxxxxxx  # Create new annual plan
```

**How to create Stripe Products:**
1. Go to Stripe Dashboard → Products
2. Create products for each tier:
   - **Starter**: $9.99/month, recurring
   - **Pro**: $24.99/month, recurring
   - **Pro Annual**: $199/year, recurring annually
   - **Elite**: $49.99/month, recurring
3. Copy the Price ID for each and add to environment variables

### Phase 3: Backend Deployment

The following backend files have been created/modified:

#### New Files:
- `backend/services/subscription_service.py` - Credit management, trial system
- `backend/scheduler.py` - Monthly credit reset & trial expiration scheduler
- `backend/migrations/update_pricing_tiers.py`
- `backend/migrations/add_credit_costs.py`
- `backend/migrations/add_subscription_fields.py`

#### Modified Files:
- `backend/models.py` - Added subscription_start_date, last_credit_reset fields
- `backend/app.py` - Updated webhook handler, initialized scheduler
- `backend/routes/analysis.py` - Added credit checking and deduction

**Deploy steps:**
1. Commit all changes to git
2. Push to your repository
3. Render will automatically deploy
4. Check logs to ensure scheduler initialized: "Subscription scheduler initialized (credit reset & trial expiration)"

### Phase 4: Frontend Deployment

#### New Components:
- `frontend/src/components/ui/CreditBalance.jsx` - Credit display widget
- `frontend/src/components/ui/UpgradeModal.jsx` - Upgrade prompt modal

#### Modified Files:
- `frontend/src/components/PricingPageV2.jsx` - Updated pricing tiers

**Integration example:**

```jsx
// In Dashboard.jsx or any component
import CreditBalance from './ui/CreditBalance';
import UpgradeModal from './ui/UpgradeModal';

function Dashboard({ userProfile }) {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  return (
    <div>
      {/* Show credit balance */}
      <CreditBalance
        credits={userProfile.credits}
        tier={userProfile.subscription_tier}
      />

      {/* Show upgrade modal when out of credits */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        creditsNeeded={1}
        creditsAvailable={userProfile.credits}
        tier={userProfile.subscription_tier}
      />
    </div>
  );
}
```

### Phase 5: Testing

#### Test Credit System:
```bash
# 1. Create a test user
# 2. Upgrade to Pro tier via Stripe checkout
# 3. Verify user gets 50 credits
# 4. Run an analysis, verify 1 credit is deducted
# 5. Check credits_remaining in response
```

#### Test Monthly Reset:
```bash
# Manually trigger the scheduler job (for testing)
python -c "from services.subscription_service import SubscriptionService; SubscriptionService.reset_monthly_credits()"
```

#### Test Trial System:
```bash
# Start a trial for a user
from services.subscription_service import SubscriptionService
SubscriptionService.start_trial(user_id=1, trial_days=7, trial_credits=10)

# Check trial expiration
SubscriptionService.check_trial_expirations()
```

## New Pricing Structure

| Tier | Monthly | Annual | Credits | Target Audience |
|------|---------|--------|---------|-----------------|
| Free | $0 | - | 3/mo | Casual users |
| Starter | $9.99 | $99.99 | 15/mo | Budget job seekers |
| Pro | $24.99 | $199.99 | 50/mo | Active job hunters |
| Elite | $49.99 | $499.99 | 200/mo | Recruiters/coaches |

## Credit Costs

| Operation | Credits | Available In |
|-----------|---------|--------------|
| Resume Analysis | 1 | All paid tiers |
| AI Feedback | 2 | Pro, Elite |
| Resume Optimization | 3 | Pro, Elite |
| Cover Letter | 2 | Pro, Elite |
| Bulk Upload | 5 | Elite only |

## Scheduler Jobs

The system now runs two daily scheduled jobs:

1. **Credit Reset** (2:00 AM UTC daily)
   - Resets monthly credits for active subscribers on their billing anniversary
   - Example: If user subscribed on Jan 15, credits reset on the 15th of each month

2. **Trial Expiration** (3:00 AM UTC daily)
   - Checks for expired trials
   - Downgrades users to free tier if trial ended and no paid subscription

## API Changes

### New Response Fields

**Analysis endpoint** now returns:
```json
{
  "status": "success",
  "data": {
    "analysis_id": 123,
    "match_score": 85,
    "credits_remaining": 49,  // NEW
    ...
  }
}
```

**Error response** when out of credits (402 Payment Required):
```json
{
  "status": "error",
  "error": "Insufficient credits",
  "credits_available": 0,
  "credits_needed": 1,
  "message": "You need 1 credit(s) but only have 0. Please upgrade your plan.",
  "upgrade_url": "/pricing"
}
```

### New Endpoints

The following subscription management endpoints are available:

```bash
# Get subscription info
GET /api/subscription/info
Authorization: Bearer <token>

Response:
{
  "user_id": 123,
  "subscription_tier": "pro",
  "subscription_status": "active",
  "credits": 49,
  "monthly_credits": 50,
  "is_trial_active": false,
  "tier_features": {...}
}
```

## Monitoring

### Key Metrics to Track:

1. **Conversion Rates**
   - Free → Paid: Target 12%
   - Monthly → Annual: Target 30%

2. **Revenue Metrics**
   - ARPU (Average Revenue Per User)
   - MRR (Monthly Recurring Revenue)
   - Churn rate by tier

3. **Usage Metrics**
   - Average credits used per tier
   - Credit utilization rate
   - Operations performed per user

### Analytics Queries:

```sql
-- Users by tier
SELECT subscription_tier, COUNT(*) as user_count
FROM users
GROUP BY subscription_tier;

-- Monthly revenue
SELECT
  subscription_tier,
  COUNT(*) * (price_cents / 100.0) as monthly_revenue
FROM users u
JOIN subscription_tier st ON u.subscription_tier = st.name
WHERE u.subscription_status = 'active'
GROUP BY subscription_tier, price_cents;

-- Credit utilization
SELECT
  subscription_tier,
  AVG(credits) as avg_remaining_credits,
  AVG(monthly_credits - credits) as avg_credits_used
FROM users u
JOIN subscription_tier st ON u.subscription_tier = st.name
WHERE u.subscription_status = 'active'
GROUP BY subscription_tier;
```

## Rollback Plan

If you need to rollback:

1. **Database**: Keep the old tier data by commenting out the DELETE in migration scripts
2. **Frontend**: Revert PricingPageV2.jsx to previous version
3. **Backend**: The webhook handler has fallback logic for old tiers
4. **Scheduler**: Non-critical - app works without it

## Support & Troubleshooting

### Common Issues:

**Issue**: Credits not resetting monthly
- **Fix**: Check scheduler logs, ensure `subscription_start_date` is set for users
- **Manual fix**: Run `SubscriptionService.reset_monthly_credits()` manually

**Issue**: Webhook not updating subscription
- **Fix**: Verify `STRIPE_WEBHOOK_SECRET` is set correctly
- **Check**: Stripe Dashboard → Webhooks → Event history

**Issue**: Users can't upgrade
- **Fix**: Verify Stripe Price IDs are correct in environment variables
- **Check**: Browser console for errors, backend logs for Stripe API errors

## Next Steps

After implementing the core system, consider:

1. **A/B Testing**: Test different price points ($24.99 vs $29.99 for Pro)
2. **Referral Program**: Give 5 credits to both referrer and referee
3. **Credit Top-ups**: Allow one-time credit purchases (5 credits for $4.99)
4. **Annual Discount**: Experiment with 15-25% discount levels
5. **Usage Reports**: Email users monthly usage summaries

## Questions?

For implementation support:
- Check backend logs in Render dashboard
- Review Stripe webhook event history
- Test with Stripe test mode first
- Monitor APScheduler logs for scheduler issues
