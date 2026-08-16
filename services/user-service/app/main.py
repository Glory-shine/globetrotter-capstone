"""
User Service — owns the `users` table (user_db) exclusively.

Responsibilities: registration, login, JWT issuance, and serving the
authenticated user's profile/preferences to other services.

Run standalone:
    uvicorn app.main:app --port 8001 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import auth_routes, users_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="GlobeTrotter — User Service",
    description="Owns user registration, login, profiles, and preferences.",
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


app.include_router(auth_routes.router)
app.include_router(users_routes.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors(), exclude={"ctx"})},
    )


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "user-service"}
