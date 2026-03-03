"""Model untuk Accounts (MSISDN) yang tersedia di sistem."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Accounts(Base, TimestampMixin):
    """Account/MSISDN record - linked to an order.

    Simple account model focused on balance tracking.
    """

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

    # Simple active flag
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    # Balance tracking - from balance check response
    balance_last: Mapped[int | None] = mapped_column(Integer, nullable=True)
    card_active_until: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grace_period_until: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expires_info: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_balance_response: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, default=None, nullable=True
    )

    # Usage tracking
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """Return a short string representation of the Account for debugging."""
        return (
            f"<Account id={self.id} msisdn={self.msisdn} "
            f"order_id={self.order_id} active={self.is_active}>"
        )
