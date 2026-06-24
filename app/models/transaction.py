"""Model SQLAlchemy: Transaction (controle financeiro)."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

# Categorias válidas (v2 — capitalizadas com acento)
EXPENSE_CATEGORIES = [
    "Alimentação", "Transporte", "Streaming", "Cinema e Shows",
    "Rolês e Encontros", "Games", "Vestuário", "Beleza",
    "Educação", "Saúde", "Compras", "Viagem", "Presentes",
    "Moradia", "Lazer", "Outros",
]
INCOME_CATEGORIES = [
    "Mesada", "Salário", "Estágio", "Freelas", "Presentes", "Bolsa/Auxílio", "Outros",
]


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="Outros")
    description: Mapped[Optional[str]] = mapped_column(Text)
    happened_on: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def is_income(self) -> bool:
        return self.transaction_type == "income"

    @property
    def signed_amount(self) -> Decimal:
        return self.amount if self.is_income else -self.amount

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_type} {self.amount} {self.category!r}>"
