# Production Deployment Checklist

## ✅ Code Changes Summary

### Fixed Issues:
1. **Payment Flow Bug**: Micro-purchases ($1.99, $6.99) now correctly redirect to payment instead of creating unwanted free trials
2. **Free Trial System**: Changed from automatic 100-credit trial (no card) to credit-card-required 7-day trial with 10 credits

### Files Modified:
- `backend/app.py` - Registration, OAuth callbacks, Stripe checkout, webhook handler
- `backend/routes_linkedin.py` - LinkedIn OAuth registration
- `frontend/src/components/AuthPage.jsx` - Payment redirect handling, skip_trial support
- `frontend/src/components/GuestAnalyze.jsx` - Plan selection logic
- `frontend/src/components/PricingPageV2.jsx` - Messaging updates

---

## 🔧 Stripe Configuration Required

### 1. Create/Verify Products and Prices in Stripe Dashboard

**Required Price IDs:**
- `STRIPE_PRO_PRICE_ID` - Pro tier monthly subscription
- `STRIPE_PRO_FOUNDING_PRICE_ID` - Pro Founding Member tier (if applicable)
- `STRIPE_ELITE_PRICE_ID` - Elite tier monthly subscription
- `STRIPE_BASIC_PRICE_ID` - Basic tier (if applicable)
- `STRIPE_STUDENT_PRICE_ID` - Student tier (if applicable)

**Important**: When creating prices in Stripe:
- **DO NOT** set trial period on the Price itself
- The trial period is handled via `subscription_data.trial_period_days` in checkout
- Prices should be recurring monthly subscriptions

### 2. Set Up Webhook Endpoint

**In Stripe Dashboard** → Developers → Webhooks → Add Endpoint:

**Endpoint URL:**
```
https://your-backend-url.onrender.com/api/payments/webhook
```

**Events to Listen For:**
- ✅ `checkout.session.completed` - When user completes checkout
- ✅ `customer.subscription.updated` - When subscription status changes (trial → active)
- ✅ `customer.subscription.deleted` - When subscription is cancelled
- ✅ `customer.subscription.trial_will_end` - (Optional) For reminder emails

**After Creating Webhook:**
1. Click "Reveal" next to "Signing secret"
2. Copy the webhook secret (starts with `whsec_`)
3. Add to Render environment variables as `STRIPE_WEBHOOK_SECRET`

### 3. Get API Keys

**From Stripe Dashboard** → Developers → API keys:
- Copy **Secret key** (starts with `sk_live_...`) → `STRIPE_SECRET_KEY`
- Copy **Publishable key** (starts with `pk_live_...`) → `STRIPE_PUBLISHABLE_KEY` (for frontend)

---

## 🚀 Render Configuration

### Backend Environment Variables

Add these to your Render backend service:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx

# Stripe Price IDs (from Stripe Dashboard)
STRIPE_PRO_PRICE_ID=price_xxxxxxxxxxxxx
STRIPE_PRO_FOUNDING_PRICE_ID=price_xxxxxxxxxxxxx
STRIPE_ELITE_PRICE_ID=price_xxxxxxxxxxxxx
STRIPE_BASIC_PRICE_ID=price_xxxxxxxxxxxxx  # Optional
STRIPE_STUDENT_PRICE_ID=price_xxxxxxxxxxxxx  # Optional

# Frontend URL (for redirects)
FRONTEND_URL=https://your-frontend-domain.com
```

### Frontend Environment Variables

Add these to your Render frontend service (or Vercel):

```bash
REACT_APP_API_URL=https://your-backend-url.onrender.com/api
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
```

---

## ⚠️ Important Notes

### Trial Period Implementation
- Trial period is set via `subscription_data.trial_period_days: 7` in checkout session
- **Do NOT** configure trial period on Stripe Price objects
- Trial only activates when user provides credit card and completes checkout
- Users get 10 credits during trial (not 100)
- After trial ends, subscription automatically becomes active and grants full credits

### Existing Users
- Users with existing active trials will be honored (grandfathered)
- New signups will NOT get automatic trial (free tier only, 10 credits)
- Trial only activates via Stripe subscription checkout

### Testing Checklist
- [ ] Test guest user selecting $1.99 plan → signs up → goes to payment (no trial)
- [ ] Test guest user selecting $6.99 plan → signs up → goes to payment (no trial)
- [ ] Test guest user selecting Pro plan → signs up → goes to checkout
- [ ] Test new user registration → gets free tier (10 credits, no trial)
- [ ] Test subscription checkout → creates trial with 10 credits
- [ ] Test trial expiration → user gets full credits
- [ ] Test webhook events are received correctly

---

## 🔍 Verification Steps

### After Deployment:

1. **Test Registration:**
   - Register new user → Should get 10 credits, no trial
   - Check user in database: `subscription_tier='free'`, `credits=10`, `is_trial_active=False`

2. **Test Subscription Checkout:**
   - Go to pricing page → Select Pro/Elite
   - Complete checkout with test card
   - Verify webhook received: `checkout.session.completed`
   - Check user: `subscription_status='trialing'`, `credits=10`, `trial_start_date` set

3. **Test Micro-Purchase:**
   - As guest, run out of credits
   - Select $1.99 or $6.99 plan
   - Sign up → Should redirect to payment modal (not create trial)

4. **Monitor Webhooks:**
   - Check Stripe Dashboard → Webhooks → Recent events
   - Verify events are being received and processed

---

## 🐛 Troubleshooting

### Webhook Not Working:
- Verify `STRIPE_WEBHOOK_SECRET` is set correctly
- Check webhook endpoint URL is accessible
- Verify webhook events are enabled in Stripe Dashboard
- Check backend logs for webhook errors

### Trial Not Activating:
- Verify `subscription_data.trial_period_days` is being set in checkout
- Check Stripe subscription object has `status='trialing'`
- Verify webhook handler is checking subscription status correctly

### Users Getting Wrong Credits:
- Check webhook handler logic for trial vs active subscription
- Verify tier configuration in database
- Check `trial_credits_granted` vs `monthly_credits` logic

---

## 📝 Deployment Steps

1. ✅ Code changes complete
2. ⏳ Configure Stripe products/prices
3. ⏳ Set up Stripe webhook
4. ⏳ Add environment variables to Render
5. ⏳ Deploy backend
6. ⏳ Deploy frontend
7. ⏳ Test all flows
8. ⏳ Monitor webhooks and logs
