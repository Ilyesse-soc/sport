from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Sport Coach API"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+psycopg://sport:sport@localhost:5432/sport"

    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "sport-backend"
    jwt_audience: str = "sport-clients"
    access_token_expire_minutes: int = 60

    allowed_origins: str = "http://localhost:3000"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    max_upload_size_mb: int = 10
    max_request_body_mb: int = 2
    max_query_length: int = 1000
    max_prompt_chars: int = 4000
    max_page_size: int = 100

    enable_local_auth: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
