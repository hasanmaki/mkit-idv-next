# app/models/transactions.py


from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Transactions(Base, TimestampMixin):
    """Log of all exchange transactions."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Identitas transaksi
    trx_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # Konteks
    server_id: Mapped[int] = mapped_column(
        ForeignKey("servers.id"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), nullable=False, index=True
    )
    binding_id: Mapped[int] = mapped_column(
        ForeignKey("bindings.id"), nullable=False, index=True
    )

    # Detail transaksi
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # dalam IDR
    product_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    voucher_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", doc="pending, success, failed"
    )
    error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Audit
    is_first_transaction: Mapped[bool] = mapped_column(default=False, nullable=False)
    requires_otp: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Transaction trx_id={self.trx_id} msisdn={self.msisdn} status={self.status}>"
