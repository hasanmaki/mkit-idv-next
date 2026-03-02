"""Session command handlers - application service layer."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.sessions.commands import (
    CreateSessionCommand,
    DeleteSessionCommand,
    ToggleSessionStatusCommand,
    UpdateSessionCommand,
)
from app.domain.sessions.entities import Session
from app.domain.sessions.exceptions import SessionNotFoundError
from app.domain.sessions.services import SessionDomainService
from app.models.sessions import Sessions
from app.repos.session_repo import SessionRepository


class SessionCommandHandler:
    """Application service for handling session commands.

    Orchestrates between domain layer and infrastructure.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SessionRepository(Sessions)
        self.domain_service = SessionDomainService(self.repo)

    async def handle_create(self, command: CreateSessionCommand) -> Session:
        """Handle create session command."""
        # Normalize input
        email = self.domain_service.normalize_email(command.email)
        name = self.domain_service.normalize_name(command.name)

        # Validate uniqueness
        await self.domain_service.validate_session_uniqueness(email=email)

        # Create domain entity
        session_entity = Session.create(
            name=name,
            email=email,
            description=command.description,
            is_active=command.is_active,
            notes=command.notes,
        )

        # Persist
        session_data = session_entity.model_dump(exclude={"_domain_events"})
        persisted_session = await self.repo.create(self.session, **session_data)

        # Pop and process domain events (could publish to event bus here)
        events = session_entity.pop_events()
        # TODO: Dispatch events to event bus if needed

        return persisted_session

    async def handle_update(self, command: UpdateSessionCommand) -> Session:
        """Handle update session command."""
        # Get existing session
        existing = await self.repo.get(self.session, command.session_id)
        if not existing:
            raise SessionNotFoundError(session_id=command.session_id)

        # Load as domain entity
        session_entity = Session.model_validate(existing)

        # Prepare update data (exclude None values)
        update_data = {
            k: v for k, v in command.model_dump().items()
            if v is not None and k != "session_id"
        }

        # Normalize email if changing
        if "email" in update_data:
            email = self.domain_service.normalize_email(update_data["email"])
            update_data["email"] = email
            # Validate email uniqueness
            await self.domain_service.validate_session_uniqueness(
                email=email,
                session_id=command.session_id,
            )

        # Normalize name if changing
        if "name" in update_data:
            update_data["name"] = self.domain_service.normalize_name(update_data["name"])

        # Apply update
        session_entity.update(**update_data)

        # Persist
        persisted_session = await self.repo.update(
            self.session,
            existing,
            **update_data,
        )

        return persisted_session

    async def handle_delete(self, command: DeleteSessionCommand) -> None:
        """Handle delete session command."""
        # Get existing session
        existing = await self.repo.get(self.session, command.session_id)
        if not existing:
            raise SessionNotFoundError(session_id=command.session_id)

        # Load as domain entity and mark for deletion
        session_entity = Session.model_validate(existing)
        session_entity.delete()

        # Delete
        await self.repo.delete(self.session, command.session_id)

    async def handle_toggle_status(
        self,
        command: ToggleSessionStatusCommand,
    ) -> Session:
        """Handle toggle session status command."""
        # Get existing session
        existing = await self.repo.get(self.session, command.session_id)
        if not existing:
            raise SessionNotFoundError(session_id=command.session_id)

        # Load as domain entity and toggle
        session_entity = Session.model_validate(existing)
        session_entity.toggle_status(command.is_active)

        # Persist
        persisted_session = await self.repo.update(
            self.session,
            existing,
            is_active=command.is_active,
        )

        return persisted_session
