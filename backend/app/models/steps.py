"""Represents the various steps in the binding process."""

from enum import StrEnum


class BindingStep(StrEnum):
    """Binding process steps for MSISDN lifecycle."""

    BOUND = "bound"
    OTP_REQUESTED = "otp_requested"
    OTP_VERIFICATION = "otp_verification"
    OTP_VERIFIED = "otp_verified"
    TOKEN_LOGIN_FETCHED = "token_login_fetched"
    LOGGED_OUT = "logged_out"
