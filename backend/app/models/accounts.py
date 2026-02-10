"""Model untuk Accounts (MSISDN) yang tersedia di sistem."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin
from app.models.statuses import AccountStatus


class Accounts(Base, TimestampMixin):
    """Account/MSISDN record."""

    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("msisdn", "batch_id", name="uq_msisdn_batch"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    msisdn: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.NEW,
        nullable=False,
        index=True,
    )
    is_reseller: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance_last: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Account id={self.id} msisdn={self.msisdn} "
            f"batch_id={self.batch_id} status={self.status}>"
        )
