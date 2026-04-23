# Personal Freelance Intelligence Dashboard (PFID)

Production-ready private intelligence dashboard for freelance jobs, contracts, and bug bounty opportunities.

## Stack

- Backend: Python 3.11, FastAPI, APScheduler, Redis, PostgreSQL
- Frontend: Next.js, React, TailwindCSS, WebSocket
- Scoring: Rule-based match/risk/region scoring + bid suggestions

## Features

- Multi-source collectors (API, RSS, passive scraping placeholders, manual placeholders)
- Normalized job model persisted in PostgreSQL
- Weighted keyword filtering and scoring
- Risk scoring for suspicious posts
- Region boosts for Japan, UAE, New Zealand
- Real-time UI updates via WebSocket
- Platform interval/enable controls in settings panel
- Browser notifications + sound alert for high-value jobs

## Project Structure

- backend/app/main.py
- backend/app/api
- backend/app/core
- backend/app/models
- backend/app/services
- backend/app/collectors
- backend/app/scoring
- backend/app/scheduler
- frontend/app
- frontend/components
- frontend/services
- frontend/hooks

## Run Locally (Docker)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Run Locally (No Docker, Windows)

Backend:

```powershell
cd "d:\Saved Games\backend"
"d:/Saved Games/.venv/Scripts/python.exe" -m pip install -r requirements.txt
"d:/Saved Games/.venv/Scripts/python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd "d:\Saved Games\frontend"
npm.cmd install
npm.cmd run dev
```

Notes:

- Local backend defaults to SQLite (`sqlite+aiosqlite:///./pfid.db`) so it starts without PostgreSQL.
- Docker deployment still uses PostgreSQL as the primary database.

## Localhost-Only Defaults

`docker-compose.yml` maps all service ports to `127.0.0.1` only.

## Cloud Deployment (VPS)

1. Build and run backend + frontend containers.
2. Put Nginx in front of services.
3. Use `nginx.example.conf` as baseline.
4. Lock inbound firewall rules and use TLS.

## Cloud Deployment (Netlify + Render)

### Frontend on Netlify

1. Push repository to GitHub.
2. In Netlify, import project from Git.
3. Netlify uses `netlify.toml` automatically (`base=frontend`, `build=npm run build`).
4. Add environment variable:
	- `NEXT_PUBLIC_API_BASE=https://<your-render-backend>.onrender.com`
5. Deploy site.

### Backend on Render

1. In Render Dashboard, create Blueprint from this repository.
2. Use `render.yaml` at repository root.
3. Render provisions:
	- `pfid-backend` (FastAPI web service)
	- `pfid-postgres` (PostgreSQL)
	- `pfid-redis` (Redis)
4. Update `CORS_ORIGINS` in Render env vars with your Netlify URL.
5. Deploy and verify:
	- `https://<your-render-backend>.onrender.com/api/health/`

Notes:

- Render often provides `postgres://...`; backend config auto-normalizes this to SQLAlchemy `postgresql+psycopg://...`.
- First request on low-cost Render plans can be slower due to cold start.

## Testing

Backend tests include:

- Unit test for scoring engine
- Collector test with mocked RemoteOK API

Run in backend container or local venv:

```bash
cd backend
pytest -q
```

## Notes on Scraping Sources

Some platforms restrict automation. The scraping collectors are intentionally conservative and low-frequency with graceful failure. Expand selectors carefully and respect each platform's terms.
