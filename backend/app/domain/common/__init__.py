"""Common domain primitives and base classes."""

from app.domain.common.entities import Entity
from app.domain.common.events import DomainEvent
from app.domain.common.exceptions import DomainException
from app.domain.common.value_objects import ValueObject

__all__ = [
    "Entity",
    "ValueObject",
    "DomainEvent",
    "DomainException",
]
