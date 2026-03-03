"""Model untuk Accounts (MSISDN) yang tersedia di sistem."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin
from app.models.statuses import AccountStatus


class Accounts(Base, TimestampMixin):
    """Account/MSISDN record - linked to an order."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("msisdn", "order_id", name="uq_msisdn_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Link to order
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Account details
    msisdn: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # Status
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.NEW,
        nullable=False,
        index=True,
    )
    is_reseller: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Tracking
    balance_last: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """Return a short string representation of the Account for debugging."""
        return (
            f"<Account id={self.id} msisdn={self.msisdn} "
            f"order_id={self.order_id} status={self.status}>"
        )
