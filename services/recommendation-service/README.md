# Recommendation Service

Owns the `destinations` table (`recommendation_db`) exclusively — Bafoussam's
real place catalog (chefferies, museums, markets, nature sites…), since
search and recommendations are both fundamentally reads over that data.

## Responsibilities

- Search/filter the destination catalog
- Generate personalized recommendations by reading the caller's
  preferences (user-service) and trip history (itinerary-service) over
  REST, then scoring destinations with a content-based engine
- Estimate moto-taxi/taxi fares between any two catalog destinations,
  using their real coordinates (`app/fare.py`)
- Consume `itinerary.created` events from RabbitMQ in the background

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/destinations` | Yes | Search/filter by `country` (commune), `tag`, `max_cost` (FCFA), `q` |
| GET | `/destinations/{id}` | Yes | Fetch one destination — used internally by itinerary-service |
| GET | `/recommendations` | Yes | Personalized picks; params `limit`, `max_budget` |
| GET | `/fare` | Yes | Moto/taxi fare estimate; params `from_id`, `to_id`, `mode` |
| GET | `/destinations/{id}/comments` | Yes | List reviews for a place, nested one level (replies) |
| POST | `/destinations/{id}/comments` | Yes | Post a review, or a reply via `parent_id` |
| POST | `/comments/{id}/like` | Yes | Toggle the caller's like on a comment |
| GET | `/health` | No | Liveness check |

The catalog is seeded automatically on first startup (`app/seed_data.py`)
with 12 real Bafoussam places, each with a short cultural anecdote — 
idempotent, so restarts don't duplicate rows. See that file's module
docstring for sourcing notes (Wikipedia, Wikivoyage, ORTOC, and Wikimedia
Commons for the hotlinked photos).

## Who this service calls

- **user-service**, synchronously, via `GET /users/me`, to read
  `preferences` (see `app/clients.py`).
- **itinerary-service**, synchronously, via `GET /itineraries`, to read
  the caller's trip history for recency-weighted scoring.

Both forward the caller's own bearer token and degrade to an empty result
if the downstream service is unavailable — a slightly-less-personalized
recommendation beats a failed request.

## Who calls this service

- **itinerary-service** calls `GET /destinations/{id}` before saving a new
  itinerary, to confirm the destination is real.
- **RabbitMQ**: this service consumes `itinerary.created` events published
  by itinerary-service (see `app/events_consumer.py`), in a background
  thread started from the app's lifespan handler. Reconnects quietly if
  the broker is down at startup.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:gloire@localhost:5432/recommendation_db` | `sqlite:///./dev.db` works for local hacking |
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | **Must match** user-service and itinerary-service |
| `USER_SERVICE_URL` | `http://localhost:8001` | |
| `ITINERARY_SERVICE_URL` | `http://localhost:8002` | |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | |
| `CONSUME_EVENTS` | `true` | Set `false` to disable the background consumer (used by the test suite) |

## Run standalone

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL=sqlite:///./dev.db CONSUME_EVENTS=false \
  .venv/bin/uvicorn app.main:app --port 8003 --reload
```

## Test

```bash
pytest
```

Tests mock the user-service/itinerary-service HTTP calls and disable the
RabbitMQ consumer via `CONSUME_EVENTS=false` (see `tests/conftest.py`), so
no other service or broker needs to be running.
