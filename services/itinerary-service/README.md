# Itinerary Service

Owns the `itineraries` table (`itinerary_db`) exclusively.

## Responsibilities

- Create and list travel itineraries for the authenticated user
- Validate trip data: destination must exist, day-by-day items must fit
  within the trip's date span
- Publish an `itinerary.created` event to RabbitMQ on every successful create

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/itineraries` | Yes | Create a validated itinerary |
| GET | `/itineraries` | Yes | List the caller's own itineraries |
| GET | `/health` | No | Liveness check |

## Auth

This service has **no local user store**. It verifies JWTs locally against
the shared `JWT_SECRET_KEY` and reads `sub` as the caller's user id — no
network call back to user-service is needed just to authenticate a request.

## Who this service calls

- **recommendation-service**, synchronously, via `GET /destinations/{id}`,
  to confirm `destination_id` is real before saving (see `app/clients.py`).
  Forwards the caller's own bearer token. If recommendation-service is
  unreachable, this returns `503` rather than silently accepting an
  unverifiable destination.
- **RabbitMQ**, asynchronously, publishing `itinerary.created` to the
  `globetrotter.events` topic exchange (see `app/events.py`). Best-effort:
  a broker outage logs a warning but never fails the request.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:gloire@localhost:5432/itinerary_db` | `sqlite:///./dev.db` works for local hacking |
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | **Must match** user-service and recommendation-service |
| `RECOMMENDATION_SERVICE_URL` | `http://localhost:8003` | |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | |
| `EVENTS_EXCHANGE` | `globetrotter.events` | |

## Run standalone

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL=sqlite:///./dev.db .venv/bin/uvicorn app.main:app --port 8002 --reload
```

## Test

```bash
pytest
```

Tests mock the recommendation-service HTTP call and the RabbitMQ publish
(see `tests/test_itineraries.py`), so no other service or broker needs to
be running.
