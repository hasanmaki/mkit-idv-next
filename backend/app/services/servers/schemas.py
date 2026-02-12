"""schemas for server management."""
# app/services/servers/schemas.py

from datetime import datetime

from pydantic import BaseModel, Field, ValidationInfo, field_validator


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


class ServerCreateBulk(BaseModel):
    """Schema for creating many servers from a host and port range."""

    base_host: str = Field(
        ...,
        min_length=10,
        max_length=255,
        description="Host without port, e.g. http://10.0.0.3",
        examples=["http://10.0.0.3", "http://localhost"],
    )
    start_port: int = Field(
        ...,
        gt=0,
        lt=65536,
        description="Range start port (inclusive)",
        examples=[9900],
    )
    end_port: int = Field(
        ...,
        gt=0,
        lt=65536,
        description="Range end port (inclusive)",
        examples=[9909],
    )
    description: str | None = Field(
        None,
        max_length=100,
        description="Optional description for each server",
        examples=["myim3 Bot"],
    )
    timeout: int = Field(10, ge=1, le=30, examples=[10])
    retries: int = Field(3, ge=0, le=10, examples=[3])
    wait_between_retries: int = Field(1, ge=0, le=10, examples=[1])
    max_requests_queued: int = Field(5, ge=1, le=20, examples=[5])
    is_active: bool = Field(True, description="Whether each server is enabled")
    notes: str | None = Field(
        None,
        max_length=255,
        description="Additional notes for each server",
        examples=["pool A"],
    )
    device_id: str | None = Field(
        None,
        max_length=100,
        description="Optional shared device id",
        examples=["0ee0deeb75df0bca"],
    )

    model_config = {"use_enum_values": True}

    @field_validator("base_host", mode="before")
    @classmethod
    def validate_base_host(cls, v: str) -> str:
        """Ensure base_host starts with protocol and has no trailing slash."""
        value = v.strip().rstrip("/")
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("base_host must start with 'http://' or 'https://'")
        return value

    @field_validator("end_port")
    @classmethod
    def validate_port_range(cls, v: int, info: ValidationInfo) -> int:
        """Validate that end_port is not below start_port and range is bounded."""
        start_port = info.data.get("start_port")
        if start_port is not None and v < start_port:
            raise ValueError("end_port must be greater than or equal to start_port")
        if start_port is not None and (v - start_port) > 500:
            raise ValueError("maximum bulk range is 501 ports")
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


class ServerBulkItemResult(BaseModel):
    """Per-port result item for bulk creation."""

    port: int = Field(..., examples=[9900])
    base_url: str = Field(..., examples=["http://10.0.0.3:9900"])
    status: str = Field(..., examples=["created", "would_create", "skipped", "failed"])
    reason: str | None = Field(None, examples=["port already in use"])
    server: ServerResponse | None = None

    model_config = {"use_enum_values": True}


class ServerBulkCreateResult(BaseModel):
    """Summary result for bulk server creation."""

    dry_run: bool = Field(..., examples=[False])
    base_host: str = Field(..., examples=["http://10.0.0.3"])
    start_port: int = Field(..., examples=[9900])
    end_port: int = Field(..., examples=[9909])
    total_requested: int = Field(..., examples=[10])
    total_created: int = Field(..., examples=[8])
    total_skipped: int = Field(..., examples=[2])
    total_failed: int = Field(..., examples=[0])
    items: list[ServerBulkItemResult]

    model_config = {"use_enum_values": True}
