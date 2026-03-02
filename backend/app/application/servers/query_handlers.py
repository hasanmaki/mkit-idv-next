"""Server query handlers - application service layer."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.servers.queries import GetServerQuery, ListServersQuery
from app.domain.servers.entities import Server
from app.domain.servers.exceptions import ServerNotFoundError
from app.repos.server_repo import ServerRepository
from app.models.servers import Servers


class ServerQueryHandler:
    """Application service for handling server queries.

    Read-only operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServerRepository(Servers)

    async def handle_get(self, query: GetServerQuery) -> Server:
        """Handle get server query."""
        server = await self.repo.get(self.session, query.server_id)
        if not server:
            raise ServerNotFoundError(server_id=query.server_id)
        return Server.model_validate(server)

    async def handle_list(self, query: ListServersQuery) -> Sequence[Server]:
        """Handle list servers query."""
        filters = {}
        if query.is_active is not None:
            filters["is_active"] = query.is_active

        servers = await self.repo.get_multi(
            self.session,
            skip=query.skip,
            limit=query.limit,
            **filters,
        )

        return [Server.model_validate(s) for s in servers]
