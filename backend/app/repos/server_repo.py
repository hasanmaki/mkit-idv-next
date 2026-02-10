"""later if needed add custom methods for Server repository."""

from backend.app.repos.base import BaseRepository

from app.models.servers import Servers


class ServerRepository(BaseRepository[Servers]):
    """Repository for Servers model."""

    pass
