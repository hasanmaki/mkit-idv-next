"""Server domain commands."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CreateServerCommand:
    """Command to create a single server."""

    name: str
    port: int
    base_url: str
    description: str | None = None
    timeout: int = 10
    retries: int = 3
    wait_between_retries: int = 1
    max_requests_queued: int = 5
    delay_per_hit: int = 0
    is_active: bool = True
    notes: str | None = None
    parameters: dict[str, Any] | None = None
    device_id: str | None = None


@dataclass
class UpdateServerCommand:
    """Command to update an existing server."""

    server_id: int
    name: str | None = None
    description: str | None = None
    port: int | None = None
    timeout: int | None = None
    retries: int | None = None
    wait_between_retries: int | None = None
    max_requests_queued: int | None = None
    delay_per_hit: int | None = None
    is_active: bool | None = None
    notes: str | None = None
    parameters: dict[str, Any] | None = None
    device_id: str | None = None


@dataclass
class DeleteServerCommand:
    """Command to delete a server."""

    server_id: int


@dataclass
class ToggleServerStatusCommand:
    """Command to toggle server active status."""

    server_id: int
    is_active: bool


@dataclass
class CreateServersBulkCommand:
    """Command to create multiple servers in bulk."""

    base_name: str
    base_host: str
    start_port: int
    end_port: int
    description: str | None = None
    timeout: int = 10
    retries: int = 3
    wait_between_retries: int = 1
    max_requests_queued: int = 5
    delay_per_hit: int = 0
    is_active: bool = True
    notes: str | None = None


@dataclass
class DryRunBulkServersCommand:
    """Command to preview bulk server creation."""

    base_host: str
    start_port: int
    end_port: int
