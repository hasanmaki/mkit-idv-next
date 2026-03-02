"""API schemas for session endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SessionCreateRequest(BaseModel):
    """Request schema for creating a session."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Session name",
        examples=["Operator 1", "Main Session", "Production"],
    )
    email: EmailStr = Field(
        ...,
        description="Session email (unique identifier)",
        examples=["operator@example.com", "admin@company.com"],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Optional description",
        examples=["Main operator session"],
    )
    is_active: bool = Field(
        True,
        description="Whether session is active",
    )
    notes: str | None = Field(
        None,
        max_length=500,
        description="Additional notes",
        examples=["Primary session for production"],
    )


class SessionUpdateRequest(BaseModel):
    """Request schema for updating a session."""

    name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    description: str | None = Field(None, max_length=255)
    is_active: bool | None = None
    notes: str | None = Field(None, max_length=500)


class SessionStatusUpdateRequest(BaseModel):
    """Request schema for toggling session status."""

    is_active: bool


class SessionResponse(BaseModel):
    """Response schema for session."""

    id: int = Field(..., examples=[1])
    name: str = Field(..., examples=["Operator 1"])
    email: str = Field(..., examples=["operator@example.com"])
    description: str | None = Field(None, examples=["Main operator session"])
    is_active: bool = Field(..., examples=[True])
    notes: str | None = Field(None, examples=["Primary session"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True}
