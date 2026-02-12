"""Service layer for bindings."""

from datetime import datetime

from sqlalchemy import select
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
from app.services.bindings.schemas import (
    BindingBulkItemInput,
    BindingBulkItemResult,
    BindingProductItem,
    BindingProductsPreviewItem,
    BindingProductsPreviewRequest,
    BindingProductsPreviewResult,
    BindingBulkRequest,
    BindingBulkResult,
    BindingCreate,
    BindingLogout,
    BindingRead,
    BindingRequestLogin,
    BindingUpdate,
    BindingViewRead,
    BindingVerifyLogin,
)
from app.services.idv import IdvService
from app.services.workflow import WorkflowGuardService

logger = get_logger("service.bindings")


class BindingService:
    """Service for managing bindings."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bindings = BindingRepository(Bindings)
        self.accounts = AccountRepository(Accounts)
        self.servers = ServerRepository(Servers)
        self.guard = WorkflowGuardService()

    @staticmethod
    def _provider_ok(payload: dict, *, require_token: bool = False) -> bool:
        """Validate provider success shape used by login OTP endpoints."""
        status = str(payload.get("status", ""))
        data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
        data_status = data.get("status")
        data_status_ok = str(data_status).lower() == "true"
        token_ok = bool(data.get("tokenid")) if require_token else True
        return status == "0" and data_status_ok and token_ok

    @staticmethod
    def _provider_error_message(payload: dict) -> str:
        """Extract readable provider error message."""
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message
        return "Provider mengembalikan respons login yang tidak valid."

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
                context={
                    "account_id": data.account_id,
                    "binding_id": active_account.id,
                },
            )

        binding = await self.bindings.create(
            self.session,
            server_id=data.server_id,
            account_id=data.account_id,
            batch_id=account.batch_id,
            device_id=None,
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

    async def update_binding(self, binding_id: int, data: BindingUpdate) -> Bindings:
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

    async def logout_binding(self, binding_id: int, data: BindingLogout) -> Bindings:
        """Logout (unbind) a binding."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        self.guard.ensure_binding_step(
            action="logout",
            current=binding.step,
            allowed={
                BindingStep.BOUND,
                BindingStep.OTP_REQUESTED,
                BindingStep.OTP_VERIFICATION,
                BindingStep.OTP_VERIFIED,
                BindingStep.TOKEN_LOGIN_FETCHED,
            },
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

    async def request_login(self, binding_id: int, payload: BindingRequestLogin) -> dict:
        """Request OTP login for a binding using payload PIN or account default PIN."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
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

        pin = payload.pin or account.pin
        if not pin:
            raise AppValidationError(
                message="PIN tidak tersedia untuk account ini.",
                error_code="account_pin_missing",
                context={"account_id": account.id},
            )

        idv = IdvService.from_server(server)
        self.guard.ensure_binding_step(
            action="request_login",
            current=binding.step,
            allowed={BindingStep.BOUND, BindingStep.OTP_REQUESTED},
            context={"binding_id": binding_id},
        )
        otp_req = await idv.request_otp(account.msisdn, pin)
        if not self._provider_ok(otp_req):
            raise AppValidationError(
                message=self._provider_error_message(otp_req),
                error_code="binding_request_login_failed",
                context={"binding_id": binding_id, "provider": otp_req},
            )
        await self.bindings.update(
            self.session, binding, step=BindingStep.OTP_REQUESTED
        )
        return {"otp_request": otp_req}

    async def verify_login_and_reseller(
        self, binding_id: int, payload: BindingVerifyLogin
    ) -> dict:
        """Verify OTP, fetch balance/token, and check reseller status."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
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

        self.guard.ensure_binding_step(
            action="verify_login",
            current=binding.step,
            allowed={BindingStep.OTP_REQUESTED},
            context={"binding_id": binding_id},
        )

        idv = IdvService.from_server(server)

        await self.bindings.update(
            self.session, binding, step=BindingStep.OTP_VERIFICATION
        )
        otp_verify = await idv.verify_otp(account.msisdn, payload.otp)
        if not self._provider_ok(otp_verify, require_token=True):
            raise AppValidationError(
                message=self._provider_error_message(otp_verify),
                error_code="binding_verify_login_failed",
                context={"binding_id": binding_id, "provider": otp_verify},
            )

        await self.bindings.update(self.session, binding, step=BindingStep.OTP_VERIFIED)

        token_login = None
        if isinstance(otp_verify, dict):
            token_login = otp_verify.get("data", {}).get("tokenid")

        await self.bindings.update(
            self.session, binding, step=BindingStep.TOKEN_LOGIN_FETCHED
        )

        balance_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_value = None
        if isinstance(balance_resp, dict):
            balance_value = (
                balance_resp.get("res", {}).get("balance")
                if balance_resp.get("res")
                else None
            )
        try:
            balance_int = int(balance_value) if balance_value is not None else None
        except ValueError:
            balance_int = None

        token_location = await idv.get_token_location3(account.msisdn)

        list_resp = await idv.list_produk(account.msisdn)
        is_reseller = False
        detected_device_id = None
        if isinstance(list_resp, dict) and (
            list_resp.get("status") == "200"
            or list_resp.get("status_msg") == "success"
            or list_resp.get("data", {}).get("product_group", {}).get("product_type")
            == "reseller"
        ):
            is_reseller = True
            detected_device_id = (
                list_resp.get("data", {}).get("identifier", {}).get("device_id")
            )
        elif isinstance(list_resp, dict):
            detected_device_id = (
                list_resp.get("data", {}).get("identifier", {}).get("device_id")
            )

        balance_start = (
            balance_int if binding.balance_start is None else binding.balance_start
        )
        await self.bindings.update(
            self.session,
            binding,
            is_reseller=is_reseller,
            balance_start=balance_start,
            balance_last=balance_int,
            token_login=token_login,
            token_location=(
                token_location.get("token")
                if isinstance(token_location, dict)
                else token_location
            ),
            token_location_refreshed_at=datetime.utcnow(),
            device_id=detected_device_id,
        )
        await self.accounts.update(
            self.session,
            account,
            balance_last=balance_int,
            is_reseller=is_reseller,
            last_device_id=detected_device_id,
        )

        return {
            "otp_verify": otp_verify,
            "balance": balance_resp,
            "token_login": token_login,
            "token_location": token_location,
            "list_produk": list_resp,
            "is_reseller": is_reseller,
        }

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

    async def list_bindings_view(
        self,
        skip: int = 0,
        limit: int = 100,
        server_id: int | None = None,
        account_id: int | None = None,
        batch_id: str | None = None,
        step: BindingStep | None = None,
        active_only: bool | None = None,
    ) -> list[BindingViewRead]:
        """List bindings with joined server/account fields for UI display."""
        stmt = (
            select(
                Bindings,
                Servers.base_url.label("server_base_url"),
                Servers.port.label("server_port"),
                Servers.is_active.label("server_is_active"),
                Servers.device_id.label("server_device_id"),
                Accounts.msisdn.label("account_msisdn"),
                Accounts.email.label("account_email"),
                Accounts.status.label("account_status"),
                Accounts.batch_id.label("account_batch_id"),
            )
            .outerjoin(Servers, Servers.id == Bindings.server_id)
            .outerjoin(Accounts, Accounts.id == Bindings.account_id)
            .offset(skip)
            .limit(limit)
        )

        if server_id is not None:
            stmt = stmt.where(Bindings.server_id == server_id)
        if account_id is not None:
            stmt = stmt.where(Bindings.account_id == account_id)
        if batch_id is not None:
            stmt = stmt.where(Bindings.batch_id == batch_id)
        if step is not None:
            stmt = stmt.where(Bindings.step == step)
        if active_only:
            stmt = stmt.where(Bindings.unbound_at.is_(None))

        stmt = stmt.order_by(Bindings.id.desc())

        rows = (await self.session.execute(stmt)).all()
        items: list[BindingViewRead] = []
        for row in rows:
            binding = row.Bindings
            items.append(
                BindingViewRead(
                    id=binding.id,
                    server_id=binding.server_id,
                    account_id=binding.account_id,
                    batch_id=binding.batch_id,
                    step=binding.step,
                    is_reseller=binding.is_reseller,
                    balance_start=binding.balance_start,
                    balance_last=binding.balance_last,
                    last_error_code=binding.last_error_code,
                    last_error_message=binding.last_error_message,
                    token_login=binding.token_login,
                    token_location=binding.token_location,
                    token_location_refreshed_at=binding.token_location_refreshed_at,
                    device_id=binding.device_id,
                    bound_at=binding.bound_at,
                    unbound_at=binding.unbound_at,
                    created_at=binding.created_at,
                    updated_at=binding.updated_at,
                    server_base_url=row.server_base_url,
                    server_port=row.server_port,
                    server_is_active=row.server_is_active,
                    server_device_id=row.server_device_id,
                    account_msisdn=row.account_msisdn,
                    account_email=row.account_email,
                    account_status=row.account_status,
                    account_batch_id=row.account_batch_id,
                )
            )
        return items

    async def _resolve_bulk_ids(
        self, item: BindingBulkItemInput
    ) -> tuple[int, int, str]:
        """Resolve server/account IDs from direct IDs or port/msisdn pair."""
        if item.server_id is not None and item.account_id is not None:
            account = await self.accounts.get(self.session, item.account_id)
            if not account:
                raise AppValidationError(
                    message=f"Account ID {item.account_id} tidak ditemukan.",
                    error_code="account_not_found",
                    context={"account_id": item.account_id},
                )
            server = await self.servers.get(self.session, item.server_id)
            if not server:
                raise AppValidationError(
                    message=f"Server ID {item.server_id} tidak ditemukan.",
                    error_code="server_not_found",
                    context={"server_id": item.server_id},
                )
            return server.id, account.id, account.batch_id

        if item.port is None or item.msisdn is None:
            raise AppValidationError(
                message="Item bulk wajib server_id+account_id atau port+msisdn.",
                error_code="binding_bulk_invalid_item",
                context=item.model_dump(),
            )

        server = await self.servers.get_by(self.session, port=item.port)
        if not server:
            raise AppValidationError(
                message=f"Server port {item.port} tidak ditemukan.",
                error_code="server_not_found",
                context={"port": item.port},
            )

        if item.batch_id:
            account = await self.accounts.get_by_msisdn_batch(
                self.session, msisdn=item.msisdn, batch_id=item.batch_id
            )
            if not account:
                raise AppValidationError(
                    message="Account msisdn+batch_id tidak ditemukan.",
                    error_code="account_not_found",
                    context={"msisdn": item.msisdn, "batch_id": item.batch_id},
                )
            return server.id, account.id, account.batch_id

        stmt = select(Accounts).where(Accounts.msisdn == item.msisdn)
        accounts = (await self.session.execute(stmt)).scalars().all()
        if len(accounts) == 0:
            raise AppValidationError(
                message=f"Account dengan msisdn {item.msisdn} tidak ditemukan.",
                error_code="account_not_found",
                context={"msisdn": item.msisdn},
            )
        if len(accounts) > 1:
            raise AppValidationError(
                message=(
                    f"MSISDN {item.msisdn} muncul di beberapa batch. "
                    "Sertakan batch_id."
                ),
                error_code="account_batch_required",
                context={"msisdn": item.msisdn, "count": len(accounts)},
            )
        return server.id, accounts[0].id, accounts[0].batch_id

    async def _build_bulk_result(
        self, payload: BindingBulkRequest, *, dry_run: bool
    ) -> BindingBulkResult:
        """Build bulk dry-run/create result."""
        items: list[BindingBulkItemResult] = []
        total_created = 0
        total_failed = 0
        seen_server_ids: set[int] = set()
        seen_account_ids: set[int] = set()

        for index, item in enumerate(payload.items):
            try:
                server_id, account_id, batch_id = await self._resolve_bulk_ids(item)

                if server_id in seen_server_ids:
                    raise AppValidationError(
                        message="Server duplicate di payload bulk.",
                        error_code="binding_bulk_duplicate_server",
                        context={"index": index, "server_id": server_id},
                    )
                if account_id in seen_account_ids:
                    raise AppValidationError(
                        message="Account duplicate di payload bulk.",
                        error_code="binding_bulk_duplicate_account",
                        context={"index": index, "account_id": account_id},
                    )

                active_server = await self.bindings.get_active_by_server(
                    self.session, server_id=server_id
                )
                if active_server:
                    raise AppValidationError(
                        message="Server masih memiliki binding aktif.",
                        error_code="binding_server_active",
                        context={"server_id": server_id},
                    )

                active_account = await self.bindings.get_active_by_account(
                    self.session, account_id=account_id
                )
                if active_account:
                    raise AppValidationError(
                        message="Account masih memiliki binding aktif.",
                        error_code="binding_account_active",
                        context={"account_id": account_id},
                    )

                seen_server_ids.add(server_id)
                seen_account_ids.add(account_id)

                if dry_run:
                    items.append(
                        BindingBulkItemResult(
                            index=index,
                            status="would_create",
                            reason=None,
                            server_id=server_id,
                            account_id=account_id,
                            port=item.port,
                            msisdn=item.msisdn,
                            batch_id=batch_id,
                            binding=None,
                        )
                    )
                    total_created += 1
                    continue

                binding = await self.create_binding(
                    BindingCreate(
                        server_id=server_id,
                        account_id=account_id,
                        balance_start=item.balance_start,
                    )
                )
                items.append(
                    BindingBulkItemResult(
                        index=index,
                        status="created",
                        reason=None,
                        server_id=server_id,
                        account_id=account_id,
                        port=item.port,
                        msisdn=item.msisdn,
                        batch_id=batch_id,
                        binding=BindingRead.model_validate(binding),
                    )
                )
                total_created += 1
            except Exception as exc:
                total_failed += 1
                items.append(
                    BindingBulkItemResult(
                        index=index,
                        status="failed",
                        reason=str(exc),
                        server_id=item.server_id,
                        account_id=item.account_id,
                        port=item.port,
                        msisdn=item.msisdn,
                        batch_id=item.batch_id,
                        binding=None,
                    )
                )
                if payload.stop_on_first_error:
                    break

        return BindingBulkResult(
            dry_run=dry_run,
            total_requested=len(payload.items),
            total_created=total_created,
            total_failed=total_failed,
            items=items,
        )

    async def bulk_create_bindings(self, payload: BindingBulkRequest) -> BindingBulkResult:
        """Create bindings in bulk."""
        return await self._build_bulk_result(payload, dry_run=False)

    async def bulk_dry_run_bindings(self, payload: BindingBulkRequest) -> BindingBulkResult:
        """Dry-run bulk binding creation without writes."""
        return await self._build_bulk_result(payload, dry_run=True)

    async def check_balance(self, binding_id: int) -> Bindings:
        """Fetch latest balance and persist it to binding/account."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        self.guard.ensure_binding_step(
            action="check_balance",
            current=binding.step,
            allowed={
                BindingStep.BOUND,
                BindingStep.OTP_REQUESTED,
                BindingStep.OTP_VERIFICATION,
                BindingStep.OTP_VERIFIED,
                BindingStep.TOKEN_LOGIN_FETCHED,
            },
            context={"binding_id": binding_id},
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
        balance_resp = await idv.get_balance_pulsa(account.msisdn)
        balance_value = (
            balance_resp.get("res", {}).get("balance")
            if isinstance(balance_resp, dict)
            else None
        )
        try:
            balance_int = int(balance_value) if balance_value is not None else None
        except ValueError:
            balance_int = None

        updated = await self.bindings.update(
            self.session, binding, balance_last=balance_int
        )
        await self.accounts.update(self.session, account, balance_last=balance_int)
        return updated

    async def refresh_token_location(self, binding_id: int) -> Bindings:
        """Refresh token_location and persist it on binding."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        self.guard.ensure_binding_step(
            action="refresh_token_location",
            current=binding.step,
            allowed={BindingStep.OTP_VERIFIED, BindingStep.TOKEN_LOGIN_FETCHED},
            context={"binding_id": binding_id},
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
        token_location_resp = await idv.get_token_location3(account.msisdn)
        token_location = (
            token_location_resp.get("token")
            if isinstance(token_location_resp, dict)
            else token_location_resp
        )
        return await self.bindings.update(
            self.session,
            binding,
            token_location=token_location,
            token_location_refreshed_at=datetime.utcnow(),
        )

    async def verify_reseller(self, binding_id: int) -> Bindings:
        """Re-check reseller status from provider and persist it."""
        binding = await self.bindings.get(self.session, binding_id)
        if not binding:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )

        self.guard.ensure_binding_step(
            action="verify_reseller",
            current=binding.step,
            allowed={BindingStep.OTP_VERIFIED, BindingStep.TOKEN_LOGIN_FETCHED},
            context={"binding_id": binding_id},
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
        list_resp = await idv.list_produk(account.msisdn)

        is_reseller = False
        detected_device_id = None
        if isinstance(list_resp, dict):
            is_reseller = (
                list_resp.get("status") == "200"
                or list_resp.get("status_msg") == "success"
                or list_resp.get("data", {})
                .get("product_group", {})
                .get("product_type")
                == "reseller"
            )
            detected_device_id = (
                list_resp.get("data", {}).get("identifier", {}).get("device_id")
            )

        updated = await self.bindings.update(
            self.session,
            binding,
            is_reseller=is_reseller,
            device_id=detected_device_id or binding.device_id,
        )
        await self.accounts.update(
            self.session,
            account,
            is_reseller=is_reseller,
            last_device_id=detected_device_id or account.last_device_id,
        )
        return updated

    async def preview_products(
        self, payload: BindingProductsPreviewRequest
    ) -> BindingProductsPreviewResult:
        """Fetch product list runtime for selected bindings."""
        items: list[BindingProductsPreviewItem] = []
        total_ok = 0
        total_skipped = 0
        total_failed = 0

        for binding_id in payload.binding_ids:
            binding = await self.bindings.get(self.session, binding_id)
            if not binding:
                total_failed += 1
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=0,
                        msisdn="-",
                        is_reseller=False,
                        status="failed",
                        reason="binding_not_found",
                        products=[],
                    )
                )
                continue

            account = await self.accounts.get(self.session, binding.account_id)
            if not account:
                total_failed += 1
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=binding.account_id,
                        msisdn="-",
                        is_reseller=False,
                        status="failed",
                        reason="account_not_found",
                        products=[],
                    )
                )
                continue

            if payload.reseller_only and not binding.is_reseller:
                total_skipped += 1
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=account.id,
                        msisdn=account.msisdn,
                        is_reseller=binding.is_reseller,
                        status="skipped",
                        reason="binding_not_reseller",
                        products=[],
                    )
                )
                continue

            server = await self.servers.get(self.session, binding.server_id)
            if not server:
                total_failed += 1
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=account.id,
                        msisdn=account.msisdn,
                        is_reseller=binding.is_reseller,
                        status="failed",
                        reason="server_not_found",
                        products=[],
                    )
                )
                continue

            try:
                idv = IdvService.from_server(server)
                products_resp = await idv.list_produk(account.msisdn)
                product_list = (
                    products_resp.get("data", {}).get("product_list", [])
                    if isinstance(products_resp, dict)
                    else []
                )
                products = [
                    BindingProductItem(
                        id=item.get("id"),
                        name=item.get("name"),
                        lower_price=(
                            int(item.get("lower_price"))
                            if str(item.get("lower_price", "")).isdigit()
                            else None
                        ),
                    )
                    for item in product_list
                    if isinstance(item, dict)
                ]
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=account.id,
                        msisdn=account.msisdn,
                        is_reseller=binding.is_reseller,
                        status="ok",
                        reason=None,
                        products=products,
                    )
                )
                total_ok += 1
            except Exception as exc:
                total_failed += 1
                items.append(
                    BindingProductsPreviewItem(
                        binding_id=binding_id,
                        account_id=account.id,
                        msisdn=account.msisdn,
                        is_reseller=binding.is_reseller,
                        status="failed",
                        reason=str(exc),
                        products=[],
                    )
                )

        return BindingProductsPreviewResult(
            total_requested=len(payload.binding_ids),
            total_ok=total_ok,
            total_skipped=total_skipped,
            total_failed=total_failed,
            items=items,
        )

    async def delete_binding(self, binding_id: int) -> None:
        """Delete binding by ID."""
        deleted = await self.bindings.delete(self.session, binding_id)
        if not deleted:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
