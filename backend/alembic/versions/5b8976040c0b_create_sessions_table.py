"""create sessions table

Revision ID: 5b8976040c0b
Revises: 981cbaae32a1
Create Date: 2026-03-02 20:33:44.268584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b8976040c0b'
down_revision: Union[str, Sequence[str], None] = '981cbaae32a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sessions_name'), 'sessions', ['name'], unique=False)
    op.create_index(op.f('ix_sessions_email'), 'sessions', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_sessions_email'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_name'), table_name='sessions')
    op.drop_table('sessions')
