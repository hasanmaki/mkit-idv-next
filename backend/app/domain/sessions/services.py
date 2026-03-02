"""Session domain service for domain-level business logic."""

from dataclasses import dataclass
from typing import Protocol

from app.domain.sessions.entities import Session
from app.domain.sessions.events import SessionCreatedEvent
from app.domain.sessions.exceptions import SessionDuplicateError


class SessionRepositoryProtocol(Protocol):
    """Protocol for session repository (dependency inversion)."""

    async def get_by(self, session: object, **filters) -> Session | None:
        """Get session by filters."""
        ...

    async def create(self, session: object, **kwargs) -> Session:
        """Create a new session."""
        ...


@dataclass
class SessionCreationResult:
    """Result of session creation."""

    session: Session
    event: SessionCreatedEvent


class SessionDomainService:
    """Domain service for session operations.

    Contains business logic that doesn't naturally fit within a single entity.
    Works with the Session entity but doesn't hold state.
    """

    def __init__(self, repository: SessionRepositoryProtocol | None = None):
        self.repository = repository

    async def validate_session_uniqueness(
        self,
        email: str,
        session_id: int | None = None,
    ) -> Session | None:
        """Validate that email is unique.

        Returns existing session if found.
        Raises SessionDuplicateError if duplicate found.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        existing_by_email = await self.repository.get_by(email=email)

        # Check email conflict
        if existing_by_email and (not session_id or existing_by_email.id != session_id):
            raise SessionDuplicateError(
                email=email,
                existing_id=existing_by_email.id,
            )

        return existing_by_email

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email for consistent comparison."""
        return email.lower().strip()

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name for consistent storage."""
        return name.strip()
