"""
Travel Recommendation API — Monolith entrypoint.

Single deployable FastAPI application. All layers (API, business logic,
data access, auth) live in this one codebase/process, satisfying the
monolith architecture constraint, while still being organized into
clean, independently-testable modules.

Run locally:
    uvicorn app.main:app --reload
"""

import os

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

allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://globetrotter-travelassistant-production-2185.up.railway.app")
allowed_origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
