"""simplify_accounts_model

Revision ID: abbbf70fc779
Revises: initial
Create Date: 2026-03-03 09:54:05.709663

Simplify accounts table:
- Remove: status, is_reseller, last_device_id
- Add: is_active, card_active_until, grace_period_until, expires_info, last_balance_response
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abbbf70fc779'
down_revision: Union[str, Sequence[str], None] = 'initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - simplify accounts model."""
    # Add new columns
    op.add_column('accounts', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('accounts', sa.Column('card_active_until', sa.String(50), nullable=True))
    op.add_column('accounts', sa.Column('grace_period_until', sa.String(50), nullable=True))
    op.add_column('accounts', sa.Column('expires_info', sa.String(100), nullable=True))
    op.add_column('accounts', sa.Column('last_balance_response', sa.JSON(), nullable=True))
    
    # Create index for is_active
    op.create_index('ix_accounts_is_active', 'accounts', ['is_active'], unique=False)
    
    # Drop old columns (use if_exists for safety)
    op.drop_column('accounts', 'status')
    op.drop_column('accounts', 'is_reseller')
    op.drop_column('accounts', 'last_device_id')


def downgrade() -> None:
    """Downgrade schema - restore old columns."""
    # Restore old columns
    op.add_column('accounts', sa.Column('last_device_id', sa.String(100), nullable=True))
    op.add_column('accounts', sa.Column('is_reseller', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('accounts', sa.Column('status', sa.String(50), nullable=False, server_default='new'))
    
    # Recreate status index
    op.create_index('ix_accounts_status', 'accounts', ['status'], unique=False)
    
    # Drop new columns
    op.drop_index('ix_accounts_is_active', table_name='accounts')
    op.drop_column('accounts', 'last_balance_response')
    op.drop_column('accounts', 'expires_info')
    op.drop_column('accounts', 'grace_period_until')
    op.drop_column('accounts', 'card_active_until')
    op.drop_column('accounts', 'is_active')
