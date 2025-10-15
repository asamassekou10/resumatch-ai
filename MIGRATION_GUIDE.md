# Migration Guide: v1.0 to v2.0

This guide will help you migrate from the original ResumeAnalyzer AI v1.0 to the production-ready v2.0.

## 🚨 Breaking Changes

### Backend Changes

1. **New Application Structure**
   - Main app file: `app.py` → `app_v2.py`
   - New configuration system in `config.py`
   - Modular route structure in `routes/` directory

2. **API Endpoint Changes**
   - All endpoints now prefixed with `/api/v1/`
   - New response format with standardized structure
   - Updated authentication flow

3. **Database Schema Updates**
   - New fields added to User and Analysis models
   - Database migrations required

### Frontend Changes

1. **New Component Structure**
   - Reorganized component hierarchy
   - New context-based state management
   - Updated API service layer

2. **Configuration Changes**
   - Environment variables now required
   - New API base URL format

## 📋 Migration Steps

### Step 1: Backup Your Data

```bash
# Backup your database
pg_dump resume_optimizer > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup your current application
cp -r backend backend_backup
cp -r frontend frontend_backup
```

### Step 2: Update Backend

1. **Install New Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Update Environment Variables**
```bash
# Create new .env file
cp .env.example .env

# Add your existing values plus new ones:
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=your-existing-database-url
GEMINI_API_KEY=your-existing-gemini-key
```

3. **Run Database Migrations**
```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create migration for existing schema
alembic revision --autogenerate -m "Initial migration from v1"

# Apply migrations
alembic upgrade head
```

4. **Update Your Deployment**
```bash
# Update your startup command
gunicorn --bind 0.0.0.0:5000 app_v2:app
```

### Step 3: Update Frontend

1. **Install New Dependencies**
```bash
cd frontend
npm install
```

2. **Update Environment Variables**
```bash
# Create .env.local file
cp env.example .env.local

# Update API URL
REACT_APP_API_URL=http://your-backend-url/api/v1
```

3. **Update API Calls**
   - Replace direct fetch calls with new ApiService
   - Update endpoint URLs to include `/api/v1/` prefix
   - Handle new response format

### Step 4: Test the Migration

1. **Run Backend Tests**
```bash
cd backend
pytest --cov=. --cov-report=html
```

2. **Run Frontend Tests**
```bash
cd frontend
npm run test:coverage
```

3. **Test Key Features**
   - User registration/login
   - Resume analysis
   - Dashboard functionality
   - AI features

## 🔄 API Migration Examples

### Authentication

**Before (v1.0):**
```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const data = await response.json();
```

**After (v2.0):**
```javascript
import ApiService from '../services/api';

const result = await ApiService.login(email, password);
if (result.success) {
  // Handle success
} else {
  // Handle error
}
```

### Resume Analysis

**Before (v1.0):**
```javascript
const formData = new FormData();
formData.append('resume', file);
formData.append('job_description', description);

const response = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

**After (v2.0):**
```javascript
import ApiService, { createFormData } from '../services/api';

const formData = createFormData(file, description, jobTitle, companyName);
const result = await ApiService.analyzeResume(formData);
```

## 🐛 Common Issues & Solutions

### Issue 1: Database Connection Errors
**Problem:** Database connection fails after migration
**Solution:** 
```bash
# Check your DATABASE_URL format
# Should be: postgresql://user:password@host:port/database

# Test connection
python -c "from models import db; print('Connection OK')"
```

### Issue 2: JWT Token Errors
**Problem:** Authentication tokens not working
**Solution:**
```bash
# Clear existing tokens and re-login
# Tokens from v1.0 are not compatible with v2.0
```

### Issue 3: CORS Errors
**Problem:** Frontend can't connect to backend
**Solution:**
```bash
# Update CORS_ORIGINS in config.py
# Add your frontend URL to the allowed origins list
```

### Issue 4: Missing Dependencies
**Problem:** Import errors for new modules
**Solution:**
```bash
# Install all new dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 📊 Performance Improvements

After migration, you should see:

1. **Faster Response Times**
   - Caching implementation
   - Optimized database queries
   - Reduced API calls

2. **Better Error Handling**
   - User-friendly error messages
   - Proper HTTP status codes
   - Detailed logging

3. **Enhanced Security**
   - Input validation
   - Rate limiting
   - Secure file uploads

## 🔍 Verification Checklist

- [ ] Database migrations completed successfully
- [ ] All environment variables configured
- [ ] Backend tests passing (80%+ coverage)
- [ ] Frontend tests passing
- [ ] User registration/login working
- [ ] Resume analysis functional
- [ ] Dashboard displaying correctly
- [ ] AI features operational
- [ ] Error handling working properly
- [ ] File uploads secure and validated

## 🆘 Rollback Plan

If you encounter critical issues:

1. **Stop the new application**
2. **Restore database backup**
```bash
psql resume_optimizer < backup_YYYYMMDD_HHMMSS.sql
```
3. **Revert to v1.0 code**
```bash
mv backend_backup backend
mv frontend_backup frontend
```
4. **Restart with v1.0**

## 📞 Support

If you encounter issues during migration:

1. Check the error logs in `logs/app.log`
2. Review the test output for specific failures
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed
5. Create an issue in the repository with:
   - Error messages
   - Your environment details
   - Steps to reproduce

## 🎉 Post-Migration

After successful migration:

1. **Monitor Performance**
   - Check response times
   - Monitor error rates
   - Review logs for issues

2. **Update Documentation**
   - Update your deployment docs
   - Inform users of new features
   - Update API documentation

3. **Plan Future Updates**
   - Set up monitoring
   - Schedule regular backups
   - Plan for scaling

---

**Migration completed successfully! Welcome to ResumeAnalyzer AI v2.0! 🚀**
