"""Binding service layer - business logic with Pydantic DTOs."""

from app.api.schemas.bindings import (
    BalanceStartUpdateRequest,
    BindAccountRequest,
    BindingResponse,
    BulkBindRequest,
    ReleaseBindingRequest,
    RequestOTPRequest,
    SmartBindRequest,
    VerifyOTPRequest,
    WorkflowStepUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.orders import Orders
from app.models.servers import Servers
from app.repos.base import BaseRepository
from app.services.idv.service import IdvService
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("service.bindings")


class BindingService:
    """Service for binding management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    Integrates with IdvService for actual provider interaction.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bindings_repo = BaseRepository(Bindings)
        self.accounts_repo = BaseRepository(Accounts)
        self.orders_repo = BaseRepository(Orders)
        self.servers_repo = BaseRepository(Servers)

    async def list_accounts_by_order(self, order_id: int) -> list[dict]:
        """List accounts for a specific order (for dropdown)."""
        await self._verify_order_exists(order_id)

        # Get accounts for this order
        accounts = await self.accounts_repo.get_multi(self.session, order_id=order_id)

        return [
            {
                "id": acc.id,
                "msisdn": acc.msisdn,
                "email": acc.email,
                "status": acc.status if hasattr(acc, "status") else "UNKNOWN",
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

        # Verify all entities exist
        await self._verify_order_exists(data.order_id)
        await self._verify_server_exists(data.server_id)
        await self._verify_account_exists(data.account_id)

        # Check if account is already bound
        await self._check_account_already_bound(data.account_id)

        # Create binding
        binding = await self.bindings_repo.create(
            self.session,
            order_id=data.order_id,
            server_id=data.server_id,
            account_id=data.account_id,
            is_reseller=data.is_reseller,
            priority=data.priority,
            description=data.description,
            notes=data.notes,
            step="BINDED",
            is_active=True,
        )

        logger.info("Account bound successfully", extra={"binding_id": binding.id})
        return BindingResponse.model_validate(binding)

    async def bulk_bind_accounts(self, data: BulkBindRequest) -> list[BindingResponse]:
        """Bind multiple accounts to a single server for an order."""
        log_ctx = {"order_id": data.order_id, "account_count": len(data.account_ids)}
        logger.info("Bulk binding accounts", extra=log_ctx)

        # Verify order and server exist
        await self._verify_order_exists(data.order_id)
        await self._verify_server_exists(data.server_id)

        results: list[BindingResponse] = []

        for account_id in data.account_ids:
            # Check if each account is already bound
            await self._check_account_already_bound(account_id)

            # Create binding
            binding = await self.bindings_repo.create(
                self.session,
                order_id=data.order_id,
                server_id=data.server_id,
                account_id=account_id,
                is_reseller=data.is_reseller,
                priority=data.priority,
                description=data.description,
                notes=data.notes,
                step="BINDED",
                is_active=True,
            )
            results.append(BindingResponse.model_validate(binding))

        await self.session.flush()

        logger.info(
            "Bulk binding completed",
            extra={"total": len(data.account_ids), "success": len(results)},
        )
        return results

    async def smart_bind_accounts(
        self, data: SmartBindRequest
    ) -> list[BindingResponse]:
        """High-efficiency pairwise binding using human-readable PENANDA (port:msisdn)."""
        log_ctx = {"order_id": data.order_id, "pair_count": len(data.mappings)}
        logger.info("Executing smart bind (port:msisdn)", extra=log_ctx)

        # 1. Verify order exists
        await self._verify_order_exists(data.order_id)

        results: list[Bindings] = []

        # 2. Process each pair
        for item in data.mappings:
            # A. Resolve Server by Port
            server = await self.servers_repo.get_by(self.session, port=item.server_port)
            if not server:
                raise AppNotFoundError(
                    message=f"Server dengan Port {item.server_port} tidak ditemukan.",
                    error_code="server_port_not_found",
                )

            # B. Resolve Account by MSISDN (within this order context)
            account = await self.accounts_repo.get_by(
                self.session, msisdn=item.msisdn.strip(), order_id=data.order_id
            )
            if not account:
                raise AppNotFoundError(
                    message=f"Akun MSISDN {item.msisdn} tidak ditemukan dalam Order {data.order_id}.",
                    error_code="account_msisdn_not_found",
                )

            # C. Check if already bound
            await self._check_account_already_bound(account.id)

            # D. Create Binding
            binding = await self.bindings_repo.create(
                self.session,
                order_id=data.order_id,
                server_id=server.id,
                account_id=account.id,
                is_reseller=data.is_reseller,
                priority=data.priority,
                step="BINDED",
                is_active=True,
            )
            results.append(binding)

        await self.session.flush()

        # 3. Return enriched responses
        final_list = []
        for b in results:
            final_list.append(await self.get_binding(b.id))

        logger.info(f"Smart bind success: {len(final_list)} created.")
        return final_list

    async def get_binding(self, binding_id: int) -> BindingResponse:
        """Get a binding by ID with joined human-readable data."""
        from sqlalchemy import select

        stmt = (
            select(
                Bindings,
                Orders.name.label("order_name"),
                Servers.name.label("server_name"),
                Accounts.msisdn.label("account_msisdn"),
            )
            .join(Orders, Bindings.order_id == Orders.id)
            .join(Servers, Bindings.server_id == Servers.id)
            .join(Accounts, Bindings.account_id == Accounts.id)
            .where(Bindings.id == binding_id)
        )

        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            raise AppNotFoundError(
                message=f"Binding dengan ID {binding_id} tidak ditemukan",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        return BindingResponse(
            **{
                c.name: getattr(row.Bindings, c.name)
                for c in Bindings.__table__.columns
            },
            order_name=row.order_name,
            server_name=row.server_name,
            account_msisdn=row.account_msisdn,
        )

    async def list_bindings(
        self,
        skip: int = 0,
        limit: int = 100,
        order_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[BindingResponse]:
        """List bindings with filtering and joined human-readable data."""
        from sqlalchemy import select

        filters = []
        if order_id is not None:
            filters.append(Bindings.order_id == order_id)
        if is_active is not None:
            filters.append(Bindings.is_active == is_active)

        stmt = (
            select(
                Bindings,
                Orders.name.label("order_name"),
                Servers.name.label("server_name"),
                Accounts.msisdn.label("account_msisdn"),
            )
            .join(Orders, Bindings.order_id == Orders.id)
            .join(Servers, Bindings.server_id == Servers.id)
            .join(Accounts, Bindings.account_id == Accounts.id)
            .where(*filters)
            .order_by(Bindings.id.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            BindingResponse(
                **{
                    c.name: getattr(row.Bindings, c.name)
                    for c in Bindings.__table__.columns
                },
                order_name=row.order_name,
                server_name=row.server_name,
                account_msisdn=row.account_msisdn,
            )
            for row in rows
        ]

    async def list_active_bindings(self) -> list[BindingResponse]:
        """List all active bindings."""
        return await self.list_bindings(is_active=True)

    async def update_workflow_step(
        self, binding_id: int, data: WorkflowStepUpdateRequest
    ) -> BindingResponse:
        """Manually update workflow step and optional token data."""
        binding = await self._get_binding_entity(binding_id)

        update_fields = {"step": data.step}
        if data.token_location is not None:
            update_fields["token_location"] = data.token_location
        if data.notes is not None:
            update_fields["notes"] = data.notes

        updated = await self.bindings_repo.update(
            self.session, binding, **update_fields
        )

        logger.info(
            "Workflow step updated", extra={"binding_id": binding_id, "step": data.step}
        )
        return await self.get_binding(binding_id)

    async def update_binding(self, binding_id: int, data: dict) -> BindingResponse:
        """Update binding properties like server_id, priority, etc."""
        binding = await self._get_binding_entity(binding_id)

        # If server is changing, verify it exists
        if "server_id" in data and data["server_id"] != binding.server_id:
            await self._verify_server_exists(data["server_id"])

        updated = await self.bindings_repo.update(self.session, binding, **data)

        logger.info("Binding updated", extra={"binding_id": binding_id})
        return await self.get_binding(binding_id)

    async def release_binding(
        self,
        binding_id: int,
        data: ReleaseBindingRequest,
    ) -> None:
        """Release (delete) a binding to free the account."""
        await self._get_binding_entity(binding_id)

        # Hard delete to free up the account_id UniqueConstraint
        await self.bindings_repo.delete(self.session, binding_id)
        logger.info("Binding released (deleted)", extra={"binding_id": binding_id})

    async def set_balance_start(
        self,
        binding_id: int,
        data: BalanceStartUpdateRequest,
    ) -> BindingResponse:
        """Set balance start for a binding and sync to Account cache."""
        binding = await self._get_binding_entity(binding_id)

        # Update balance in Binding
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            balance_start=data.balance_start,
            balance_source=data.source,
        )

        # Sync to Account cache
        await self._sync_balance_to_account(
            account_id=binding.account_id, balance=data.balance_start
        )

        logger.info(
            "Balance start updated and synced to account",
            extra={"binding_id": binding_id, "balance": data.balance_start},
        )
        return BindingResponse.model_validate(updated_binding)

    async def request_otp(
        self,
        binding_id: int,
        data: RequestOTPRequest,
    ) -> BindingResponse:
        """Request OTP from provider for a binding."""
        binding = await self._get_binding_entity(binding_id)
        server = await self.servers_repo.get(self.session, binding.server_id)
        account = await self.accounts_repo.get(self.session, binding.account_id)

        if not server or not account:
            raise AppValidationError("Data server atau akun tidak lengkap.")

        # Initialize IDV Service and make actual call
        idv_service = IdvService.from_server(server)
        response = await idv_service.request_otp(username=account.msisdn, pin=data.pin)

        # Parse provider response (assuming 'status': 'success' based on typical IDV patterns)
        if response.get("status") != "success":
            msg = response.get("message", "Gagal meminta OTP dari provider.")
            raise AppValidationError(
                message=f"Provider Error: {msg}",
                error_code="provider_request_otp_failed",
                context={"provider_response": response},
            )

        # Update step to REQUEST_OTP
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            step="REQUEST_OTP",
            notes=f"OTP Requested. Provider: {response.get('message', 'OK')}",
        )

        logger.info("OTP requested successfully", extra={"binding_id": binding_id})
        return BindingResponse.model_validate(updated_binding)

    async def verify_otp(
        self,
        binding_id: int,
        data: VerifyOTPRequest,
    ) -> BindingResponse:
        """Verify OTP and automatically sync results to Account cache."""
        binding = await self._get_binding_entity(binding_id)
        server = await self.servers_repo.get(self.session, binding.server_id)
        account = await self.accounts_repo.get(self.session, binding.account_id)

        if not server or not account:
            raise AppValidationError("Data server atau akun tidak lengkap.")

        # Initialize IDV Service and verify
        idv_service = IdvService.from_server(server)
        verify_res = await idv_service.verify_otp(username=account.msisdn, otp=data.otp)

        if verify_res.get("status") != "success":
            msg = verify_res.get("message", "Kode OTP salah atau kedaluwarsa.")
            raise AppValidationError(
                message=f"Verifikasi Gagal: {msg}",
                error_code="provider_verify_otp_failed",
                context={"provider_response": verify_res},
            )

        # SUCCESS: Fetch latest data
        logger.info(
            "OTP verified, fetching balance and token...",
            extra={"binding_id": binding_id},
        )

        # 1. Fetch Balance
        balance_res = await idv_service.get_balance_pulsa(account.msisdn)
        balance_val = None
        if balance_res.get("status") == "success":
            # Assuming balance string like "Rp 50.000" or similar, need to parse if it's integer in DB
            # For now let's try to extract digits
            raw_balance = str(balance_res.get("balance", "0"))
            balance_val = int("".join(filter(str.isdigit, raw_balance)))

        # 2. Fetch Token Location
        token_res = await idv_service.get_token_location3(account.msisdn)
        token_loc = token_res.get("token")

        # Update binding with all results
        updated_binding = await self.bindings_repo.update(
            self.session,
            binding,
            step="VERIFIED",
            balance_start=balance_val,
            balance_source="AUTO_CHECK",
            token_location=token_loc,
            notes=f"Verified & Initialized. Balance: {balance_val}",
        )

        # Sync results to Account cache
        await self._sync_balance_to_account(
            account_id=binding.account_id,
            balance=balance_val,
            balance_response=balance_res,
            card_active=balance_res.get("cardactiveuntil"),
            grace_period=balance_res.get("graceperioduntil"),
            expires=balance_res.get("expires"),
        )

        logger.info(
            "OTP verified and synced to account cache", extra={"binding_id": binding_id}
        )
        return BindingResponse.model_validate(updated_binding)

    async def delete_binding(self, binding_id: int) -> None:
        """Delete a binding."""
        await self._get_binding_entity(binding_id)
        await self.bindings_repo.delete(self.session, binding_id)
        logger.info("Binding deleted", extra={"binding_id": binding_id})

    # --- Private Helpers ---

    async def _sync_balance_to_account(
        self,
        account_id: int,
        balance: int | None,
        balance_response: dict | None = None,
        card_active: str | None = None,
        grace_period: str | None = None,
        expires: str | None = None,
    ) -> None:
        """Internal helper to push latest balance data to Account table."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            return

        update_fields = {}
        if balance is not None:
            update_fields["balance_last"] = balance
        if balance_response:
            update_fields["last_balance_response"] = balance_response
        if card_active:
            update_fields["card_active_until"] = card_active
        if grace_period:
            update_fields["grace_period_until"] = grace_period
        if expires:
            update_fields["expires_info"] = expires

        if update_fields:
            await self.accounts_repo.update(self.session, account, **update_fields)

    async def _get_binding_entity(self, binding_id: int) -> Bindings:
        """Internal helper to get raw Binding model."""
        binding = await self.bindings_repo.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding dengan ID {binding_id} tidak ditemukan",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
        return binding

    async def _verify_order_exists(self, order_id: int) -> None:
        """Verify that an order exists."""
        order = await self.orders_repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order dengan ID {order_id} tidak ditemukan",
                error_code="order_not_found",
                context={"order_id": order_id},
            )

    async def _verify_server_exists(self, server_id: int) -> None:
        """Verify that a server exists."""
        server = await self.servers_repo.get(self.session, server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server dengan ID {server_id} tidak ditemukan",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

    async def _verify_account_exists(self, account_id: int) -> None:
        """Verify that an account exists."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Akun dengan ID {account_id} tidak ditemukan",
                error_code="account_not_found",
                context={"account_id": account_id},
            )

    async def _check_account_already_bound(self, account_id: int) -> None:
        """Check if an account is already actively bound."""
        existing = await self.bindings_repo.get_by(
            self.session, account_id=account_id, is_active=True
        )
        if existing:
            raise AppValidationError(
                message=f"Akun dengan ID {account_id} sudah terikat pada Binding aktif (ID: {existing.id})",
                error_code="account_already_bound",
                context={
                    "account_id": account_id,
                    "existing_binding_id": existing.id,
                },
            )
