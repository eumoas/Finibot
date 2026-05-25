"""Model SQLAlchemy: User."""
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    income_source: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # mesada | estagio | freelas | trabalho | outros
    monthly_income: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    profile_type: Mapped[str] = mapped_column(
        String(30), default="iniciante"
    )  # iniciante | em_desenvolvimento | avancado

    points: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_entry_date: Mapped[Optional[date]] = mapped_column(Date)
    report_opt_out: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Estado de conversa (flow atual)
    current_flow: Mapped[Optional[str]] = mapped_column(String(50))
    flow_step: Mapped[Optional[str]] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} {self.first_name!r} lv{self.level}>"
