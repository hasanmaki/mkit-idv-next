"""Model untuk Bindings antara Accounts (MSISDN) dan Server Instance."""

from sqlalchemy import Enum, ForeignKey, Integer
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

    step: Mapped[BindingStep] = mapped_column(
        Enum(BindingStep, name="binding_step"),
        default=BindingStep.BOUND,
        nullable=False,
    )

    is_reseller: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Binding id={self.id} account_id={self.account_id} "
            f"server_id={self.server_id} step={self.step}>"
        )
