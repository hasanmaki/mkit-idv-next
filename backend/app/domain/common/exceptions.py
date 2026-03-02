"""Domain exceptions for business rule violations."""

from app.core.exceptions.base import AppBaseExceptionError


class DomainException(AppBaseExceptionError):
    """Base exception for all domain-related errors.

    Use this for business rule violations and domain invariants.

    Extends AppBaseExceptionError to ensure proper HTTP status code
    and error details are propagated to the API response.
    """

    DEFAULT_STATUS_CODE: int = 400
    DEFAULT_CODE: str = "domain_error"
    EXPOSE_CONTEXT: bool = True

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict | None = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )
