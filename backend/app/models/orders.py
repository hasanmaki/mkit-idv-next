"""Model untuk Orders - entitas utama untuk manajemen customer orders."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Orders(Base, TimestampMixin):
    """Order record - merepresentasikan customer order yang dapat memiliki multiple accounts.

    Order adalah entitas utama yang mewakili customer,
    dengan daftar MSISDN yang akan di-bind ke server.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Customer identity
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Default credentials for accounts
    default_pin: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Order status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        """Return a short string representation of the Order for debugging."""
        return (
            f"<Order id={self.id} name='{self.name}' "
            f"email={self.email} active={self.is_active}>"
        )
