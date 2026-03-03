"""API schemas for account endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AccountCreateRequest(BaseModel):
    """Request schema for creating an account."""

    order_id: int = Field(..., gt=0, description="Order ID this account belongs to")
    msisdn: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Phone number (MSISDN)",
        examples=["081234567890", "6281234567890"],
    )
    email: EmailStr = Field(
        ...,
        description="Email address",
        examples=["customer@example.com"],
    )
    pin: str | None = Field(
        None,
        min_length=4,
        max_length=10,
        description="PIN (leave empty to use order's default)",
        examples=["1234"],
    )
    is_reseller: bool | None = Field(
        False,
        description="Whether this account is a reseller",
    )


class AccountUpdateRequest(BaseModel):
    """Request schema for updating an account."""

    email: EmailStr | None = None
    pin: str | None = Field(None, min_length=4, max_length=10)
    is_reseller: bool | None = None
    notes: str | None = Field(None, max_length=255)


class AccountResponse(BaseModel):
    """Response schema for account."""

    id: int = Field(..., examples=[1])
    order_id: int = Field(..., examples=[1])
    msisdn: str = Field(..., examples=["081234567890"])
    email: str = Field(..., examples=["customer@example.com"])
    pin: str | None = Field(None, examples=["1234"])
    status: str = Field(..., examples=["NEW"])
    is_reseller: bool = Field(..., examples=[False])
    balance_last: int | None = Field(None, examples=[50000])
    used_count: int = Field(..., examples=[0])
    last_used_at: datetime | None = Field(None)
    last_device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    notes: str | None = Field(None, examples=["Priority account"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True}
