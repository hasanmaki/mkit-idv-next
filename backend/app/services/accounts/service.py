"""Account service layer - business logic with Pydantic DTOs."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.accounts import (
    AccountCreateRequest,
    AccountResponse,
    AccountUpdateRequest,
    BulkAccountCreateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.orders import Orders
from app.repos.base import BaseRepository

logger = get_logger("service.accounts")


class AccountService:
    """Service for account management - business logic layer."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.accounts_repo = BaseRepository(Accounts)
        self.orders_repo = BaseRepository(Orders)

    async def create_account(self, data: AccountCreateRequest) -> AccountResponse:
        """Create a single account."""
        log_ctx = {"msisdn": data.msisdn, "order_id": data.order_id}
        logger.info("Creating account", extra=log_ctx)

        # Verify order exists
        order = await self.orders_repo.get(self.session, data.order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order dengan ID {data.order_id} tidak ditemukan",
                error_code="order_not_found",
                context={"order_id": data.order_id},
            )

        # Check if MSISDN already exists for this order
        existing = await self.accounts_repo.get_by(
            self.session, msisdn=data.msisdn, order_id=data.order_id
        )
        if existing:
            err_ctx = {"msisdn": data.msisdn, "order_id": data.order_id, "existing_id": existing.id}
            logger.warning("MSISDN already exists for this order", extra=err_ctx)
            raise AppValidationError(
                message=f"Nomor MSISDN '{data.msisdn}' sudah terdaftar dalam Order ini (ID Akun: {existing.id})",
                error_code="account_msisdn_duplicate",
                context=err_ctx,
            )

        # Create account
        account = await self.accounts_repo.create(
            self.session,
            order_id=data.order_id,
            msisdn=data.msisdn.strip(),
            email=data.email.strip(),
            pin=data.pin or order.default_pin,
            is_active=True,
            is_processed=False,
        )

        logger.info("Account created successfully", extra={"account_id": account.id})
        return AccountResponse.model_validate(account)

    async def bulk_create_accounts(
        self,
        data: BulkAccountCreateRequest,
    ) -> list[AccountResponse]:
        """Create multiple accounts for an order at once.

        - Verifies order exists
        - Validates no duplicate MSISDNs within the batch
        - Validates no duplicate MSISDNs already in database
        - Creates all accounts in a single transaction
        """
        log_ctx = {"order_id": data.order_id, "account_count": len(data.accounts)}
        logger.info("Creating bulk accounts", extra=log_ctx)

        # Verify order exists
        order = await self.orders_repo.get(self.session, data.order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order dengan ID {data.order_id} tidak ditemukan",
                error_code="order_not_found",
                context={"order_id": data.order_id},
            )

        # Validate no duplicate MSISDNs within the batch
        msisdn_set: set[str] = set()
        for idx, acc_data in enumerate(data.accounts):
            msisdn_normalized = acc_data.msisdn.strip()
            if msisdn_normalized in msisdn_set:
                raise AppValidationError(
                    message=f"Daftar mengandung MSISDN ganda: '{msisdn_normalized}'",
                    error_code="account_msisdn_duplicate_in_batch",
                    context={
                        "order_id": data.order_id,
                        "msisdn": msisdn_normalized,
                        "index": idx,
                    },
                )
            msisdn_set.add(msisdn_normalized)

        # Check for existing MSISDNs in database
        existing_accounts = await self.accounts_repo.get_multi(
            self.session, order_id=data.order_id
        )
        existing_msisdns = {acc.msisdn: acc.id for acc in existing_accounts}

        for idx, acc_data in enumerate(data.accounts):
            msisdn_normalized = acc_data.msisdn.strip()
            if msisdn_normalized in existing_msisdns:
                existing_id = existing_msisdns[msisdn_normalized]
                raise AppValidationError(
                    message=f"Nomor MSISDN '{msisdn_normalized}' sudah terdaftar dalam Order ini (ID Akun: {existing_id})",
                    error_code="account_msisdn_duplicate",
                    context={"order_id": data.order_id, "msisdn": msisdn_normalized, "existing_id": existing_id},
                )

        # Create all accounts
        created_accounts: list[Accounts] = []
        for acc_data in data.accounts:
            account = await self.accounts_repo.create(
                self.session,
                order_id=data.order_id,
                msisdn=acc_data.msisdn.strip(),
                email=acc_data.email.strip(),
                pin=acc_data.pin or order.default_pin,
                is_active=True,
                is_processed=False,
            )
            created_accounts.append(account)
            logger.info(
                "Account created",
                extra={
                    "account_id": account.id,
                    "msisdn": account.msisdn,
                    "order_id": data.order_id,
                },
            )

        logger.info(
            "Bulk accounts created successfully",
            extra={"order_id": data.order_id, "created_count": len(created_accounts)},
        )
        return [AccountResponse.model_validate(acc) for acc in created_accounts]

    async def get_account(self, account_id: int) -> AccountResponse:
        """Get an account by ID."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Akun dengan ID {account_id} tidak ditemukan",
                error_code="account_not_found",
                context={"account_id": account_id},
            )
        return AccountResponse.model_validate(account)

    async def list_accounts(
        self,
        order_id: int | None = None,
        msisdn: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
        is_processed: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """List accounts with comprehensive filtering.
        
        Returns accounts with order_name included.
        """
        from sqlalchemy import select

        # Build query with join to get order_name
        stmt = select(Accounts, Orders.name.label('order_name')).join(
            Orders, Accounts.order_id == Orders.id
        )

        # Apply filters
        if order_id is not None:
            stmt = stmt.where(Accounts.order_id == order_id)

        if msisdn:
            stmt = stmt.where(Accounts.msisdn.like(f"%{msisdn.strip()}%"))

        if email:
            stmt = stmt.where(Accounts.email.like(f"%{email.strip()}%"))

        if is_active is not None:
            stmt = stmt.where(Accounts.is_active == is_active)

        if is_processed is not None:
            stmt = stmt.where(Accounts.is_processed == is_processed)

        # Apply pagination and sorting
        stmt = stmt.order_by(Accounts.id.desc()).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        # Format response
        return [
            {
                **{c.name: getattr(row.Accounts, c.name) for c in Accounts.__table__.columns},
                'order_name': row.order_name,
            }
            for row in rows
        ]

    async def update_account(
        self,
        account_id: int,
        data: AccountUpdateRequest,
    ) -> AccountResponse:
        """Update an account."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Akun dengan ID {account_id} tidak ditemukan",
                error_code="account_not_found",
                context={"account_id": account_id},
            )

        # Prepare update data (exclude None values)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Update account
        updated_account = await self.accounts_repo.update(
            self.session, account, **update_data
        )

        logger.info("Account updated", extra={"account_id": account_id})
        return AccountResponse.model_validate(updated_account)

    async def delete_account(self, account_id: int) -> None:
        """Delete an account."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Akun dengan ID {account_id} tidak ditemukan",
                error_code="account_not_found",
                context={"account_id": account_id},
            )

        await self.accounts_repo.delete(self.session, account_id)
        logger.info("Account deleted", extra={"account_id": account_id})
