"""Domain exceptions for business rule violations."""


class DomainException(Exception):
    """Base exception for all domain-related errors.

    Use this for business rule violations and domain invariants.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict | None = None,
    ):
        self.message = message
        self.error_code = error_code or "domain_error"
        self.context = context or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }
