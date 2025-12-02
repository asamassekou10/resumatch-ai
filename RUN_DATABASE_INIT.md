# Database Initialization on Render

## 🔴 CRITICAL: Run This Immediately to Fix All Errors

Your production database is **empty** - no tables exist. This is why everything fails:
- Google OAuth: `relation "users" does not exist`
- Email Login: `relation "users" does not exist`
- Guest Session: `relation "guest_session" does not exist`

## Quick Fix - Run Database Initialization

### Option 1: Run via Render Shell (RECOMMENDED)

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Find your **Backend service** (resumatch-backend-7qdb)
   - Click on it

2. **Open Shell**
   - Click the **"Shell"** tab in the left sidebar
   - Wait for the shell to connect

3. **Run the initialization script**
   ```bash
   python backend/init_database.py
   ```

4. **Expected Output**
   ```
   Creating database tables...
   ✅ Database tables created successfully!

   📊 Created 11 tables:
      - analyses
      - career_paths
      - company_intel
      - guest_analyses
      - guest_session
      - interview_prep
      - job_matches
      - job_postings
      - keywords
      - system_configuration
      - users
   ```

5. **If successful**: Your app should work immediately! Test login and guest session.

### Option 2: Add as One-Time Deploy Command

If Shell doesn't work, you can run it during deployment:

1. **Go to Backend Service Settings**
   - Render Dashboard → Backend service
   - Click **"Settings"** tab

2. **Update Build Command** (temporarily)
   - Find "Build Command"
   - Change from: `pip install -r requirements.txt`
   - To: `pip install -r requirements.txt && python backend/init_database.py`
   - Click **"Save Changes"**

3. **Manual Deploy**
   - Go to "Manual Deploy" section
   - Click **"Deploy latest commit"**
   - Wait for build to complete

4. **Revert Build Command** (after successful init)
   - Go back to Settings
   - Change Build Command back to: `pip install -r requirements.txt`
   - Save

## Verify Database Initialization

### Test 1: Check Health Endpoint
```
https://resumatch-backend-7qdb.onrender.com/api/v1/health
```

Should now show:
```json
{
  "status": "success",
  "data": {
    "database": "healthy"
  }
}
```

### Test 2: Check Backend Logs
- Go to Render → Backend service → Logs
- Should NOT see "relation does not exist" errors anymore

### Test 3: Try Login
1. Go to https://resumeanalyzerai.com
2. Try email registration
3. Should work without "Login failed" error

### Test 4: Try Guest Session
1. Go to your site
2. Click "Try as Guest"
3. Should work without "Failed to fetch" error

### Test 5: Try Google OAuth
1. Click "Sign in with Google"
2. Should complete successfully and create account

## Troubleshooting

### Error: "No module named 'app'"
**Fix**: Run from the correct directory
```bash
cd /opt/render/project/src
python backend/init_database.py
```

### Error: "No such file or directory"
**Fix**: Ensure you're in the project root
```bash
ls backend/init_database.py  # Should show the file exists
python backend/init_database.py
```

### Error: "Database connection failed"
**Fix**: Check DATABASE_URL is set correctly
```bash
echo $DATABASE_URL  # Should show postgresql://...
```

If empty, update it in Render Environment variables.

### Error: "Permission denied"
**Fix**: Render shell should have all permissions, but try:
```bash
python3 backend/init_database.py
```

### Tables Already Exist
If you see: "Table already exists" - that's fine! It means tables are already initialized.

## After Successful Initialization

✅ **All features should now work**:
- Email registration and login
- Google OAuth sign-in
- Guest session analysis
- Job matching
- Interview prep
- All AI features

🎉 **Your app is ready to use!**

## Still Having Issues?

If you still see errors after initialization, collect:

1. **Output from init_database.py**
   - Did it show "✅ Database tables created successfully!"?
   - How many tables were created?

2. **Health check response**
   - Visit: https://resumatch-backend-7qdb.onrender.com/api/v1/health
   - Copy the JSON response

3. **Backend logs after trying to login**
   - Render → Backend → Logs
   - Try to login or use guest session
   - Copy any ERROR lines

Share this information and I'll help further!
