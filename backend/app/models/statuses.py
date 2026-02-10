"""Shared status enums for models."""

from enum import StrEnum


class AccountStatus(StrEnum):
    """Account lifecycle status."""

    NEW = "new"
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    DISABLED = "disabled"
