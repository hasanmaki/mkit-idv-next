"""Schemas for transaction service."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.transaction_statuses import TransactionOtpStatus, TransactionStatus


class TransactionCreate(BaseModel):
    """Create transaction header after trx_idv."""

    binding_id: int = Field(..., description="Binding ID", examples=[10])
    trx_id: str = Field(
        ...,
        description="trx_id from trx_idv",
        examples=["2208fd6ca3e6e5ab53b23bfbb72d6e9e"],
    )
    t_id: str | None = Field(
        None,
        description="t_id from trx_idv",
        examples=["dc23d2f32c704dea928323e90f9f2994"],
    )
    product_id: str | None = Field(None, description="Product ID", examples=["650"])
    email: str | None = Field(
        None, description="Email used in trx", examples=["user@example.com"]
    )
    limit_harga: int | None = Field(None, description="limit_harga", examples=[100000])
    amount: int | None = Field(None, description="Amount", examples=[100000])
    is_success: int | None = Field(
        None, description="is_success from trx_idv", examples=[2]
    )
    otp_required: bool = Field(False, description="OTP required", examples=[True])
    error_message: str | None = None

    model_config = {"use_enum_values": True}


class TransactionStatusUpdate(BaseModel):
    """Update transaction status after status_idv."""

    status: TransactionStatus = Field(
        ...,
        description="PROCESSING/SUKSES/SUSPECT/GAGAL",
        examples=[TransactionStatus.SUKSES],
    )
    is_success: int | None = Field(None, examples=[2])
    voucher_code: str | None = Field(None, examples=["P8JF876WSSY9P8EB"])
    error_message: str | None = Field(None, examples=["Invalid OTP"])
    otp_status: TransactionOtpStatus | None = Field(
        None, examples=[TransactionOtpStatus.SUCCESS]
    )

    model_config = {"use_enum_values": True}


class TransactionSnapshotCreate(BaseModel):
    """Create snapshot with balance_start and trx_idv_raw."""

    balance_start: int | None = Field(None, examples=[7851])
    trx_idv_raw: dict | None = Field(
        None, examples=[{"res": {"data": {"trx_id": "..."}}}]
    )

    model_config = {"use_enum_values": True}


class TransactionSnapshotUpdate(BaseModel):
    """Update snapshot with balance_end and status_idv_raw."""

    balance_end: int | None = Field(None, examples=[0])
    status_idv_raw: dict | None = Field(
        None, examples=[{"res": {"data": {"voucher": "..."}}}]
    )

    model_config = {"use_enum_values": True}


class TransactionStartRequest(BaseModel):
    """Start transaction orchestration."""

    binding_id: int = Field(..., description="Binding ID", examples=[10])
    product_id: str = Field(..., description="Product ID", examples=["650"])
    email: str = Field(..., description="Email", examples=["user@example.com"])
    limit_harga: int = Field(..., description="Limit harga", examples=[100000])
    otp_required: bool = Field(
        False, description="OTP required for first trx", examples=[True]
    )

    model_config = {"use_enum_values": True}


class TransactionOtpRequest(BaseModel):
    """OTP input for transaction."""

    otp: str = Field(..., description="OTP code", examples=["358372"])

    model_config = {"use_enum_values": True}


class TransactionContinueRequest(BaseModel):
    """Continue transaction (after no OTP or retry status)."""

    model_config = {"use_enum_values": True}


class TransactionStopRequest(BaseModel):
    """Stop/abort transaction manually."""

    reason: str | None = Field(None, examples=["user_stop"])

    model_config = {"use_enum_values": True}


class TransactionPauseRequest(BaseModel):
    """Pause active transaction."""

    reason: str = Field(
        ..., description="Reason for pausing", examples=["manual_pause"]
    )

    model_config = {"use_enum_values": True}


class TransactionResumeRequest(BaseModel):
    """Resume paused transaction."""

    model_config = {"use_enum_values": True}


class TransactionCreateRequest(BaseModel):
    """Create transaction + optional snapshot in one request."""

    transaction: TransactionCreate
    snapshot: TransactionSnapshotCreate | None = None

    model_config = {"use_enum_values": True}


class TransactionRead(BaseModel):
    """Read transaction header."""

    id: int = Field(..., examples=[1])
    trx_id: str = Field(..., examples=["2208fd6ca3e6e5ab53b23bfbb72d6e9e"])
    t_id: str | None = Field(None, examples=["dc23d2f32c704dea928323e90f9f2994"])
    server_id: int = Field(..., examples=[1])
    account_id: int = Field(..., examples=[100])
    binding_id: int = Field(..., examples=[10])
    batch_id: str = Field(..., examples=["batch-2026-02-10"])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    product_id: str | None = Field(None, examples=["650"])
    email: str | None = Field(None, examples=["user@example.com"])
    limit_harga: int | None = Field(None, examples=[100000])
    amount: int | None = Field(None, examples=[100000])
    voucher_code: str | None = Field(None, examples=["P8JF876WSSY9P8EB"])
    status: TransactionStatus = Field(..., examples=[TransactionStatus.PROCESSING])
    is_success: int | None = Field(None, examples=[2])
    error_message: str | None = Field(None, examples=["Invalid OTP"])
    otp_required: bool = Field(..., examples=[True])
    otp_status: TransactionOtpStatus | None = Field(
        None, examples=[TransactionOtpStatus.PENDING]
    )
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True, "use_enum_values": True}


class TransactionSnapshotRead(BaseModel):
    """Read transaction snapshot."""

    id: int = Field(..., examples=[1])
    transaction_id: int = Field(..., examples=[1])
    balance_start: int | None = Field(None, examples=[7851])
    balance_end: int | None = Field(None, examples=[0])
    trx_idv_raw: dict | None = Field(
        None, examples=[{"res": {"data": {"trx_id": "..."}}}]
    )
    status_idv_raw: dict | None = Field(
        None, examples=[{"res": {"data": {"voucher": "..."}}}]
    )
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True, "use_enum_values": True}
