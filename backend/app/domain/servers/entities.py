"""Server domain entity - rich domain model with business logic."""

from datetime import datetime
from typing import Any

from pydantic import Field

from app.domain.common.entities import Entity
from app.domain.common.events import DomainEvent
from app.domain.servers.events import (
    ServerCreatedEvent,
    ServerDeletedEvent,
    ServerStatusToggledEvent,
    ServerUpdatedEvent,
)
from app.domain.servers.exceptions import ServerDuplicateError
from app.domain.servers.value_objects import ServerConfig, ServerId, ServerUrl


class Server(Entity):
    """Server aggregate root.

    Represents a configured API server that handles IDV operations.
    Contains all business rules and invariants for server management.
    """

    id: int | None = None  # Optional to allow creation before persistence

    # User-friendly identity
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="User-friendly server name (unique)",
    )
    
    # Core identity
    port: int = Field(..., gt=0, lt=65536, description="Port number")
    base_url: str = Field(..., min_length=10, max_length=255, description="Base URL")
    description: str | None = Field(None, max_length=255)

    # Configuration
    timeout: int = Field(10, ge=1, le=30)
    retries: int = Field(3, ge=0, le=10)
    wait_between_retries: int = Field(1, ge=0, le=10)
    max_requests_queued: int = Field(5, ge=1, le=20)
    
    # Rate limiting
    delay_per_hit: int = Field(
        0,
        ge=0,
        le=10000,
        description="Delay in milliseconds between requests",
    )

    # Status
    is_active: bool = Field(True)

    # Additional metadata
    parameters: dict[str, Any] | None = None
    device_id: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=500)

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Domain events (not persisted, just for in-memory tracking)
    _domain_events: list[DomainEvent] = []

    @classmethod
    def create(
        cls,
        name: str,
        port: int,
        base_url: str,
        description: str | None = None,
        timeout: int = 10,
        retries: int = 3,
        wait_between_retries: int = 1,
        max_requests_queued: int = 5,
        delay_per_hit: int = 0,
        is_active: bool = True,
        notes: str | None = None,
        parameters: dict[str, Any] | None = None,
        device_id: str | None = None,
    ) -> "Server":
        """Factory method to create a new server.

        Records a ServerCreatedEvent for event-driven workflows.
        """
        server = cls(
            name=name.strip(),
            port=port,
            base_url=base_url,
            description=description,
            timeout=timeout,
            retries=retries,
            wait_between_retries=wait_between_retries,
            max_requests_queued=max_requests_queued,
            delay_per_hit=delay_per_hit,
            is_active=is_active,
            notes=notes,
            parameters=parameters,
            device_id=device_id,
        )

        # Record domain event
        server._record_event(
            ServerCreatedEvent(
                server_id=server.id or 0,
                name=server.name,
                port=port,
                base_url=base_url,
                description=description,
            )
        )

        return server

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        wait_between_retries: int | None = None,
        max_requests_queued: int | None = None,
        delay_per_hit: int | None = None,
        is_active: bool | None = None,
        notes: str | None = None,
        parameters: dict[str, Any] | None = None,
        device_id: str | None = None,
    ) -> list[str]:
        """Update server properties.

        Returns list of updated field names for audit trail.
        Records a ServerUpdatedEvent.
        """
        updated_fields: list[str] = []
        old_values: dict[str, Any] = {}

        field_mappings = {
            "name": name,
            "description": description,
            "timeout": timeout,
            "retries": retries,
            "wait_between_retries": wait_between_retries,
            "max_requests_queued": max_requests_queued,
            "delay_per_hit": delay_per_hit,
            "is_active": is_active,
            "notes": notes,
            "parameters": parameters,
            "device_id": device_id,
        }

        for field_name, new_value in field_mappings.items():
            if new_value is not None:
                old_values[field_name] = getattr(self, field_name)
                setattr(self, field_name, new_value)
                updated_fields.append(field_name)

        if updated_fields:
            self._record_event(
                ServerUpdatedEvent(
                    server_id=self.id or 0,
                    updated_fields=updated_fields,
                    old_values=old_values,
                )
            )

        return updated_fields

    def toggle_status(self, is_active: bool) -> None:
        """Toggle server active status.

        Records a ServerStatusToggledEvent.
        """
        if self.is_active == is_active:
            return  # No change needed

        previous_status = self.is_active
        self.is_active = is_active

        self._record_event(
            ServerStatusToggledEvent(
                server_id=self.id or 0,
                is_active=is_active,
                previous_status=previous_status,
            )
        )

    def activate(self) -> None:
        """Activate the server."""
        self.toggle_status(True)

    def deactivate(self) -> None:
        """Deactivate the server."""
        self.toggle_status(False)

    def delete(self) -> None:
        """Mark server for deletion.

        Records a ServerDeletedEvent.
        """
        self._record_event(
            ServerDeletedEvent(
                server_id=self.id or 0,
                base_url=self.base_url,
                deleted_at=datetime.utcnow(),
            )
        )

    def get_config(self) -> ServerConfig:
        """Get server configuration as a value object."""
        return ServerConfig(
            timeout=self.timeout,
            retries=self.retries,
            wait_between_retries=self.wait_between_retries,
            max_requests_queued=self.max_requests_queued,
        )

    def get_url(self) -> ServerUrl:
        """Get server URL as a value object."""
        return ServerUrl(value=self.base_url)

    def get_id(self) -> ServerId | None:
        """Get server ID as a value object."""
        if self.id is None:
            return None
        return ServerId(value=self.id)

    def is_same_url(self, url: str) -> bool:
        """Check if server has the same URL (case-insensitive)."""
        return self.base_url.lower() == url.lower()

    def is_same_port(self, port: int) -> bool:
        """Check if server has the same port."""
        return self.port == port

    def validate_uniqueness(
        self, existing_by_port: "Server | None", existing_by_url: "Server | None"
    ) -> None:
        """Validate server uniqueness constraints.

        Raises ServerDuplicateError if constraints are violated.
        """
        if existing_by_port and existing_by_port.id != self.id:
            raise ServerDuplicateError(
                field="port",
                value=self.port,
                existing_id=existing_by_port.id,
            )

        if existing_by_url and existing_by_url.id != self.id:
            raise ServerDuplicateError(
                field="base_url",
                value=self.base_url,
                existing_id=existing_by_url.id,
            )

    def pop_events(self) -> list[DomainEvent]:
        """Pop and return all recorded domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event (internal use)."""
        self._domain_events.append(event)

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        validate_assignment = True
