"""Account service layer - business logic with Pydantic DTOs."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.accounts import (
    AccountCreateRequest,
    AccountResponse,
    AccountUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.orders import Orders
from app.models.statuses import AccountStatus
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
                message=f"Order with ID {data.order_id} not found",
                error_code="order_not_found",
                context={"order_id": data.order_id},
            )

        # Check if MSISDN already exists for this order
        existing = await self.accounts_repo.get_by(
            self.session, msisdn=data.msisdn, order_id=data.order_id
        )
        if existing:
            raise AppValidationError(
                message=f"MSISDN '{data.msisdn}' already exists for this order",
                error_code="account_msisdn_duplicate",
                context={"msisdn": data.msisdn, "order_id": data.order_id},
            )

        # Create account
        account = await self.accounts_repo.create(
            self.session,
            order_id=data.order_id,
            msisdn=data.msisdn.strip(),
            email=data.email.strip(),
            pin=data.pin or order.default_pin,
            status=AccountStatus.NEW,
            is_reseller=data.is_reseller or False,
        )

        logger.info("Account created successfully", extra={"account_id": account.id})
        return AccountResponse.model_validate(account)

    async def get_account(self, account_id: int) -> AccountResponse:
        """Get an account by ID."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account with ID {account_id} not found",
                error_code="account_not_found",
                context={"account_id": account_id},
            )
        return AccountResponse.model_validate(account)

    async def list_accounts(
        self,
        order_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AccountResponse]:
        """List accounts with optional order filter."""
        filters = {}
        if order_id is not None:
            filters["order_id"] = order_id

        accounts = await self.accounts_repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        return [AccountResponse.model_validate(a) for a in accounts]

    async def update_account(
        self,
        account_id: int,
        data: AccountUpdateRequest,
    ) -> AccountResponse:
        """Update an account."""
        account = await self.accounts_repo.get(self.session, account_id)
        if not account:
            raise AppNotFoundError(
                message=f"Account with ID {account_id} not found",
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
                message=f"Account with ID {account_id} not found",
                error_code="account_not_found",
                context={"account_id": account_id},
            )

        await self.accounts_repo.delete(self.session, account_id)
        logger.info("Account deleted", extra={"account_id": account_id})
