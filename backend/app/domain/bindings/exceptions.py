"""Binding domain exceptions."""

from app.domain.common.exceptions import DomainException


class BindingDomainException(DomainException):
    """Base exception for binding domain."""

    def __init__(
        self,
        message: str,
        error_code: str = "binding_domain_error",
        context: dict | None = None,
    ):
        super().__init__(message, error_code, context)


class AccountAlreadyBoundError(BindingDomainException):
    """Raised when trying to bind an account that is already bound."""

    def __init__(
        self,
        account_id: int,
        existing_binding_id: int | None = None,
    ):
        msg = f"Account {account_id} is already bound"
        context = {"account_id": account_id}
        if existing_binding_id:
            context["existing_binding_id"] = existing_binding_id
            msg += f" to binding {existing_binding_id}"

        super().__init__(
            message=msg,
            error_code="account_already_bound",
            context=context,
        )


class BindingNotFoundError(BindingDomainException):
    """Raised when a binding is not found."""

    def __init__(
        self,
        binding_id: int,
        message: str | None = None,
    ):
        msg = message or f"Binding with ID {binding_id} not found"
        super().__init__(
            message=msg,
            error_code="binding_not_found",
            context={"binding_id": binding_id},
        )


class BindingValidationError(BindingDomainException):
    """Raised when binding validation fails."""

    def __init__(
        self,
        message: str,
        error_code: str = "binding_validation_error",
        context: dict | None = None,
    ):
        super().__init__(message, error_code, context)


class InvalidWorkflowTransitionError(BindingDomainException):
    """Raised when an invalid workflow transition is attempted."""

    def __init__(
        self,
        current_step: str,
        target_step: str,
        action: str | None = None,
    ):
        msg = f"Cannot transition from '{current_step}' to '{target_step}'"
        context = {
            "current_step": current_step,
            "target_step": target_step,
        }
        if action:
            context["action"] = action
            msg += f" (action: {action})"

        super().__init__(
            message=msg,
            error_code="invalid_workflow_transition",
            context=context,
        )
