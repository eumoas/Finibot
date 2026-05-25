"""Session Service — contexto de conversa em Redis (janela deslizante)."""
from __future__ import annotations

import json
import logging
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

KEY_PATTERN = "session:{telegram_id}"
TTL_SECONDS = 3600  # 1 hora de inatividade reseta sessão
RATE_KEY = "rate:{telegram_id}"
RATE_TTL = 3600
PENDING_TRANSACTION_KEY = "pending_transaction:{telegram_id}"


class SessionService:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    def _key(self, telegram_id: int) -> str:
        return f"session:{telegram_id}"

    def _rate_key(self, telegram_id: int) -> str:
        return f"rate:{telegram_id}"

    def _pending_transaction_key(self, telegram_id: int) -> str:
        return f"pending_transaction:{telegram_id}"

    async def get_context(self, telegram_id: int) -> list[dict]:
        """Retorna últimas N mensagens para o LLM."""
        raw = await self.redis.get(self._key(telegram_id))
        if not raw:
            return []
        messages = json.loads(raw)
        return messages[-settings.context_window_size :]

    async def add_message(self, telegram_id: int, role: str, content: str):
        """Adiciona mensagem mantendo janela deslizante."""
        key = self._key(telegram_id)
        raw = await self.redis.get(key)
        messages = json.loads(raw) if raw else []
        messages.append({"role": role, "content": content})
        # Mantém apenas 2x o window para não crescer infinitamente
        messages = messages[-(settings.context_window_size * 2) :]
        await self.redis.setex(key, TTL_SECONDS, json.dumps(messages))

    async def clear(self, telegram_id: int):
        await self.redis.delete(self._key(telegram_id))

    async def set_pending_transaction(self, telegram_id: int, payload: dict):
        await self.redis.setex(
            self._pending_transaction_key(telegram_id),
            TTL_SECONDS,
            json.dumps(payload),
        )

    async def get_pending_transaction(self, telegram_id: int) -> dict | None:
        raw = await self.redis.get(self._pending_transaction_key(telegram_id))
        if not raw:
            return None
        return json.loads(raw)

    async def clear_pending_transaction(self, telegram_id: int):
        await self.redis.delete(self._pending_transaction_key(telegram_id))

    async def check_rate_limit(self, telegram_id: int) -> bool:
        """Retorna True se dentro do limite, False se passou do limite."""
        key = self._rate_key(telegram_id)
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, RATE_TTL)
        return count <= settings.max_messages_per_hour
