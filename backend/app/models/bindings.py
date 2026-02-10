"""Model untuk Bindings antara Accounts (MSISDN) dan Server Instance."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin
from app.models.steps import BindingStep


class Bindings(Base, TimestampMixin):
    """Active MSISDN bound to a server instance."""

    __tablename__ = "bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    server_id: Mapped[int] = mapped_column(
        ForeignKey("servers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    batch_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    step: Mapped[BindingStep] = mapped_column(
        Enum(BindingStep, name="binding_step"),
        default=BindingStep.BOUND,
        nullable=False,
    )

    is_reseller: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balance_last: Mapped[int | None] = mapped_column(Integer, nullable=True)

    last_error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_login: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    token_location: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    bound_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    unbound_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Binding id={self.id} account_id={self.account_id} "
            f"server_id={self.server_id} step={self.step}>"
        )
