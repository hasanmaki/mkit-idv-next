"""Model untuk Bindings antara Accounts (MSISDN) dan Server instance."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Bindings(Base, TimestampMixin):
    """Binding antara Order, Account, dan Server.

    Satu account hanya bisa di-bind sekali di seluruh sistem.
    Binding merepresentasikan "pakaian yang sedang dicuci di mesin tertentu untuk grup tertentu".
    """

    __tablename__ = "bindings"
    __table_args__ = (
        UniqueConstraint('account_id', name='uq_binding_account'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Ownership - Order adalah "grup" yang punya binding
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Resource bindings
    server_id: Mapped[int] = mapped_column(
        ForeignKey("servers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    
    # Workflow tracking (simplified)
    step: Mapped[str] = mapped_column(
        String(50),
        default="BINDED",
        nullable=False,
        index=True,
    )  # BINDED, REQUEST_OTP, VERIFY_OTP, VERIFIED, LOGGED_OUT
    
    # Device untuk OTP
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Control
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Balance tracking
    balance_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balance_source: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # 'MANUAL' atau 'AUTO_CHECK'
    
    # Metadata
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
