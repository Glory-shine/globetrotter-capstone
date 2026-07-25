# GlobeTrotter — Travel Assistant (Frontend)

A Vue 3 + Vite + Tailwind CSS frontend for the GlobeTrotter FastAPI backend.
No build config beyond what's checked in — clone, install, run.

## Design concept

The visual language borrows from travel documents themselves: destination
cards are cut like **luggage tags** (a dashed perforation with die-cut
grommet holes separating the description from the cost/climate stub),
and itineraries render as a **dotted flight-path timeline** with day
markers, like a route map. A deep "night-flight" navy, warm boarding-pass
paper, coral accent, and a gold "passport stamp" motif carry that through
consistently. Display type is Fraunces (a characterful serif for
headlines), body text is Plus Jakarta Sans, and dates/prices/tickets use
JetBrains Mono to read like printed ticket data.

## Setup

Requires Node 18+.

```bash
npm install
npm run dev        # http://localhost:5173
```

Make sure the FastAPI backend is running first (see the backend's own
README) — by default the app expects it at `http://127.0.0.1:8000`.

To point at a different backend, copy `.env.example` to `.env` and set
`VITE_API_BASE_URL`. Everything else reads from `src/config.js`.

## Project structure

```
src/
├── config.js              # API_BASE_URL + shared constants — single source of truth
├── router.js               # Routes + auth guards (protects destinations/recommendations/itineraries)
├── api/
│   ├── client.js            # Axios instance: attaches JWT, turns HTTP errors into toasts
│   ├── auth.js               # register / login
│   ├── destinations.js       # GET /destinations
│   ├── recommendations.js    # GET /recommendations
│   └── itineraries.js        # POST/GET /itineraries
├── stores/
│   ├── auth.js               # JWT + username, persisted to localStorage
│   ├── toast.js               # Global toast notification queue
│   └── destinationsCache.js   # id → destination lookup, shared across views
├── components/               # DestinationCard, ItineraryForm, ItineraryCard, LoginForm, etc.
└── views/                    # One view per route/page
tests/                       # Vitest + @vue/test-utils
```

## Auth & route protection

On login/register, the JWT is stored in `localStorage` and attached to
every request automatically via an Axios request interceptor — no manual
header wiring anywhere else in the app. `router.js` runs a
`beforeEach` guard that redirects unauthenticated visitors away from
`/destinations`, `/recommendations`, and `/itineraries`, and keeps
signed-in users off `/login`/`/register`.

## Error handling

A single Axios response interceptor in `api/client.js` catches every
backend error and converts it into a toast: 401 clears the session and
returns to login, 422 renders the validation messages field-by-field,
409/404/400 show the backend's own `detail` text, and network failures
get a friendly "can't reach the server" message.

## Testing

```bash
npm test
```

15 Vitest + Vue Test Utils cases cover:
- `LoginForm` — captures input, blocks submit and shows inline errors for
  short usernames/passwords, emits a clean payload once valid.
- `DestinationCard` — renders mock destination JSON (name, tags, cost,
  description) and emits a `plan` event.
- `ItineraryCard` — renders a mock itinerary + destination, sorts
  day-by-day items correctly, and handles missing-destination/empty-days
  states.

## Build

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally
```
