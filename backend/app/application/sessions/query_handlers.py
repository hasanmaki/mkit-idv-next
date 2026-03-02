"""Session query handlers - application service layer."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.sessions.queries import GetSessionQuery, ListSessionsQuery
from app.domain.sessions.entities import Session
from app.domain.sessions.exceptions import SessionNotFoundError
from app.models.sessions import Sessions
from app.repos.session_repo import SessionRepository


class SessionQueryHandler:
    """Application service for handling session queries.

    Read-only operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SessionRepository(Sessions)

    async def handle_get(self, query: GetSessionQuery) -> Session:
        """Handle get session query."""
        session = await self.repo.get(self.session, query.session_id)
        if not session:
            raise SessionNotFoundError(session_id=query.session_id)
        return Session.model_validate(session)

    async def handle_list(self, query: ListSessionsQuery) -> Sequence[Session]:
        """Handle list sessions query."""
        filters = {}
        if query.is_active is not None:
            filters["is_active"] = query.is_active

        sessions = await self.repo.get_multi(
            self.session,
            skip=query.skip,
            limit=query.limit,
            **filters,
        )

        return [Session.model_validate(s) for s in sessions]
