"""Runtime configuration for the ZACMA API.

The defaults deliberately make the repository usable as a local demo without
requiring cloud credentials. Production deployments must supply their own
environment values and set ``DEMO_MODE=false``.
"""

from pathlib import Path
from typing import Optional

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
    cors_origins: str = "https://zacmagroup.com,https://www.zacmagroup.com,https://api.zacmagroup.com,http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    demo_mode: bool = True
    demo_tenant_id: str = "zacma-demo"

    # Database & Supabase
    supabase_url: str = "http://localhost:54321"
    supabase_service_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
    )
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/zacma",
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
    )

    # Payment Configuration (Multi-Provider Platform)
    payment_environment: str = Field(
        default="test",
        validation_alias=AliasChoices("PAYMENT_ENV", "PAYMENT_ENVIRONMENT"),
    )
    default_payment_methods: str = "Chapa,CBE,TeleBirr,Awash,Abyssinia"
    chapa_base_url: str = "https://api.chapa.co/v1"
    chapa_secret_key: str = Field(default="", validation_alias=AliasChoices("CHAPA_SECRET_KEY", "CHAPA_KEY"))
    chapa_public_key: str = Field(default="", validation_alias=AliasChoices("CHAPA_PUBLIC_KEY"))
    chapa_webhook_secret: str = Field(default="", validation_alias=AliasChoices("CHAPA_WEBHOOK_SECRET"))
    chapa_callback_url: str = Field(
        default="http://127.0.0.1:8000/api/v1/payments/webhooks/chapa",
        validation_alias=AliasChoices("CHAPA_CALLBACK_URL"),
    )
    chapa_return_url: str = Field(
        default="http://localhost:3000/portal?payment_status=success",
        validation_alias=AliasChoices("CHAPA_RETURN_URL"),
    )

    # Storage & Uploads
    storage_upload_dir: str = str(BACKEND_DIR / "uploads")

    # Email / Notification
    mail_from: str = "noreply@zacma.com"
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # AI & Multi-Provider Gateway (Gemini, OpenAI, Anthropic, Grok, Ollama)
    ai_provider: str = Field(default="gemini", validation_alias=AliasChoices("AI_PROVIDER"))
    ai_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("AI_MODEL"))
    gemini_api_key: str = Field(default="", validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    omniroute_url: str = "http://localhost:20128/v1"
    omniroute_key: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_api_key: str = "ollama"
    redis_url: str = "redis://localhost:6379"

    # Google Cloud Platform & Firebase Infrastructure
    gcp_project_id: Optional[str] = Field(default=None, validation_alias=AliasChoices("GCP_PROJECT_ID", "GOOGLE_CLOUD_PROJECT"))
    firebase_project_id: Optional[str] = Field(default=None, validation_alias=AliasChoices("FIREBASE_PROJECT_ID"))
    storage_provider: str = Field(default="local", validation_alias=AliasChoices("STORAGE_PROVIDER"))
    gcp_storage_bucket: Optional[str] = Field(default=None, validation_alias=AliasChoices("GCP_STORAGE_BUCKET", "GCS_BUCKET"))
    gcp_pubsub_enabled: bool = Field(default=False, validation_alias=AliasChoices("GCP_PUBSUB_ENABLED"))
    gcp_pubsub_topic: str = Field(default="zacma-platform-events", validation_alias=AliasChoices("GCP_PUBSUB_TOPIC"))
    automation_engine: str = Field(default="google_workflows", validation_alias=AliasChoices("AUTOMATION_ENGINE"))

    # Automation & Integration Engine
    automation_webhook_url: Optional[str] = Field(default=None, validation_alias=AliasChoices("AUTOMATION_WEBHOOK_URL", "N8N_WEBHOOK_URL"))
    automation_webhook_secret: str = Field(default="zacma_automation_secret_key", validation_alias=AliasChoices("AUTOMATION_WEBHOOK_SECRET"))

    # Telegram Bot Integration
    telegram_bot_token: str = Field(
        default="8903928763:AAFrzueg5A4RU3u3Y64YhflZwhJ5dKXZjNw",
        validation_alias=AliasChoices("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN"),
    )

    # Security
    secret_key: str = "secret-jwt-signing-key-override-this"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    @property
    def allowed_origins(self) -> list[str]:
        """Return a cleaned CORS origin list without accepting wildcards by accident."""
        return [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def payment_methods_list(self) -> list[str]:
        """Return the list of configured payment methods."""
        return [m.strip() for m in self.default_payment_methods.split(",") if m.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_environment.lower() in {"production", "prod"}


settings = Settings()
