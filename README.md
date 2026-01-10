# ResumeAnalyzer AI - AI-Powered Resume Analysis & Job Matching Platform

[![CI](https://github.com/asamassekou10/resumatch-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/asamassekou10/resumatch-ai/actions)
[![pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://github.com/asamassekou10/resumatch-ai)
[![coverage](https://img.shields.io/badge/coverage-%3E=80%25-brightgreen.svg)](https://github.com/asamassekou10/resumatch-ai)

**Live Application**: [https://resumeanalyzerai.com](https://resumeanalyzerai.com)

An enterprise-grade AI resume optimization platform that helps job seekers land their dream jobs through intelligent resume analysis, ATS optimization, and personalized job matching. Built with production-ready Flask backend and React frontend, featuring advanced machine learning algorithms, NLP-powered skill extraction, and real-time market intelligence.

ResumeAnalyzer AI streamlines the job search process by providing data-driven insights, identifying resume gaps, and connecting candidates with the most relevant opportunities.

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
- **Email Verification**: Resend integration for secure account activation

### User Experience
- **Interactive Dashboard**: Historical analysis tracking with visualizations
- **PDF Resume Upload**: Secure file processing and storage
- **Email Delivery**: Results sent via Resend (on-demand)
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
   - `RESEND_API_KEY` - Resend API key for email delivery
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
   # Configure admin accounts via environment variables or database
   cd /app && python update_admin_passwords.py
   ```

4. **Sample Data** (for demo/presentation):
   ```bash
   # Insert 5 sample job postings
   cd /app && python insert_sample_jobs.py
   ```

### Admin Access

Admin dashboard provides comprehensive system diagnostics, user management, and analytics.

Access admin diagnostics at: `/api/v1/admin/diagnostics/full-diagnostic`

## Configuration

Edit environment variables in `docker-compose.yml` or in a local `.env` file. Important variables include `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, and `RESEND_API_KEY` for email. See `SETUP_GUIDE.md` for more details.

## 🏗️ Architecture & Technical Implementation

ResumeAnalyzer AI demonstrates enterprise-level software engineering practices:

- **AI/ML Integration**: Google Gemini 1.5 for intelligent resume feedback, spaCy for NLP, scikit-learn for semantic job matching
- **Full-Stack Architecture**: RESTful API with Flask + modern React SPA with responsive design
- **Database Design**: PostgreSQL with 28+ tables, optimized indexing, and proper relationships
- **Cloud Infrastructure**: Production deployment on Render with automated CI/CD pipelines
- **Security & Authentication**: JWT tokens, OAuth 2.0 (Google), bcrypt password hashing, CSRF protection, input validation
- **Software Engineering**: Comprehensive test coverage (pytest), Docker containerization, Git version control
- **Data Visualization**: Interactive dashboards with historical analysis tracking
- **Scalability**: Rate limiting, caching, async processing, connection pooling
- **Monitoring & Logging**: Structured logging, performance metrics, error tracking

## 🙏 Acknowledgments

Built with powerful open-source technologies:
- **Google Gemini** for advanced AI capabilities
- **spaCy** for natural language processing
- **scikit-learn** for machine learning algorithms
- **Flask** and **React** communities for robust frameworks
- **PostgreSQL** for reliable data storage

## 📧 Support

For technical support or questions:
1. Check the comprehensive documentation in `SETUP_GUIDE.md`
2. Review API documentation for integration details
3. Check application logs: `docker-compose logs backend`
4. Visit the help center at [resumeanalyzerai.com/help](https://resumeanalyzerai.com/help)

## 📄 License

This project is proprietary software. All rights reserved.

For licensing inquiries, please contact the development team.
