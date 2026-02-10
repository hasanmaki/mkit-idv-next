"""Model untuk Bindings antara MSISDN dan Server Instance."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin
from app.models.steps import BindingStep, DisabledReason


class Bindings(Base, TimestampMixin):
    """Active MSISDN bound to a server instance."""

    __tablename__ = "bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    server_id: Mapped[int] = mapped_column(
        ForeignKey("servers.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    msisdn: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    step: Mapped[BindingStep] = mapped_column(default=BindingStep.BOUND, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    disabled_reason: Mapped[DisabledReason | None] = mapped_column(
        String(100), nullable=True
    )

    is_reseller: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance: Mapped[int | None] = mapped_column(Integer, nullable=True)

    bound_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Binding id={self.id} msisdn={self.msisdn} step={self.step} active={self.is_active}>"
