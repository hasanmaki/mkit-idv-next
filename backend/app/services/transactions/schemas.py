"""Schemas for transaction service."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.transaction_statuses import TransactionOtpStatus, TransactionStatus


class TransactionCreate(BaseModel):
    """Create transaction header after trx_idv."""

    binding_id: int = Field(..., description="Binding ID", examples=[10])
    trx_id: str = Field(..., description="trx_id from trx_idv", examples=["2208fd6ca3e6e5ab53b23bfbb72d6e9e"])
    t_id: str | None = Field(None, description="t_id from trx_idv", examples=["dc23d2f32c704dea928323e90f9f2994"])
    product_id: str | None = Field(None, description="Product ID", examples=["650"])
    email: str | None = Field(None, description="Email used in trx", examples=["user@example.com"])
    limit_harga: int | None = Field(None, description="limit_harga", examples=[100000])
    amount: int | None = Field(None, description="Amount", examples=[100000])
    is_success: int | None = Field(None, description="is_success from trx_idv", examples=[2])
    otp_required: bool = Field(False, description="OTP required", examples=[True])
    error_message: str | None = None

    model_config = {"use_enum_values": True}


class TransactionStatusUpdate(BaseModel):
    """Update transaction status after status_idv."""

    status: TransactionStatus = Field(..., description="PROCESSING/SUKSES/SUSPECT/GAGAL", examples=[TransactionStatus.SUKSES])
    is_success: int | None = Field(None, examples=[2])
    voucher_code: str | None = Field(None, examples=["P8JF876WSSY9P8EB"])
    error_message: str | None = Field(None, examples=["Invalid OTP"])
    otp_status: TransactionOtpStatus | None = Field(None, examples=[TransactionOtpStatus.SUCCESS])

    model_config = {"use_enum_values": True}


class TransactionSnapshotCreate(BaseModel):
    """Create snapshot with balance_start and trx_idv_raw."""

    balance_start: int | None = Field(None, examples=[7851])
    trx_idv_raw: dict | None = Field(None, examples=[{"res": {"data": {"trx_id": "..."}}}])

    model_config = {"use_enum_values": True}


class TransactionSnapshotUpdate(BaseModel):
    """Update snapshot with balance_end and status_idv_raw."""

    balance_end: int | None = Field(None, examples=[0])
    status_idv_raw: dict | None = Field(None, examples=[{"res": {"data": {"voucher": "..."}}}])

    model_config = {"use_enum_values": True}


class TransactionStartRequest(BaseModel):
    """Start transaction orchestration."""

    binding_id: int = Field(..., description="Binding ID", examples=[10])
    product_id: str = Field(..., description="Product ID", examples=["650"])
    email: str = Field(..., description="Email", examples=["user@example.com"])
    limit_harga: int = Field(..., description="Limit harga", examples=[100000])
    otp_required: bool = Field(False, description="OTP required for first trx", examples=[True])

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


class TransactionCreateRequest(BaseModel):
    """Create transaction + optional snapshot in one request."""

    transaction: TransactionCreate
    snapshot: TransactionSnapshotCreate | None = None

    model_config = {"use_enum_values": True}


class TransactionRead(BaseModel):
    """Read transaction header."""

    id: int
    trx_id: str
    t_id: str | None
    server_id: int
    account_id: int
    binding_id: int
    batch_id: str
    device_id: str | None
    product_id: str | None
    email: str | None
    limit_harga: int | None
    amount: int | None
    voucher_code: str | None
    status: TransactionStatus
    is_success: int | None
    error_message: str | None
    otp_required: bool
    otp_status: TransactionOtpStatus | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class TransactionSnapshotRead(BaseModel):
    """Read transaction snapshot."""

    id: int
    transaction_id: int
    balance_start: int | None
    balance_end: int | None
    trx_idv_raw: dict | None
    status_idv_raw: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}
