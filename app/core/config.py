"""Configurações centrais via pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str
    telegram_secret_token: str = "dev-secret"

    # LLM (primary — qualquer API OpenAI-compatible: xAI, Groq, OpenRouter...)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.x.ai/v1/chat/completions"
    llm_model: str = "grok-3-mini"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "gemma3:4b"
    max_tokens_response: int = 350

    # Database
    database_url: str = "postgresql+asyncpg://fini:finidev123@localhost:5432/finibot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    admin_api_key: str = "dev-admin-key"

    # Limites
    max_messages_per_hour: int = 30
    context_window_size: int = 10

    # Webhook (produção)
    webhook_url: str = ""

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def use_webhook(self) -> bool:
        return self.is_production and bool(self.webhook_url)

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
