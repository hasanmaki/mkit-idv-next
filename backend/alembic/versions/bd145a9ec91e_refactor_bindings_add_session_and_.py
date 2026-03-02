"""Refactor bindings: add session and simplify workflow

Revision ID: bd145a9ec91e
Revises: e11b9852fac9
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = 'bd145a9ec91e'
down_revision: Union[str, Sequence[str], None] = 'e11b9852fac9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Clear existing data first (data dummy)
    op.execute("DELETE FROM bindings")
    
    # For SQLite, we need to recreate the table
    # Get existing connection
    conn = op.get_bind()
    
    # Drop old table
    op.drop_table('bindings')
    
    # Create new table with new schema
    op.create_table('bindings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('step', sa.String(50), nullable=False, server_default='BINDED'),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('balance_start', sa.Integer(), nullable=True),
        sa.Column('balance_source', sa.String(20), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', name='uq_binding_account'),
    )
    
    # Create indexes
    op.create_index(op.f('ix_bindings_session_id'), 'bindings', ['session_id'], unique=False)
    op.create_index(op.f('ix_bindings_server_id'), 'bindings', ['server_id'], unique=False)
    op.create_index(op.f('ix_bindings_account_id'), 'bindings', ['account_id'], unique=False)
    op.create_index(op.f('ix_bindings_step'), 'bindings', ['step'], unique=False)
    op.create_index(op.f('ix_bindings_is_active'), 'bindings', ['is_active'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new table
    op.drop_table('bindings')
    
    # Recreate old table structure (simplified - won't restore data)
    op.create_table('bindings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.String(50), nullable=False),
        sa.Column('step', sa.Enum('BOUND', 'REQUESTING_OTP', 'OTP_REQUESTED', 'VERIFYING_OTP', 'OTP_VERIFIED', 'READY', name='binding_step'), nullable=False),
        sa.Column('is_reseller', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('balance_start', sa.Integer(), nullable=True),
        sa.Column('balance_last', sa.Integer(), nullable=True),
        sa.Column('last_error_code', sa.String(100), nullable=True),
        sa.Column('last_error_message', sa.String(255), nullable=True),
        sa.Column('token_login', sa.String(1024), nullable=True),
        sa.Column('token_location', sa.String(1024), nullable=True),
        sa.Column('token_location_refreshed_at', sa.DateTime(), nullable=True),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('bound_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('unbound_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
