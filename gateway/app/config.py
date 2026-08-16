from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    user_service_url: str = "http://localhost:8001"
    itinerary_service_url: str = "http://localhost:8002"
    recommendation_service_url: str = "http://localhost:8003"

    request_timeout_seconds: float = 15.0


settings = Settings()
