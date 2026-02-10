"""create database tables and run migrations."""

from app.core.log_config import get_logger
from app.database.session import sessionmanager
from app.models.mixins import Base

logger = get_logger("tables and migrations")


# Create tables
async def create_tables():
    """Create all tables in the database."""
    if sessionmanager.engine is None:
        logger.info("TABLES", extra={"message": "Database engine not initialized"})
        raise RuntimeError("Database engine not initialized")
    async with sessionmanager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("TABLES", extra={"message": "Tables created successfully"})
