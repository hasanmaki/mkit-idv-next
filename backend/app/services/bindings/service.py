"""Service layer for bindings."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.servers import Servers
from app.models.statuses import AccountStatus
from app.models.steps import BindingStep
from app.repos.account_repo import AccountRepository
from app.repos.binding_repo import BindingRepository
from app.repos.server_repo import ServerRepository
from app.services.bindings.schemas import BindingCreate, BindingLogout, BindingUpdate

logger = get_logger("service.bindings")


class BindingService:
    """Service for managing bindings."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bindings = BindingRepository(Bindings)
        self.accounts = AccountRepository(Accounts)
        self.servers = ServerRepository(Servers)

    async def create_binding(self, data: BindingCreate) -> Bindings:
        """Create a new binding if server and account are available."""
        server = await self.servers.get(self.session, data.server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server ID {data.server_id} tidak ditemukan.",
                error_code="server_not_found",
                context={"server_id": data.server_id},
            )

        account = await self.accounts.get(self.session, data.account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account ID {data.account_id} tidak ditemukan.",
                error_code="account_not_found",
                context={"account_id": data.account_id},
            )

        active_server = await self.bindings.get_active_by_server(
            self.session, server_id=data.server_id
        )
        if active_server:
            raise AppValidationError(
                message="Server masih memiliki binding aktif.",
                error_code="binding_server_active",
                context={"server_id": data.server_id, "binding_id": active_server.id},
            )

        active_account = await self.bindings.get_active_by_account(
            self.session, account_id=data.account_id
        )
        if active_account:
            raise AppValidationError(
                message="Account masih terikat pada server lain.",
                error_code="binding_account_active",
                context={"account_id": data.account_id, "binding_id": active_account.id},
            )

        binding = await self.bindings.create(
            self.session,
            server_id=data.server_id,
            account_id=data.account_id,
            batch_id=account.batch_id,
            step=BindingStep.BOUND,
            balance_start=data.balance_start,
            balance_last=data.balance_start,
        )
        await self.accounts.update(
            self.session,
            account,
            status=AccountStatus.ACTIVE,
            used_count=account.used_count + 1,
            last_used_at=datetime.utcnow(),
        )

        logger.info(
            "Binding created",
            extra={"binding_id": binding.id, "server_id": data.server_id},
        )
        return binding

    async def update_binding(
        self, binding_id: int, data: BindingUpdate
    ) -> Bindings:
        """Update binding fields."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return binding

        updated = await self.bindings.update(self.session, binding, **update_data)
        logger.info("Binding updated", extra={"binding_id": binding_id})
        return updated

    async def logout_binding(
        self, binding_id: int, data: BindingLogout
    ) -> Bindings:
        """Logout (unbind) a binding."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        if binding.unbound_at is not None:
            raise AppValidationError(
                message="Binding sudah logout sebelumnya.",
                error_code="binding_already_logged_out",
                context={"binding_id": binding_id},
            )

        updated = await self.bindings.update(
            self.session,
            binding,
            step=BindingStep.LOGGED_OUT,
            unbound_at=datetime.utcnow(),
            **data.model_dump(exclude_unset=True),
        )
        account = await self.accounts.get(self.session, binding.account_id)
        if account:
            new_status = (
                data.account_status
                if data.account_status is not None
                else AccountStatus.EXHAUSTED
            )
            await self.accounts.update(self.session, account, status=new_status)
        logger.info("Binding logged out", extra={"binding_id": binding_id})
        return updated

    async def get_binding(self, binding_id: int) -> Bindings:
        """Get binding by ID."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
        return binding

    async def list_bindings(
        self,
        skip: int = 0,
        limit: int = 100,
        server_id: int | None = None,
        account_id: int | None = None,
        batch_id: str | None = None,
        step: BindingStep | None = None,
        active_only: bool | None = None,
    ) -> list[Bindings]:
        """List bindings with optional filters."""
        filters: dict = {}
        if server_id is not None:
            filters["server_id"] = server_id
        if account_id is not None:
            filters["account_id"] = account_id
        if batch_id is not None:
            filters["batch_id"] = batch_id
        if step is not None:
            filters["step"] = step

        bindings = list(
            await self.bindings.get_multi(
                self.session, skip=skip, limit=limit, **filters
            )
        )
        if active_only:
            bindings = [b for b in bindings if b.unbound_at is None]
        logger.debug("Bindings retrieved", extra={"count": len(bindings)})
        return bindings

    async def delete_binding(self, binding_id: int) -> None:
        """Delete binding by ID."""
        deleted = await self.bindings.delete(self.session, binding_id)
        if not deleted:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
