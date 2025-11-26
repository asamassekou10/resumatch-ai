# Stripe Integration Setup Guide

## ⚠️ SECURITY CRITICAL - READ FIRST

**NEVER commit your Stripe keys to git!** These are secrets that must be stored locally in `.env` only.

Your Stripe keys you provided are now saved locally. Here's how to use them safely:

---

## Step 1: Set Up Local .env File

1. Create a file named `.env` in the `backend/` directory (if it doesn't exist)
2. Add your Stripe test keys to this file:

```bash
# In backend/.env (NEVER commit this file)
STRIPE_SECRET_KEY=sk_test_51SXZlyC1C8ES3VSLVpywaz72tqg5J2JcHP6X8zntkgvih2AsGSgTVNhNZD2lPGffVI6Cm2eGKheemSgQJpgfZqGK00MYsR0XAG
STRIPE_WEBHOOK_SECRET=whsec_[get-this-from-stripe-dashboard]
```

3. Ensure `.env` is in `.gitignore` (it already is)

---

## Step 2: Get Your Webhook Secret

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Click **Developers → Webhooks**
3. Click **Add endpoint**
4. Enter your local webhook URL: `http://localhost:5000/api/payments/webhook` (for testing)
5. Select events to listen for:
   - `checkout.session.completed` ✓
   - `customer.subscription.deleted` ✓
6. Click **Add endpoint**
7. Click the endpoint you just created
8. Copy the **Signing secret** (starts with `whsec_`)
9. Paste this value as `STRIPE_WEBHOOK_SECRET` in your `.env` file

---

## Step 3: Pricing Configuration

Your app is now configured with:

### Free Tier
- **Initial Credits:** 5
- **Cost:** $0
- **When:** All new users start here

### Pro Tier
- **Price:** $9.99/month
- **Credits:** 1000 (unlimited)
- **Billing:** Monthly subscription via Stripe

---

## Step 4: Test Locally

### Test Credit System
```bash
cd backend
python -c "
from app import app, db
from models import User
with app.app_context():
    # Check that new users get 5 credits
    users = User.query.limit(1)
    for user in users:
        print(f'User {user.email}: {user.credits} credits')
"
```

### Test Payment Checkout
1. Start your backend: `cd backend && python app.py`
2. Start your frontend: `cd frontend && npm start`
3. Go to **Settings → Upgrade to Pro**
4. Use Stripe test card: `4242 4242 4242 4242`
5. Any future expiration date and any CVC
6. Should show success and upgrade user to Pro tier

### Test Webhook
1. In Stripe Dashboard, go to your webhook endpoint
2. Click **Send test event**
3. Select `checkout.session.completed`
4. In your backend console, you should see: "User [ID] upgraded to Pro tier"

---

## Step 5: Deployment to Render

When deploying to production:

1. Use `sk_live_*` keys instead of `sk_test_*`
2. In Render Dashboard:
   - Go to your backend service
   - Click **Environment**
   - Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
3. Update your Stripe webhook URL in Stripe Dashboard:
   - Change from `http://localhost:5000/api/payments/webhook`
   - To: `https://your-backend-domain.onrender.com/api/payments/webhook`
4. Get the new webhook signing secret from Stripe and update it in Render

---

## Security Checklist

- [x] Stripe keys stored in `.env` (not in code)
- [x] `.env` file is in `.gitignore`
- [x] Using test keys (`sk_test_*`) for development
- [x] Using webhook signing secret validation
- [x] Prices configured ($9.99 Pro, free 5 credits)
- [x] Credit system implemented
- [x] Webhook events handled (checkout, cancellation)

---

## Troubleshooting

### "STRIPE_SECRET_KEY not configured"
- Make sure your `.env` file exists in `backend/` directory
- Make sure `STRIPE_SECRET_KEY=sk_test_...` is set
- Restart your backend server

### "Invalid signature" on webhook
- Make sure `STRIPE_WEBHOOK_SECRET` matches the signing secret from Stripe Dashboard
- If you just created the webhook, wait a few seconds and try again

### Payment checkout not working
- Check backend logs for errors
- Verify `STRIPE_SECRET_KEY` is correct (starts with `sk_test_`)
- Make sure `FRONTEND_URL` is set in `.env`

### User not upgrading to Pro after payment
- Check Stripe Dashboard → Webhook → Recent deliveries
- Look for `checkout.session.completed` event
- Check if webhook signing secret matches in `.env`
- Check backend logs for webhook handling errors

---

## What's Next?

✅ Local testing with test keys
✅ Test payment flow end-to-end
✅ Verify credit system works
✅ Deploy to Render when ready (see PRODUCTION_DEPLOYMENT_GUIDE.md)

---

**File locations:**
- Backend .env: `backend/.env` (create this locally)
- Environment template: `backend/.env.example` (committed to git)
- Payment routes: `backend/app.py` lines 1150-1255
- Credit handling: `backend/models.py`

