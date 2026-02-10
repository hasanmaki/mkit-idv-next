"""Schemas for transaction service."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.transaction_statuses import TransactionOtpStatus, TransactionStatus


class TransactionCreate(BaseModel):
    """Create transaction header after trx_idv."""

    binding_id: int = Field(..., description="Binding ID")
    trx_id: str = Field(..., description="trx_id from trx_idv")
    t_id: str | None = Field(None, description="t_id from trx_idv")
    product_id: str | None = Field(None, description="Product ID")
    email: str | None = Field(None, description="Email used in trx")
    limit_harga: int | None = Field(None, description="limit_harga")
    amount: int | None = Field(None, description="Amount")
    is_success: int | None = Field(None, description="is_success from trx_idv")
    otp_required: bool = Field(False, description="OTP required")
    error_message: str | None = None

    model_config = {"use_enum_values": True}


class TransactionStatusUpdate(BaseModel):
    """Update transaction status after status_idv."""

    status: TransactionStatus = Field(..., description="PROCESSING/SUKSES/SUSPECT/GAGAL")
    is_success: int | None = None
    voucher_code: str | None = None
    error_message: str | None = None
    otp_status: TransactionOtpStatus | None = None

    model_config = {"use_enum_values": True}


class TransactionSnapshotCreate(BaseModel):
    """Create snapshot with balance_start and trx_idv_raw."""

    balance_start: int | None = None
    trx_idv_raw: dict | None = None

    model_config = {"use_enum_values": True}


class TransactionSnapshotUpdate(BaseModel):
    """Update snapshot with balance_end and status_idv_raw."""

    balance_end: int | None = None
    status_idv_raw: dict | None = None

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
