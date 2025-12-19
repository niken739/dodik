# Frontend (Lab7)

This is a minimal Vite + React + TypeScript scaffold for the lab7 frontend.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

Set the backend API URL in `.env` (default points to `http://localhost:5000/api`).

Routes:
- `/login` — login page
- `/register` — registration page
- `/dashboard` — protected dashboard (basic)
- any other — 404

The app uses fetch to call the backend endpoints:
- `POST /api/auth/registration`
- `POST /api/auth/login`
- `GET /api/health_check`
