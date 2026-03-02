"""Bindings domain module."""

from app.domain.bindings.entities import Binding
from app.domain.bindings.events import (
    BindingActivatedEvent,
    BindingCreatedEvent,
    BindingReleasedEvent,
    OTPRequestedEvent,
    OTPVerifiedEvent,
)
from app.domain.bindings.exceptions import (
    AccountAlreadyBoundError,
    BindingNotFoundError,
    BindingValidationError,
    InvalidWorkflowTransitionError,
)
from app.domain.bindings.services import BindingDomainService

__all__ = [
    # Entity
    "Binding",
    # Value Objects (will add if needed)
    # Domain Events
    "BindingCreatedEvent",
    "BindingActivatedEvent",
    "OTPRequestedEvent",
    "OTPVerifiedEvent",
    "BindingReleasedEvent",
    # Domain Exceptions
    "AccountAlreadyBoundError",
    "BindingNotFoundError",
    "BindingValidationError",
    "InvalidWorkflowTransitionError",
    # Domain Service
    "BindingDomainService",
]
