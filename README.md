# ResumeAnalyzer AI (resumatch-ai)

[![CI](https://github.com/asamassekou10/resumatch-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/asamassekou10/resumatch-ai/actions)
[![pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://github.com/asamassekou10/resumatch-ai)
[![coverage](https://img.shields.io/badge/coverage-%3E=80%25-brightgreen.svg)](https://github.com/asamassekou10/resumatch-ai)

A production-oriented AI resume analysis platform (Flask backend + React frontend). It analyzes resumes against job descriptions, extracts keywords and skills, and provides AI-powered feedback and resume/cover-letter generation.

This repository contains the backend API, frontend app, tests, and deployment artifacts. For more detailed guides see `SETUP_GUIDE.md`, `QUICKSTART.md`, and other docs in the repo.

## Key features

- Resume analysis and match scoring
- Keyword extraction and missing-skill highlighting
- AI feedback and resume optimization (Gemini integration)
- Cover letter generation
- User accounts with JWT auth and Google OAuth
- Email delivery of results (SendGrid)
- Dashboard with history and visualizations
- Dockerized for easy deployment

## Quickstart (recommended: Docker)

Requirements: Docker & Docker Compose

1. Build and start services:

```powershell
docker-compose up --build
```

2. Backend API will be available at http://localhost:5000
3. Frontend will be available at http://localhost:3000

For a manual local setup, see `SETUP_GUIDE.md` or the `backend/` and `frontend/` directories for platform-specific instructions.

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

## Deployment

- Docker Compose (recommended): `docker-compose up --build`
- For production, use a WSGI server (gunicorn) and a production-grade web server or container platform. See `README_V2.md` for deployment checklist and CI/CD notes.

## Configuration

Edit environment variables in `docker-compose.yml` or in a local `.env` file. Important variables include `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, and email/sendgrid settings. See `SETUP_GUIDE.md` for more details.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Run tests and linters locally
4. Open a PR with a clear description and tested changes

## License & attribution

This project is provided for educational purposes. See the repository license for details.

---

If you'd like, I can also:
- Add CI badges to the top of this README
- Create a concise `README_FRONTEND.md` and `README_BACKEND.md` with step-by-step commands
- Run backend tests and report results now

Next step: I'll run backend tests (quick) if you'd like — tell me to proceed.
Course: ITAI 2277 – Artificial Intelligence

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

This project fulfills the requirements for Phase 01 of the AI course project, demonstrating:
- Full-stack development skills
- AI/ML integration
- Database design
- User authentication
- Data visualization
- Ethical AI considerations

---

**Note**: Remember to change the `JWT_SECRET_KEY` before deploying to production!