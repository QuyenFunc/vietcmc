"""add password to clients

Revision ID: 003
Revises: 002
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clients', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('clients', 'password_hash')

