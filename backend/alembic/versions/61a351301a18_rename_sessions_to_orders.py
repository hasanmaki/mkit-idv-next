"""rename_sessions_to_orders

Revision ID: 61a351301a18
Revises: bd145a9ec91e
Create Date: 2026-03-03 06:08:34.967928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61a351301a18'
down_revision: Union[str, Sequence[str], None] = 'bd145a9ec91e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.
    
    Rename sessions table to orders and update FK references in bindings.
    """
    # Drop FK constraint in bindings that references sessions
    op.drop_constraint('bindings_session_id_fkey', 'bindings', type_='foreignkey')
    
    # Rename sessions table to orders
    op.rename_table('sessions', 'orders')
    
    # Recreate FK constraint with new table name
    op.create_foreign_key(
        'bindings_order_id_fkey',
        'bindings',
        'orders',
        ['session_id'],  # Keep column name as session_id for now
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema.
    
    Rename orders table back to sessions.
    """
    # Drop FK constraint
    op.drop_constraint('bindings_order_id_fkey', 'bindings', type_='foreignkey')
    
    # Rename orders table back to sessions
    op.rename_table('orders', 'sessions')
    
    # Recreate original FK constraint
    op.create_foreign_key(
        'bindings_session_id_fkey',
        'bindings',
        'sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE'
    )
