"""Binding domain commands."""

from dataclasses import dataclass


@dataclass
class BindAccountCommand:
    """Command to bind a single account to a server."""

    session_id: int
    server_id: int
    account_id: int
    priority: int = 1
    description: str | None = None
    notes: str | None = None


@dataclass
class BulkBindAccountsCommand:
    """Command to bind multiple accounts to a server."""

    session_id: int
    server_id: int
    account_ids: list[int]
    priority: int = 1
    description: str | None = None
    notes: str | None = None


@dataclass
class RequestOTPCommand:
    """Command to request OTP for a binding."""

    binding_id: int
    pin: str


@dataclass
class VerifyOTPCommand:
    """Command to verify OTP for a binding."""

    binding_id: int
    otp: str


@dataclass
class ReleaseBindingCommand:
    """Command to release a binding (logout)."""

    binding_id: int


@dataclass
class SetBalanceStartCommand:
    """Command to set balance start for a binding."""

    binding_id: int
    balance_start: int
    source: str  # 'MANUAL' or 'AUTO_CHECK'
