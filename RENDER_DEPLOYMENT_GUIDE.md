# Render Deployment Guide

## Backend Environment Variables

Add these environment variables in your **Backend** service on Render:

### Critical (Required for app to work):
```bash
# Database (Render provides this automatically when you add PostgreSQL)
DATABASE_URL=<your-render-postgresql-connection-string>

# Security Keys (Generate new ones for production!)
JWT_SECRET_KEY=<use: openssl rand -hex 32>
SECRET_KEY=<use: openssl rand -hex 32>

# AI Service (Required for all features) - Copy from backend/.env
GEMINI_API_KEY=<your-gemini-api-key>

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py

# URLs (Update with your actual URLs after deployment)
FRONTEND_URL=https://<your-frontend-name>.onrender.com
BACKEND_URL=https://<your-backend-name>.onrender.com
```

### Payment (Stripe):
```bash
# Copy these from backend/.env file
STRIPE_PUBLISHABLE_KEY=<your-stripe-publishable-key>
STRIPE_SECRET_KEY=<your-stripe-secret-key>
STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret>
```

### Job Matching (Adzuna API):
```bash
# Copy these from backend/.env file
ADZUNA_APP_ID=<your-adzuna-app-id>
ADZUNA_APP_KEY=<your-adzuna-app-key>
```

### OAuth (Update redirect URIs with your backend URL):
```bash
# Google OAuth - Copy from backend/.env file
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=https://<your-backend-name>.onrender.com/api/auth/callback

# LinkedIn OAuth - Copy from backend/.env file
LINKEDIN_CLIENT_ID=<your-linkedin-client-id>
LINKEDIN_CLIENT_SECRET=<your-linkedin-client-secret>
LINKEDIN_REDIRECT_URI=https://<your-backend-name>.onrender.com/api/auth/linkedin/callback
```

### Email (SendGrid):
```bash
# Copy from backend/.env file
SENDGRID_API_KEY=<your-sendgrid-api-key>
FROM_EMAIL=<your-email-address>
```

### Optional:
```bash
RATELIMIT_ENABLED=true
LOG_LEVEL=INFO
```

---

## Frontend Environment Variables

Add these environment variables in your **Frontend** service on Render:

### Required:
```bash
# Point to your backend (CRITICAL - without this, login won't work!)
REACT_APP_API_URL=https://<your-backend-name>.onrender.com/api

# Environment
REACT_APP_ENV=production

# API Timeout
REACT_APP_API_TIMEOUT=30000
```

### Optional (Analytics):
```bash
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG=false
REACT_APP_SENTRY_DSN=
REACT_APP_GOOGLE_ANALYTICS_ID=
```

---

## Important Notes:

### 1. **Generate Strong Keys**
```bash
# Run these commands locally and copy the output:
openssl rand -hex 32  # Use for JWT_SECRET_KEY
openssl rand -hex 32  # Use for SECRET_KEY
```

### 2. **Update Google OAuth Console**
- Go to: https://console.cloud.google.com/apis/credentials
- Find your OAuth 2.0 Client ID
- Add to "Authorized redirect URIs":
  ```
  https://<your-backend-name>.onrender.com/api/auth/callback
  ```

### 3. **Update LinkedIn OAuth**
- Go to: https://www.linkedin.com/developers/apps
- Update redirect URL to:
  ```
  https://<your-backend-name>.onrender.com/api/auth/linkedin/callback
  ```

### 4. **Database Setup**
- In Render Dashboard, create a new PostgreSQL database
- Copy the "Internal Database URL"
- Paste it as `DATABASE_URL` in backend environment variables

### 5. **Verify Deployment**
After configuring all variables:
1. Check backend logs for errors
2. Try accessing: `https://<your-backend-name>.onrender.com/api/health` (if available)
3. Test login from frontend
4. Test Google OAuth login

---

## Troubleshooting

### "Unexpected token '<', "<!doctype"... is not valid JSON"
- **Cause**: Frontend can't reach backend or wrong API URL
- **Fix**: Set `REACT_APP_API_URL` in frontend environment variables

### Google OAuth 503 Error
- **Cause**: Backend environment variables not configured
- **Fix**: Add all required backend environment variables listed above

### CORS Errors
- **Cause**: Frontend URL not in allowed origins
- **Fix**: Set `FRONTEND_URL` environment variable in backend

### Database Connection Errors
- **Cause**: DATABASE_URL not set or incorrect
- **Fix**: Add PostgreSQL database in Render and set DATABASE_URL
