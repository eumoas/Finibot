"""Model SQLAlchemy: Goal (Metas Financeiras)."""
import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @property
    def progress_pct(self) -> int:
        """Retorna progresso de 0 a 100."""
        if self.target_amount <= 0:
            return 100
        pct = (self.current_amount / self.target_amount) * 100
        return min(int(pct), 100)

    @property
    def progress_bar(self) -> str:
        """Barra de progresso visual em texto."""
        filled = self.progress_pct // 10
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}] {self.progress_pct}%"

    def __repr__(self) -> str:
        return f"<Goal {self.title!r} {self.progress_pct}%>"
