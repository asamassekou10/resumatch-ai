## Backend — ResumeAnalyzer AI

This file contains focused instructions for developing and running the backend API locally.

Prerequisites
- Python 3.11+
- PostgreSQL (or use Docker)

Quick local setup (Windows PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# configure .env or set environment variables (see SETUP_GUIDE.md)
alembic upgrade head
python app.py
```

Run tests

```powershell
cd backend
pytest -q
```

Notes
- Check `alembic/` for DB migrations
- Environment variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, `SENDGRID_API_KEY`
- Use the `logs/` directory to inspect backend logs if enabled

If you want a containerized backend only (no frontend):

```powershell
docker build -t resumatch-backend ./backend
docker run --env-file .env -p 5000:5000 resumatch-backend
```

For detailed configuration and production checklist see `README_V2.md` and `SETUP_GUIDE.md`.
