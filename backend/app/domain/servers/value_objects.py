"""Server domain value objects."""

from typing import Annotated

from pydantic import Field, field_validator

from app.domain.common.value_objects import ValueObject


class ServerId(ValueObject):
    """Value object for Server ID."""

    value: int = Field(gt=0, description="Server identifier")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value


class ServerUrl(ValueObject):
    """Value object for Server URL.

    Ensures URL is properly formatted with protocol and port.
    """

    value: str = Field(
        ...,
        min_length=10,
        max_length=255,
        description="Full server URL including protocol and port",
        examples=["http://localhost:9900", "https://example.com:8080"],
    )

    @field_validator("value")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Validate URL format."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with 'http://' or 'https://'")

        # Extract host part after protocol
        parts = v.split("//", 1)
        if len(parts) != 2:
            raise ValueError("Invalid URL format")

        host_part = parts[1]
        if ":" not in host_part:
            raise ValueError("URL must include a port number")

        return v

    @property
    def host(self) -> str:
        """Extract host without port."""
        parts = self.value.split("//", 1)
        if len(parts) != 2:
            return ""
        host_with_port = parts[1]
        return f"{parts[0]}//{host_with_port.split(':')[0]}"

    @property
    def port(self) -> int:
        """Extract port number."""
        parts = self.value.split("//", 1)
        if len(parts) != 2:
            raise ValueError("Invalid URL format")
        host_part = parts[1]
        port_str = host_part.split(":")[1].split("/")[0]
        return int(port_str)

    def __str__(self) -> str:
        return self.value


class ServerConfig(ValueObject):
    """Value object for Server configuration settings."""

    timeout: Annotated[
        int,
        Field(ge=1, le=30, description="Request timeout in seconds"),
    ] = 10
    retries: Annotated[
        int,
        Field(ge=0, le=10, description="Number of retry attempts"),
    ] = 3
    wait_between_retries: Annotated[
        int,
        Field(ge=0, le=10, description="Seconds to wait between retries"),
    ] = 1
    max_requests_queued: Annotated[
        int,
        Field(ge=1, le=20, description="Max concurrent requests allowed"),
    ] = 5

    def __str__(self) -> str:
        return (
            f"ServerConfig(timeout={self.timeout}, retries={self.retries}, "
            f"wait={self.wait_between_retries}, max_queued={self.max_requests_queued})"
        )
