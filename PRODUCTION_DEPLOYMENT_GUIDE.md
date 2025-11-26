# Production Deployment Guide - Render

## Pre-Deployment Checklist (DO THIS NOW)

### 1. Generate Secure Secrets
Run these commands locally and save the outputs:

```bash
# Generate JWT secret (copy output to JWT_SECRET_KEY)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate Session secret (copy output to SECRET_KEY)
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 2. Required Accounts & API Keys (Gather These)

- ✅ **Stripe**: https://dashboard.stripe.com/apikeys
  - Copy `sk_live_*` (Secret Key) → STRIPE_SECRET_KEY
  - Copy webhook secret → STRIPE_WEBHOOK_SECRET
  - Set up webhook: `https://your-backend.onrender.com/api/payments/webhook`

- ✅ **Google OAuth**: https://console.cloud.google.com/
  - Create OAuth 2.0 credentials
  - Authorized JavaScript origins: `https://your-frontend.onrender.com`
  - Authorized redirect URIs: `https://your-backend.onrender.com/api/auth/callback`

- ✅ **SendGrid**: https://app.sendgrid.com/settings/api_keys
  - Create API key → SENDGRID_API_KEY
  - Set from email → FROM_EMAIL

- ✅ **Google Gemini**: https://aistudio.google.com/app/apikey
  - Create API key → GEMINI_API_KEY

---

## Step 1: Deploy Backend on Render

### Create a New Web Service

1. **Go to render.com → New Web Service**
2. **Connect your GitHub repository**
3. **Configure the service:**

```
Name: resume-analyzer-backend
Environment: Python 3.11
Region: Choose closest to users (us-east-1 recommended)
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```bash
# Critical - DO NOT SKIP
FLASK_ENV=production
JWT_SECRET_KEY=<paste generated secret from step 1>
SECRET_KEY=<paste generated secret from step 1>
DATABASE_URL=<will setup next>

# Payment Processing
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
FRONTEND_URL=https://your-frontend-domain.onrender.com

# OAuth
GOOGLE_CLIENT_ID=xxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxx

# Email
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
FROM_EMAIL=noreply@your-domain.com

# AI
GEMINI_API_KEY=xxxxxxxxxxxxx

# Logging
LOG_LEVEL=INFO
```

---

## Step 2: Deploy PostgreSQL Database

### Create PostgreSQL Database

1. **In Render Dashboard → New → PostgreSQL**
2. **Configure:**

```
Name: resume-analyzer-db
PostgreSQL Version: 15
Region: Same as backend
Datadog: No
```

3. **Once created, copy the Internal Database URL** (not the external one)
   - Format: `postgresql://user:password@host:5432/dbname`
   - Paste this as **DATABASE_URL** in backend environment variables

### Initialize Database

Once backend is deployed:

1. **Go to backend service on Render**
2. **Click "Shell" tab**
3. **Run these commands:**

```bash
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
```

---

## Step 3: Deploy Frontend on Render

### Create a New Static Site

1. **Go to render.com → New → Static Site**
2. **Connect your GitHub repository**
3. **Configure:**

```
Name: resume-analyzer-frontend
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/build
```

### Add Build Environment Variables

```
REACT_APP_API_URL=https://your-backend-domain.onrender.com/api
REACT_APP_ENV=production
```

---

## Step 4: Configure Stripe Webhook

1. **Go to Stripe Dashboard → Developers → Webhooks**
2. **Click "Add endpoint"**
3. **Endpoint URL:** `https://your-backend-domain.onrender.com/api/payments/webhook`
4. **Select events:**
   - `checkout.session.completed`
   - `customer.subscription.deleted`
5. **Copy webhook signing secret**
6. **Paste into Render as STRIPE_WEBHOOK_SECRET**

---

## Step 5: Configure Google OAuth

1. **Go to Google Cloud Console**
2. **APIs & Services → OAuth 2.0 Client IDs**
3. **Update authorized origins:**
   - Remove: `http://localhost:5000`, `http://localhost:3000`
   - Add: `https://your-frontend-domain.onrender.com`
4. **Update authorized redirect URIs:**
   - Remove: `http://localhost:5000/api/auth/callback`
   - Add: `https://your-backend-domain.onrender.com/api/auth/callback`

---

## Step 6: Final Security Checks

### ✅ SSL/HTTPS
- Render automatically provides HTTPS for all domains
- All traffic is encrypted end-to-end

### ✅ Security Headers
Verified in code:
- X-Content-Type-Options: nosniff ✓
- X-Frame-Options: DENY ✓
- X-XSS-Protection: 1; mode=block ✓
- Strict-Transport-Security ✓

### ✅ Rate Limiting
- Active on all auth endpoints
- /login: 5 per minute
- /register: 3 per hour
- /analyze: tier-based

### ✅ Data Encryption
- JWT tokens expire in 7 days
- Passwords hashed with bcrypt
- All CORS requests validated

