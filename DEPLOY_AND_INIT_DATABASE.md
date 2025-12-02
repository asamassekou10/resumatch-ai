# Deploy Latest Changes and Initialize Database

## Step 1: Deploy Latest Commit to Render

The `init_database.py` script was just pushed to GitHub, but Render hasn't deployed it yet.

### Option A: Automatic Deploy (If Auto-Deploy is Enabled)

1. Go to Render Dashboard: https://dashboard.render.com
2. Click on your **Backend service** (resumatch-backend-7qdb)
3. Check the **"Events"** tab
4. Look for a deploy in progress or wait 1-2 minutes for auto-deploy to trigger
5. Wait until you see **"Deploy live"** status

### Option B: Manual Deploy (Recommended - Faster)

1. Go to Render Dashboard: https://dashboard.render.com
2. Click on your **Backend service** (resumatch-backend-7qdb)
3. Click **"Manual Deploy"** button at the top right
4. Select **"Deploy latest commit"**
5. Wait 2-3 minutes for the build to complete
6. You'll see **"Deploy live"** when ready

---

## Step 2: Initialize Database

Once the deployment is complete (you see "Deploy live"), run the initialization:

### Open Shell and Initialize:

1. In your Backend service page, click **"Shell"** tab (left sidebar)
2. Wait for shell to connect
3. Check current directory and files:
   ```bash
   pwd
   ls -la
   ```

4. The init_database.py should be in the backend folder. Run:
   ```bash
   python backend/init_database.py
   ```

### If That Doesn't Work:

Try these alternative paths:

**Option 1**: Navigate first
```bash
cd backend
python init_database.py
```

**Option 2**: Use absolute path
```bash
python /opt/render/project/src/backend/init_database.py
```

**Option 3**: Find the file
```bash
find . -name "init_database.py"
# Use the path it returns
```

---

## Step 3: Verify Success

### Expected Output:
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

### Verify Database Tables Exist:

Stay in the shell and run:
```bash
python -c "
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Found {len(tables)} tables: {tables}')
"
```

Should show: `Found 11 tables: ['analyses', 'career_paths', ...]`

---

## Step 4: Test Your Application

### Test 1: Health Check
Visit: https://resumatch-backend-7qdb.onrender.com/api/v1/health

Should now show:
```json
{
  "status": "success",
  "data": {
    "database": "healthy"
  }
}
```

### Test 2: Guest Session
1. Go to https://resumeanalyzerai.com
2. Try guest session
3. Should work without "Failed to fetch" error

### Test 3: Email Registration
1. Try to register with email
2. Should work without errors

### Test 4: Google OAuth
1. Click "Sign in with Google"
2. Should complete successfully

---

## Troubleshooting

### Issue: File still not found after deploy

Check if the commit deployed:
```bash
# In Render shell:
git log -1 --oneline
```

Should show: `Add database initialization script for production deployment`

If it shows an older commit, the deploy failed or didn't pick up the latest code. Try:
1. Go to Render → Backend → Settings
2. Check the **Branch** is set to `main`
3. Try Manual Deploy again

### Issue: Import errors when running script

If you see errors like "No module named 'app'", run from the correct directory:
```bash
cd /opt/render/project/src
python backend/init_database.py
```

### Issue: Database connection error

Check DATABASE_URL is set:
```bash
echo $DATABASE_URL
```

Should show a PostgreSQL connection string. If empty:
1. Go to Render → Backend → Environment
2. Verify DATABASE_URL is set to your PostgreSQL **Internal** URL

### Issue: Permission denied

Try with python3:
```bash
python3 backend/init_database.py
```

---

## Alternative: Initialize via Build Command (If Shell Doesn't Work)

If the shell method doesn't work, you can run it during deployment:

1. Go to Render → Backend service → **Settings**
2. Find **"Build Command"**
3. Temporarily change to:
   ```bash
   pip install -r requirements.txt && python backend/init_database.py || true
   ```
   (The `|| true` ensures build doesn't fail if tables already exist)

4. Click **"Save Changes"**
5. Trigger a **Manual Deploy**
6. Check the build logs - you should see the initialization output
7. After successful initialization, **revert the Build Command** back to:
   ```bash
   pip install -r requirements.txt
   ```

---

## Summary

1. ✅ **Deploy**: Manual Deploy → Wait for "Deploy live"
2. ✅ **Initialize**: Shell → `python backend/init_database.py`
3. ✅ **Verify**: Health check shows database "healthy"
4. ✅ **Test**: All features (login, OAuth, guest) work

**Total time: ~5 minutes**
