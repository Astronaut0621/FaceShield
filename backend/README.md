# FaceShield Backend

FastAPI backend for the FaceShield prototype. The default database is local SQLite for quick development. To connect openGauss, set `DATABASE_URL` to a PostgreSQL-compatible SQLAlchemy URL.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```text
GET http://localhost:8000/api/health
```

API docs:

```text
http://localhost:8000/docs
```

## openGauss Configuration

```text
DATABASE_URL=postgresql+psycopg2://gaussdb:your_password@localhost:5432/faceshield
```

## Initial APIs

- `GET /api/health`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/detect`
- `GET /api/records`
- `GET /api/records/{id}`
- `GET /api/model-version`

Compatibility APIs are still available for earlier frontend experiments:

- `POST /api/files/upload`
- `POST /api/detection/start`
- `POST /api/detection/upload-and-detect`
- `GET /api/history/list`
- `GET /api/history/{task_id}`

All business APIs except `/api/health` and `/api/auth/login` require:

```text
Authorization: Bearer <access_token>
```

Demo account:

```text
username: demo
password: demo123456
```

## Backend Layers

```text
api/           HTTP routing and request dependency wiring
services/      Use-case orchestration
repositories/  SQLAlchemy data access
domain/        Business enums, policies, and application exceptions
serializers/   ORM-to-response mapping
models/        SQLAlchemy table models
schemas/       Pydantic request/response schemas
algorithm/     Stable detector adapter interface
core/          App factory, config, database, logging, exception handlers
utils/         Small cross-cutting helpers
```

Keep new features aligned with these boundaries: routes should not query the database directly, services should not build HTTP responses, and repositories should not know about FastAPI.
