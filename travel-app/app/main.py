"""
Travel Recommendation API — Monolith entrypoint.

Single deployable FastAPI application. All layers (API, business logic,
data access, auth) live in this one codebase/process, satisfying the
monolith architecture constraint, while still being organized into
clean, independently-testable modules.

Run locally:
    uvicorn app.main:app --reload

Cross-platform accessibility: this is a stateless REST/JSON HTTP API, so
any client capable of making HTTP requests — a native mobile app, a
desktop app, or a browser-based single-page app — can consume it
identically. CORS is left open here; lock `allow_origins` down to your
real client origins before shipping to production.
"""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth_routes, destinations, itineraries, recommendations

app = FastAPI(
    title="Travel Recommendation API",
    description="Monolithic, cross-platform travel recommendation and itinerary planning service.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(destinations.router)
app.include_router(recommendations.router)
app.include_router(itineraries.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 422 with a clean, consistent error payload for bad input."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors(), exclude={"ctx"})},
    )


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
