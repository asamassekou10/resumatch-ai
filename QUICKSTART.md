# 🚀 Quick Start Guide - AI Resume Optimizer

Get your AI Resume Optimizer up and running in **under 10 minutes**!

## ⚡ Super Quick Start (Docker - Recommended)

If you have Docker installed, this is the fastest way:

```bash
# 1. Create project directory
mkdir ai-resume-optimizer && cd ai-resume-optimizer
mkdir backend && cd backend

# 2. Create all required files (copy from artifacts)
# - app.py
# - ai_processor.py
# - requirements.txt
# - Dockerfile
# - docker-compose.yml

# 3. Start everything
docker-compose up --build

# 4. Wait for startup (about 2 minutes first time)
# Backend will be at: http://localhost:5000
```

That's it! Your backend is running. Now skip to [Frontend Setup](#frontend-setup).

## 📋 Prerequisites

Choose one setup method:

### Option A: Docker (Easiest)
- Docker Desktop installed ([Get Docker](https://www.docker.com/get-started))
- That's it!

### Option B: Manual Setup
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+
- npm or yarn

## 🔧 Detailed Setup

### Step 1: Project Structure

Create this folder structure:

```
ai-resume-optimizer/
├── backend/
│   ├── app.py
│   ├── ai_processor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend/
    └── (will be created with create-react-app)
```

### Step 2: Backend Setup

#### Option A: Using Docker 🐳

1. **Navigate to backend folder:**
```bash
cd backend
```

2. **Create all files** (copy from the artifacts I provided):
   - app.py
   - ai_processor.py
   - requirements.txt
   - Dockerfile
   - docker-compose.yml

3. **Start Docker containers:**
```bash
docker-compose up --build
```

4. **Verify backend is running:**
```bash
curl http://localhost:5000/api/health
```

Expected response: `{"status": "healthy", ...}`

#### Option B: Manual Setup 🛠️

1. **Install Python dependencies:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Setup PostgreSQL:**
```bash
# Install PostgreSQL (if not installed)
# Ubuntu: sudo apt-get install postgresql
# Mac: brew install postgresql
# Windows: Download from postgresql.org

# Create database
createdb resume_optimizer
```

3. **Set environment variables:**
```bash
export DATABASE_URL="postgresql://localhost/resume_optimizer"
export JWT_SECRET_KEY="your-secret-key-change-me"
```

4. **Run the backend:**
```bash
python app.py
```

### Step 3: Frontend Setup

1. **Create React app:**
```bash
cd ..  # Back to project root
npx create-react-app frontend
cd frontend
```

2. **Install dependencies:**
```bash
npm install recharts
```

3. **Replace App.jsx:**
- Delete `src/App.js`
- Create `src/App.jsx`
- Copy the React component code from the artifact

4. **Update Tailwind CSS:**

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

Or install Tailwind properly:
```bash
npm install -D tailwindcss
npx tailwindcss init
```

5. **Start frontend:**
```bash
npm start
```

The app will open at `http://localhost:3000`

## ✅ Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:5000/api/health
```
✅ Should return: `{"status": "healthy", "message": "AI Resume Optimizer API is running"}`

### 2. Check Database
```bash
# If using Docker:
docker-compose exec postgres psql -U postgres -d resume_optimizer -c "\dt"

# Manual setup:
psql resume_optimizer -c "\dt"
```
✅ Should show tables: `user`, `analysis`

### 3. Check Frontend
Open browser to `http://localhost:3000`
✅ Should see login page

### 4. Test Registration
- Click "Sign Up"
- Enter email and password
- Click "Sign Up" button
✅ Should redirect to dashboard

### 5. Test Analysis
- Click "New Analysis"
- Upload a resume (PDF, DOCX, or TXT)
- Paste a job description
- Click "Analyze Resume"
✅ Should show match score and keywords

## 🎯 First Time Usage

### Create Your First Analysis

1. **Register an account:**
   - Email: your@email.com
   - Password: (secure password)

2. **Create a test resume** (test_resume.txt):
```
JANE DOE
Software Engineer

SKILLS
Python, Flask, PostgreSQL, Docker, Git, React

EXPERIENCE
Software Engineer at Tech Co
- Built web applications using Python and Flask
- Worked with PostgreSQL databases
- Deployed applications using Docker
```

3. **Use this test job description:**
```
Looking for a Python Developer with Flask experience.
Must know PostgreSQL and Docker. React is a plus.
```

4. **Expected Results:**
   - Match Score: ~70-80%
   - Keywords Found: python, flask, postgresql, docker
   - Keywords Missing: (varies)

## 🐛 Troubleshooting

### Problem: Backend won't start

**Docker:**
```bash
docker-compose down -v
docker-compose up --build
docker-compose logs backend
```

**Manual:**
```bash
# Check if port 5000 is available
lsof -i :5000
# Kill process if needed
kill -9 <PID>
```

### Problem: Frontend can't connect to backend

1. Check backend is running:
```bash
curl http://localhost:5000/api/health
```

2. Check CORS configuration in `app.py`:
```python
CORS(app)  # Should be present
```

3. Verify API_URL in `App.jsx`:
```javascript
const API_URL = 'http://localhost:5000/api';
```

### Problem: PDF parsing fails

**Solution:**
- Use TXT format instead
- Ensure PDF has selectable text (not scanned image)
- Try a different PDF

### Problem: Database connection error

**Docker:**
```bash
docker-compose restart postgres
```

**Manual:**
```bash
# Check PostgreSQL is running
pg_isready
# Start if needed
sudo service postgresql start
```

### Problem: spaCy model not found

```bash
python -m spacy download en_core_web_sm
```

### Problem: Port already in use

**Change backend port:**

In `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Use 5001 instead of 5000
```

Update frontend `API_URL` accordingly.

## 📝 Common Commands

### Docker Commands
```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Clean everything
docker-compose down -v
```

### Backend Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run server
python app.py

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Frontend Commands
```bash
# Start dev server
npm start

# Build for production
npm run build

# Install package
npm install package-name
```

## 🎓 Next Steps

After setup:

1. ✅ Read [README.md](README.md) for full documentation
2. ✅ Check [TESTING.md](TESTING.md) for testing guide
3. ✅ Review [test_data.md](test_data.md) for sample data
4. ✅ Test with your own resume
5. ✅ Customize features as needed

## 💡 Pro Tips

1. **Use test data:** Start with provided sample resumes and job descriptions
2. **Check logs:** Always check `docker-compose logs` if something fails
3. **Clear browser cache:** If frontend acts weird, clear cache or use incognito
4. **Database reset:** `docker-compose down -v` removes all data (fresh start)
5. **API testing:** Use Postman or curl to test API directly

## 📊 Performance Optimization

If analysis is slow:

1. **Reduce TF-IDF features** in `ai_processor.py`:
```python
vectorizer = TfidfVectorizer(max_features=15)  # Reduce from 20
```

2. **Cache spaCy model** (load once at startup)

3. **Use smaller spaCy model**:
```bash
python -m spacy download en_core_web_sm  # Already smallest
```

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change JWT_SECRET_KEY
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up proper firewall rules
- [ ] Use strong database password
- [ ] Enable rate limiting
- [ ] Add input validation
- [ ] Review CORS settings

## 🌐 Accessing from Other Devices

To test on phone or another computer:

1. **Find your IP address:**
```bash
# Linux/Mac
ifconfig | grep inet
# Windows
ipconfig
```

2. **Update frontend API_URL:**
```javascript
const API_URL = 'http://192.168.1.X:5000/api';  // Use your IP
```

3. **Allow connections in Docker:**

Already configured in docker-compose.yml with `0.0.0.0:5000`

## 📞 Getting Help

If you're stuck:

1. **Check logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Verify services:**
   ```bash
   docker-compose ps
   ```

3. **Test API directly:**
   ```bash
   curl -v http://localhost:5000/api/health
   ```

4. **Check this guide again** - most issues are covered here

5. **Review error messages** - they usually tell you what's wrong

## 🎉 You're Ready!

If you've completed the setup:
- ✅ Backend running at http://localhost:5000
- ✅ Frontend running at http://localhost:3000
- ✅ Database connected
- ✅ Can register and login
- ✅ Can analyze resumes

**Congratulations! Your AI Resume Optimizer is ready to use! 🚀**

Now start optimizing resumes and tracking your career progress!