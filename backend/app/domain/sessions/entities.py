"""Session domain entity - rich domain model with business logic."""

from datetime import datetime

from pydantic import Field

from app.domain.common.entities import Entity
from app.domain.common.events import DomainEvent
from app.domain.sessions.events import (
    SessionCreatedEvent,
    SessionDeletedEvent,
    SessionStatusToggledEvent,
    SessionUpdatedEvent,
)
from app.domain.sessions.exceptions import SessionDuplicateError
from app.domain.sessions.value_objects import SessionEmail, SessionId, SessionName


class Session(Entity):
    """Session aggregate root.

    Represents a user session that can have multiple bindings to servers.
    Contains all business rules and invariants for session management.
    """

    id: int | None = None  # Optional to allow creation before persistence

    # Session identity
    name: str = Field(..., min_length=3, max_length=100, description="Session name")
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Session email (unique)",
    )

    # Session status
    is_active: bool = Field(True, description="Whether session is active")

    # Metadata
    description: str | None = Field(None, max_length=255)
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
        email: str,
        description: str | None = None,
        is_active: bool = True,
        notes: str | None = None,
    ) -> "Session":
        """Factory method to create a new session.

        Records a SessionCreatedEvent for event-driven workflows.
        """
        session = cls(
            name=name.strip(),
            email=email.lower().strip(),
            description=description,
            is_active=is_active,
            notes=notes,
        )

        # Record domain event
        session._record_event(
            SessionCreatedEvent(
                session_id=session.id or 0,
                name=session.name,
                email=session.email,
                description=description,
            )
        )

        return session

    def update(
        self,
        name: str | None = None,
        email: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        notes: str | None = None,
    ) -> list[str]:
        """Update session properties.

        Returns list of updated field names for audit trail.
        Records a SessionUpdatedEvent.
        """
        updated_fields: list[str] = []
        old_values: dict = {}

        field_mappings = {
            "name": name,
            "email": email,
            "description": description,
            "is_active": is_active,
            "notes": notes,
        }

        for field_name, new_value in field_mappings.items():
            if new_value is not None:
                old_values[field_name] = getattr(self, field_name)
                setattr(self, field_name, new_value)
                updated_fields.append(field_name)

        if updated_fields:
            self._record_event(
                SessionUpdatedEvent(
                    session_id=self.id or 0,
                    updated_fields=updated_fields,
                    old_values=old_values,
                )
            )

        return updated_fields

    def toggle_status(self, is_active: bool) -> None:
        """Toggle session active status.

        Records a SessionStatusToggledEvent.
        """
        if self.is_active == is_active:
            return  # No change needed

        previous_status = self.is_active
        self.is_active = is_active

        self._record_event(
            SessionStatusToggledEvent(
                session_id=self.id or 0,
                is_active=is_active,
                previous_status=previous_status,
            )
        )

    def activate(self) -> None:
        """Activate the session."""
        self.toggle_status(True)

    def deactivate(self) -> None:
        """Deactivate the session."""
        self.toggle_status(False)

    def delete(self) -> None:
        """Mark session for deletion.

        Records a SessionDeletedEvent.
        """
        self._record_event(
            SessionDeletedEvent(
                session_id=self.id or 0,
                email=self.email,
                deleted_at=datetime.utcnow(),
            )
        )

    def get_name(self) -> SessionName:
        """Get session name as a value object."""
        return SessionName(value=self.name)

    def get_email(self) -> SessionEmail:
        """Get session email as a value object."""
        return SessionEmail(value=self.email)

    def get_id(self) -> SessionId | None:
        """Get session ID as a value object."""
        if self.id is None:
            return None
        return SessionId(value=self.id)

    def is_same_email(self, email: str) -> bool:
        """Check if session has the same email (case-insensitive)."""
        return self.email.lower() == email.lower()

    def validate_uniqueness(self, existing_by_email: "Session | None") -> None:
        """Validate session uniqueness constraints.

        Raises SessionDuplicateError if constraints are violated.
        """
        if existing_by_email and existing_by_email.id != self.id:
            raise SessionDuplicateError(
                email=self.email,
                existing_id=existing_by_email.id,
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
