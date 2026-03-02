"""add name and delay_per_hit to servers clear data

Revision ID: e11b9852fac9
Revises: 5b8976040c0b
Create Date: 2026-03-02 21:11:31.080185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e11b9852fac9'
down_revision: Union[str, Sequence[str], None] = '5b8976040c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Clear existing data first
    op.execute("DELETE FROM servers")
    
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('servers', schema=None) as batch_op:
        # Add name column (required, unique)
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False, server_default='Server 0'))
        
        # Add delay_per_hit column
        batch_op.add_column(sa.Column('delay_per_hit', sa.Integer(), nullable=False, server_default='0'))
        
        # Create index on name
        batch_op.create_index(op.f('ix_servers_name'), ['name'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('servers', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_servers_name'))
        batch_op.drop_column('delay_per_hit')
        batch_op.drop_column('name')
