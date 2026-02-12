"""Alembic environment configuration for migrations.

This module configures Alembic to work with SQLAlchemy and the application's
Pydantic settings, supporting both Docker and development environments.

Uses synchronous engine for migrations which works reliably with SQLite.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from alembic import context

# Import models and base for autogenerate support
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.mixins import Base
from app.models.servers import Servers
from app.models.statuses import AccountStatus
from app.models.steps import BindingStep
from app.models.transaction_statuses import TransactionStatus, TransactionOtpStatus
from app.models.transactions import TransactionSnapshots, Transactions

# Import settings to get database URL
from app.core.settings import get_app_settings

# Interpret the config file for Python logging
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Get database URL from settings
settings = get_app_settings()

# Convert async URL to sync for migrations
# sqlite+aiosqlite:///./application.db -> sqlite:///./application.db
database_url = settings.db.db_url.replace("+aiosqlite", "", 1)

# Add our model's MetaData object for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode.

    This configures the context with just a URL and not an Engine.
    """
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode.

    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    # Create synchronous engine for migrations
    engine = create_engine(
        database_url,
        poolclass=NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
