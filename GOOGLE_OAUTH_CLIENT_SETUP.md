# Google OAuth Client ID Configuration

## Error You're Seeing

```
Access blocked: Authorization Error
The OAuth client was not found.
Error 401: invalid_client
```

## Root Cause

The Google Client ID in the code (`535154830356-36e2i2u5rj74tsk0s0hib3d1f3kpkqvj.apps.googleusercontent.com`) is either:

1. From a different project/developer
2. Not configured for your domain (`https://www.resumeanalyzerai.com`)
3. Missing from environment variables

## How to Fix

### Option 1: Use Existing Client ID (If You Have One)

If you already have a Google Cloud project with OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your project
3. Find your OAuth 2.0 Client ID
4. Copy the Client ID
5. Set it as an environment variable:

**Vercel:**
- Go to your Vercel project settings
- Navigate to Environment Variables
- Add: `REACT_APP_GOOGLE_CLIENT_ID` = `YOUR_CLIENT_ID_HERE`
- Redeploy the application

### Option 2: Create New OAuth Credentials

If you don't have OAuth credentials set up:

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note the project ID

#### Step 2: Enable Google+ API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click "Enable"

#### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Fill in required fields:
   - **App name**: ResumeAnalyzer AI
   - **User support email**: Your email
   - **Developer contact**: Your email
   - **Authorized domains**: `resumeanalyzerai.com`
4. Click "Save and Continue"
5. Skip Scopes (click "Save and Continue")
6. Add test users if needed
7. Click "Back to Dashboard"

#### Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Configure:
   - **Name**: ResumeAnalyzer AI Web Client
   - **Authorized JavaScript origins**:
     - `https://www.resumeanalyzerai.com`
     - `https://resumeanalyzerai.com`
     - `http://localhost:3000` (for development)
   - **Authorized redirect URIs**:
     - `https://www.resumeanalyzerai.com`
     - `https://resumeanalyzerai.com`
     - `http://localhost:3000` (for development)
5. Click "Create"
6. **Copy the Client ID** (looks like: `123456789-abcdefg.apps.googleusercontent.com`)

#### Step 5: Update Environment Variables

**For Vercel (Production):**
```bash
# In Vercel Dashboard > Settings > Environment Variables
REACT_APP_GOOGLE_CLIENT_ID=YOUR_NEW_CLIENT_ID_HERE
```

**For Local Development:**
```bash
# In frontend/.env.local (create if doesn't exist)
REACT_APP_GOOGLE_CLIENT_ID=YOUR_NEW_CLIENT_ID_HERE
```

**For Backend:**
```bash
# In backend .env or Render environment variables
GOOGLE_CLIENT_ID=YOUR_NEW_CLIENT_ID_HERE
```

#### Step 6: Redeploy

After setting environment variables, redeploy your application:
- Vercel will auto-deploy on the next git push
- Or manually trigger a redeploy in Vercel dashboard

## Verification

After deploying with the correct Client ID:

1. Go to https://www.resumeanalyzerai.com/login
2. Click "Continue with Google"
3. You should see the Google account selection popup
4. Select your Google account
5. Grant permissions
6. You should be redirected to the dashboard

## Fallback

If Google OAuth continues to have issues, users can still:
- ✅ Register with email/password
- ✅ Use LinkedIn OAuth (if configured)
- ✅ Access guest analysis

## Current Code Location

The Client ID is used in:
- **Frontend**: `frontend/src/components/AuthPage.jsx` line 150
- **Environment**: Set via `REACT_APP_GOOGLE_CLIENT_ID`

```javascript
client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID || '535154830356-...',
```

The fallback ID (`535154830356-...`) is a placeholder and won't work for production.

## Security Note

**Never commit OAuth credentials to Git!**
- ✅ Use environment variables
- ✅ Add `.env.local` to `.gitignore`
- ✅ Store in Vercel/Render settings
- ❌ Never hardcode in source code

## Troubleshooting

### "OAuth client was not found"
- Client ID is incorrect
- Client ID not configured for your domain

### "redirect_uri_mismatch"
- Add your domain to "Authorized redirect URIs" in Google Cloud Console

### "This app isn't verified"
- Normal for apps in testing mode
- Click "Advanced" > "Go to ResumeAnalyzer AI (unsafe)"
- Or complete Google's verification process (takes weeks)

### Still not working?
1. Clear browser cache and cookies
2. Try incognito mode
3. Check browser console for errors
4. Verify environment variable is set correctly
5. Check Google Cloud Console audit logs
