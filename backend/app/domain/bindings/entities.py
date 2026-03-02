"""Binding domain entity - rich domain model with business logic."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from app.domain.common.entities import Entity
from app.domain.common.events import DomainEvent
from app.domain.bindings.events import (
    BindingActivatedEvent,
    BindingCreatedEvent,
    BindingReleasedEvent,
    OTPRequestedEvent,
    OTPVerifiedEvent,
)
from app.domain.bindings.exceptions import InvalidWorkflowTransitionError


class Binding(Entity):
    """Binding aggregate root.

    Represents a binding between a Session, Account, and Server.
    Contains workflow state machine and business rules.
    """

    id: int | None = None  # Optional to allow creation before persistence

    # Ownership
    session_id: int = Field(..., gt=0, description="Owner session ID")
    
    # Resource bindings
    server_id: int = Field(..., gt=0, description="Server ID")
    account_id: int = Field(..., gt=0, description="Account ID (unique)")
    
    # Workflow
    step: str = Field(
        default="BINDED",
        description="BINDED, REQUEST_OTP, VERIFY_OTP, VERIFIED, LOGGED_OUT",
    )
    device_id: str | None = Field(None, max_length=100)
    
    # Control
    is_active: bool = Field(True)
    priority: int = Field(1, ge=1)
    
    # Balance
    balance_start: int | None = Field(None, ge=0)
    balance_source: str | None = Field(None)  # 'MANUAL' or 'AUTO_CHECK'
    
    # Metadata
    description: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=500)
    last_used_at: datetime | None = None
    
    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    # Domain events
    _domain_events: list[DomainEvent] = []

    # Valid workflow transitions
    WORKFLOW_TRANSITIONS: ClassVar[dict[str, set[str]]] = {
        "BINDED": {"REQUEST_OTP", "LOGGED_OUT"},
        "REQUEST_OTP": {"VERIFY_OTP", "BINDED", "LOGGED_OUT"},
        "VERIFY_OTP": {"VERIFIED", "REQUEST_OTP", "LOGGED_OUT"},
        "VERIFIED": {"LOGGED_OUT", "BINDED"},
        "LOGGED_OUT": set(),  # Terminal state
    }

    @classmethod
    def create(
        cls,
        session_id: int,
        server_id: int,
        account_id: int,
        priority: int = 1,
        description: str | None = None,
        notes: str | None = None,
    ) -> "Binding":
        """Factory method to create a new binding."""
        binding = cls(
            session_id=session_id,
            server_id=server_id,
            account_id=account_id,
            priority=priority,
            description=description,
            notes=notes,
            step="BINDED",
            is_active=True,
        )

        # Record domain event
        binding._record_event(
            BindingCreatedEvent(
                binding_id=binding.id or 0,
                session_id=session_id,
                server_id=server_id,
                account_id=account_id,
            )
        )

        return binding

    def activate(self) -> None:
        """Activate the binding."""
        if not self.is_active:
            self.is_active = True
            self._record_event(
                BindingActivatedEvent(
                    binding_id=self.id or 0,
                    session_id=self.session_id,
                )
            )

    def request_otp(self, device_id: str | None = None) -> None:
        """Transition to REQUEST_OTP state."""
        self._ensure_can_transition_to("REQUEST_OTP")
        self.step = "REQUEST_OTP"
        self.device_id = device_id
        self.last_used_at = datetime.utcnow()

        self._record_event(
            OTPRequestedEvent(
                binding_id=self.id or 0,
                account_id=self.account_id,
                device_id=device_id,
            )
        )

    def verify_otp(self, device_id: str | None = None) -> None:
        """Transition to VERIFY_OTP state."""
        self._ensure_can_transition_to("VERIFY_OTP")
        self.step = "VERIFY_OTP"
        if device_id:
            self.device_id = device_id
        self.last_used_at = datetime.utcnow()

    def mark_verified(self) -> None:
        """Transition to VERIFIED state (ready for transactions)."""
        self._ensure_can_transition_to("VERIFIED")
        self.step = "VERIFIED"
        self.last_used_at = datetime.utcnow()

        self._record_event(
            OTPVerifiedEvent(
                binding_id=self.id or 0,
                account_id=self.account_id,
                device_id=self.device_id,
            )
        )

    def release(self) -> None:
        """Release the binding (logout)."""
        self._ensure_can_transition_to("LOGGED_OUT")
        old_step = self.step
        self.step = "LOGGED_OUT"
        self.is_active = False
        self.last_used_at = datetime.utcnow()

        self._record_event(
            BindingReleasedEvent(
                binding_id=self.id or 0,
                session_id=self.session_id,
                account_id=self.account_id,
                final_step=old_step,
            )
        )

    def set_balance_start(self, amount: int, source: str) -> None:
        """Set the starting balance."""
        if source not in ("MANUAL", "AUTO_CHECK"):
            raise ValueError("balance_source must be 'MANUAL' or 'AUTO_CHECK'")
        
        self.balance_start = amount
        self.balance_source = source

    def can_request_otp(self) -> bool:
        """Check if OTP can be requested."""
        return self.step in ("BINDED", "REQUEST_OTP")

    def can_verify_otp(self) -> bool:
        """Check if OTP can be verified."""
        return self.step == "VERIFY_OTP"

    def is_verified(self) -> bool:
        """Check if binding is verified and ready for transactions."""
        return self.step == "VERIFIED" and self.is_active

    def _ensure_can_transition_to(self, target_step: str) -> None:
        """Ensure the transition to target_step is valid."""
        allowed_transitions = self.WORKFLOW_TRANSITIONS.get(self.step, set())
        
        if target_step not in allowed_transitions:
            raise InvalidWorkflowTransitionError(
                current_step=self.step,
                target_step=target_step,
                action=f"transition to {target_step}",
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
