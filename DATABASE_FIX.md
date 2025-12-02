# Database Connection Fix

## Error
```
could not translate host name "dpg-d3lguu0gjchc73cddftg-a" to address: Name or service not known
```

## Root Cause
You're using the **External Database URL** which isn't accessible from within Render's network. You need to use the **Internal Database URL** instead.

## Fix Steps

### Step 1: Get the Correct DATABASE_URL

1. Go to your Render Dashboard
2. Find your PostgreSQL database service
3. Click on it
4. Look for **"Internal Database URL"** (NOT "External Database URL")
5. Copy the **Internal Database URL**

It should look like:
```
postgresql://username:password@dpg-xxxxx-a.oregon-postgres.render.com/dbname
```

The key difference is it will have the full `.oregon-postgres.render.com` or `.ohio-postgres.render.com` domain.

### Step 2: Update Backend Environment Variable

1. Go to your **Backend service** on Render
2. Click **Environment** tab
3. Find the `DATABASE_URL` variable
4. **Delete the old value**
5. **Paste the Internal Database URL** you copied
6. Click **Save Changes**

### Step 3: Verify

Render will automatically redeploy. After ~2 minutes, check:
```
https://resumatch-backend-7qdb.onrender.com/api/v1/health
```

You should see:
```json
{
  "status": "success",
  "data": {
    "database": "healthy",
    "environment": {
      "has_database_url": "yes"
    }
  }
}
```

If `database` shows `unhealthy`, check the backend logs for errors.

## Common Issues

### Issue: "SSL connection required"
**Fix**: Make sure the DATABASE_URL includes `?sslmode=require` at the end:
```
postgresql://user:pass@host/db?sslmode=require
```

### Issue: Still can't connect
**Checklist**:
1. ✅ Using **Internal** Database URL (not External)
2. ✅ Database and backend are in the **same region** (e.g., both Oregon)
3. ✅ DATABASE_URL is saved in backend environment variables
4. ✅ No typos in the URL

### Issue: Database exists but empty tables
This means the database connected successfully but migrations haven't run. You may need to:
1. SSH into your backend service (if Render allows)
2. Run: `flask db upgrade`

Or the tables will be created automatically on first request.
