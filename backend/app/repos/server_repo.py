"""later if needed add custom methods for Server repository."""

from app.models.servers import Servers
from app.repos.base import BaseRepository


class ServerRepository(BaseRepository[Servers]):
    """Repository for Servers model."""

    pass
