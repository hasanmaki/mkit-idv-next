"""Initial schema with orders and accounts linked

Revision ID: initial
Revises: 
Create Date: 2026-03-03 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with proper FK relationships."""
    
    # 1. Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('default_pin', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_orders_name', 'orders', ['name'], unique=False)
    op.create_index('ix_orders_email', 'orders', ['email'], unique=True)
    
    # 2. Create servers table
    op.create_table(
        'servers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('base_url', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=False, default=10),
        sa.Column('retries', sa.Integer(), nullable=False, default=3),
        sa.Column('wait_between_retries', sa.Integer(), nullable=False, default=1),
        sa.Column('max_requests_queued', sa.Integer(), nullable=False, default=5),
        sa.Column('delay_per_hit', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('port'),
        sa.UniqueConstraint('base_url')
    )
    op.create_index('ix_servers_name', 'servers', ['name'], unique=False)
    
    # 3. Create accounts table (with order_id FK)
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('msisdn', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('pin', sa.String(20), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='NEW'),
        sa.Column('is_reseller', sa.Boolean(), nullable=False, default=False),
        sa.Column('balance_last', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('last_device_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('msisdn', 'order_id', name='uq_msisdn_order'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE')
    )
    op.create_index('ix_accounts_order_id', 'accounts', ['order_id'], unique=False)
    op.create_index('ix_accounts_msisdn', 'accounts', ['msisdn'], unique=False)
    op.create_index('ix_accounts_email', 'accounts', ['email'], unique=False)
    
    # 4. Create bindings table
    op.create_table(
        'bindings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('step', sa.String(50), nullable=False, default='BINDED'),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=1),
        sa.Column('balance_start', sa.Integer(), nullable=True),
        sa.Column('balance_source', sa.String(20), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', name='uq_binding_account'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_bindings_order_id', 'bindings', ['order_id'], unique=False)
    op.create_index('ix_bindings_server_id', 'bindings', ['server_id'], unique=False)
    op.create_index('ix_bindings_account_id', 'bindings', ['account_id'], unique=False)
    op.create_index('ix_bindings_step', 'bindings', ['step'], unique=False)
    op.create_index('ix_bindings_is_active', 'bindings', ['is_active'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('bindings')
    op.drop_table('accounts')
    op.drop_table('servers')
    op.drop_table('orders')
