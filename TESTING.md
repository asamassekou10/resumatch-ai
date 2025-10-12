# Testing & Validation Guide

This guide will help you test all features of the AI Resume Optimizer to ensure everything works correctly.

## 🧪 Backend API Testing

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "message": "AI Resume Optimizer API is running"
}
```

### 2. User Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```
**Expected Response:**
```json
{
  "message": "User created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com"
  }
}
```

### 3. User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 4. Resume Analysis
Save your JWT token from login, then:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "resume=@/path/to/your/resume.pdf" \
  -F "job_description=We are looking for a Python developer with Flask experience and knowledge of machine learning..." \
  -F "job_title=Senior Python Developer" \
  -F "company_name=Tech Corp"
```

### 5. Get Analysis History
```bash
curl -X GET http://localhost:5000/api/analyses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 6. Get Dashboard Statistics
```bash
curl -X GET http://localhost:5000/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 🎨 Frontend Testing

### Manual Testing Checklist

#### Authentication Flow
- [ ] Can register a new account
- [ ] Can login with existing account
- [ ] Invalid credentials show error message
- [ ] Token persists after page refresh
- [ ] Logout clears session

#### Resume Analysis
- [ ] Can upload PDF resume
- [ ] Can upload DOCX resume
- [ ] Can upload TXT resume
- [ ] Invalid file types show error
- [ ] Can paste job description
- [ ] Can add optional job title and company
- [ ] Analysis completes in < 10 seconds
- [ ] Match score displays correctly
- [ ] Keywords found list appears
- [ ] Keywords missing list appears
- [ ] Suggestions are helpful and clear

#### Dashboard
- [ ] Total analyses count is accurate
- [ ] Average score calculates correctly
- [ ] Score trend chart displays
- [ ] Top skills gap chart shows
- [ ] Analysis history table loads
- [ ] Can click on history item to view details
- [ ] Score badges show correct colors (green/yellow/red)

#### UI/UX
- [ ] All buttons are clickable
- [ ] Loading states show during operations
- [ ] Error messages are clear
- [ ] Navigation between views works
- [ ] Responsive on mobile devices
- [ ] Forms validate input

## 🔬 AI Processing Testing

### Test Case 1: High Match Resume
Create a resume with these keywords: Python, Flask, Machine Learning, Docker, PostgreSQL, REST API

Create a job description with similar keywords.

**Expected Result:**
- Match score > 70%
- Most keywords found
- Few missing keywords

### Test Case 2: Low Match Resume
Create a resume focused on Java and Android development.

Use a job description for Python/AI role.

**Expected Result:**
- Match score < 50%
- Many missing keywords
- Suggestions to add relevant skills

### Test Case 3: Edge Cases
- [ ] Empty resume file
- [ ] Corrupted PDF
- [ ] Very short job description (< 50 words)
- [ ] Very long job description (> 5000 words)
- [ ] Resume with no text (scanned image PDF)
- [ ] Special characters in job description

## 📊 Performance Testing

### Response Time Benchmarks
Test with Apache Bench or similar tool:

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint (should be < 100ms)
ab -n 100 -c 10 http://localhost:5000/api/health

# Test login endpoint (should be < 500ms)
ab -n 50 -c 5 -p login.json -T application/json \
  http://localhost:5000/api/auth/login
```

**Target Metrics:**
- Health check: < 100ms
- Login: < 500ms
- Resume analysis: < 10 seconds
- Dashboard stats: < 1 second

### Memory Usage
```bash
# Check Docker container stats
docker stats backend
```

**Target:**
- Memory usage < 512MB under normal load

## 🛡️ Security Testing

### Authentication Tests
- [ ] Cannot access protected routes without token
- [ ] Expired tokens are rejected
- [ ] Invalid tokens are rejected
- [ ] Cannot access other user's data

### SQL Injection Tests
Try these in input fields:
- `' OR '1'='1`
- `1'; DROP TABLE users--`
- `admin'--`

**Expected:** All should be safely handled by SQLAlchemy ORM

### XSS Tests
Try these in job descriptions:
- `<script>alert('XSS')</script>`
- `<img src=x onerror=alert('XSS')>`

**Expected:** Should be escaped in display

## 📈 Accuracy Testing

### Keyword Extraction Accuracy
Create 10 job descriptions with known keywords. Manually identify the top 20 keywords.

Run analysis and compare:
```
Accuracy = (Correctly Identified Keywords / Total Keywords) * 100
```

**Target:** > 80% accuracy

### Match Score Validation
Create these test pairs:
1. Identical resume and job description → Should score ~100%
2. Completely unrelated → Should score < 30%
3. Partially related → Should score 40-60%

## 🐛 Bug Testing Scenarios

### Scenario 1: Concurrent Users
- Open app in 2 different browsers
- Register different users
- Perform analyses simultaneously
- Verify data doesn't mix

### Scenario 2: Large Files
- Upload 10MB+ resume PDF
- Should handle gracefully or show size limit error

### Scenario 3: Database Failure
- Stop PostgreSQL container: `docker-compose stop postgres`
- Try to login
- Should show appropriate error
- Restart: `docker-compose start postgres`

### Scenario 4: Network Issues
- Simulate slow network in browser dev tools
- Test if loading states appear
- Test if timeouts are handled

## 📝 Automated Testing Script

Create `test_api.py`:
```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_registration():
    data = {
        "email": "automated@test.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    assert response.status_code == 201
    print("✓ Registration passed")
    return response.json()["access_token"]

def test_login():
    data = {
        "email": "automated@test.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    assert response.status_code == 200
    print("✓ Login passed")
    return response.json()["access_token"]

if __name__ == "__main__":
    test_health()
    token = test_registration()
    test_login()
    print("\n✅ All tests passed!")
```

Run with: `python test_api.py`

## 📊 Success Criteria Validation

Based on your project proposal:

### Technical Metrics
- [x] **Functionality**: All key features implemented ✅
- [ ] **Performance**: API response < 10 seconds ⏱️
- [ ] **Accuracy**: 80%+ keyword identification 🎯
- [ ] **Deployment**: Successfully containerized 🐳

### User-Centric Metrics
- [ ] **Usability**: User completes analysis without guidance 👤
- [ ] **Actionability**: Clear, helpful suggestions 💡
- [ ] **Insightfulness**: Valuable dashboard insights 📈

## 🔄 Regression Testing

After any code changes, run this checklist:
1. Health endpoint works
2. Can register new user
3. Can login
4. Can analyze resume
5. Dashboard loads
6. No console errors in browser
7. Docker containers healthy

## 📞 Getting Help

If tests fail:
1. Check Docker logs: `docker-compose logs backend`
2. Verify database is running: `docker-compose ps`
3. Check network connectivity: `curl http://localhost:5000/api/health`
4. Review error messages carefully

## 🎓 Testing Report Template

For your project submission, document:

```markdown
# Testing Report

## Date: [DATE]
## Tester: [NAME]

### Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Success Rate: (Y/X * 100)%

### Functional Tests
| Test Case | Status | Notes |
|-----------|--------|-------|
| User Registration | ✅ | Works as expected |
| Resume Analysis | ✅ | < 10s response time |
| ... | ... | ... |

### Performance Tests
- Average API Response: Xms
- Peak Memory Usage: XMB
- Concurrent Users: X

### Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Status: Fixed/Open
   
### Recommendations
- [Recommendation 1]
- [Recommendation 2]
```