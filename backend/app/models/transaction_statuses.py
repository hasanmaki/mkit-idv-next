"""Enums for transaction statuses."""

from enum import StrEnum


class TransactionStatus(StrEnum):
    """Transaction lifecycle status."""

    PROCESSING = "PROCESSING"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"
    SUKSES = "SUKSES"
    SUSPECT = "SUSPECT"
    GAGAL = "GAGAL"


class TransactionOtpStatus(StrEnum):
    """OTP status for transactions."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
