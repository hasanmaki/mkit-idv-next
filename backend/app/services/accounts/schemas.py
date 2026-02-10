"""schemas for accounts service.

This module contains Pydantic schemas used by the Accounts service.

Conventions used here:
- `AccountCreateBulk` expects a list of raw `msisdn` strings (not full account objects).
- `model_config = {"coerce_numbers_to_str": True}` is applied where appropriate to coerce numeric msisdn inputs.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.statuses import AccountStatus


class AccountBase(BaseModel):
    """Base schema for account fields shared across create/update operations."""

    msisdn: str = Field(
        ...,
        description="Phone number associated with the account",
        examples=["085777076575"],
    )
    pin: str | None = Field(
        None, description="Optional PIN for the account", examples=["1234"]
    )
    notes: str | None = Field(
        None, description="Additional notes about the account", examples=["myim3 #1"]
    )

    model_config = {
        "coerce_numbers_to_str": True,
        "use_enum_values": True,
    }

    @field_validator("msisdn", mode="before")
    @classmethod
    def validate_msisdn(cls, v: str) -> str:
        """Validate msisdn contains only digits and has length between 10-13."""
        v = v.strip()
        if not v.isdigit():
            raise ValueError("msisdn must contain digits only (0-9)")
        if not (10 <= len(v) <= 13):
            raise ValueError("msisdn length must be between 10 and 13 digits")
        return v


class AccountCreateSingle(AccountBase):
    """Schema for creating a single account."""

    email: str = Field(
        ...,
        description="Email address associated with the account",
        examples=["user@example.com"],
    )
    batch_id: str = Field(
        ...,
        description="Batch identifier for grouping accounts",
        examples=["batch-2026-02-10"],
    )

    model_config = {
        "coerce_numbers_to_str": True,
        "use_enum_values": True,
    }


class AccountCreateBulk(BaseModel):
    """Schema for creating multiple accounts in one request.

    Expectation:
    - `msisdns`: list of phone numbers (strings) without pins/emails.
    - `email` and `batch_id` will be applied to each created account.
    - Optional `pin` can provide a default PIN for all accounts in the batch.
    """

    msisdns: list[str] = Field(
        ...,
        description="List of phone numbers (msisdn) to create",
        examples=[["085777076575", "08156142731"]],
    )

    @field_validator("msisdns", mode="before")
    @classmethod
    def validate_msisdns(cls, v: list[str]) -> list[str]:
        """Validate the msisdns list and each msisdn item."""
        if not isinstance(v, (list, tuple)):
            raise TypeError("msisdns must be a list of msisdn strings")
        out: list[str] = []
        for item in v:
            s = item.strip()
            if not s.isdigit():
                raise ValueError("each msisdn must contain digits only (0-9)")
            if not (10 <= len(s) <= 13):
                raise ValueError("each msisdn length must be between 10 and 13 digits")
            out.append(s)
        return out

    email: str = Field(
        ...,
        description="Email address to associate with all accounts",
        examples=["user@example.com"],
    )
    batch_id: str = Field(
        ...,
        description="Batch identifier for grouping accounts",
        examples=["batch-2026-02-10"],
    )
    pin: str | None = Field(
        None, description="Optional default PIN for all new accounts"
    )

    model_config = {
        "coerce_numbers_to_str": True,
        "use_enum_values": True,
    }


class AccountRead(BaseModel):
    """Schema returned by read endpoints for an account."""

    id: int = Field(..., description="Primary key of the account", examples=[100])
    msisdn: str = Field(..., examples=["085777076575"])
    email: str = Field(..., examples=["user@example.com"])
    batch_id: str = Field(..., examples=["batch-2026-02-10"])
    pin: str | None = Field(
        None, description="PIN for the account (included per project choice)"
    )
    status: AccountStatus = Field(..., examples=[AccountStatus.ACTIVE])
    is_reseller: bool = Field(False, examples=[True])
    balance_last: int | None = Field(None, examples=[7851])
    used_count: int = Field(0, examples=[3])
    last_used_at: datetime | None = Field(None, examples=["2026-02-10T19:29:04.984Z"])
    last_device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    notes: str | None = Field(None, examples=["myim3 #1"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {
        "coerce_numbers_to_str": True,
        "from_attributes": True,
        "use_enum_values": True,
    }


class AccountUpdate(BaseModel):
    """Schema used to update an account's mutable fields."""

    email: str | None = Field(
        None, description="Update email if provided", examples=["new@example.com"]
    )
    pin: str | None = Field(None, description="Update or clear pin", examples=["1234"])
    notes: str | None = Field(None, description="Update notes", examples=["testing"])
    status: AccountStatus | None = Field(None, description="Set account status")
    is_reseller: bool | None = Field(None, description="Set reseller flag")
    last_device_id: str | None = Field(None, description="Update last device id")

    model_config = {
        "coerce_numbers_to_str": True,
        "use_enum_values": True,
    }


class AccountDelete(BaseModel):
    """Schema for deleting an account.

    The API can accept either an `id` or a combination of `msisdn` + `batch_id`.
    """

    id: int | None = Field(None, description="Primary key to delete")
    msisdn: str | None = Field(
        None, description="Phone number to delete (requires batch_id)"
    )

    @field_validator("msisdn", mode="before")
    @classmethod
    def validate_msisdn_for_delete(cls, v: str | None) -> str | None:
        """Validate msisdn for delete when provided."""
        if v is None:
            return v
        v = v.strip()
        if not v.isdigit():
            raise ValueError("msisdn must contain digits only (0-9)")
        if not (10 <= len(v) <= 13):
            raise ValueError("msisdn length must be between 10 and 13 digits")
        return v

    batch_id: str | None = Field(
        None, description="Batch id used together with msisdn for deletion"
    )

    model_config = {
        "coerce_numbers_to_str": True,
        "use_enum_values": True,
    }

    @field_validator("batch_id", mode="before")
    @classmethod
    def validate_batch_for_delete(cls, v: str | None, info):  # type: ignore[override]
        """Validate that batch_id and msisdn are provided together when required."""
        msisdn = info.data.get("msisdn")
        if msisdn and not v:
            raise ValueError("batch_id is required when msisdn is provided")
        if v and not msisdn:
            raise ValueError("msisdn is required when batch_id is provided")
        return v
