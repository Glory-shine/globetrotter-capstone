from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "recommendation-service"

    # Postgres — this service owns the "destinations" table exclusively
    # (the catalog itself, not user data — it's the natural owner since
    # search and recommendations are both destination-catalog reads).
    database_url: str = "postgresql+psycopg://postgres:gloire@localhost:5432/recommendation_db"

    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"

    # Synchronous REST call targets.
    user_service_url: str = "http://localhost:8001"
    itinerary_service_url: str = "http://localhost:8002"

    # Asynchronous event consumption (best-effort — see app/events_consumer.py).
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    events_exchange: str = "globetrotter.events"
    events_queue: str = "recommendation.itinerary_events"
    consume_events: bool = True


settings = Settings()
