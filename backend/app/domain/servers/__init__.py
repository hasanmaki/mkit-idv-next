"""Server domain module."""

from app.domain.servers.entities import Server
from app.domain.servers.events import (
    ServerBulkCreatedEvent,
    ServerCreatedEvent,
    ServerDeletedEvent,
    ServerStatusToggledEvent,
    ServerUpdatedEvent,
)
from app.domain.servers.exceptions import (
    ServerBulkValidationError,
    ServerDomainException,
    ServerDuplicateError,
    ServerNotFoundError,
)
from app.domain.servers.services import ServerDomainService
from app.domain.servers.value_objects import (
    ServerConfig,
    ServerId,
    ServerUrl,
)

__all__ = [
    # Entity
    "Server",
    # Value Objects
    "ServerId",
    "ServerUrl",
    "ServerConfig",
    # Domain Events
    "ServerCreatedEvent",
    "ServerUpdatedEvent",
    "ServerDeletedEvent",
    "ServerStatusToggledEvent",
    "ServerBulkCreatedEvent",
    # Domain Exceptions
    "ServerDomainException",
    "ServerNotFoundError",
    "ServerDuplicateError",
    "ServerBulkValidationError",
    # Domain Service
    "ServerDomainService",
]
