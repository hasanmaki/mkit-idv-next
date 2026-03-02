"""Session domain events."""

from datetime import datetime

from app.domain.common.events import DomainEvent


class SessionCreatedEvent(DomainEvent):
    """Event fired when a new session is created."""

    session_id: int
    name: str
    email: str
    description: str | None = None

    def __str__(self) -> str:
        return f"Session {self.session_id} created for {self.email}"


class SessionUpdatedEvent(DomainEvent):
    """Event fired when a session is updated."""

    session_id: int
    updated_fields: list[str]
    old_values: dict | None = None

    def __str__(self) -> str:
        return f"Session {self.session_id} updated: {', '.join(self.updated_fields)}"


class SessionStatusToggledEvent(DomainEvent):
    """Event fired when session active status is toggled."""

    session_id: int
    is_active: bool
    previous_status: bool

    def __str__(self) -> str:
        status = "activated" if self.is_active else "deactivated"
        return f"Session {self.session_id} {status}"


class SessionDeletedEvent(DomainEvent):
    """Event fired when a session is deleted."""

    session_id: int
    email: str
    deleted_at: datetime

    def __str__(self) -> str:
        return f"Session {self.session_id} ({self.email}) deleted"
