"""later if needed add custom methods for Server repository."""

from app.models.accounts import Accounts
from app.repos.base import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    """Repository for Accounts model."""

    pass
