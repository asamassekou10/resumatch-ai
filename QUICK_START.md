# Quick Start Guide

## Option 1: Use the PowerShell Scripts (Easiest)

### Terminal 1 - Backend:
```powershell
.\start-backend.ps1
```

### Terminal 2 - Frontend:
```powershell
.\start-frontend.ps1
```

## Option 2: Manual Commands

### Terminal 1 - Start Backend:

```powershell
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Create .env file if it doesn't exist (see below for content)
# Then start server
python app.py
```

### Terminal 2 - Start Frontend:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Create .env file if it doesn't exist
# Add: REACT_APP_API_URL=http://localhost:5000/api

# Start server
npm start
```

## Environment Setup

### Backend .env file (backend/.env):
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///resumeanalyzer.db
JWT_SECRET_KEY=dev-jwt-secret-key
GEMINI_API_KEY=your-gemini-api-key-here
```

**Note:** For quick testing, you can use SQLite (as shown above). For production, use PostgreSQL.

### Frontend .env file (frontend/.env):
```env
REACT_APP_API_URL=http://localhost:5000/api
```

## First Time Setup

1. **Backend:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   # Create .env file (see above)
   flask db upgrade  # Initialize database
   python app.py
   ```

2. **Frontend:**
   ```powershell
   cd frontend
   npm install
   # Create .env file (see above)
   npm start
   ```

## Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000/api

## Testing Your Changes

1. Open http://localhost:3000 in your browser
2. Register/Login to test authenticated features
3. Go to Analyze page - should see the new beautiful design
4. Upload a resume and job description
5. Check that scores are realistic (not 0% when there are matches)
6. Check dashboard for new user onboarding

## Troubleshooting

- **Backend won't start:** Make sure virtual environment is activated and all dependencies are installed
- **Frontend won't start:** Make sure you're in the frontend directory and ran `npm install`
- **API connection errors:** Make sure backend is running on port 5000
- **Database errors:** For quick testing, use SQLite (see .env example above)
