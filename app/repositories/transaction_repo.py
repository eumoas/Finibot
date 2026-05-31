"""Repository: Transaction — entradas e saidas financeiras."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        transaction_type: str,
        amount: Decimal,
        category: str,
        description: str | None = None,
        happened_on: date | None = None,
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            category=category[:80] or "geral",
            description=description,
            happened_on=happened_on or date.today(),
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def list_by_period(
        self,
        user_id: uuid.UUID,
        start_on: date,
        end_before: date,
    ) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.happened_on >= start_on,
                Transaction.happened_on < end_before,
            )
            .order_by(Transaction.happened_on.desc(), Transaction.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_recent(self, user_id: uuid.UUID, limit: int = 8) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.happened_on.desc(), Transaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, transaction: Transaction, **kwargs) -> Transaction:
        for key, value in kwargs.items():
            setattr(transaction, key, value)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def delete_all_for_user(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(delete(Transaction).where(Transaction.user_id == user_id))
        await self.db.commit()
        return result.rowcount or 0
