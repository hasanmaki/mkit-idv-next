"""Session domain value objects."""

import re

from pydantic import Field, field_validator

from app.domain.common.value_objects import ValueObject


class SessionId(ValueObject):
    """Value object for Session ID."""

    value: int = Field(gt=0, description="Session identifier")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value


class SessionName(ValueObject):
    """Value object for Session Name.

    Ensures name is properly formatted and within length limits.
    """

    value: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Session name",
        examples=["Operator 1", "Main Session", "Production"],
    )

    @field_validator("value")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Validate name format."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()

    def __str__(self) -> str:
        return self.value


class SessionEmail(ValueObject):
    """Value object for Session Email.

    Ensures email is properly formatted.
    """

    value: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Session email (unique identifier)",
        examples=["operator@example.com", "admin@company.com"],
    )

    @field_validator("value")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format."""
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    def __str__(self) -> str:
        return self.value
