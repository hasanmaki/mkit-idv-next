"""Binding query handlers - application service layer."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.bindings.queries import (
    GetBindingQuery,
    ListActiveBindingsQuery,
    ListBindingsBySessionQuery,
)
from app.domain.bindings.entities import Binding
from app.domain.bindings.exceptions import BindingNotFoundError
from app.models.bindings import Bindings
from app.repos.binding_repo import BindingRepository


class BindingQueryHandler:
    """Application service for handling binding queries."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BindingRepository(Bindings)

    async def handle_get(self, query: GetBindingQuery) -> Binding:
        """Handle get binding query."""
        binding = await self.repo.get(self.session, query.binding_id)
        if not binding:
            raise BindingNotFoundError(binding_id=query.binding_id)
        return Binding.model_validate(binding)

    async def handle_list_by_session(
        self,
        query: ListBindingsBySessionQuery,
    ) -> Sequence[Binding]:
        """Handle list bindings by session query."""
        filters = {"session_id": query.session_id}
        if query.is_active is not None:
            filters["is_active"] = query.is_active

        bindings = await self.repo.get_multi(self.session, **filters)
        return [Binding.model_validate(b) for b in bindings]

    async def handle_list_active(
        self,
        query: ListActiveBindingsQuery,
    ) -> Sequence[Binding]:
        """Handle list active bindings query."""
        filters = {"is_active": True}
        if query.server_id is not None:
            filters["server_id"] = query.server_id
        if query.step is not None:
            filters["step"] = query.step

        bindings = await self.repo.get_multi(self.session, **filters)
        return [Binding.model_validate(b) for b in bindings]
