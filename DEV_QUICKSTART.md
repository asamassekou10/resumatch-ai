## Developer quickstart (very short)

These commands are intended for quick onboarding on Windows (PowerShell). They focus on starting both backend and frontend locally using the repository defaults.

1) Start backend (from repo root):

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
alembic upgrade head
python app.py
```

2) In a separate terminal, start frontend:

```powershell
cd frontend
npm install
cp env.example .env.local
# edit .env.local if needed then:
npm start
```

3) Health check:

```powershell
Invoke-RestMethod http://localhost:5000/api/health
```

If you prefer containers, run:

```powershell
docker-compose up --build
```

That's it — open http://localhost:3000 for the frontend and http://localhost:5000/api for the backend.
