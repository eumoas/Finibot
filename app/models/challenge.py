"""Models SQLAlchemy: Challenge e UserChallenge."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer,
    String, Text, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    points_reward: Mapped[int] = mapped_column(Integer, default=50)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # orcamento | poupanca | credito | investimento | consumo | matematica
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    # facil | medio | dificil
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Challenge {self.title!r} {self.difficulty}>"


class UserChallenge(Base):
    __tablename__ = "user_challenges"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", "week_number", "year", name="uq_user_challenge_week_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)  # ISO week
    year: Mapped[int] = mapped_column(Integer, nullable=False)  # ISO year
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
