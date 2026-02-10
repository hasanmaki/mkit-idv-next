"""schemas for server management."""
# app/services/servers/schemas.py

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ServerCreate(BaseModel):
    """Schema for creating a new server instance."""

    port: int = Field(
        gt=0,
        lt=65536,
        description="Port number the server listens on",
        examples=[9900, 8080, 5000],
    )
    base_url: str = Field(
        ...,
        min_length=10,
        max_length=255,
        description="Full base URL including protocol and port",
        examples=["http://localhost:9900", "https://example.com:8080"],
    )
    description: str | None = Field(
        None,
        max_length=100,
        description="Optional human-readable description",
        examples=["myim3 Bot #1"],
    )
    timeout: int = Field(
        10,
        ge=1,
        le=30,
        description="Request timeout in seconds",
    )
    retries: int = Field(
        3,
        ge=0,
        le=10,
        description="Number of retry attempts on failure",
    )
    wait_between_retries: int = Field(
        1,
        ge=0,
        le=10,
        description="Seconds to wait between retries",
    )
    max_requests_queued: int = Field(
        5,
        ge=1,
        le=20,
        description="Max concurrent requests allowed",
    )
    is_active: bool = Field(
        True,
        description="Whether the server is enabled for use",
    )
    notes: str | None = Field(
        None,
        max_length=255,
        description="Additional notes or metadata",
    )

    @field_validator("base_url", mode="before")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base_url starts with http:// or https:// and include the port."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("base_url must start with 'http://' or 'https://''")
        if ":" not in v.split("//")[1]:
            raise ValueError("base_url must include a port number")
        return v


class ServerUpdate(BaseModel):
    """Schema for updating an existing server."""

    description: str | None = Field(None, max_length=100)
    timeout: int | None = Field(None, ge=1, le=30)
    retries: int | None = Field(None, ge=0, le=10)
    wait_between_retries: int | None = Field(None, ge=0, le=10)
    max_requests_queued: int | None = Field(None, ge=1, le=20)
    is_active: bool | None = None
    notes: str | None = Field(None, max_length=255)


class ServerResponse(BaseModel):
    """Schema for server response."""

    id: int
    port: int
    base_url: str
    description: str | None
    timeout: int
    retries: int
    wait_between_retries: int
    max_requests_queued: int
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
