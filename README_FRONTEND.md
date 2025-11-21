## Frontend — ResumeAnalyzer AI

This file contains focused instructions for developing and running the frontend locally.

Prerequisites
- Node.js 18+
- npm or yarn

Quick local setup (Windows PowerShell)

```powershell
cd frontend
npm install
cp env.example .env.local
# edit .env.local and set REACT_APP_API_URL to http://localhost:5000 or your backend URL
npm start
```

Run tests and lint

```powershell
cd frontend
npm test
npm run lint
```

Build for production

```powershell
cd frontend
npm run build
# Serve `build/` with a static server or include in your chosen deployment pipeline
```

Notes
- The frontend is bootstrapped with Create React App. See `frontend/src` for components and `frontend/src/services/api.js` for the API wrapper.
- For styling adjustments check `tailwind` or `App.css` depending on repo usage.
