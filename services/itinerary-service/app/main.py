"""
Itinerary Service — owns the `itineraries` table (itinerary_db) exclusively.

Responsibilities: create and list travel itineraries for the authenticated
user. Validates destinations by calling recommendation-service over REST,
and publishes an `itinerary.created` event to RabbitMQ on every successful
create.

Run standalone:
    uvicorn app.main:app --port 8002 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import itineraries_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="GlobeTrotter — Itinerary Service",
    description="Owns trip itineraries: creation, scheduling, retrieval, and sharing.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(itineraries_routes.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors(), exclude={"ctx"})},
    )


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "itinerary-service"}
