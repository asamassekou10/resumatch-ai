# How to Run the Application

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **PostgreSQL** database running (or use SQLite for testing)
4. **Redis** (optional, for rate limiting)

## Quick Start

### Step 1: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the `backend` directory with:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost/resumeanalyzer
   # Or for SQLite (simpler for testing):
   # DATABASE_URL=sqlite:///resumeanalyzer.db
   
   # Google Gemini API (for AI features)
   GEMINI_API_KEY=your-gemini-api-key
   
   # JWT Secret
   JWT_SECRET_KEY=your-jwt-secret-key
   
   # Optional: Redis for rate limiting
   REDIS_URL=redis://localhost:6379/0
   ```

6. **Initialize database:**
   ```bash
   flask db upgrade
   # Or if first time:
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. **Run the backend:**
   ```bash
   python app.py
   # Or:
   flask run
   ```
   
   Backend should start on `http://localhost:5000`

### Step 2: Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `frontend` directory:
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   ```

4. **Run the frontend:**
   ```bash
   npm start
   ```
   
   Frontend should start on `http://localhost:3000`

## Testing the Changes

Once both servers are running:

1. **Open your browser** and go to `http://localhost:3000`

2. **Test the new features:**
   - **Login/Register** to test authenticated user experience
   - **Go to Analyze page** - You should see the new beautiful design matching the guest page
   - **Upload a resume** and job description to test the improved scoring system
   - **Check the dashboard** - Should show onboarding for new users
   - **View analysis results** - Should show realistic scores (not 0% when there are matches)

## Troubleshooting

### Backend Issues

- **Database connection error:** Make sure PostgreSQL is running, or switch to SQLite
- **Import errors:** Make sure virtual environment is activated and all packages are installed
- **Port already in use:** Change the port in `app.py` or kill the process using port 5000

### Frontend Issues

- **Port 3000 in use:** React will automatically try port 3001, 3002, etc.
- **API connection error:** Make sure backend is running and `REACT_APP_API_URL` is correct
- **Module not found:** Run `npm install` again

### Common Commands

**Backend:**
```bash
# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Mac/Linux)
source venv/bin/activate

# Run backend
python app.py

# Check if backend is running
curl http://localhost:5000/api/health
```

**Frontend:**
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Quick Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access `http://localhost:3000`
- [ ] Can register/login
- [ ] Analyze page shows new design (matches guest page)
- [ ] Can upload resume and job description
- [ ] Analysis completes and shows realistic scores
- [ ] Dashboard shows onboarding for new users
- [ ] Analysis results page looks good (not blue background)
