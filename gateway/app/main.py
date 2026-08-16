"""
API Gateway — the single entry point for all client requests.

Deliberately "dumb": it does not verify JWTs itself (each service enforces
its own auth independently — a core microservices tenet, and it avoids
two places that can disagree about what a valid token looks like). Its
only job is:

  1. Receive every request on one public port (8000, same as the old
     monolith).
  2. Look up which service owns that path (see app/routing.py).
  3. Forward the request byte-for-byte (method, headers, query string,
     body) and stream the response back unchanged.

Run standalone:
    uvicorn app.main:app --port 8000 --reload
"""

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routing import resolve_target

app = FastAPI(
    title="GlobeTrotter — API Gateway",
    description="Single entry point routing client requests to the User, Itinerary, and Recommendation services.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Port de ton Frontend
    allow_credentials=True,
    allow_methods=["*"],  # S'assure de permettre POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

_client = httpx.AsyncClient(timeout=settings.request_timeout_seconds)

# Headers that must not be blindly forwarded between hops (hop-by-hop
# headers per RFC 7230, plus content-length which httpx recalculates).
_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "host",
}


@app.get("/health", tags=["system"])
async def health_check():
    """Pings every downstream service so `GET /health` gives a full
    picture of system health, not just the gateway's own liveness."""
    targets = {
        "user-service": settings.user_service_url,
        "itinerary-service": settings.itinerary_service_url,
        "recommendation-service": settings.recommendation_service_url,
    }
    statuses = {}
    for name, base_url in targets.items():
        try:
            resp = await _client.get(f"{base_url}/health", timeout=3.0)
            statuses[name] = "ok" if resp.status_code == 200 else f"unhealthy ({resp.status_code})"
        except httpx.RequestError:
            statuses[name] = "unreachable"

    overall = "ok" if all(v == "ok" for v in statuses.values()) else "degraded"
    return {"status": overall, "gateway": "ok", "services": statuses}


# NOTE: this catch-all must be registered LAST — Starlette matches routes in
# registration order, and its `{full_path:path}` converter would otherwise
# swallow /health and any other specific route declared after it.
@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy(full_path: str, request: Request):
    path = f"/{full_path}"
    target_base = resolve_target(path)

    if target_base is None:
        return Response(
            content=f'{{"detail":"No service is registered for path \'{path}\'"}}',
            status_code=404,
            media_type="application/json",
        )

    body = await request.body()
    forward_headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS}

    try:
        upstream_response = await _client.request(
            method=request.method,
            url=f"{target_base}{path}",
            params=request.query_params,
            headers=forward_headers,
            content=body,
        )
    except httpx.RequestError:
        return Response(
            content='{"detail":"Upstream service is unavailable. Please try again shortly."}',
            status_code=503,
            media_type="application/json",
        )

    response_headers = {
        k: v for k, v in upstream_response.headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
