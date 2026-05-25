"""Repository: MessageLog — histórico de conversa."""
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message_log import MessageLog
from app.core.config import settings


class MessageLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent(self, user_id: uuid.UUID) -> list[MessageLog]:
        """Retorna as últimas N mensagens para contexto do LLM."""
        result = await self.db.execute(
            select(MessageLog)
            .where(MessageLog.user_id == user_id)
            .order_by(MessageLog.created_at.desc())
            .limit(settings.context_window_size)
        )
        msgs = list(result.scalars().all())
        return list(reversed(msgs))  # ordem cronológica

    async def add(self, user_id: uuid.UUID, role: str, content: str) -> MessageLog:
        log = MessageLog(user_id=user_id, role=role, content=content)
        self.db.add(log)
        await self.db.commit()
        return log

    async def purge_old(self, days: int = 90):
        """Remove mensagens com mais de N dias (job de limpeza)."""
        from datetime import timedelta, datetime, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        await self.db.execute(
            delete(MessageLog).where(MessageLog.created_at < cutoff)
        )
        await self.db.commit()
