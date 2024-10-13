"""add column triggered to watchlist

Revision ID: 8da83cd1ae4a
Revises: 6080cab90fc3
Create Date: 2024-10-13 00:38:09.872134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8da83cd1ae4a'
down_revision = '6080cab90fc3'
branch_labels = None
depends_on = None


def upgrade():
   op.add_column('watchlist', sa.Column('triggered', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))


def downgrade():
    op.drop_column('watchlist', 'triggered')