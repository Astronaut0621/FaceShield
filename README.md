# FaceShield

FaceShield is a prototype system for AI face forgery detection. This repository contains a backend-first scaffold with minimal frontend, algorithm, and database modules.

## Structure

```text
backend/   FastAPI service, SQLAlchemy models, file upload, mock detection, history APIs
frontend/  Minimal Vue 3 + Vite client scaffold
database/  openGauss-compatible SQL scripts
design.md  Original project design document
```

## Backend Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

By default, the backend uses `backend/faceshield.db`. Set `DATABASE_URL` to use openGauss.

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`.

Frontend framework notes live in `frontend/README.md`. The current frontend is intentionally a scaffold: it has feature folders, shared components, stores, composables, and service boundaries ready for expansion.

## Algorithm Framework

The backend algorithm package now exposes a stable `predict_image(image_path)` entry backed by contracts, engine registry, and pipeline stages. It still uses a mock engine only. See `backend/app/algorithm/README.md`.

## Database Framework

Database framework notes live in `database/README.md`. The database folder now includes migration, seed, schema, docs, and script placeholders without implementing concrete provisioning.

## Demo Login

The development spec requires authenticated business APIs. The backend seeds a demo account on startup:

```text
username: demo
password: demo123456
```

Public APIs: `/api/health`, `/api/auth/login`. Detection and records APIs require a bearer token.
