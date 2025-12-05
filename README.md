# ResuMatch AI - AI-Powered Resume Analysis & Job Matching Platform

[![CI](https://github.com/asamassekou10/resumatch-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/asamassekou10/resumatch-ai/actions)
[![pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://github.com/asamassekou10/resumatch-ai)
[![coverage](https://img.shields.io/badge/coverage-%3E=80%25-brightgreen.svg)](https://github.com/asamassekou10/resumatch-ai)

**Live Application**: [https://resumeanalyzerai.com](https://resumeanalyzerai.com)

A production-grade AI resume analysis and job matching platform (Flask backend + React frontend). It analyzes resumes against job descriptions using machine learning, extracts skills with NLP, provides AI-powered feedback, and offers intelligent job matching with market intelligence insights.

This repository contains the complete full-stack application: backend API, frontend React app, PostgreSQL database, comprehensive tests, and production deployment configuration.

## ✨ Key Features

### Resume Analysis & Optimization
- **AI-Powered Analysis**: Gemini 1.5 integration for intelligent resume feedback
- **Match Scoring**: TF-IDF and cosine similarity algorithms for job-resume matching
- **Keyword Extraction**: spaCy NLP for skills and keyword identification
- **Gap Analysis**: Identifies missing skills and provides improvement suggestions
- **Cover Letter Generation**: AI-generated personalized cover letters

### Job Matching & Market Intelligence
- **Semantic Job Matching**: ML-based job recommendations using TF-IDF vectorization
- **Market Trends Analysis**: Real-time job market insights and salary data
- **Skills Demand Tracking**: Identify in-demand skills across industries
- **Salary Intelligence**: Competitive salary ranges for target roles
- **Top Companies**: Discover leading employers in your field

### Authentication & User Management
- **JWT Authentication**: Secure token-based authentication
- **Google OAuth Integration**: One-click social login
- **Guest Access**: Try features without registration (with limits)
- **Admin Dashboard**: User management and system diagnostics
- **Email Verification**: SendGrid integration for secure account activation

### User Experience
- **Interactive Dashboard**: Historical analysis tracking with visualizations
- **PDF Resume Upload**: Secure file processing and storage
- **Email Delivery**: Results sent via SendGrid
- **Responsive Design**: Mobile-friendly React UI
- **Real-time Feedback**: Interactive skill verification system

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0 (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **AI/ML**: Google Gemini 1.5, spaCy NLP, scikit-learn (TF-IDF, cosine similarity)
- **Authentication**: Flask-JWT-Extended, Google OAuth 2.0
- **File Processing**: PyPDF2, python-docx
- **Testing**: pytest, pytest-cov
- **Deployment**: Gunicorn WSGI server, Docker

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: CSS3, Responsive Design
- **Deployment**: Nginx, Docker

### Infrastructure
- **Hosting**: Render.com (auto-deploy from GitHub)
- **Database**: Render PostgreSQL
- **Domain**: resumeanalyzerai.com
- **CI/CD**: GitHub Actions

## 🚀 Quickstart (Docker)

Requirements: Docker & Docker Compose

1. Build and start services:

```bash
docker-compose up --build
```

2. Access the application:
   - Backend API: http://localhost:5000
   - Frontend: http://localhost:3000

For manual local setup without Docker, see `SETUP_GUIDE.md` or the `backend/` and `frontend/` README files.

## Repo layout

```
.
├── backend/            # Flask API, models, AI processing, tests, migrations
├── frontend/           # React app (Create React App)
├── migrations/         # Alembic DB migrations
├── tests/              # Backend pytest tests
├── docker-compose.yml
├── README_V2.md        # More detailed production README
└── SETUP_GUIDE.md      # Configuration and setup notes
```

Quick links:

- Backend README: `README_BACKEND.md`
- Frontend README: `README_FRONTEND.md`
- Developer quickstart: `DEV_QUICKSTART.md`

## Backend — local dev

1. Create and activate a virtualenv

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Configure environment variables (copy `.env.example` if present)

3. Initialize the database and run migrations

```powershell
# create DB (Postgres)
# adjust DATABASE_URL as needed
alembic upgrade head
```

4. Run the app

```powershell
python app.py
```

## Frontend — local dev

```powershell
cd frontend
npm install
cp env.example .env.local
# edit .env.local to point REACT_APP_API_URL to the backend
npm start
```

## Testing

- Backend tests: run from `backend/` using pytest

```powershell
cd backend
pytest -q
```

- Frontend tests: run from `frontend/`

```powershell
cd frontend
npm test
```

## 🚀 Deployment

### Production Environment

**Current Deployment**: Render.com (auto-deploy from GitHub main branch)

- **Frontend**: [https://resumeanalyzerai.com](https://resumeanalyzerai.com)
- **Backend API**: [https://resumatch-backend-7qdb.onrender.com](https://resumatch-backend-7qdb.onrender.com)
- **Database**: PostgreSQL (Render managed)

### Local Deployment

```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Backend will be at http://localhost:5000
# Frontend will be at http://localhost:3000
```

### Production Setup Checklist

1. **Environment Variables** (set in Render dashboard):
   - `DATABASE_URL` - PostgreSQL connection string
   - `JWT_SECRET_KEY` - Secure random key for JWT
   - `GEMINI_API_KEY` - Google Gemini API key
   - `SENDGRID_API_KEY` - SendGrid for email
   - `GOOGLE_CLIENT_ID` - Google OAuth
   - `GOOGLE_CLIENT_SECRET` - Google OAuth
   - `ADZUNA_APP_ID` - Adzuna job API (optional)
   - `ADZUNA_APP_KEY` - Adzuna job API (optional)

2. **Database Initialization**:
   ```bash
   # In Render shell
   cd /app && python final_db_init.py
   ```

3. **Admin Account Setup**:
   ```bash
   # Create/update admin accounts
   cd /app && python update_admin_passwords.py
   ```

4. **Sample Data** (for demo/presentation):
   ```bash
   # Insert 5 sample job postings
   cd /app && python insert_sample_jobs.py
   ```

### Admin Credentials

Two admin accounts are pre-configured:
- **Admin 1**: alhassane.samassekou@gmail.com / AdminResuMatch2024!
- **Admin 2**: sitaram.ayyagari@project.review / ProfessorReview2024!

Access admin diagnostics at: `/api/v1/admin/diagnostics/full-diagnostic`

## Configuration

Edit environment variables in `docker-compose.yml` or in a local `.env` file. Important variables include `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, and email/sendgrid settings. See `SETUP_GUIDE.md` for more details.

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- scikit-learn for ML algorithms
- Flask and React communities

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the API documentation
3. Check Docker logs: `docker-compose logs backend`

## 🎓 Academic Context

**Course**: ITAI 2277 – Artificial Intelligence
**Institution**: HOUSTON COMMUNITY COLLEGE
**Project Phase**: Complete Full-Stack AI Application

This project demonstrates mastery of:
- **AI/ML Integration**: Gemini 1.5 for resume feedback, spaCy for NLP, scikit-learn for job matching
- **Full-Stack Development**: Flask REST API + React SPA architecture
- **Database Design**: PostgreSQL with 28+ tables, proper indexing and relationships
- **Cloud Deployment**: Production-ready deployment on Render with CI/CD
- **Authentication & Security**: JWT tokens, OAuth 2.0, password hashing, input validation
- **Software Engineering**: Testing (pytest), version control (Git), Docker containerization
- **Data Visualization**: Interactive dashboards and analytics
- **Ethical AI**: Transparent scoring, user feedback loops, bias consideration
