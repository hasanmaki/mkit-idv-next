"""Model untuk Sessions - entitas utama untuk manajemen user/session."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Sessions(Base, TimestampMixin):
    """Session record - merepresentasikan user session yang dapat memiliki multiple bindings.

    Session adalah entitas utama yang mewakili konteks user/operator,
    sedangkan SessionBinding (akan dibuat nanti) akan mengikat session ke server tertentu.
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Session identity
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Session status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        """Return a short string representation of the Session for debugging."""
        return (
            f"<Session id={self.id} name='{self.name}' "
            f"email={self.email} active={self.is_active}>"
        )
