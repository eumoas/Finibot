"""Repository: Challenge — desafios e progresso do usuário."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.challenge import Challenge, UserChallenge


class ChallengeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_random_active(self, category: str | None = None) -> Challenge | None:
        from sqlalchemy import func as sql_func
        query = select(Challenge).where(Challenge.active == True)
        if category:
            query = query.where(Challenge.category == category)
        query = query.order_by(sql_func.random()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_challenge_this_week(
        self, user_id: uuid.UUID
    ) -> UserChallenge | None:
        iso_date = datetime.now(timezone.utc).isocalendar()
        result = await self.db.execute(
            select(UserChallenge).where(
                UserChallenge.user_id == user_id,
                UserChallenge.week_number == iso_date.week,
                UserChallenge.year == iso_date.year,
            )
        )
        return result.scalar_one_or_none()

    async def accept_challenge(
        self, user_id: uuid.UUID, challenge_id: uuid.UUID
    ) -> UserChallenge:
        iso_date = datetime.now(timezone.utc).isocalendar()
        uc = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            week_number=iso_date.week,
            year=iso_date.year,
        )
        self.db.add(uc)
        await self.db.commit()
        await self.db.refresh(uc)
        return uc

    async def complete_challenge(self, uc: UserChallenge) -> UserChallenge:
        uc.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(uc)
        return uc

    async def get_challenge_by_id(self, challenge_id: uuid.UUID) -> Challenge | None:
        result = await self.db.execute(
            select(Challenge).where(Challenge.id == challenge_id)
        )
        return result.scalar_one_or_none()
