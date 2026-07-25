# GlobeTrotter Recommendation API

A monolithic, cross-platform travel recommendation and itinerary-planning 
backend. Single FastAPI codebase, flat-file JSON storage, stateless JWT auth.

## Architecture

```
travel-app/
├── app/
│   ├── main.py            # FastAPI app, router wiring, error handling
│   ├── auth.py             # Auth layer: password hashing, JWT issue/verify
│   ├── storage.py          # Data access layer: thread-safe atomic JSON I/O
│   ├── models.py           # Pydantic request/response schemas + validation
│   ├── recommendation.py   # Business logic: recommendation engine
│   ├── trip_planner.py     # Business logic: itinerary validation
│   ├── routers/
│   │   ├── auth_routes.py       # POST /register, POST /login
│   │   ├── destinations.py      # GET /destinations
│   │   ├── recommendations.py   # GET /recommendations
│   │   └── itineraries.py       # POST/GET /itineraries
│   └── data/db.json         # Flat-file datastore (seeded with mock destinations)
├── tests/                   # pytest suite
├── requirements.txt
└── pytest.ini
```

Everything ships as one deployable process (monolith), but is split into
clean modules by responsibility, so the API, business logic, data access,
and auth layers are independently testable.

**Cross-platform accessibility:** the app exposes a stateless JSON/REST API
over HTTP, so it can be called identically from a mobile app, a desktop
client, or a browser SPA — CORS is enabled and no server-side session state
is kept (auth is a bearer JWT the client stores itself).

## Setup

```bash
python -m venv globaltrotter
source globaltrotter/bin/activate   # Windows: globaltrotter\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Interactive API docs: `http://127.0.0.1:8000/docs`

## Configuration (environment variables)

| Variable                    | Default                         | Purpose                              |
|------------------------------|----------------------------------|---------------------------------------|
| `TRAVEL_APP_DB_PATH`         | `app/data/db.json`              | Path to the JSON datastore            |
| `TRAVEL_APP_SECRET_KEY`      | `dev-secret-change-in-production`| JWT signing secret — **set this in prod** |
| `TRAVEL_APP_TOKEN_EXPIRE_MIN`| `60`                             | JWT access token lifetime in minutes  |

## API

All endpoints except `/register`, `/login`, and `/health` require an
`Authorization: Bearer <token>` header.

| Method | Path              | Auth | Description                                  |
|--------|-------------------|------|-----------------------------------------------|
| POST   | `/register`       | No   | Create a user, returns a JWT                  |
| POST   | `/login`          | No   | Authenticate, returns a JWT                   |
| GET    | `/destinations`   | Yes  | Search/filter by `country`, `tag`, `max_cost`, `q` |
| GET    | `/recommendations`| Yes  | Personalized picks; params `limit`, `max_budget` |
| POST   | `/itineraries`    | Yes  | Create a validated itinerary                  |
| GET    | `/itineraries`    | Yes  | List the caller's own itineraries             |

### Example flow

```bash
# Register
curl -X POST localhost:8000/register -H "Content-Type: application/json" -d \
  '{"username":"jane","email":"jane@example.com","password":"password123","preferences":["beach","food"]}'

# -> {"access_token": "...", "token_type": "bearer"}

# Search destinations
curl localhost:8000/destinations?tag=beach -H "Authorization: Bearer <token>"

# Get recommendations
curl localhost:8000/recommendations -H "Authorization: Bearer <token>"

# Create an itinerary
curl -X POST localhost:8000/itineraries -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d \
  '{"title":"Bali trip","destination_id":"dest-001","start_date":"2026-09-01","end_date":"2026-09-07","items":[{"day":1,"activity":"Beach sunset"}]}'
```

## Data storage design

`app/storage.py` is the sole gateway to `db.json`. A `threading.RLock`
serializes access across FastAPI's threadpool, every write is atomic
(write-to-temp + `os.replace`), and all I/O is dispatched via
`asyncio.to_thread` so it never blocks the event loop. This prevents
corruption under concurrent requests without needing a real database.

## Testing

```bash
pytest
```

Each test gets an isolated, disposable JSON file (via `TRAVEL_APP_DB_PATH`
pointed at a pytest `tmp_path`), so tests never share or corrupt state.

## Git

```bash
git init
git add .
git commit -m "initial commit: globetrotter recommendation monolith"
```
