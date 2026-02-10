"""Shared status enums for models."""

from enum import StrEnum


class AccountStatus(StrEnum):
    """Account lifecycle status."""

    NEW = "new"  # account baru dibuat, belum pernah digunakan
    ACTIVE = (
        "active"  # account aktif, saat sudah binding dan bisa digunakan untuk transaksi
    )
    EXHAUSTED = "exhausted"  # account pulsa habis, tidak bisa dipakai transaksi
    DISABLED = "disabled"  # account dinonaktifkan secara manual atau otomatis
