# Test Deployment Checklist

Your backend is **LIVE** ✅ at: https://resumatch-backend-7qdb.onrender.com

The database errors you see are just warnings - they don't block the app from working.

## Quick Tests

### Test 1: Health Check (Backend)
Open this URL in your browser:
```
https://resumatch-backend-7qdb.onrender.com/api/v1/health
```

**Expected result:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "database": "healthy",
    "environment": {
      "flask_env": "production",
      "frontend_url": "https://resumeanalyzerai.com",
      "backend_url": "https://resumatch-backend-7qdb.onrender.com",
      "has_jwt_secret": "yes",
      "has_google_oauth": "yes",
      "has_gemini_key": "yes",
      "has_database_url": "yes",
      "has_adzuna_keys": "yes"
    }
  }
}
```

**If any value shows "no" or "not set":**
- Go to Render Backend service → Environment
- Add that missing variable from your backend/.env file

---

### Test 2: Frontend Can Reach Backend
1. Open https://resumeanalyzerai.com
2. Open browser Developer Tools (F12)
3. Go to Console tab
4. Look for errors

**Common errors:**

**Error: "Unexpected token '<'"**
- **Cause**: Frontend can't find backend
- **Fix**: Check Frontend environment variable `REACT_APP_API_URL` is set to:
  ```
  https://resumatch-backend-7qdb.onrender.com/api
  ```

**Error: "CORS policy"**
- **Cause**: Backend FRONTEND_URL doesn't match
- **Fix**: Set Backend `FRONTEND_URL` to:
  ```
  https://resumeanalyzerai.com
  ```

---

### Test 3: Guest Session
1. Go to https://resumeanalyzerai.com
2. Try "Try as Guest" or guest analysis
3. Check browser Console for errors

**If you see errors:**
- Check Network tab in Developer Tools
- Look for failed requests to `/api/guest/session`
- Copy the error response and share it

---

### Test 4: Email Login
1. Go to https://resumeanalyzerai.com
2. Try to register or login with email
3. Check for errors

**If registration fails:**
- Check backend logs on Render
- Look for errors related to JWT or database

---

### Test 5: Google OAuth
1. Go to https://resumeanalyzerai.com
2. Click "Sign in with Google"
3. Note where you get redirected

**If you get "oauth_failed" or 503 error:**

Check Google OAuth Console:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client
3. Under "Authorized redirect URIs", verify you have:
   ```
   https://resumatch-backend-7qdb.onrender.com/api/auth/callback
   ```
4. If not, add it and click Save
5. Wait 5 minutes for Google to update
6. Try again

---

## Debug Information to Collect

If things still don't work, collect this information:

### From Browser (F12 Console):
1. Any error messages in Console tab
2. Failed requests in Network tab (filter: XHR)
3. The URL it tries to call
4. The response it gets

### From Render Backend Logs:
1. Go to Render Dashboard → Backend service → Logs
2. Try to login/register again
3. Copy any ERROR lines that appear
4. Share them with me

### Environment Variables to Verify:

**Backend:**
```bash
✓ DATABASE_URL - set to Internal URL
✓ JWT_SECRET_KEY - 64 character random string
✓ SECRET_KEY - 64 character random string
✓ GEMINI_API_KEY - starts with AIza...
✓ FRONTEND_URL - https://resumeanalyzerai.com
✓ BACKEND_URL - https://resumatch-backend-7qdb.onrender.com
✓ GOOGLE_CLIENT_ID - from backend/.env
✓ GOOGLE_CLIENT_SECRET - from backend/.env
✓ FLASK_ENV - production
```

**Frontend:**
```bash
✓ REACT_APP_API_URL - https://resumatch-backend-7qdb.onrender.com/api
✓ REACT_APP_ENV - production
```

---

## Quick Fixes

### If nothing works:
1. Clear browser cache and cookies for resumeanalyzerai.com
2. Try in incognito/private browsing mode
3. Try a different browser

### If only OAuth fails:
1. Update Google OAuth Console redirect URI
2. Wait 5 minutes
3. Clear cookies
4. Try again

### If only guest session fails:
1. Check health endpoint shows database: "healthy"
2. Check backend logs for database errors
3. Try email registration instead
