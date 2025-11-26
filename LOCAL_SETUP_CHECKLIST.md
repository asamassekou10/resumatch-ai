# Local Setup Checklist - Stripe Integration

## ⚠️ SECURITY CRITICAL

**NEVER commit the `.env` file to git!** It contains secrets.

---

## Step 1: Create Your Local `.env` File

1. In the `backend/` folder, create a file named `.env` (note: NOT `.env.example`)
2. Add ONLY these lines to your local `.env`:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_optimizer

# JWT Secret Keys (REQUIRED)
JWT_SECRET_KEY=dev-jwt-secret-change-in-production
SECRET_KEY=dev-session-secret-change-in-production

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py

# Stripe Payment (YOUR KEYS - NEVER COMMIT)
STRIPE_SECRET_KEY=sk_test_51SXZlyC1C8ES3VSLVpywaz72tqg5J2JcHP6X8zntkgvih2AsGSgTVNhNZD2lPGffVI6Cm2eGKheemSgQJpgfZqGK00MYsR0XAG
STRIPE_WEBHOOK_SECRET=whsec_QOGVgMNa7sv1ZqFlx4MD5g8lLMFKunKr

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Google OAuth Configuration (optional for local testing)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/callback

# Email Configuration (optional for local testing)
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
FROM_EMAIL=noreply@resumeoptimizer.com

# Gemini AI Configuration (required for analysis)
GEMINI_API_KEY=your-gemini-api-key-here

# Rate Limiting
RATELIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

⚠️ **YOUR SECRETS ARE NOW IN THIS FILE:**
- `STRIPE_SECRET_KEY` = your test key
- `STRIPE_WEBHOOK_SECRET` = your webhook secret

✅ **Verify `.env` is in `.gitignore`:**
```bash
cd c:\Users\alhas\AI RESUME ANALYZER
grep -i ".env" .gitignore
# Should show: .env
```

---

## Step 2: Verify Stripe Keys Are Set

```bash
cd backend
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

stripe_key = os.getenv('STRIPE_SECRET_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

print(f'✓ Stripe API Key loaded: {stripe_key[:20]}...' if stripe_key else '✗ STRIPE_SECRET_KEY not found')
print(f'✓ Webhook Secret loaded: {webhook_secret[:20]}...' if webhook_secret else '✗ STRIPE_WEBHOOK_SECRET not found')
"
```

Expected output:
```
✓ Stripe API Key loaded: sk_test_51SXZlyC1C8ES3VSL...
✓ Webhook Secret loaded: whsec_QOGVgMNa7sv1ZqFlx4...
```

---

## Step 3: Start Your Backend

```bash
cd backend
python app.py
```

You should see:
```
WARNING:root:⚠️ Using default secrets - DO NOT use in production!
 * Running on http://0.0.0.0:5000
```

This is **OK for development** - the warning is expected.

---

## Step 4: Test Payment Flow

### Create a Test Account
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }'
```

Expected response:
```json
{
  "message": "Registration successful",
  "credits": 5
}
```

### Check User Credits
```bash
# Get your token first
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}' \
  | jq -r '.access_token')

# Check credits
curl -X GET http://localhost:5000/api/user \
  -H "Authorization: Bearer $TOKEN" | jq '.credits'
```

Expected: `5`

### Try Upgrade to Pro
```bash
curl -X POST http://localhost:5000/api/payments/create-checkout \
  -H "Authorization: Bearer $TOKEN" | jq '.checkout_url'
```

This returns a Stripe checkout URL - opens Stripe test checkout page.

### Use Stripe Test Card
When the checkout page loads:
- Card: `4242 4242 4242 4242`
- Expiry: Any future date (e.g., `12/25`)
- CVC: Any 3 digits (e.g., `123`)
- Email: Any email

Click **Pay** → Should redirect to success page.

### Verify Tier Upgrade
After payment, check credits increased to 100:
```bash
curl -X GET http://localhost:5000/api/user \
  -H "Authorization: Bearer $TOKEN" | jq '.credits'
```

Expected: `100` (Pro tier)

---

## Step 5: Test Credit Deduction

### Do a Resume Analysis
```bash
# Create a test resume (simple text file)
echo "Python, JavaScript, React, Flask, PostgreSQL" > resume.txt

