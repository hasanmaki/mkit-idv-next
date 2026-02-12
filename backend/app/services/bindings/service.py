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
    BindingCreate,
    BindingLogout,
    BindingRequestLogin,
    BindingUpdate,
    BindingViewRead,
    BindingVerifyLogin,
)
from app.services.idv import IdvService

logger = get_logger("service.bindings")


class BindingService:
    """Service for managing bindings."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bindings = BindingRepository(Bindings)
        self.accounts = AccountRepository(Accounts)
        self.servers = ServerRepository(Servers)

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

        if binding.step != BindingStep.OTP_REQUESTED:
            raise AppValidationError(
                message="Flow invalid. Jalankan request-login terlebih dahulu.",
                error_code="binding_step_invalid",
                context={"binding_id": binding_id, "step": binding.step},
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

    async def delete_binding(self, binding_id: int) -> None:
        """Delete binding by ID."""
        deleted = await self.bindings.delete(self.session, binding_id)
        if not deleted:
            raise AppNotFoundError(
                message=f"Binding ID {binding_id} tidak ditemukan.",
                error_code="binding_not_found",
                context={"binding_id": binding_id},
            )
