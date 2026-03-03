"""API schemas for account endpoints."""

from datetime import datetime
from typing import Any

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


class AccountCreateInput(BaseModel):
    """Input schema for account data in bulk operations."""

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


class BulkAccountCreateRequest(BaseModel):
    """Request schema for creating multiple accounts at once."""

    order_id: int = Field(..., gt=0, description="Order ID these accounts belong to")
    accounts: list[AccountCreateInput] = Field(
        ...,
        min_length=1,
        description="List of accounts to create",
    )


class AccountUpdateRequest(BaseModel):
    """Request schema for updating an account."""

    email: EmailStr | None = None
    pin: str | None = Field(None, min_length=4, max_length=10)
    is_active: bool | None = None
    notes: str | None = Field(None, max_length=255)


class BalanceCheckResponse(BaseModel):
    """Schema for balance check response data."""

    cardactiveuntil: str | None = Field(None, description="Card active until date")
    balance: str | None = Field(None, description="Current balance")
    graceperioduntil: str | None = Field(None, description="Grace period until date")
    expires: str | None = Field(None, description="Expiry info")


class AccountResponse(BaseModel):
    """Response schema for account."""

    id: int = Field(..., examples=[1])
    order_id: int = Field(..., examples=[1])
    order_name: str = Field(..., examples=["Operator 1"], description="Name of the order this account belongs to")
    msisdn: str = Field(..., examples=["081234567890"])
    email: str = Field(..., examples=["customer@example.com"])
    pin: str | None = Field(None, examples=["1234"])
    is_active: bool = Field(..., examples=[True], description="Whether account is active")
    balance_last: int | None = Field(None, examples=[50000], description="Last known balance")
    card_active_until: str | None = Field(None, examples=["02 Mar 2027"])
    grace_period_until: str | None = Field(None, examples=["01 May 2027"])
    expires_info: str | None = Field(None, examples=["Berlaku hingga 02 Mar 27"])
    used_count: int = Field(..., examples=[0], description="Number of times used")
    last_used_at: datetime | None = Field(None)
    last_device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    last_balance_response: dict[str, Any] | None = Field(None, description="Raw balance check response")
    notes: str | None = Field(None, examples=["Priority account"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True}
