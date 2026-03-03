"""API schemas for binding endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class BindAccountRequest(BaseModel):
    """Request schema for binding a single account."""

    order_id: int = Field(..., gt=0, description="Order ID")
    server_id: int = Field(..., gt=0, description="Server ID")
    account_id: int = Field(..., gt=0, description="Account ID to bind")
    priority: int = Field(1, ge=1, description="Priority (lower = higher priority)")
    description: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=500)


class BulkBindRequest(BaseModel):
    """Request schema for bulk binding accounts."""

    order_id: int = Field(..., gt=0, description="Order ID")
    server_id: int = Field(..., gt=0, description="Server ID")
    account_ids: list[int] = Field(..., min_length=1, description="List of account IDs")
    priority: int = Field(1, ge=1, description="Priority for all bindings")
    description: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=500)


class RequestOTPRequest(BaseModel):
    """Request schema for requesting OTP."""

    pin: str = Field(
        ..., min_length=4, max_length=10, description="PIN for OTP request"
    )


class VerifyOTPRequest(BaseModel):
    """Request schema for verifying OTP."""

    otp: str = Field(..., min_length=4, max_length=10, description="OTP code")


class ReleaseBindingRequest(BaseModel):
    """Request schema for releasing a binding."""

    pass


class BalanceStartUpdateRequest(BaseModel):
    """Request schema for setting balance start."""

    balance_start: int = Field(..., ge=0, description="Starting balance")
    source: str = Field(
        ..., pattern="^(MANUAL|AUTO_CHECK)$", description="Balance source"
    )


class BindingResponse(BaseModel):
    """Response schema for binding."""

    id: int = Field(..., examples=[1])
    order_id: int = Field(..., examples=[1])
    server_id: int = Field(..., examples=[1])
    account_id: int = Field(..., examples=[100])
    step: str = Field(..., examples=["BINDED"])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    is_active: bool = Field(..., examples=[True])
    priority: int = Field(..., examples=[1])
    balance_start: int | None = Field(None, examples=[50000])
    balance_source: str | None = Field(None, examples=["MANUAL"])
    description: str | None = Field(None, examples=["Main binding"])
    notes: str | None = Field(None, examples=["Priority account"])
    last_used_at: datetime | None = Field(None)
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True}
