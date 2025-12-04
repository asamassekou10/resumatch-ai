# Admin Diagnostics & Fixes

This document explains how to diagnose and fix issues with Market Pages and Skill Extraction using the admin diagnostic endpoints.

## Prerequisites

- You must be logged in as an admin user
- Admin accounts:
  - `sitaram.ayyagari@project.review` / `ProfessorReview2024!`
  - `alhassane.samassekou@gmail.com` / `AdminResuMatch2024!`

## API Endpoints

All endpoints require JWT authentication and admin privileges.

### 1. Full Diagnostic Check

**Endpoint**: `GET /api/v1/admin/diagnostics/full-diagnostic`

**Description**: Runs a complete diagnostic check on both market intelligence and skill extraction.

**Example**:
```bash
curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/full-diagnostic \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response**:
```json
{
  "status": "needs_attention",
  "timestamp": "2025-12-04T05:51:46",
  "market_intelligence": {
    "status": "warning",
    "data": {
      "job_postings": 150,
      "skills": 450,
      "recent_jobs_30_days": 0
    },
    "issues": ["LOW_JOB_COUNT (150) - Should have 50,000+"]
  },
  "skill_extraction": {
    "status": "warning",
    "data": {
      "total_extractions": 0,
      "analyses_without_extractions": 15
    },
    "issues": ["15 recent analyses WITHOUT skill extractions"]
  }
}
```

---

### 2. Check Market Intelligence Data

**Endpoint**: `GET /api/v1/admin/diagnostics/market-data`

**Description**: Checks the status of job postings, skills, and market intelligence data.

**Example**:
```bash
curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/market-data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Issues Detected**:
- `NO_JOB_POSTINGS` - Market pages will be empty
- `LOW_JOB_COUNT` - Less than 1,000 jobs (should be 50,000+)
- `NO_SKILLS` - Cannot show skills demand
- `NO_JOB_SKILL_RELATIONSHIPS` - Market analysis will fail
- `NO_RECENT_JOBS` - Data may be stale

**Fix**: Run job ingestion from Adzuna API:
```bash
# Using the API endpoint
curl -X POST https://resumeanalyzerai.onrender.com/api/v1/jobs/ingest-real \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 3. Check Skill Extraction Status

**Endpoint**: `GET /api/v1/admin/diagnostics/skill-extraction`

**Description**: Checks if skill extraction is working for resume analyses.

**Example**:
```bash
curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/skill-extraction \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Issues Detected**:
- `NO_SKILL_EXTRACTIONS` - Feature is not working at all
- `NO_RECENT_EXTRACTIONS` - May not be integrated with analysis
- `X recent analyses WITHOUT skill extractions` - Missing extractions

**Response**:
```json
{
  "status": "warning",
  "data": {
    "total_extractions": 0,
    "recent_extractions_7_days": 0,
    "feedback": {
      "confirmed": 0,
      "rejected": 0,
      "pending": 0
    },
    "analyses_without_extractions": 15,
    "sample_extractions": []
  },
  "issues": [
    "NO_SKILL_EXTRACTIONS - Feature is not working",
    "15 recent analyses WITHOUT skill extractions"
  ]
}
```

---

### 4. Fix Skill Extractions (AUTO-FIX)

**Endpoint**: `POST /api/v1/admin/diagnostics/fix-skill-extractions`

**Description**: Automatically creates skill extractions for recent analyses (last 30 days) that don't have any. This will enable the self-learning feedback feature.

