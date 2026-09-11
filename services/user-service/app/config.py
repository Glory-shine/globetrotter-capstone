"""
Centralized configuration for the User Service.

Every setting is overridable via environment variable (see docker-compose.yml
and .env.example at the repo root). Nothing is hardcoded so the same image
can run in dev, CI, or prod with different env files.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "user-service"

    # Postgres — this service owns the "users" table exclusively. No other
    # service is allowed to connect to this database directly (see README).
    database_url: str = "postgresql+psycopg://postgres:gloire@localhost:5432/user_db"

    # Shared JWT signing secret. Must be identical across every service so
    # tokens minted here are independently verifiable by itinerary-service
    # and recommendation-service without a round-trip back to this service.
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


settings = Settings()
