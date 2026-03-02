"""Server domain queries."""

from dataclasses import dataclass


@dataclass
class GetServerQuery:
    """Query to get a single server by ID."""

    server_id: int


@dataclass
class ListServersQuery:
    """Query to list servers with optional filters."""

    skip: int = 0
    limit: int = 100
    is_active: bool | None = None
