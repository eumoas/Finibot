"""Repository: User — CRUD e queries de usuário."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_seen_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_or_create(
        self, telegram_id: int, username: str | None = None, first_name: str | None = None
    ) -> tuple[User, bool]:
        """Retorna (user, created)."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.last_seen_at = datetime.now(timezone.utc)
            await self.db.commit()
            return user, False
        user = await self.create(telegram_id, username, first_name)
        return user, True

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def add_points(self, user: User, points: int) -> User:
        user.points += points
        # Recalcula nível
        user.level = self._calculate_level(user.points)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    @staticmethod
    def _calculate_level(points: int) -> int:
        if points >= 2000:
            return 5
        if points >= 1000:
            return 4
        if points >= 500:
            return 3
        if points >= 200:
            return 2
        return 1
