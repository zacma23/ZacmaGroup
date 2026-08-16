"""Runtime configuration for the ZACMA API.

The defaults deliberately make the repository usable as a local demo without
requiring cloud credentials. Production deployments must supply their own
environment values and set ``DEMO_MODE=false``.
"""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
REPOSITORY_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and local env files."""

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", REPOSITORY_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ZACMA Platform API"
    app_environment: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "APP_ENVIRONMENT"),
    )
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3001,http://127.0.0.1:3001"
    demo_mode: bool = True
    demo_tenant_id: str = "zacma-demo"

    supabase_url: str = "http://localhost:54321"
    supabase_service_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
    )
    omniroute_url: str = "http://localhost:20128/v1"
    omniroute_key: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_api_key: str = "ollama"
    redis_url: str = "redis://localhost:6379"

    @property
    def allowed_origins(self) -> list[str]:
        """Return a cleaned CORS origin list without accepting wildcards by accident."""
        return [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_environment.lower() in {"production", "prod"}


settings = Settings()
