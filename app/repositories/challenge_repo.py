"""Repository: Challenge — desafios e progresso do usuário."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.challenge import Challenge, UserChallenge


def _weekly_index(year: int, week_number: int, count: int) -> int:
    """Índice determinístico de rotação — mesma semana sempre gera o mesmo desafio.

    Substitui sorteio aleatório: o valor do desafio da semana não pode depender
    de acaso (critério de design contra recompensa em razão variável).
    """
    return (year * 53 + week_number) % count


class ChallengeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_weekly_challenge(self, category: str | None = None) -> Challenge | None:
        query = select(Challenge).where(Challenge.active == True)
        if category:
            query = query.where(Challenge.category == category)
        query = query.order_by(Challenge.code)
        result = await self.db.execute(query)
        challenges = result.scalars().all()
        if not challenges:
            return None
        iso_date = datetime.now(timezone.utc).isocalendar()
        index = _weekly_index(iso_date.year, iso_date.week, len(challenges))
        return challenges[index]

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
