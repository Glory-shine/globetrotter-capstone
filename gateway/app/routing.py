"""
Path → service routing table.

The whole point of this table is backward compatibility: the frontend was
built against the Phase 1 monolith's paths (`/register`, `/login`,
`/destinations`, `/recommendations`, `/itineraries`) and a base URL of
`http://127.0.0.1:8000`. By keeping the gateway on port 8000 and mapping
these exact paths to the right microservice, the frontend needs **zero
code changes** — it still just talks to one base URL and never learns
that three separate services exist behind it.
"""

from app.config import settings

# Ordered so more specific prefixes can be added later without reordering
# concerns — exact-path and prefix matches are both supported.
ROUTES = [
    ("/register", settings.user_service_url),
    ("/login", settings.user_service_url),
    ("/users", settings.user_service_url),
    ("/destinations", settings.recommendation_service_url),
    ("/favorites", settings.recommendation_service_url),
    ("/recommendations", settings.recommendation_service_url),
    ("/fare", settings.recommendation_service_url),
    ("/comments", settings.recommendation_service_url),
    ("/itineraries", settings.itinerary_service_url),
]


def resolve_target(path: str) -> str | None:
    """Return the base URL of the service that owns `path`, or None if no
    route matches (the gateway will answer with 404 in that case)."""
    for prefix, target in ROUTES:
        if path == prefix or path.startswith(prefix + "/"):
            return target
    return None
