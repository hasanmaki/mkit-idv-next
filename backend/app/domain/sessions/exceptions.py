"""Session domain exceptions."""

from app.domain.common.exceptions import DomainException


class SessionDomainException(DomainException):
    """Base exception for session domain."""

    def __init__(
        self,
        message: str,
        error_code: str = "session_domain_error",
        context: dict | None = None,
    ):
        super().__init__(message, error_code, context)


class SessionNotFoundError(SessionDomainException):
    """Raised when a session is not found."""

    def __init__(
        self,
        session_id: int,
        message: str | None = None,
    ):
        msg = message or f"Session with ID {session_id} not found"
        super().__init__(
            message=msg,
            error_code="session_not_found",
            context={"session_id": session_id},
        )


class SessionDuplicateError(SessionDomainException):
    """Raised when creating a session with duplicate email."""

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
            error_code="session_duplicate",
            context=context,
        )
