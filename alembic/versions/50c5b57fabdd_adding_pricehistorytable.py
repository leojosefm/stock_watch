"""adding pricehistorytable

Revision ID: 50c5b57fabdd
Revises: 6274de6c4612
Create Date: 2024-10-14 00:43:49.921001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50c5b57fabdd'
down_revision = '6274de6c4612'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('open', sa.Numeric(), nullable=True),
        sa.Column('high', sa.Numeric(), nullable=True),
        sa.Column('low', sa.Numeric(), nullable=True),
        sa.Column('close', sa.Numeric(), nullable=True),
        sa.Column('adj_close', sa.Numeric(), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.Column('RSI', sa.Numeric(), nullable=True),
        sa.Column('ticker', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('price_history')
