"""Server domain events."""

from datetime import datetime
from typing import Any

from app.domain.common.events import DomainEvent
from app.domain.servers.value_objects import ServerId, ServerUrl


class ServerCreatedEvent(DomainEvent):
    """Event fired when a new server is created."""

    server_id: int
    name: str
    port: int
    base_url: str
    description: str | None = None

    def __str__(self) -> str:
        return f"Server {self.server_id} ('{self.name}') created at {self.base_url}"


class ServerUpdatedEvent(DomainEvent):
    """Event fired when a server is updated."""

    server_id: int
    updated_fields: list[str]
    old_values: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"Server {self.server_id} updated: {', '.join(self.updated_fields)}"


class ServerStatusToggledEvent(DomainEvent):
    """Event fired when server active status is toggled."""

    server_id: int
    is_active: bool
    previous_status: bool

    def __str__(self) -> str:
        status = "activated" if self.is_active else "deactivated"
        return f"Server {self.server_id} {status}"


class ServerDeletedEvent(DomainEvent):
    """Event fired when a server is deleted."""

    server_id: int
    base_url: str
    deleted_at: datetime

    def __str__(self) -> str:
        return f"Server {self.server_id} deleted"


class ServerBulkCreatedEvent(DomainEvent):
    """Event fired when multiple servers are created in bulk."""

    total_requested: int
    total_created: int
    total_skipped: int
    total_failed: int
    server_ids: list[int]
    base_host: str
    start_port: int
    end_port: int

    def __str__(self) -> str:
        return (
            f"Bulk server creation: {self.total_created}/{self.total_requested} created"
        )
