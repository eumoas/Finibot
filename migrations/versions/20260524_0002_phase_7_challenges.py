"""phase 7 challenge codes and yearly user challenges

Revision ID: 20260524_0002
Revises: 20260524_0001
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa


revision = "20260524_0002"
down_revision = "20260524_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("challenges", sa.Column("code", sa.String(length=10), nullable=True))
    op.create_unique_constraint("uq_challenges_code", "challenges", ["code"])

    op.add_column("user_challenges", sa.Column("year", sa.Integer(), nullable=True))
    op.execute("UPDATE user_challenges SET year = EXTRACT(ISOYEAR FROM accepted_at)::integer WHERE year IS NULL")
    op.alter_column("user_challenges", "year", nullable=False)

    op.drop_constraint("uq_user_challenge_week", "user_challenges", type_="unique")
    op.create_unique_constraint(
        "uq_user_challenge_week_year",
        "user_challenges",
        ["user_id", "challenge_id", "week_number", "year"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_challenge_week_year", "user_challenges", type_="unique")
    op.create_unique_constraint(
        "uq_user_challenge_week",
        "user_challenges",
        ["user_id", "challenge_id", "week_number"],
    )
    op.drop_column("user_challenges", "year")
    op.drop_constraint("uq_challenges_code", "challenges", type_="unique")
    op.drop_column("challenges", "code")
