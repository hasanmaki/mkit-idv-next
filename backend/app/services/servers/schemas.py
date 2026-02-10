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
        examples=[10],
    )
    retries: int = Field(
        3,
        ge=0,
        le=10,
        description="Number of retry attempts on failure",
        examples=[3],
    )
    wait_between_retries: int = Field(
        1,
        ge=0,
        le=10,
        description="Seconds to wait between retries",
        examples=[1],
    )
    max_requests_queued: int = Field(
        5,
        ge=1,
        le=20,
        description="Max concurrent requests allowed",
        examples=[5],
    )
    is_active: bool = Field(
        True,
        description="Whether the server is enabled for use",
    )
    notes: str | None = Field(
        None,
        max_length=255,
        description="Additional notes or metadata",
        examples=["server pool A"],
    )
    device_id: str | None = Field(
        None,
        max_length=100,
        description="Optional device id for this server instance",
        examples=["0ee0deeb75df0bca"],
    )

    model_config = {"use_enum_values": True}

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

    description: str | None = Field(None, max_length=100, examples=["myim3 Bot #2"])
    timeout: int | None = Field(None, ge=1, le=30, examples=[12])
    retries: int | None = Field(None, ge=0, le=10, examples=[2])
    wait_between_retries: int | None = Field(None, ge=0, le=10, examples=[1])
    max_requests_queued: int | None = Field(None, ge=1, le=20, examples=[8])
    is_active: bool | None = None
    notes: str | None = Field(None, max_length=255, examples=["maintenance"])
    device_id: str | None = Field(None, max_length=100, examples=["0ee0deeb75df0bca"])

    model_config = {"use_enum_values": True}


class ServerResponse(BaseModel):
    """Schema for server response."""

    id: int = Field(..., examples=[1])
    port: int = Field(..., examples=[9900])
    base_url: str = Field(..., examples=["http://localhost:9900"])
    description: str | None = Field(None, examples=["myim3 Bot #1"])
    timeout: int = Field(..., examples=[10])
    retries: int = Field(..., examples=[3])
    wait_between_retries: int = Field(..., examples=[1])
    max_requests_queued: int = Field(..., examples=[5])
    is_active: bool = Field(..., examples=[True])
    notes: str | None = Field(None, examples=["server pool A"])
    device_id: str | None = Field(None, examples=["0ee0deeb75df0bca"])
    created_at: datetime = Field(..., examples=["2026-02-10T19:00:00.000Z"])
    updated_at: datetime = Field(..., examples=["2026-02-10T19:30:00.000Z"])

    model_config = {"from_attributes": True, "use_enum_values": True}
