"""Schemas for bindings service."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.statuses import AccountStatus
from app.models.steps import BindingStep


class BindingCreate(BaseModel):
    """Create a new binding between server and account."""

    server_id: int = Field(..., description="Server ID to bind", examples=[1])
    account_id: int = Field(..., description="Account ID to bind", examples=[100])
    balance_start: int | None = Field(
        None, description="Initial balance snapshot", examples=[7851]
    )

    model_config = {"use_enum_values": True}


class BindingUpdate(BaseModel):
    """Update binding step or balance."""

    step: BindingStep | None = Field(None, examples=[BindingStep.OTP_VERIFIED])
    balance_last: int | None = Field(None, examples=[7500])
    is_reseller: bool | None = Field(None, examples=[True])
    last_error_code: str | None = Field(None, examples=["otp_failed"])
    last_error_message: str | None = Field(None, examples=["Invalid OTP"])
    token_login: str | None = Field(None, examples=["eyJhbGciOiJIUzUxMiJ9..."])
    token_location: str | None = Field(None, examples=["eyJ0eXAiOiJKV1QiLCJhb..."])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])

    model_config = {"use_enum_values": True}


class BindingLogout(BaseModel):
    """Logout/unbind a binding."""

    last_error_code: str | None = Field(None, examples=["manual_logout"])
    last_error_message: str | None = Field(None, examples=["User requested"])
    account_status: AccountStatus | None = Field(None, examples=[AccountStatus.EXHAUSTED])

    model_config = {"use_enum_values": True}


class BindingVerifyLogin(BaseModel):
    """Payload to verify login and reseller status."""

    otp: str = Field(..., description="OTP code for verification", examples=["123456"])
    pin: str | None = Field(None, description="Optional PIN override", examples=["1234"])

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
