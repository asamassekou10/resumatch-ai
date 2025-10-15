# 🧪 Testing Guide - ResumeAnalyzer AI v2.0

This guide will help you test the new v2.0 version safely and thoroughly.

## 🚀 Quick Start Testing

### 1. Backend Quick Test

```bash
cd backend
python test_v2.py
```

This will run basic import and functionality tests without requiring a full setup.

### 2. Frontend Quick Test

```bash
cd frontend
node test_v2.js
```

This will check if all new files are in place and package.json is updated.

## 📋 Complete Testing Process

### Phase 1: Basic Setup Test

#### Backend Setup
```bash
cd backend

# 1. Create environment file
cp .env.example .env
# Edit .env with your actual values

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Run quick test
python test_v2.py
```

#### Frontend Setup
```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Set up environment
cp env.example .env.local
# Edit .env.local with your API URL

# 3. Run quick test
node test_v2.js
```

### Phase 2: Full Application Test

#### Start Backend Server
```bash
cd backend
python app_v2.py
```

The server will start at `http://localhost:5000`

#### Start Frontend Server
```bash
cd frontend
npm start
```

The frontend will start at `http://localhost:3000`

### Phase 3: Functional Testing

#### Test API Endpoints

1. **Health Check**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

2. **User Registration**
   ```bash
   curl -X POST http://localhost:5000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

3. **User Login**
   ```bash
   curl -X POST http://localhost:5000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

#### Test Frontend Features

1. **Landing Page** - Visit `http://localhost:3000`
2. **User Registration** - Test the sign-up form
3. **User Login** - Test the login form
4. **Resume Upload** - Test file upload functionality
5. **Analysis Results** - Test the analysis display
6. **Dashboard** - Test the dashboard features

## 🧪 Automated Testing

### Backend Tests
```bash
cd backend

# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_auth.py -v
pytest tests/test_analysis.py -v
pytest tests/test_health.py -v

# Run with verbose output
pytest -v
```

### Frontend Tests
```bash
cd frontend

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm test

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

## 🔍 Manual Testing Checklist

### Authentication Flow
- [ ] User can register with valid email/password
- [ ] User cannot register with invalid email
- [ ] User cannot register with weak password
- [ ] User can login with correct credentials
- [ ] User cannot login with wrong credentials
- [ ] JWT tokens are properly stored and used
- [ ] User can logout successfully

### Resume Analysis
- [ ] User can upload PDF files
- [ ] User can upload DOCX files
- [ ] User can upload TXT files
- [ ] File size validation works (16MB limit)
- [ ] File type validation works
- [ ] Job description validation works (min 50 chars)
- [ ] Analysis generates match score
- [ ] Analysis shows keywords found/missing
- [ ] Analysis provides suggestions

### AI Features
- [ ] AI feedback generation works
- [ ] Resume optimization works
- [ ] Cover letter generation works
- [ ] Skill suggestions work
- [ ] Fallback responses work when AI is unavailable

### Dashboard
- [ ] Dashboard loads user statistics
- [ ] Analysis history is displayed
- [ ] Charts and graphs render correctly
- [ ] Insights are generated
- [ ] Pagination works for analysis list

### Error Handling
- [ ] Network errors are handled gracefully
- [ ] Validation errors show user-friendly messages
- [ ] 404 errors show appropriate messages
- [ ] 500 errors don't expose sensitive information
- [ ] File upload errors are handled

### Security
- [ ] CORS is properly configured
- [ ] Input validation prevents XSS
- [ ] File uploads are validated
- [ ] Rate limiting works
- [ ] JWT tokens expire properly

## 🐛 Troubleshooting Common Issues

### Backend Issues

#### Import Errors
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### Database Connection Errors
```bash
# Solution: Check DATABASE_URL in .env file
# Ensure PostgreSQL is running
# Create database if it doesn't exist
createdb resume_optimizer
```

#### spaCy Model Errors
```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

#### JWT Errors
```bash
# Solution: Check JWT_SECRET_KEY in .env file
# Ensure it's set and not empty
```

### Frontend Issues

#### API Connection Errors
```bash
# Solution: Check REACT_APP_API_URL in .env.local
# Ensure backend server is running
# Check CORS configuration
```

#### Build Errors
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Test Failures
```bash
# Solution: Update test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

## 📊 Performance Testing

### Load Testing
```bash
# Install artillery for load testing
npm install -g artillery

# Create load test config
cat > load-test.yml << EOF
config:
  target: 'http://localhost:5000'
  phases:
    - duration: 60
      arrivalRate: 5
scenarios:
  - name: "Health Check"
    requests:
      - get:
          url: "/api/v1/health"
EOF

# Run load test
artillery run load-test.yml
```

### Memory Usage
```bash
# Monitor memory usage
ps aux | grep python
ps aux | grep node
```

## 🔒 Security Testing

### Input Validation
- Test with malicious input in all forms
- Test SQL injection attempts
- Test XSS attempts
- Test file upload with malicious files

### Authentication
- Test with expired tokens
- Test with invalid tokens
- Test with no tokens
- Test rate limiting

### File Upload Security
- Test with oversized files
- Test with invalid file types
- Test with malicious file content
- Test with executable files

## 📈 Monitoring

### Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Check for errors
grep "ERROR" backend/logs/app.log
```

### Health Checks
```bash
# Basic health check
curl http://localhost:5000/api/v1/health

# Detailed health check (requires auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/v1/health/detailed
```

## ✅ Success Criteria

The new version is ready for production when:

- [ ] All automated tests pass (80%+ coverage)
- [ ] All manual tests pass
- [ ] Performance is acceptable (<2s response times)
- [ ] Security tests pass
- [ ] Error handling works correctly
- [ ] Documentation is complete
- [ ] Migration guide is tested

## 🆘 Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Review the troubleshooting section
3. Run the quick test scripts
4. Check environment variables
5. Verify all dependencies are installed
6. Create an issue in the repository

---

**Happy Testing! 🚀**
