"""New view added

Revision ID: c6d2a3303cf1
Revises: 
Create Date: 2026-03-01 12:25:49.474041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6d2a3303cf1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    create or replace view pegy_ratio_latest_v as
    with ranked as (
    select ph.*, row_number() over(partition by ticker order by (pegy_ratio IS NOT NULL) desc, date desc) rn from public.price_history ph  
    )
    select id,date,open,high,low,close,adj_close,volume,"RSI",ticker,pegy_ratio from ranked where rn = 1 
    """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS pegy_ratio_latest_v")
