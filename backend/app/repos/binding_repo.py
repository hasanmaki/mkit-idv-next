"""Repository for Bindings model."""

from sqlalchemy import Select

from app.models.bindings import Bindings
from app.repos.base import BaseRepository


class BindingRepository(BaseRepository[Bindings]):
    """Repository for Bindings model."""

    async def get_by_account(
        self,
        session,
        account_id: int,
    ) -> Bindings | None:
        """Get binding by account ID."""
        return await self.get_by(session, account_id=account_id)

    async def get_by_session(
        self,
        session,
        session_id: int,
    ) -> list[Bindings]:
        """Get all bindings for a session."""
        return await self.get_multi(session, session_id=session_id)

    async def get_active_by_server(
        self,
        session,
        server_id: int,
    ) -> list[Bindings]:
        """Get active bindings by server ID."""
        return await self.get_multi(session, server_id=server_id, is_active=True)

    def _filter_query(self, query: Select, **filters) -> Select:
        """Add filters to query."""
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(Bindings, key) == value)
        return query
