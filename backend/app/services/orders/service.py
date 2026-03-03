"""Order service layer - business logic with Pydantic DTOs."""

from app.api.schemas.accounts import AccountCreateInput, BulkAccountCreateRequest
from app.api.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.orders import Orders
from app.repos.base import BaseRepository
from app.services.accounts.service import AccountService
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("service.orders")


class OrderService:
    """Service for order management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BaseRepository(Orders)
        self.accounts_repo = BaseRepository(Accounts)
        self.account_service = AccountService(session)

    async def create_order(self, data: OrderCreateRequest) -> OrderResponse:
        """Create a new order with optional MSISDN list.

        This operation is atomic. If account creation fails, the order 
        creation will be rolled back by the session handler.
        """
        log_ctx = {"name": data.name, "email": data.email}
        logger.info("Creating order", extra=log_ctx)

        # 1. Validate Email Uniqueness
        await self._validate_email_uniqueness(data.email)

        # 2. Fail-fast: Validate MSISDNs in request
        msisdn_list = self._normalize_msisdns(data.msisdns)

        # 3. Create Order Entity
        order = await self.repo.create(
            self.session,
            name=data.name.strip(),
            email=data.email.lower().strip(),
            default_pin=data.default_pin,
            description=data.description,
            is_active=data.is_active,
            notes=data.notes,
        )

        # 4. Process Accounts if provided
        if msisdn_list:
            await self._create_associated_accounts(order, msisdn_list)

        # 5. Flush and refresh to ensure DB consistency before fetching counts
        await self.session.flush()

        logger.info("Order created successfully", extra={"order_id": order.id})

        # Return fully populated order (with account_count from get_order)
        return await self.get_order(order.id)
    async def get_order(self, order_id: int) -> OrderResponse:
        """Get an order by ID with validation."""
        order = await self.repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order dengan ID {order_id} tidak ditemukan",
                error_code="order_not_found",
                context={"order_id": order_id},
            )
        return OrderResponse.model_validate(order)

    async def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List orders with account count summary."""
        filters = []
        if is_active is not None:
            filters.append(Orders.is_active == is_active)

        # Build query with outer join to count accounts
        stmt = (
            select(Orders, func.count(Accounts.id).label("account_count"))
            .outerjoin(Accounts, Orders.id == Accounts.order_id)
            .where(*filters)
            .group_by(Orders.id)
            .order_by(Orders.id.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                **{
                    c.name: getattr(row.Orders, c.name)
                    for c in Orders.__table__.columns
                },
                "account_count": row.account_count,
            }
            for row in rows
        ]

    async def update_order(
        self,
        order_id: int,
        data: OrderUpdateRequest,
    ) -> OrderResponse:
        """Update an order's information."""
        order = await self._get_order_entity(order_id)

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Validate email uniqueness if it's being changed
        if "email" in update_data:
            await self._validate_email_uniqueness(
                update_data["email"], exclude_id=order_id
            )

        updated_order = await self.repo.update(self.session, order, **update_data)
        logger.info("Order updated", extra={"order_id": order_id})

        return OrderResponse.model_validate(updated_order)

    async def delete_order(self, order_id: int) -> None:
        """Delete an order and its associated data."""
        order = await self._get_order_entity(order_id)

        # BaseRepository handles the deletion
        await self.repo.delete(self.session, order.id)
        logger.info("Order deleted", extra={"order_id": order_id})

    async def toggle_order_status(
        self,
        order_id: int,
        is_active: bool,
    ) -> OrderResponse:
        """Quick toggle for order active status."""
        order = await self._get_order_entity(order_id)

        updated_order = await self.repo.update(self.session, order, is_active=is_active)

        logger.info(
            "Order status toggled",
            extra={"order_id": order_id, "is_active": is_active},
        )
        return OrderResponse.model_validate(updated_order)

    # --- Private Helpers ---

    async def _get_order_entity(self, order_id: int) -> Orders:
        """Internal helper to get the raw SQLAlchemy model."""
        order = await self.repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order dengan ID {order_id} tidak ditemukan",
                error_code="order_not_found",
                context={"order_id": order_id},
            )
        return order

    async def _validate_email_uniqueness(
        self, email: str, exclude_id: int | None = None
    ) -> None:
        """Ensure email is not already used by another order."""
        existing = await self.repo.get_by(self.session, email=email.lower().strip())
        if existing and (exclude_id is None or existing.id != exclude_id):
            err_ctx = {"email": email, "existing_id": existing.id}
            raise AppValidationError(
                message=f"Email '{email}' sudah terdaftar dengan ID {existing.id}",
                error_code="order_email_duplicate",
                context=err_ctx,
            )

    def _normalize_msisdns(self, msisdns: list[str] | None) -> list[str]:
        """Strip and validate MSISDN list for duplicates in request."""
        if not msisdns:
            return []

        msisdn_list = [m.strip() for m in msisdns if m.strip()]
        if len(msisdn_list) != len(set(msisdn_list)):
            raise AppValidationError(
                message="Daftar MSISDN mengandung duplikasi nomor dalam satu permintaan.",
                error_code="order_msisdn_duplicate_in_request",
            )
        return msisdn_list

    async def _create_associated_accounts(
        self, order: Orders, msisdns: list[str]
    ) -> None:
        """Delegate bulk account creation to AccountService."""
        logger.info(
            f"Creating {len(msisdns)} accounts for order",
            extra={"order_id": order.id},
        )

        bulk_request = BulkAccountCreateRequest(
            order_id=order.id,
            accounts=[
                AccountCreateInput(
                    msisdn=m,
                    email=order.email,
                    pin=order.default_pin,
                )
                for m in msisdns
            ],
        )
        await self.account_service.bulk_create_accounts(bulk_request)
