"""Session domain commands."""

from dataclasses import dataclass


@dataclass
class CreateSessionCommand:
    """Command to create a single session."""

    name: str
    email: str
    description: str | None = None
    is_active: bool = True
    notes: str | None = None


@dataclass
class UpdateSessionCommand:
    """Command to update an existing session."""

    session_id: int
    name: str | None = None
    email: str | None = None
    description: str | None = None
    is_active: bool | None = None
    notes: str | None = None


@dataclass
class DeleteSessionCommand:
    """Command to delete a session."""

    session_id: int


@dataclass
class ToggleSessionStatusCommand:
    """Command to toggle session active status."""

    session_id: int
    is_active: bool
