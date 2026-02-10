"""Repository for Bindings model with helpers."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bindings import Bindings
from app.repos.base import BaseRepository


class BindingRepository(BaseRepository[Bindings]):
    """Repository for Bindings model."""

    async def get_active_by_server(
        self, db: AsyncSession, *, server_id: int
    ) -> Bindings | None:
        """Get active binding by server_id (unbound_at is NULL)."""
        stmt = select(Bindings).where(
            and_(Bindings.server_id == server_id, Bindings.unbound_at.is_(None))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_active_by_account(
        self, db: AsyncSession, *, account_id: int
    ) -> Bindings | None:
        """Get active binding by account_id (unbound_at is NULL)."""
        stmt = select(Bindings).where(
            and_(Bindings.account_id == account_id, Bindings.unbound_at.is_(None))
        )
        result = await db.execute(stmt)
        return result.scalars().first()
