"""Change watchlist table schema

Revision ID: 6080cab90fc3
Revises: d07779acaf04
Create Date: 2024-10-12 15:23:16.442631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6080cab90fc3'
down_revision = 'd07779acaf04'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('watchlist')


def downgrade():
    op.create_table('watchlist',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('company_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('ticker_symbol', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('rsi_threshold', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='companies_pkey')
    )
