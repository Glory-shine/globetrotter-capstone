from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "itinerary-service"

    # Postgres — this service owns the "itineraries" table exclusively.
    database_url: str = "postgresql+psycopg://postgres:gloire@localhost:5432/itinerary_db"

    # Must match user-service's signing secret — JWTs are verified locally
    # here, no synchronous call back to user-service is needed just to
    # authenticate a request.
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"

    # Synchronous REST call target: recommendation-service owns destination
    # data, so itinerary-service asks it "does this destination exist?"
    # before persisting a new itinerary.
    recommendation_service_url: str = "http://localhost:8003"

    # Asynchronous event publishing (best-effort — see app/events.py).
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    events_exchange: str = "globetrotter.events"


settings = Settings()
