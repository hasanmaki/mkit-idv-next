# Copyright (c) 2026 okedigitalmedia/hasanmaki. All rights reserved.
# [ ] TODO : Fix Later About Docstring
"""representasi api myim3.

tabale ini untuk holder data api server yg sudah di konfigurasi.

"""

from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, TimestampMixin


class Servers(Base, TimestampMixin):
    """Server instance (e.g., localhost:9900) that handles one MSISDN at a time."""

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    port: Mapped[int] = mapped_column(unique=True, nullable=False)  # e.g., 9900
    base_url: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )  # e.g., "http://localhost:9900"
    description: Mapped[str] = mapped_column(String(100), nullable=True)

    # Connection settings
    timeout: Mapped[int] = mapped_column(default=10, nullable=False)
    retries: Mapped[int] = mapped_column(default=3, nullable=False)
    wait_between_retries: Mapped[int] = mapped_column(default=1, nullable=False)
    max_requests_queued: Mapped[int] = mapped_column(default=5, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Flexible config (e.g., provider type, headers, etc.)
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Server id={self.id} port={self.port} url={self.base_url}>"
