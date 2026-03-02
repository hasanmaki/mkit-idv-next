"""Binding domain queries."""

from dataclasses import dataclass


@dataclass
class GetBindingQuery:
    """Query to get a single binding by ID."""

    binding_id: int


@dataclass
class ListBindingsBySessionQuery:
    """Query to list bindings by session ID."""

    session_id: int
    is_active: bool | None = None


@dataclass
class ListActiveBindingsQuery:
    """Query to list active bindings."""

    server_id: int | None = None
    step: str | None = None
