"""Binding domain events."""

from app.domain.common.events import DomainEvent


class BindingCreatedEvent(DomainEvent):
    """Event fired when a binding is created."""

    binding_id: int
    session_id: int
    server_id: int
    account_id: int
    step: str = "BINDED"

    def __str__(self) -> str:
        return f"Binding {self.binding_id} created: Session {self.session_id} → Account {self.account_id} → Server {self.server_id}"


class BindingActivatedEvent(DomainEvent):
    """Event fired when a binding is activated."""

    binding_id: int
    session_id: int

    def __str__(self) -> str:
        return f"Binding {self.binding_id} activated"


class OTPRequestedEvent(DomainEvent):
    """Event fired when OTP is requested for a binding."""

    binding_id: int
    account_id: int
    device_id: str | None = None

    def __str__(self) -> str:
        return f"OTP requested for binding {self.binding_id} (account {self.account_id})"


class OTPVerifiedEvent(DomainEvent):
    """Event fired when OTP is verified for a binding."""

    binding_id: int
    account_id: int
    device_id: str | None = None

    def __str__(self) -> str:
        return f"OTP verified for binding {self.binding_id} (account {self.account_id})"


class BindingReleasedEvent(DomainEvent):
    """Event fired when a binding is released (logout)."""

    binding_id: int
    session_id: int
    account_id: int
    final_step: str

    def __str__(self) -> str:
        return f"Binding {self.binding_id} released: Account {self.account_id} freed"
