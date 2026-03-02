"""Repository for Orders model."""

from app.models.orders import Orders
from app.repos.base import BaseRepository


class OrderRepository(BaseRepository[Orders]):
    """Repository for Orders model."""

    pass
