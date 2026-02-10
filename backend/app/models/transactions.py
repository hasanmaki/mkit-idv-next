"""Transaction models for voucher exchange."""

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin
from app.models.transaction_statuses import TransactionOtpStatus, TransactionStatus


class Transactions(Base, TimestampMixin):
    """Header transaksi voucher."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Identitas transaksi
    trx_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    t_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

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
    batch_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Detail transaksi
    product_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    limit_harga: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voucher_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"),
        nullable=False,
        default=TransactionStatus.PROCESSING,
        doc="PROCESSING, SUKSES, SUSPECT, GAGAL",
    )
    is_success: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    otp_required: Mapped[bool] = mapped_column(default=False, nullable=False)
    otp_status: Mapped[TransactionOtpStatus | None] = mapped_column(
        Enum(TransactionOtpStatus, name="transaction_otp_status"), nullable=True
    )

    def __repr__(self) -> str:
        """Return a compact representation of the Transaction for debugging."""
        return f"<Transaction trx_id={self.trx_id} status={self.status}>"


class TransactionSnapshots(Base, TimestampMixin):
    """Snapshot bukti saldo dan response transaksi."""

    __tablename__ = "transaction_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"), nullable=False, index=True
    )

    balance_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balance_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    trx_idv_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status_idv_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        """Return a short representation of the TransactionSnapshot for debugging."""
        return (
            f"<TransactionSnapshot id={self.id} transaction_id={self.transaction_id}>"
        )
