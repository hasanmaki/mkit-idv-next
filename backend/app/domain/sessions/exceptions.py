"""Session domain exceptions."""

from app.domain.common.exceptions import DomainException


class SessionDomainException(DomainException):
    """Base exception for session domain."""

    DEFAULT_STATUS_CODE: int = 400
    DEFAULT_CODE: str = "session_domain_error"

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict | None = None,
    ):
        super().__init__(message, error_code or self.DEFAULT_CODE, context)


class SessionNotFoundError(SessionDomainException):
    """Raised when a session is not found."""

    DEFAULT_STATUS_CODE: int = 404
    DEFAULT_CODE: str = "session_not_found"

    def __init__(
        self,
        session_id: int,
        message: str | None = None,
    ):
        msg = message or f"Session with ID {session_id} not found"
        super().__init__(
            message=msg,
            context={"session_id": session_id},
        )


class SessionDuplicateError(SessionDomainException):
    """Raised when creating a session with duplicate email."""

    DEFAULT_CODE: str = "session_duplicate"

    def __init__(
        self,
        email: str,
        existing_id: int | None = None,
    ):
        msg = f"Email '{email}' is already registered"
        context = {"email": email}
        if existing_id:
            context["existing_session_id"] = existing_id
            msg += f" by session ID {existing_id}"

        super().__init__(
            message=msg,
            context=context,
        )
