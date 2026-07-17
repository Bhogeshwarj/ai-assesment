from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Tea Packaging Optimization Platform"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://tea:tea@localhost:5432/tea_packaging"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
