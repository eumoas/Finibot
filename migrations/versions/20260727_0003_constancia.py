"""replace streak with cumulative constancia counters

Revision ID: 20260727_0003
Revises: 20260524_0002
Create Date: 2026-07-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260727_0003"
down_revision = "20260524_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("constancia_total", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "users", sa.Column("constancia_mes_atual", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("users", sa.Column("constancia_mes_referencia", sa.Date(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "constancia_marcos_atingidos",
            postgresql.ARRAY(sa.Integer()),
            nullable=False,
            server_default="{}",
        ),
    )

    # O streak existente vira o total acumulado — nenhum progresso é perdido.
    op.execute("UPDATE users SET constancia_total = streak_days")
    op.execute(
        "UPDATE users SET constancia_marcos_atingidos = "
        "(SELECT array_agg(m) FROM unnest(ARRAY[7, 15, 30, 60]) AS m WHERE m <= streak_days) "
        "WHERE streak_days >= 7"
    )

    op.drop_column("users", "streak_days")


def downgrade() -> None:
    op.add_column("users", sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"))
    op.execute("UPDATE users SET streak_days = constancia_total")

    op.drop_column("users", "constancia_marcos_atingidos")
    op.drop_column("users", "constancia_mes_referencia")
    op.drop_column("users", "constancia_mes_atual")
    op.drop_column("users", "constancia_total")