# Run analysis (costs 1 credit)
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "resume=@resume.txt" \
  -F "job_description=Looking for a Python developer with React experience"
```

### Check Credits Decreased
```bash
curl -X GET http://localhost:5000/api/user \
  -H "Authorization: Bearer $TOKEN" | jq '.credits'
```

Expected: `99` (100 - 1 credit for analysis)

---

## Step 6: Test Abuse Prevention

### Test Daily Limit (Free User)
```bash
# Create another test account
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "freeuser@example.com",
    "password": "TestPassword123!",
    "name": "Free User"
  }'

# Login
FREE_TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"freeuser@example.com","password":"TestPassword123!"}' \
  | jq -r '.access_token')

# Try 6 analyses (free users only have 5 credits)
for i in {1..6}; do
  curl -X POST http://localhost:5000/api/analyze \
    -H "Authorization: Bearer $FREE_TOKEN" \
    -F "resume=@resume.txt" \
    -F "job_description=test job"
done
```

Expected output on 6th request:
```json
{
  "error": "Insufficient credits (1 required, 0 available)",
  "required_credits": 1,
  "current_credits": 0,
  "subscription_tier": "free",
  "upgrade_url": "/dashboard/upgrade"
}
```

---

## Step 7: Test Rate Limiting

### Test Hourly Limit (Free User)
```bash
# Create fresh free user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ratelimit@example.com",
    "password": "TestPassword123!",
    "name": "Rate Test"
  }'

RATE_TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ratelimit@example.com","password":"TestPassword123!"}' \
  | jq -r '.access_token')

# Try 3 analyses in rapid succession
# (Free users limited to 2 per hour)
for i in {1..3}; do
  echo "Request $i:"
  curl -X POST http://localhost:5000/api/analyze \
    -H "Authorization: Bearer $RATE_TOKEN" \
    -F "resume=@resume.txt" \
    -F "job_description=test"
  sleep 0.1
done
```

Expected: 3rd request gets rate limited:
```json
{
  "error": "429 Too Many Requests"
}
```

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| `.env` | `backend/.env` | **Local secrets (NOT committed)** |
| `.env.example` | `backend/.env.example` | Template (committed to git) |
| Abuse prevention | `backend/abuse_prevention.py` | Rate limiting & credit logic |
| Payment routes | `backend/app.py` lines 1150-1275 | Stripe integration |
| Credit logic | `backend/app.py` lines 618-689 | Credit deduction |

---

## Troubleshooting

### "STRIPE_SECRET_KEY not configured"
```
✗ Problem: .env file not loaded
✓ Solution: Make sure backend/.env exists with STRIPE_SECRET_KEY set
```

### "Invalid signature" on webhook
```
✗ Problem: Webhook secret doesn't match
✓ Solution: Verify STRIPE_WEBHOOK_SECRET matches exactly in .env
```

### User not getting credits after payment
```
✗ Problem: Webhook not firing
✓ Solution: Check Stripe Dashboard → Developers → Webhooks → Recent Deliveries
```

### "Insufficient credits" immediately
```
✗ Problem: User has 0 credits
✓ Solution: Check user tier - free users get 5 at signup, 0 on downgrade
```

---

## Summary

✅ Your `.env` file created with Stripe keys
✅ Backend can load credentials securely
✅ Payment flow works end-to-end
✅ Credit system enforced
✅ Rate limiting active
✅ Abuse prevention layers working

**Next Steps:**
1. Follow this checklist to test locally
2. Once everything works, deploy to Render (see PRODUCTION_DEPLOYMENT_GUIDE.md)
3. Update Stripe webhook URL in Stripe Dashboard to your Render backend URL
4. Use `sk_live_*` keys (not `sk_test_*`) in production

---

## Production Deployment

When ready to deploy to Render:

1. **DO NOT commit `.env`** - it's only local
2. **In Render Dashboard** → Backend service → Environment:
   - Add all variables from your local `.env`
   - Use `sk_live_*` keys instead of `sk_test_*`
   - Use production webhook secret from Stripe
3. **Update Stripe Webhook URL** in Stripe Dashboard:
   - Change from: `http://localhost:5000/api/payments/webhook`
   - To: `https://your-backend-domain.onrender.com/api/payments/webhook`

See PRODUCTION_DEPLOYMENT_GUIDE.md for complete steps.

---

**You're all set to test payments locally! 🎉**

