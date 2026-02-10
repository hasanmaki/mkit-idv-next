"""Repository for Transactions models."""

from app.models.transactions import Transactions, TransactionSnapshots
from app.repos.base import BaseRepository


class TransactionRepository(BaseRepository[Transactions]):
    """Repository for Transactions."""


class TransactionSnapshotRepository(BaseRepository[TransactionSnapshots]):
    """Repository for TransactionSnapshots."""
