"""Repository for Accounts model with optional helpers."""

from app.models.accounts import Accounts
from app.repos.base import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    """Repository for Accounts model."""

    async def get_by_msisdn_batch(
        self, db, *, msisdn: str, batch_id: str
    ) -> Accounts | None:
        """Get account by msisdn + batch_id."""
        return await self.get_by(db, msisdn=msisdn, batch_id=batch_id)
