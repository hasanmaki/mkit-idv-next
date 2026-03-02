"""Base value object class for domain-driven design."""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """Base class for all value objects.

    Value objects are immutable objects that describe characteristics
    and are compared by their attributes, not by ID.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,  # Value objects are immutable
    )

    def __eq__(self, other: object) -> bool:
        """Value objects are equal if all their attributes are equal."""
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    def __hash__(self) -> int:
        """Hash based on all attribute values."""
        return hash(tuple(sorted(self.model_dump().items())))
