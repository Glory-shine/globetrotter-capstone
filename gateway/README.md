# API Gateway

The single entry point for all client requests. Listens on port `8000` —
the same port and same paths the Phase 1 monolith used — so the frontend
needs no changes at all.

## What it does

1. Receives every request from the client (the frontend, or `curl`, or
   anything else).
2. Looks up which service owns the request's path (`app/routing.py`).
3. Forwards the request — method, headers (including `Authorization`),
   query string, body — unchanged, and streams the response back exactly
   as the upstream service returned it.

That's it. The gateway does **not** verify JWTs itself — each service
enforces its own auth independently, which avoids having two places that
could disagree about what a valid token looks like. If a downstream
service is unreachable, the gateway returns `503` rather than hanging.

## Routing table

| Path prefix | Routed to |
|---|---|
| `/register`, `/login`, `/users` | user-service |
| `/destinations`, `/recommendations`, `/fare`, `/comments` | recommendation-service |
| `/itineraries` | itinerary-service |

## Endpoints

| Method | Path | Description |
|---|---|---|
| ANY | `/{path}` | Proxied to the owning service |
| GET | `/health` | Pings the gateway itself **and** all three services, reports aggregate status |

## Environment variables

| Variable | Default |
|---|---|
| `USER_SERVICE_URL` | `http://localhost:8001` |
| `ITINERARY_SERVICE_URL` | `http://localhost:8002` |
| `RECOMMENDATION_SERVICE_URL` | `http://localhost:8003` |
| `REQUEST_TIMEOUT_SECONDS` | `15.0` |

In Docker Compose, these are set to the service names (`http://user-service:8001`,
etc.) and resolved via Compose's built-in DNS.

## Run standalone

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000 --reload
```

## Test

```bash
pytest
```

Tests cover the routing table directly and the proxy behavior against a
mocked `httpx` client (request forwarding, response relay, 503 on upstream
failure, 404 for unknown paths) — no real backend services need to be
running.
