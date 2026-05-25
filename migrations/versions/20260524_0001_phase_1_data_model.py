"""phase 1 data model additions

Revision ID: 20260524_0001
Revises:
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa


revision = "20260524_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("income_source", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("monthly_income", sa.Numeric(10, 2), nullable=True))
    op.add_column("users", sa.Column("last_entry_date", sa.Date(), nullable=True))
    op.add_column(
        "users",
        sa.Column("report_opt_out", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "transactions",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transactions", "updated_at")
    op.drop_column("users", "report_opt_out")
    op.drop_column("users", "last_entry_date")
    op.drop_column("users", "monthly_income")
    op.drop_column("users", "income_source")
