"""added_unique_constraint_watchlist

Revision ID: 0476a183ae44
Revises: 50c5b57fabdd
Create Date: 2024-10-16 13:11:51.703629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0476a183ae44'
down_revision = '50c5b57fabdd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('watchlist', sa.Column('rsi_triggered', sa.Numeric(), nullable=True))

    op.create_unique_constraint(
        '_user_ticker_rsi_trigger_uc', 
        'watchlist', 
        ['user_id', 'ticker_symbol', 'rsi_threshold', 'triggered']
    )


def downgrade():
    op.drop_constraint('_user_ticker_rsi_trigger_uc', 'watchlist', type_='unique')
    op.drop_column('watchlist', 'rsi_triggered')