**Example**:
```bash
curl -X POST https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/fix-skill-extractions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**What it does**:
1. Finds analyses from the last 30 days without skill extractions
2. Creates extractions for found skills (high confidence: 0.85)
3. Creates extractions for missing skills (lower confidence: 0.65)
4. Limits to 50 analyses per run to avoid timeouts

**Response**:
```json
{
  "status": "success",
  "message": "Created skill extractions for 15 analyses",
  "fixed_count": 15,
  "total_found": 15
}
```

---

## Step-by-Step Fix Guide

### Problem 1: Market Pages Not Working

**Symptoms**:
- Market intelligence pages show "No data available"
- Skills demand charts are empty
- Salary analysis not working

**Solution**:

1. **Check the issue**:
   ```bash
   curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/market-data \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. **Fix by ingesting jobs**:
   - Login to admin account
   - Navigate to: https://resumeanalyzerai.onrender.com/admin
   - Click "Ingest Jobs from Adzuna"

   OR use API:
   ```bash
   curl -X POST https://resumeanalyzerai.onrender.com/api/v1/jobs/ingest-real \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Wait for completion** (may take 5-10 minutes for 50,000+ jobs)

4. **Verify fix**:
   ```bash
   curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/market-data \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```
   - Should show 50,000+ jobs
   - `status` should be `"healthy"`

---

### Problem 2: Skill Extraction Feedback Not Showing

**Symptoms**:
- After resume analysis, "Skill Verification" section is empty
- No skills shown for confirmation/rejection
- Self-learning feature not working

**Solution**:

1. **Check the issue**:
   ```bash
   curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/skill-extraction \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. **Run auto-fix**:
   ```bash
   curl -X POST https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/fix-skill-extractions \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Verify fix**:
   - Upload a new resume
   - Check if "Help Us Learn - Skill Verification" section shows skills
   - OR check via API:
   ```bash
   curl -X GET https://resumeanalyzerai.onrender.com/api/v1/skills/extract/ANALYSIS_ID \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

4. **Long-term fix** (for future analyses):
   - The issue is likely that `skill_extractor` module is failing silently
   - Check backend logs:
   ```bash
   # On Render dashboard
   View Logs → Filter for "Skill extraction failed"
   ```
   - Possible causes:
     - spaCy model not loaded correctly
     - Database connection issues during extraction
     - Exception being caught and suppressed

---

## Getting Your JWT Token

### Method 1: Via Browser (Easiest)

1. Login to https://www.resumeanalyzerai.com
2. Open Browser DevTools (F12)
3. Go to: Application → Local Storage → `https://www.resumeanalyzerai.com`
4. Copy the value of `resume_analyzer_token`
5. Use in API calls: `Authorization: Bearer <token>`

### Method 2: Via API

```bash
curl -X POST https://resumeanalyzerai.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sitaram.ayyagari@project.review",
    "password": "ProfessorReview2024!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {...}
}
```

---

## Troubleshooting

### Endpoint Returns 403 Forbidden

**Cause**: Not logged in as admin
**Fix**: Use admin account credentials

### Endpoint Returns 401 Unauthorized

**Cause**: Invalid or expired JWT token
**Fix**: Login again to get a fresh token

### "Fix" endpoint doesn't fix the issue

**Cause**: Root cause may be in the analysis route
**Fix**: Check if future analyses create extractions automatically

### Market pages still empty after job ingestion

**Cause**: Job ingestion may have failed
**Fix**:
1. Check backend logs for errors
2. Verify Adzuna API key is set correctly
3. Check database connectivity

---

## Monitoring

Run the full diagnostic periodically:

```bash
# Add to cron or scheduled task
curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/full-diagnostic \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  | jq .
```

---

## Summary

**Quick Fix Commands**:

```bash
# 1. Get JWT Token
TOKEN=$(curl -X POST https://resumeanalyzerai.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sitaram.ayyagari@project.review","password":"ProfessorReview2024!"}' \
  | jq -r .access_token)

# 2. Run Full Diagnostic
curl -X GET https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/full-diagnostic \
  -H "Authorization: Bearer $TOKEN"

# 3. Fix Market Pages (if needed)
curl -X POST https://resumeanalyzerai.onrender.com/api/v1/jobs/ingest-real \
  -H "Authorization: Bearer $TOKEN"

# 4. Fix Skill Extractions (if needed)
curl -X POST https://resumeanalyzerai.onrender.com/api/v1/admin/diagnostics/fix-skill-extractions \
  -H "Authorization: Bearer $TOKEN"
```

---

**Notes**:
- All endpoints are production-ready and safe to use
- The fix endpoints only create missing data, they don't delete anything
- Run diagnostics before and after fixes to verify
- Check Render logs if issues persist
