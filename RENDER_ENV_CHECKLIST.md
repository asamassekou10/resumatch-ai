# Render Environment Variables Checklist

## Issue Summary
You're getting `oauth_failed` errors because environment variables aren't configured on Render.

## Critical Fix Steps

### Step 1: Backend Environment Variables

Go to your **Backend service** on Render → **Environment** tab → Add these variables:

#### ✅ Required for app to start:
```bash
DATABASE_URL=<copy-from-render-postgresql-database>
JWT_SECRET_KEY=<run: openssl rand -hex 32>
SECRET_KEY=<run: openssl rand -hex 32>
GEMINI_API_KEY=<copy-from-backend/.env>
FLASK_ENV=production
FLASK_APP=app.py
```

#### ✅ Required for OAuth and frontend communication:
```bash
FRONTEND_URL=https://resumeanalyzerai.com
BACKEND_URL=https://resumatch-backend-7qdb.onrender.com
GOOGLE_CLIENT_ID=<copy-from-backend/.env>
GOOGLE_CLIENT_SECRET=<copy-from-backend/.env>
GOOGLE_REDIRECT_URI=https://resumatch-backend-7qdb.onrender.com/api/auth/callback
```

#### ✅ Required for job matching:
```bash
ADZUNA_APP_ID=<copy-from-backend/.env>
ADZUNA_APP_KEY=<copy-from-backend/.env>
```

#### ✅ Optional (but recommended):
```bash
STRIPE_PUBLISHABLE_KEY=<copy-from-backend/.env>
STRIPE_SECRET_KEY=<copy-from-backend/.env>
STRIPE_WEBHOOK_SECRET=<copy-from-backend/.env>
LINKEDIN_CLIENT_ID=<copy-from-backend/.env>
LINKEDIN_CLIENT_SECRET=<copy-from-backend/.env>
LINKEDIN_REDIRECT_URI=https://resumatch-backend-7qdb.onrender.com/api/auth/linkedin/callback
SENDGRID_API_KEY=<copy-from-backend/.env>
FROM_EMAIL=<copy-from-backend/.env>
RATELIMIT_ENABLED=true
LOG_LEVEL=INFO
```

### Step 2: Frontend Environment Variables

Go to your **Frontend service** on Render → **Environment** tab → Add these:

#### ✅ Critical - Without this, frontend can't talk to backend:
```bash
REACT_APP_API_URL=https://resumatch-backend-7qdb.onrender.com/api
REACT_APP_ENV=production
REACT_APP_API_TIMEOUT=30000
```

### Step 3: Update Google OAuth Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID (starts with: 541653508225...)
3. Click "Edit"
4. Under "Authorized redirect URIs", add:
   ```
   https://resumatch-backend-7qdb.onrender.com/api/auth/callback
   ```
5. Click "Save"

### Step 4: Verify Configuration

After adding all environment variables, visit:
```
https://resumatch-backend-7qdb.onrender.com/api/health
```

You should see:
```json
{
  "status": "ok",
  "database": "connected",
  "environment": {
    "flask_env": "production",
    "frontend_url": "https://resumeanalyzerai.com",
    "backend_url": "https://resumatch-backend-7qdb.onrender.com",
    "has_jwt_secret": "yes",
    "has_google_oauth": "yes",
    "has_gemini_key": "yes",
    "has_database_url": "yes"
  }
}
```

If any value shows "not set" or "no", add that environment variable!

### Step 5: Test Login

1. Go to: https://resumeanalyzerai.com
2. Try "Sign in with Google"
3. If it still fails, check backend logs on Render for detailed error messages

## Common Issues

### "Unexpected token '<'" Error
- **Cause**: Frontend can't reach backend
- **Fix**: Set `REACT_APP_API_URL` in frontend environment variables

### oauth_failed Error
- **Cause**: Environment variables not set on backend
- **Fix**: Add all backend environment variables listed above

### Google OAuth 503 Error
- **Cause**: Database not connected or environment variables missing
- **Fix**: Add `DATABASE_URL` and all critical environment variables

### Guest Session Not Working
- **Cause**: Database not connected or Gemini API key missing
- **Fix**: Verify `DATABASE_URL` and `GEMINI_API_KEY` are set

## How to Get Values

### Generate Security Keys:
```bash
openssl rand -hex 32   # For JWT_SECRET_KEY
openssl rand -hex 32   # For SECRET_KEY
```

### Get Values from backend/.env:
Open `backend/.env` and copy the values for:
- GEMINI_API_KEY
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- ADZUNA_APP_ID
- ADZUNA_APP_KEY
- STRIPE_* keys
- SENDGRID_API_KEY
- etc.

### Get DATABASE_URL:
1. In Render Dashboard, find your PostgreSQL database
2. Copy the "Internal Database URL"
3. Paste as `DATABASE_URL` value

## After Configuration

Once all variables are added:
1. Render will automatically redeploy both services
2. Wait ~2-3 minutes for deployment to complete
3. Test login at https://resumeanalyzerai.com
4. Check health endpoint for confirmation
