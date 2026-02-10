"""represents the various steps in the binding process."""

from enum import StrEnum


class BindingStep(StrEnum):
    """Binding process steps for MSISDN lifecycle."""

    BOUND = "bound"
    OTP_REQUESTED = "otp_requested"
    LOGGED_IN = "logged_in"
    RESELLER_VERIFIED = "reseller_verified"


class DisabledReason(StrEnum):
    """Reasons for disabling a binding."""

    OTP_FAILED = "otp_verification_failed"
    NOT_RESELLER = "not_reseller"
    MANUAL = "manual"
    REPLACED = "replaced_by_new_msisdn"
    ERROR = "unexpected_error"
