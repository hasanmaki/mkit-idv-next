"""Repository untuk Sessions."""

from app.models.sessions import Sessions
from app.repos.base import BaseRepository


class SessionRepository(BaseRepository[Sessions]):
    """Repository untuk Sessions model."""

    pass
