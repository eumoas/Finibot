"""Repository: Goal — metas financeiras do usuário."""
import uuid
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
        from decimal import Decimal
        goal.current_amount = Decimal(str(amount))
        if goal.current_amount >= goal.target_amount:
            goal.completed = True
        await self.db.commit()
        await self.db.refresh(goal)
        return goal