### ✅ Error Handling
- No stack traces exposed
- Generic error messages
- Full errors logged server-side

---

## Step 7: Health Checks & Monitoring

### Verify Backend Health

```bash
curl https://your-backend-domain.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {"status": "healthy"},
    "gemini_api": {"status": "healthy"},
    "cache": {"status": "healthy"},
    "memory": {"status": "healthy"},
    "disk": {"status": "healthy"}
  }
}
```

### Verify Frontend

Visit `https://your-frontend-domain.onrender.com` - should load the app

### Verify OAuth

1. Click "Login with Google"
2. Should redirect to Google login
3. After login, should redirect back to dashboard

---

## Step 8: Set Up Database Backups

1. **In Render dashboard → PostgreSQL service → Datadog tab**
2. **Enable automated backups** (optional but recommended)
   - Daily backups recommended for production

---

## Post-Deployment Tasks

### 1. Create Admin User

```bash
# In backend shell
cd backend
python create_admin.py
```

Follow prompts to create admin account.

### 2. Test Payment Processing

1. **Go to app → Settings → Upgrade to Pro**
2. **Use Stripe test card:** `4242 4242 4242 4242`
3. **Any future date and CVC**
4. Should complete checkout and show success

### 3. Monitor Logs

In Render dashboard:
- Click backend service
- View "Logs" tab
- Should see info messages but NO errors

### 4. Set Up Email Alerts (Optional)

Create alerts for:
- Backend service crashes
- Database connection failures
- High error rates (>1%)

---

## Troubleshooting

### Backend returns 502 Bad Gateway

1. Check logs: `Backend service → Logs`
2. Verify all environment variables are set
3. Check DATABASE_URL is correct
4. Restart service: `Backend service → Restart`

### Email not sending

1. Verify SENDGRID_API_KEY is correct (starts with `SG.`)
2. Verify FROM_EMAIL is verified in SendGrid
3. Check backend logs for SendGrid API errors

### Google login not working

1. Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct
2. Check authorized origins and redirect URIs in Google Console
3. Clear browser cache and cookies

### Stripe webhook not firing

1. Verify webhook signing secret is correct
2. Check Stripe → Developers → Webhooks for delivery status
3. Look for 401/403 errors in webhook logs

---

## Security Hardening Checklist

- ✅ All environment variables use STRONG random secrets (64+ chars)
- ✅ FLASK_ENV=production (not development)
- ✅ No debug=True in production
- ✅ Database URL is encrypted in transit (SSL)
- ✅ No hardcoded secrets in code
- ✅ No stack traces exposed to users
- ✅ Rate limiting active on auth endpoints
- ✅ HTTPS/SSL enabled (automatic on Render)
- ✅ CORS restricted to frontend domain
- ✅ JWT tokens have 7-day expiration
- ✅ Passwords hashed with bcrypt
- ✅ API error messages are generic (no details)
- ✅ Logs don't contain sensitive data
- ✅ Stripe webhook validated
- ✅ Database backups enabled

---

## Performance Configuration

### Backend Workers
- **Current:** 2 workers (for $7/month plan)
- **Upgrade:** 4 workers (for $12+/month plan)

Modify start command:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

### Database Optimization
- Indexes are automatically created
- Connection pooling enabled
- Query caching active

### Frontend CDN
- Render serves frontend from edge locations
- CSS/JS files cached for 1 year
- HTML cached for 5 minutes

---

## Maintenance Schedule

**Daily:**
- Monitor error logs
- Check health endpoint

**Weekly:**
- Review security logs
- Check database size
- Monitor API response times

**Monthly:**
- Update dependencies
- Rotate API keys
- Review billing

**Quarterly:**
- Security audit
- Performance optimization
- Backup verification

---

## Support & Emergency Contacts

**If production is down:**
1. Check Render status page
2. Review recent deployments
3. Check environment variables (might have been reset)
4. Restart services in order:
   - PostgreSQL (wait 2 min)
   - Backend (wait 1 min)
   - Frontend

---

## Summary of Changes for Production

**This deployment includes:**
- ✅ Stripe integration (import fixed + webhook secret configured)
- ✅ Production environment variables (no hardcoded secrets)
- ✅ Removed debug mode (set to production)
- ✅ Removed traceback printing (using proper logging)
- ✅ Generic error messages (no stack traces exposed)
- ✅ Secure Stripe URLs (environment-based)
- ✅ No sensitive data in logs (email replaced with ID)
- ✅ HTTPS enforcement (automatic on Render)
- ✅ Rate limiting configured
- ✅ Security headers in place

**All changes are backward compatible - no code breaking changes.**

---

**Deployment Time: ~30 minutes**
**Cost Estimate: $7-15/month (PostgreSQL + 2 services)**

Good luck! Your app is production-ready! 🚀
