"""Sessions domain module."""

from app.domain.sessions.entities import Session
from app.domain.sessions.events import (
    SessionCreatedEvent,
    SessionDeletedEvent,
    SessionStatusToggledEvent,
    SessionUpdatedEvent,
)
from app.domain.sessions.exceptions import (
    SessionDomainException,
    SessionDuplicateError,
    SessionNotFoundError,
)
from app.domain.sessions.services import SessionDomainService
from app.domain.sessions.value_objects import (
    SessionEmail,
    SessionId,
    SessionName,
)

__all__ = [
    # Entity
    "Session",
    # Value Objects
    "SessionId",
    "SessionName",
    "SessionEmail",
    # Domain Events
    "SessionCreatedEvent",
    "SessionUpdatedEvent",
    "SessionDeletedEvent",
    "SessionStatusToggledEvent",
    # Domain Exceptions
    "SessionDomainException",
    "SessionNotFoundError",
    "SessionDuplicateError",
    # Domain Service
    "SessionDomainService",
]
