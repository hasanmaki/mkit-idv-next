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
    account_status: AccountStatus | None = Field(
        None, examples=[AccountStatus.EXHAUSTED]
    )

    model_config = {"use_enum_values": True}


class BindingVerifyLogin(BaseModel):
    """Payload to verify login and reseller status."""

    otp: str = Field(..., description="OTP code for verification", examples=["123456"])

    model_config = {"use_enum_values": True}


class BindingRequestLogin(BaseModel):
    """Payload to request login OTP."""

    pin: str | None = Field(
        None, description="Optional PIN override", examples=["1234"]
    )

    model_config = {"use_enum_values": True}


class BindingRead(BaseModel):
    """Binding read schema."""

    id: int = Field(..., examples=[1])
    server_id: int = Field(..., examples=[1])
    account_id: int = Field(..., examples=[100])
    batch_id: str = Field(..., examples=["batch-2026-02-10"])
    step: BindingStep = Field(..., examples=[BindingStep.OTP_VERIFIED])
    is_reseller: bool = Field(..., examples=[True])
    balance_start: int | None = Field(None, examples=[7851])
    balance_last: int | None = Field(None, examples=[7500])
    last_error_code: str | None = Field(None, examples=["otp_failed"])
    last_error_message: str | None = Field(None, examples=["Invalid OTP"])
    token_login: str | None = Field(None, examples=["eyJhbGciOiJIUzUxMiJ9..."])
    token_location: str | None = Field(None, examples=["eyJ0eXAiOiJKV1QiLCJhb..."])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    bound_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    unbound_at: datetime | None = Field(None, examples=["2026-02-10T20:00:00.000Z"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True, "use_enum_values": True}


class BindingViewRead(BaseModel):
    """Binding read schema with joined server/account display fields."""

    id: int = Field(..., examples=[1])
    server_id: int = Field(..., examples=[1])
    account_id: int = Field(..., examples=[100])
    batch_id: str = Field(..., examples=["batch-2026-02-10"])
    step: BindingStep = Field(..., examples=[BindingStep.OTP_VERIFIED])
    is_reseller: bool = Field(..., examples=[True])
    balance_start: int | None = Field(None, examples=[7851])
    balance_last: int | None = Field(None, examples=[7500])
    last_error_code: str | None = Field(None, examples=["otp_failed"])
    last_error_message: str | None = Field(None, examples=["Invalid OTP"])
    token_login: str | None = Field(None, examples=["eyJhbGciOiJIUzUxMiJ9..."])
    token_location: str | None = Field(None, examples=["eyJ0eXAiOiJKV1QiLCJhb..."])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    bound_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    unbound_at: datetime | None = Field(None, examples=["2026-02-10T20:00:00.000Z"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])
    server_base_url: str | None = Field(None, examples=["http://10.0.0.3:9900"])
    server_port: int | None = Field(None, examples=[9900])
    server_is_active: bool | None = Field(None, examples=[True])
    server_device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    account_msisdn: str | None = Field(None, examples=["085773197010"])
    account_email: str | None = Field(None, examples=["user@example.com"])
    account_status: AccountStatus | None = Field(None, examples=[AccountStatus.ACTIVE])
    account_batch_id: str | None = Field(None, examples=["batch-2026-02-10"])

    model_config = {"use_enum_values": True}
