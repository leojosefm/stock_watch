"""add pegy_ratio_latest_v view

Revision ID: 3fd63a465f16
Revises: 
Create Date: 2026-07-12 12:14:24.857507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fd63a465f16'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS pegy_ratio_latest_v")
    op.execute("""
    create or replace view pegy_ratio_latest_v as
    with ranked as (
        select ph.*, row_number() over (
            partition by ticker
            order by (pegy_ratio is not null) desc, date desc
        ) rn
        from public.price_history ph
    )
    select id, date, open, high, low, close, adj_close, volume, "RSI", ticker, pegy_ratio
    from ranked
    where rn = 1
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS pegy_ratio_latest_v")