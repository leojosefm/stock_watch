"""added date time columns

Revision ID: 6274de6c4612
Revises: 8da83cd1ae4a
Create Date: 2024-10-13 12:53:16.000457

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6274de6c4612'
down_revision = '8da83cd1ae4a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('watchlist', sa.Column('added_datetime', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('watchlist', sa.Column('triggered_datetime', sa.DateTime(), nullable=False, server_default='9999-12-31 00:00:00'))


def downgrade():
    op.drop_column('watchlist', 'added_datetime')
    op.drop_column('watchlist', 'triggered_datetime')
