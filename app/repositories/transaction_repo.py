"""Repository: Transaction — entradas e saidas financeiras."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy import select
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
