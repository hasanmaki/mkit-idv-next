"""Session domain queries."""

from dataclasses import dataclass


@dataclass
class GetSessionQuery:
    """Query to get a single session by ID."""

    session_id: int


@dataclass
class ListSessionsQuery:
    """Query to list sessions with optional filters."""

    skip: int = 0
    limit: int = 100
    is_active: bool | None = None
