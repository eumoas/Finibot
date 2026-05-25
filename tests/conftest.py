"""conftest.py — fixtures globais e configuração para testes."""
import os
import pytest

# Define variáveis de ambiente mínimas ANTES de importar qualquer módulo do app
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token_000000:test_fake_token_for_testing")
os.environ.setdefault("LLM_API_KEY", "test_llm_key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://fini:test@localhost:5432/finibot_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ["DEBUG"] = "false"
