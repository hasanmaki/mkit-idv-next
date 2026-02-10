"""Service layer for transactions."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.servers import Servers
from app.models.transactions import TransactionSnapshots, Transactions
from app.models.transaction_statuses import TransactionOtpStatus, TransactionStatus
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
    TransactionStartRequest,
    TransactionOtpRequest,
    TransactionStopRequest,
)
from app.services.idv import IdvService

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
        status: TransactionStatus | None = None,
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

    async def start_transaction(self, payload: TransactionStartRequest) -> Transactions:
        """Start transaction flow: balance_start -> trx_idv -> status_idv -> balance_end."""
        binding = await self.bindings.get(self.session, payload.binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {payload.binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": payload.binding_id},
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

        idv = IdvService.from_server(server)

        balance_start_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_start = None
        if isinstance(balance_start_resp, dict):
            balance_start = (
                balance_start_resp.get("res", {}).get("balance")
                if balance_start_resp.get("res")
                else None
            )
        try:
            balance_start_int = (
                int(balance_start) if balance_start is not None else None
            )
        except ValueError:
            balance_start_int = None

        trx_resp = await idv.trx_voucher_idv(
            account.msisdn,
            payload.product_id,
            payload.email,
            payload.limit_harga,
        )
        trx_id = None
        t_id = None
        is_success = None
        if isinstance(trx_resp, dict):
            res = trx_resp.get("res", {})
            data = res.get("data", {}) if res else {}
            trx_id = data.get("trx_id")
            t_id = data.get("t_id")
            is_success = data.get("is_success")

        if not trx_id:
            raise AppValidationError(
                message="trx_id tidak ditemukan pada response transaksi.",
                error_code="transaction_trx_id_missing",
                context={"response": trx_resp},
            )

        trx = await self.create_transaction(
            TransactionCreate(
                binding_id=binding.id,
                trx_id=str(trx_id),
                t_id=str(t_id) if t_id else None,
                product_id=payload.product_id,
                email=payload.email,
                limit_harga=payload.limit_harga,
                amount=payload.limit_harga,
                is_success=int(is_success) if is_success is not None else None,
                otp_required=payload.otp_required,
            ),
            snapshot=TransactionSnapshotCreate(
                balance_start=balance_start_int,
                trx_idv_raw=trx_resp,
            ),
        )

        status_resp = await idv.status_trx(account.msisdn, str(trx_id))
        is_success_status = None
        voucher_code = None
        if isinstance(status_resp, dict):
            res = status_resp.get("res", {})
            data = res.get("data", {}) if res else {}
            is_success_status = data.get("is_success")
            voucher_code = data.get("voucher")

        if is_success_status == 2 and voucher_code:
            status_value = TransactionStatus.SUKSES
        elif is_success_status == 2 and not voucher_code:
            status_value = TransactionStatus.SUSPECT
        else:
            status_value = TransactionStatus.PROCESSING

        balance_end_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_end = None
        if isinstance(balance_end_resp, dict):
            balance_end = (
                balance_end_resp.get("res", {}).get("balance")
                if balance_end_resp.get("res")
                else None
            )
        try:
            balance_end_int = int(balance_end) if balance_end is not None else None
        except ValueError:
            balance_end_int = None

        await self.update_status(
            trx.id,
            TransactionStatusUpdate(
                status=status_value,
                is_success=int(is_success_status)
                if is_success_status is not None
                else None,
                voucher_code=voucher_code,
                otp_status=TransactionOtpStatus.PENDING
                if status_value == TransactionStatus.PROCESSING
                else None,
            ),
        )
        await self.update_snapshot(
            trx.id,
            TransactionSnapshotUpdate(
                balance_end=balance_end_int,
                status_idv_raw=status_resp,
            ),
        )

        return await self.get_transaction(trx.id)

    async def submit_otp(
        self, transaction_id: int, payload: TransactionOtpRequest
    ) -> Transactions:
        """Submit OTP and re-check status."""
        trx = await self.get_transaction(transaction_id)
        binding = await self.bindings.get(self.session, trx.binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {trx.binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": trx.binding_id},
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

        idv = IdvService.from_server(server)
        otp_resp = await idv.otp_trx(account.msisdn, payload.otp)

        status_resp = await idv.status_trx(account.msisdn, trx.trx_id)
        is_success_status = None
        voucher_code = None
        if isinstance(status_resp, dict):
            res = status_resp.get("res", {})
            data = res.get("data", {}) if res else {}
            is_success_status = data.get("is_success")
            voucher_code = data.get("voucher")

        if is_success_status == 2 and voucher_code:
            status_value = TransactionStatus.SUKSES
        elif is_success_status == 2 and not voucher_code:
            status_value = TransactionStatus.SUSPECT
        else:
            status_value = TransactionStatus.GAGAL

        balance_end_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_end = None
        if isinstance(balance_end_resp, dict):
            balance_end = (
                balance_end_resp.get("res", {}).get("balance")
                if balance_end_resp.get("res")
                else None
            )
        try:
            balance_end_int = int(balance_end) if balance_end is not None else None
        except ValueError:
            balance_end_int = None

        await self.update_status(
            trx.id,
            TransactionStatusUpdate(
                status=status_value,
                is_success=int(is_success_status)
                if is_success_status is not None
                else None,
                voucher_code=voucher_code,
                otp_status=TransactionOtpStatus.SUCCESS
                if status_value in (TransactionStatus.SUKSES, TransactionStatus.SUSPECT)
                else TransactionOtpStatus.FAILED,
                error_message=str(otp_resp.get("res", {}).get("message"))
                if isinstance(otp_resp, dict)
                else None,
            ),
        )
        await self.update_snapshot(
            trx.id,
            TransactionSnapshotUpdate(
                balance_end=balance_end_int,
                status_idv_raw=status_resp,
            ),
        )

        return await self.get_transaction(trx.id)

    async def stop_transaction(
        self, transaction_id: int, payload: TransactionStopRequest
    ) -> Transactions:
        """Stop transaction manually."""
        trx = await self.get_transaction(transaction_id)
        return await self.update_status(
            trx.id,
            TransactionStatusUpdate(
                status=TransactionStatus.GAGAL,
                error_message=payload.reason,
            ),
        )

    async def continue_transaction(self, transaction_id: int) -> Transactions:
        """Continue transaction: re-check status_idv and balance_end."""
        trx = await self.get_transaction(transaction_id)
        binding = await self.bindings.get(self.session, trx.binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {trx.binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": trx.binding_id},
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

        idv = IdvService.from_server(server)
        status_resp = await idv.status_trx(account.msisdn, trx.trx_id)
        is_success_status = None
        voucher_code = None
        if isinstance(status_resp, dict):
            res = status_resp.get("res", {})
            data = res.get("data", {}) if res else {}
            is_success_status = data.get("is_success")
            voucher_code = data.get("voucher")

        if is_success_status == 2 and voucher_code:
            status_value = TransactionStatus.SUKSES
        elif is_success_status == 2 and not voucher_code:
            status_value = TransactionStatus.SUSPECT
        else:
            status_value = TransactionStatus.GAGAL

        balance_end_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_end = None
        if isinstance(balance_end_resp, dict):
            balance_end = (
                balance_end_resp.get("res", {}).get("balance")
                if balance_end_resp.get("res")
                else None
            )
        try:
            balance_end_int = int(balance_end) if balance_end is not None else None
        except ValueError:
            balance_end_int = None

        await self.update_status(
            trx.id,
            TransactionStatusUpdate(
                status=status_value,
                is_success=int(is_success_status)
                if is_success_status is not None
                else None,
                voucher_code=voucher_code,
                otp_status=trx.otp_status,
            ),
        )
        await self.update_snapshot(
            trx.id,
            TransactionSnapshotUpdate(
                balance_end=balance_end_int,
                status_idv_raw=status_resp,
            ),
        )

        return await self.get_transaction(trx.id)
