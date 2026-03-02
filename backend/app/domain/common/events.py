"""Domain events for capturing business events."""

from abc import ABC
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel, ABC):
    """Base class for all domain events.

    Domain events capture something meaningful that happened in the domain.
    They are immutable and named in the past tense.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
    )

    event_id: str = Field(
        default_factory=lambda: str(datetime.now(timezone.utc).timestamp()),
        description="Unique event identifier",
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred",
    )
    version: int = Field(
        default=1,
        description="Event version for schema evolution",
    )

    @property
    def event_type(self) -> str:
        """Return the event type name."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return self.model_dump()
