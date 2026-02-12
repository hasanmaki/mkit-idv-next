"""Workflow guard service for state-machine validations."""

from app.core.exceptions import AppValidationError
from app.models.steps import BindingStep
from app.models.transaction_statuses import TransactionStatus


class WorkflowGuardService:
    """Centralized state transition guards for binding and transaction flows."""

    @staticmethod
    def ensure_binding_step(
        *,
        action: str,
        current: BindingStep,
        allowed: set[BindingStep],
        context: dict | None = None,
    ) -> None:
        """Ensure binding step is in the allowed set for an action."""
        if current not in allowed:
            raise AppValidationError(
                message=(
                    f"Action '{action}' tidak valid untuk step '{current}'. "
                    f"Allowed: {[step.value for step in sorted(allowed)]}"
                ),
                error_code="binding_invalid_step_transition",
                context={
                    "action": action,
                    "current_step": current.value,
                    "allowed_steps": [step.value for step in sorted(allowed)],
                    **(context or {}),
                },
            )

    @staticmethod
    def ensure_transaction_status(
        *,
        action: str,
        current: TransactionStatus,
        allowed: set[TransactionStatus],
        context: dict | None = None,
    ) -> None:
        """Ensure transaction status is in the allowed set for an action."""
        if current not in allowed:
            raise AppValidationError(
                message=(
                    f"Action '{action}' tidak valid untuk status '{current}'. "
                    f"Allowed: {[status.value for status in sorted(allowed)]}"
                ),
                error_code="transaction_invalid_status_transition",
                context={
                    "action": action,
                    "current_status": current.value,
                    "allowed_statuses": [status.value for status in sorted(allowed)],
                    **(context or {}),
                },
            )

