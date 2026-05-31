"""Repository: Goal — metas financeiras do usuário."""
from __future__ import annotations

import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[Goal]:
        result = await self.db.execute(
            select(Goal)
            .where(Goal.user_id == user_id, Goal.completed == False)
            .order_by(Goal.created_at.desc())
            .limit(5)
        )
        return list(result.scalars().all())

    async def get_active_by_id(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal | None:
        result = await self.db.execute(
            select(Goal).where(
                Goal.id == goal_id,
                Goal.user_id == user_id,
                Goal.completed == False,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        target_amount: float,
        deadline=None,
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            deadline=deadline,
        )
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def update_progress(self, goal: Goal, amount: float) -> Goal:
        goal.current_amount = Decimal(str(amount))
        if goal.current_amount >= goal.target_amount:
            goal.completed = True
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def add_progress(self, goal: Goal, amount: Decimal) -> Goal:
        goal.current_amount = Decimal(str(goal.current_amount or 0)) + amount
        if goal.current_amount >= goal.target_amount:
            goal.current_amount = goal.target_amount
            goal.completed = True
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def complete(self, goal: Goal) -> Goal:
        goal.current_amount = goal.target_amount
        goal.completed = True
        await self.db.commit()
        await self.db.refresh(goal)
        return goal
