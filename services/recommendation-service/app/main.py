"""
Recommendation Service — owns the `destinations` catalog (recommendation_db)
exclusively.

Responsibilities: destination search/filter, personalized recommendations.
Reads user preferences from user-service and trip history from
itinerary-service over synchronous REST, and consumes `itinerary.created`
events from RabbitMQ in the background.

Run standalone:
    uvicorn app.main:app --port 8003 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.events_consumer import start_consumer_in_background, stop_consumer
from app.routers import comments_routes, destinations_routes, fare_routes, recommendations_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_consumer_in_background()
    yield
    stop_consumer()


app = FastAPI(
    title="GlobeTrotter — Recommendation Service",
    description="Owns the destination catalog and generates personalized recommendations.",
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

app.include_router(destinations_routes.router)
app.include_router(recommendations_routes.router)
app.include_router(fare_routes.router)
app.include_router(comments_routes.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors(), exclude={"ctx"})},
    )


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "recommendation-service"}
