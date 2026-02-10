"""Service layer for Accounts."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.statuses import AccountStatus
from app.repos.account_repo import AccountRepository
from app.services.accounts.schemas import (
    AccountCreateBulk,
    AccountCreateSingle,
    AccountDelete,
    AccountUpdate,
)

logger = get_logger("service.accounts")


class AccountsService:
    """Service for managing accounts."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AccountRepository(Accounts)

    async def create_single(self, data: AccountCreateSingle) -> Accounts:
        """Create a single account."""
        existing = await self.repo.get_by_msisdn_batch(
            self.session, msisdn=data.msisdn, batch_id=data.batch_id
        )
        if existing:
            raise AppValidationError(
                message="Account dengan msisdn + batch_id sudah ada.",
                error_code="account_duplicate",
                context={"msisdn": data.msisdn, "batch_id": data.batch_id},
            )
        account = await self.repo.create(self.session, **data.model_dump())
        logger.info("Account created", extra={"account_id": account.id})
        return account

    async def create_bulk(self, data: AccountCreateBulk) -> list[Accounts]:
        """Create multiple accounts in one batch."""
        if not data.msisdns:
            raise AppValidationError(
                message="msisdns tidak boleh kosong.",
                error_code="account_msisdns_empty",
            )

        seen: set[str] = set()
        duplicates = [m for m in data.msisdns if m in seen or seen.add(m)]  # type: ignore[misc]
        if duplicates:
            raise AppValidationError(
                message="Terdapat duplikasi msisdn dalam request.",
                error_code="account_msisdn_duplicate_request",
                context={"duplicates": duplicates},
            )

        created: list[Accounts] = []
        for msisdn in data.msisdns:
            existing = await self.repo.get_by_msisdn_batch(
                self.session, msisdn=msisdn, batch_id=data.batch_id
            )
            if existing:
                raise AppValidationError(
                    message="Account sudah ada untuk msisdn + batch_id.",
                    error_code="account_duplicate",
                    context={"msisdn": msisdn, "batch_id": data.batch_id},
                )
            account = await self.repo.create(
                self.session,
                msisdn=msisdn,
                email=data.email,
                batch_id=data.batch_id,
                pin=data.pin,
                status=AccountStatus.NEW,
            )
            created.append(account)

        logger.info(
            "Bulk account created",
            extra={"count": len(created), "batch_id": data.batch_id},
        )
        return created

    async def get_account(self, account_id: int) -> Accounts:
        """Get account by ID."""
        account = await self.repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account dengan ID {account_id} tidak ditemukan.",
                error_code="account_not_found",
                context={"account_id": account_id},
            )
        return account

    async def list_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: AccountStatus | None = None,
        is_reseller: bool | None = None,
        batch_id: str | None = None,
        email: str | None = None,
        msisdn: str | None = None,
    ) -> Sequence[Accounts]:
        """List accounts with optional filters."""
        filters: dict = {}
        if status is not None:
            filters["status"] = status
        if is_reseller is not None:
            filters["is_reseller"] = is_reseller
        if batch_id is not None:
            filters["batch_id"] = batch_id
        if email is not None:
            filters["email"] = email
        if msisdn is not None:
            filters["msisdn"] = msisdn

        accounts = await self.repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        logger.debug("Accounts retrieved", extra={"count": len(accounts)})
        return accounts

    async def update_account(
        self, account_id: int, data: AccountUpdate
    ) -> Accounts:
        """Update account by ID."""
        account = await self.repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account dengan ID {account_id} tidak ditemukan.",
                error_code="account_not_found",
                context={"account_id": account_id},
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return account

        updated = await self.repo.update(self.session, account, **update_data)
        logger.info("Account updated", extra={"account_id": account_id})
        return updated

    async def delete_account(self, payload: AccountDelete) -> None:
        """Delete account by ID or msisdn+batch_id."""
        if payload.id is not None:
            deleted = await self.repo.delete(self.session, payload.id)
            if not deleted:
                raise AppNotFoundError(
                    message=f"Account dengan ID {payload.id} tidak ditemukan.",
                    error_code="account_not_found",
                    context={"account_id": payload.id},
                )
            logger.info("Account deleted", extra={"account_id": payload.id})
            return

        if payload.msisdn and payload.batch_id:
            account = await self.repo.get_by_msisdn_batch(
                self.session, msisdn=payload.msisdn, batch_id=payload.batch_id
            )
            if not account:
                raise AppNotFoundError(
                    message="Account dengan msisdn + batch_id tidak ditemukan.",
                    error_code="account_not_found",
                    context={"msisdn": payload.msisdn, "batch_id": payload.batch_id},
                )
            await self.repo.delete(self.session, account.id)
            logger.info(
                "Account deleted",
                extra={"msisdn": payload.msisdn, "batch_id": payload.batch_id},
            )
            return

        raise AppValidationError(
            message="Harus isi id atau msisdn + batch_id.",
            error_code="account_delete_invalid",
        )
