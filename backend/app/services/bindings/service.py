"""Binding service layer - business logic with Pydantic DTOs."""

from app.api.schemas.bindings import (
    BalanceStartUpdateRequest,
    BindAccountRequest,
    BindingResponse,
    BulkBindRequest,
    ReleaseBindingRequest,
    RequestOTPRequest,
    VerifyOTPRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.orders import Orders
from app.models.servers import Servers
from app.repos.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("service.bindings")


class BindingService:
    """Service for binding management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    No redundant command/query objects.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bindings_repo = BaseRepository(Bindings)
        self.accounts_repo = BaseRepository(Accounts)
        self.orders_repo = BaseRepository(Orders)
        self.servers_repo = BaseRepository(Servers)

    async def list_accounts_by_order(self, order_id: int) -> list[dict]:
        """List accounts for a specific order (for dropdown)."""
        # Verify order exists
        order = await self.orders_repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order with ID {order_id} not found",
                error_code="order_not_found",
                context={"order_id": order_id},
            )

        # Get accounts for this order
        accounts = await self.accounts_repo.get_multi(self.session, order_id=order_id)

        return [
            {
                "id": acc.id,
                "msisdn": acc.msisdn,
                "email": acc.email,
                "status": acc.status,
            }
            for acc in accounts
        ]

    async def list_active_servers(self) -> list[dict]:
        """List active servers (for dropdown)."""
        servers = await self.servers_repo.get_multi(self.session, is_active=True)

        return [
            {
                "id": srv.id,
                "name": srv.name,
                "base_url": srv.base_url,
                "port": srv.port,
            }
            for srv in servers
        ]

    async def bind_account(self, data: BindAccountRequest) -> BindingResponse:
        """Bind an account to a server for an order."""
        log_ctx = {"order_id": data.order_id, "account_id": data.account_id}
        logger.info("Binding account", extra=log_ctx)

        # Verify order exists
        order = await self.orders_repo.get(self.session, data.order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order with ID {data.order_id} not found",
                error_code="order_not_found",
                context={"order_id": data.order_id},
            )

        # Verify server exists
        server = await self.servers_repo.get(self.session, data.server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server with ID {data.server_id} not found",
                error_code="server_not_found",
                context={"server_id": data.server_id},
            )

        # Verify account exists
        account = await self.accounts_repo.get(self.session, data.account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account with ID {data.account_id} not found",
                error_code="account_not_found",
                context={"account_id": data.account_id},
            )

        # Check if account is already bound
        existing_binding = await self.bindings_repo.get_by(
            self.session, account_id=data.account_id, is_active=True
        )
        if existing_binding:
            raise AppValidationError(
                message=f"Account {data.account_id} is already bound",
                error_code="account_already_bound",
                context={
                    "account_id": data.account_id,
                    "existing_binding_id": existing_binding.id,
                },
            )

        # Create binding
        binding = await self.bindings_repo.create(
            self.session,
            order_id=data.order_id,
            server_id=data.server_id,
            account_id=data.account_id,
            priority=data.priority,
            description=data.description,
            notes=data.notes,
            step="BINDED",
            is_active=True,
        )

        logger.info("Account bound successfully", extra={"binding_id": binding.id})
        return BindingResponse.model_validate(binding)

    async def bulk_bind_accounts(self, data: BulkBindRequest) -> list[BindingResponse]:
        """Bind multiple accounts to a server for an order."""
        log_ctx = {"order_id": data.order_id, "account_count": len(data.account_ids)}
        logger.info("Bulk binding accounts", extra=log_ctx)

        results: list[BindingResponse] = []

        for account_id in data.account_ids:
            try:
                # Create binding for each account
                binding = await self.bindings_repo.create(
                    self.session,
                    order_id=data.order_id,
                    server_id=data.server_id,
                    account_id=account_id,
                    priority=data.priority,
                    description=data.description,
                    notes=data.notes,
                    step="BINDED",
                    is_active=True,
                )
                results.append(BindingResponse.model_validate(binding))
            except Exception as e:
                logger.warning(
                    f"Failed to bind account {account_id}: {e!s}",
                    extra={"account_id": account_id},
                )
                # Continue with next account

        logger.info(
            "Bulk binding completed",
            extra={"total": len(data.account_ids), "success": len(results)},
        )
        return results

    async def get_binding(self, binding_id: int) -> BindingResponse:
        """Get a binding by ID."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
        return BindingResponse.model_validate(binding)

    async def list_bindings(
        self,
        skip: int = 0,
        limit: int = 100,
        order_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[BindingResponse]:
        """List bindings with optional filtering."""
        filters = {}
        if order_id is not None:
            filters["order_id"] = order_id
        if is_active is not None:
            filters["is_active"] = is_active

        bindings = await self.bindings_repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        return [BindingResponse.model_validate(b) for b in bindings]

    async def list_active_bindings(self) -> list[BindingResponse]:
        """List all active bindings."""
        return await self.list_bindings(is_active=True)

    async def release_binding(
        self,
        binding_id: int,
        data: ReleaseBindingRequest,
    ) -> None:
        """Release (deactivate) a binding."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        # Deactivate binding
        await self.bindings_repo.update(self.session, binding, is_active=False)

        logger.info("Binding released", extra={"binding_id": binding_id})

    async def set_balance_start(
        self,
        binding_id: int,
        data: BalanceStartUpdateRequest,
    ) -> BindingResponse:
        """Set balance start for a binding."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        # Update balance
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            balance_start=data.balance_start,
            balance_source=data.source,
        )

        logger.info(
            "Balance start updated",
            extra={"binding_id": binding_id, "balance": data.balance_start},
        )
        return BindingResponse.model_validate(updated_binding)

    async def request_otp(
        self,
        binding_id: int,
        data: RequestOTPRequest,
    ) -> BindingResponse:
        """Request OTP for a binding (workflow step)."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        # Update step to REQUEST_OTP
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            step="REQUEST_OTP",
        )

        logger.info("OTP requested", extra={"binding_id": binding_id})
        return BindingResponse.model_validate(updated_binding)

    async def verify_otp(
        self,
        binding_id: int,
        data: VerifyOTPRequest,
    ) -> BindingResponse:
        """Verify OTP for a binding (workflow step)."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        # Update step to VERIFIED
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            step="VERIFIED",
        )

        logger.info("OTP verified", extra={"binding_id": binding_id})
        return BindingResponse.model_validate(updated_binding)

    async def delete_binding(self, binding_id: int) -> None:
        """Delete a binding."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding with ID {binding_id} not found",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        await self.bindings_repo.delete(self.session, binding_id)

        logger.info("Binding deleted", extra={"binding_id": binding_id})
