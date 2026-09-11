# User Service

Owns the `users` table (`user_db`) exclusively. No other service is
permitted to query this database directly.

## Responsibilities

- User registration and login
- Password hashing (salted PBKDF2-HMAC-SHA256 — stdlib only, no native deps)
- Issuing JWTs signed with `JWT_SECRET_KEY` (must match the other services)
- Serving the authenticated user's profile + preferences to callers,
  **including other services** calling on the user's behalf

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create a user, returns a JWT |
| POST | `/login` | No | Authenticate, returns a JWT |
| GET | `/users/me` | Yes | Current user's profile + preferences |
| GET | `/health` | No | Liveness check |

Interactive docs at `/docs` once running.

## Who calls this service

- The frontend, via the gateway, for register/login.
- **recommendation-service** calls `GET /users/me` synchronously,
  forwarding the caller's own bearer token, to read `preferences` when
  building recommendations (see `app/routers/recommendations_routes.py`
  in that service).

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:gloire@localhost:5432/user_db` | Set to `sqlite:///./dev.db` for local hacking without Postgres |
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | **Must match** itinerary-service and recommendation-service |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRE_MINUTES` | `60` | |

## Run standalone

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL=sqlite:///./dev.db .venv/bin/uvicorn app.main:app --port 8001 --reload
```

## Test

```bash
pytest
```
