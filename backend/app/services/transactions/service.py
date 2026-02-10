"""Service layer for transactions."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.servers import Servers
from app.models.transactions import TransactionSnapshots, Transactions
from app.repos.account_repo import AccountRepository
from app.repos.binding_repo import BindingRepository
from app.repos.server_repo import ServerRepository
from app.repos.transaction_repo import (
    TransactionRepository,
    TransactionSnapshotRepository,
)
from app.services.transactions.schemas import (
    TransactionCreate,
    TransactionSnapshotCreate,
    TransactionSnapshotUpdate,
    TransactionStatusUpdate,
)

logger = get_logger("service.transactions")


class TransactionService:
    """Service for transaction header + snapshot."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transactions = TransactionRepository(Transactions)
        self.snapshots = TransactionSnapshotRepository(TransactionSnapshots)
        self.bindings = BindingRepository(Bindings)
        self.accounts = AccountRepository(Accounts)
        self.servers = ServerRepository(Servers)

    async def create_transaction(
        self,
        data: TransactionCreate,
        snapshot: TransactionSnapshotCreate | None = None,
    ) -> Transactions:
        """Create transaction header + optional snapshot."""
        binding = await self.bindings.get(self.session, data.binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {data.binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": data.binding_id},
            )

        account = await self.accounts.get(self.session, binding.account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account ID {binding.account_id} tidak ditemukan.",
                error_code="account_not_found",
                context={"account_id": binding.account_id},
            )

        server = await self.servers.get(self.session, binding.server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server ID {binding.server_id} tidak ditemukan.",
                error_code="server_not_found",
                context={"server_id": binding.server_id},
            )

        trx = await self.transactions.create(
            self.session,
            trx_id=data.trx_id,
            t_id=data.t_id,
            server_id=server.id,
            account_id=account.id,
            binding_id=binding.id,
            batch_id=account.batch_id,
            device_id=binding.device_id,
            product_id=data.product_id,
            email=data.email,
            limit_harga=data.limit_harga,
            amount=data.amount,
            is_success=data.is_success,
            otp_required=data.otp_required,
            error_message=data.error_message,
        )

        if snapshot:
            await self.snapshots.create(
                self.session,
                transaction_id=trx.id,
                balance_start=snapshot.balance_start,
                trx_idv_raw=snapshot.trx_idv_raw,
            )

        logger.info("Transaction created", extra={"transaction_id": trx.id})
        return trx

    async def update_status(
        self, transaction_id: int, data: TransactionStatusUpdate
    ) -> Transactions:
        """Update transaction status fields."""
        trx = await self.transactions.get(self.session, transaction_id)
        if not trx:
            raise AppNotFoundError(
                message=f"Transaction ID {transaction_id} tidak ditemukan.",
                error_code="transaction_not_found",
                context={"transaction_id": transaction_id},
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return trx

        updated = await self.transactions.update(self.session, trx, **update_data)
        logger.info("Transaction updated", extra={"transaction_id": transaction_id})
        return updated

    async def update_snapshot(
        self, transaction_id: int, data: TransactionSnapshotUpdate
    ) -> TransactionSnapshots:
        """Update snapshot for a transaction."""
        snapshot = await self.snapshots.get_by(
            self.session, transaction_id=transaction_id
        )
        if not snapshot:
            raise AppNotFoundError(
                message="Snapshot transaksi tidak ditemukan.",
                error_code="transaction_snapshot_not_found",
                context={"transaction_id": transaction_id},
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return snapshot

        updated = await self.snapshots.update(self.session, snapshot, **update_data)
        logger.info("Transaction snapshot updated", extra={"transaction_id": transaction_id})
        return updated

    async def get_transaction(self, transaction_id: int) -> Transactions:
        """Get transaction by ID."""
        trx = await self.transactions.get(self.session, transaction_id)
        if not trx:
            raise AppNotFoundError(
                message=f"Transaction ID {transaction_id} tidak ditemukan.",
                error_code="transaction_not_found",
                context={"transaction_id": transaction_id},
            )
        return trx

    async def list_transactions(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        binding_id: int | None = None,
        account_id: int | None = None,
        server_id: int | None = None,
        batch_id: str | None = None,
    ) -> Sequence[Transactions]:
        """List transactions with optional filters."""
        filters: dict = {}
        if status is not None:
            filters["status"] = status
        if binding_id is not None:
            filters["binding_id"] = binding_id
        if account_id is not None:
            filters["account_id"] = account_id
        if server_id is not None:
            filters["server_id"] = server_id
        if batch_id is not None:
            filters["batch_id"] = batch_id

        return await self.transactions.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )

    async def delete_transaction(self, transaction_id: int) -> None:
        """Delete transaction by ID."""
        deleted = await self.transactions.delete(self.session, transaction_id)
        if not deleted:
            raise AppNotFoundError(
                message=f"Transaction ID {transaction_id} tidak ditemukan.",
                error_code="transaction_not_found",
                context={"transaction_id": transaction_id},
            )
