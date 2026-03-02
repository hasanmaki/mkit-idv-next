"""Base entity class for domain-driven design."""

from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel, ABC):
    """Base class for all domain entities.

    Entities are objects with a distinct identity that runs through
    different states and has a lifecycle.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        from_attributes=True,
    )

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same type and ID."""
        if not isinstance(other, Entity):
            return False
        if type(self) is not type(other):
            return False
        return self.id == other.id  # noqa: SIM103

    def __hash__(self) -> int:
        """Hash based on entity type and ID."""
        return hash((self.__class__.__name__, self.id))

    @property
    def entity_type(self) -> str:
        """Return the entity type name."""
        return self.__class__.__name__
