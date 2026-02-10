"""Schemas for bindings service."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.statuses import AccountStatus
from app.models.steps import BindingStep


class BindingCreate(BaseModel):
    """Create a new binding between server and account."""

    server_id: int = Field(..., description="Server ID to bind")
    account_id: int = Field(..., description="Account ID to bind")
    balance_start: int | None = Field(None, description="Initial balance snapshot")

    model_config = {"use_enum_values": True}


class BindingUpdate(BaseModel):
    """Update binding step or balance."""

    step: BindingStep | None = None
    balance_last: int | None = None
    is_reseller: bool | None = None
    last_error_code: str | None = None
    last_error_message: str | None = None
    token_login: str | None = None
    token_location: str | None = None
    device_id: str | None = None

    model_config = {"use_enum_values": True}


class BindingLogout(BaseModel):
    """Logout/unbind a binding."""

    last_error_code: str | None = None
    last_error_message: str | None = None
    account_status: AccountStatus | None = None

    model_config = {"use_enum_values": True}


class BindingVerifyLogin(BaseModel):
    """Payload to verify login and reseller status."""

    otp: str = Field(..., description="OTP code for verification")
    pin: str | None = Field(None, description="Optional PIN override")

    model_config = {"use_enum_values": True}


class BindingRead(BaseModel):
    """Binding read schema."""

    id: int
    server_id: int
    account_id: int
    batch_id: str
    step: BindingStep
    is_reseller: bool
    balance_start: int | None
    balance_last: int | None
    last_error_code: str | None
    last_error_message: str | None
    token_login: str | None
    token_location: str | None
    device_id: str | None
    bound_at: datetime
    unbound_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}
