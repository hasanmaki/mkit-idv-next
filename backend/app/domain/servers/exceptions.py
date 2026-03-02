"""Server domain exceptions."""

from app.domain.common.exceptions import DomainException


class ServerDomainException(DomainException):
    """Base exception for server domain."""

    def __init__(
        self,
        message: str,
        error_code: str = "server_domain_error",
        context: dict | None = None,
    ):
        super().__init__(message, error_code, context)


class ServerNotFoundError(ServerDomainException):
    """Raised when a server is not found."""

    def __init__(
        self,
        server_id: int,
        message: str | None = None,
    ):
        msg = message or f"Server with ID {server_id} not found"
        super().__init__(
            message=msg,
            error_code="server_not_found",
            context={"server_id": server_id},
        )


class ServerDuplicateError(ServerDomainException):
    """Raised when creating a server with duplicate port or URL."""

    def __init__(
        self,
        field: str,
        value: str | int,
        existing_id: int | None = None,
    ):
        field_display = "Port" if field == "port" else "Base URL"
        msg = f"{field_display} '{value}' is already in use"
        context = {field: value}
        if existing_id:
            context["existing_server_id"] = existing_id
            msg += f" by server ID {existing_id}"

        super().__init__(
            message=msg,
            error_code="server_duplicate",
            context=context,
        )


class ServerBulkValidationError(ServerDomainException):
    """Raised when bulk server creation has validation errors."""

    def __init__(
        self,
        errors: list[dict],
        message: str | None = None,
    ):
        msg = message or "Bulk server creation validation failed"
        super().__init__(
            message=msg,
            error_code="server_bulk_validation_error",
            context={"errors": errors},
        )
