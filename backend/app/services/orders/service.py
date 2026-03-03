"""Order service layer - business logic with Pydantic DTOs."""

from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.accounts import Accounts
from app.models.orders import Orders
from app.models.statuses import AccountStatus
from app.repos.base import BaseRepository

logger = get_logger("service.orders")


class OrderService:
    """Service for order management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    No redundant command/query objects.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BaseRepository(Orders)
        self.accounts_repo = BaseRepository(Accounts)

    async def create_order(self, data: OrderCreateRequest) -> OrderResponse:
        """Create a new order with optional MSISDN list."""
        log_ctx = {"name": data.name, "email": data.email}
        logger.info("Creating order", extra=log_ctx)

        # Check for email duplicate
        existing_by_email = await self.repo.get_by(self.session, email=data.email)
        if existing_by_email:
            err_ctx = {"email": data.email, "existing_id": existing_by_email.id}
            logger.warning("Email already registered", extra=err_ctx)
            raise AppValidationError(
                message=f"Email '{data.email}' is already registered",
                error_code="order_email_duplicate",
                context=err_ctx,
            )

        # Create order
        order = await self.repo.create(
            self.session,
            name=data.name.strip(),
            email=data.email.lower().strip(),
            default_pin=data.default_pin,
            description=data.description,
            is_active=data.is_active,
            notes=data.notes,
        )

        # Create accounts if MSISDNs provided
        if data.msisdns:
            logger.info(
                f"Creating {len(data.msisdns)} accounts for order",
                extra={"order_id": order.id},
            )
            for msisdn in data.msisdns:
                try:
                    await self.accounts_repo.create(
                        self.session,
                        order_id=order.id,
                        msisdn=msisdn.strip(),
                        email=data.email.lower().strip(),
                        pin=data.default_pin,
                        status=AccountStatus.NEW,
                        is_reseller=False,
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to create account for MSISDN {msisdn}: {str(e)}",
                        extra={"msisdn": msisdn, "order_id": order.id},
                    )

        logger.info("Order created successfully", extra={"order_id": order.id})
        return OrderResponse.model_validate(order)

    async def get_order(self, order_id: int) -> OrderResponse:
        """Get an order by ID with account count."""
        order = await self.repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order with ID {order_id} not found",
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
        """List orders with account count."""
        from sqlalchemy import func
        
        filters = []
        if is_active is not None:
            filters.append(Orders.is_active == is_active)

        # Query orders with account count
        stmt = (
            sa.select(Orders, func.count(Accounts.id).label('account_count'))
            .outerjoin(Accounts, Orders.id == Accounts.order_id)
            .where(*filters)
            .group_by(Orders.id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        return [
            {
                **{c.name: getattr(row.Orders, c.name) for c in Orders.__table__.columns},
                'account_count': row.account_count,
            }
            for row in rows
        ]

    async def update_order(
        self,
        order_id: int,
        data: OrderUpdateRequest,
    ) -> OrderResponse:
        """Update an order."""
        order = await self.repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order with ID {order_id} not found",
                error_code="order_not_found",
                context={"order_id": order_id},
            )

        # Prepare update data (exclude None values)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Validate email uniqueness if changing email
        if "email" in update_data:
            existing_by_email = await self.repo.get_by(
                self.session, email=update_data["email"]
            )
            if existing_by_email and existing_by_email.id != order_id:
                raise AppValidationError(
                    message=f"Email '{update_data['email']}' is already in use",
                    error_code="order_email_duplicate",
                    context={"email": update_data["email"], "existing_id": existing_by_email.id},
                )

        # Update order
        updated_order = await self.repo.update(self.session, order, **update_data)

        logger.info("Order updated", extra={"order_id": order_id})
        return OrderResponse.model_validate(updated_order)

    async def delete_order(self, order_id: int) -> None:
        """Delete an order."""
        order = await self.repo.get(self.session, order_id)
        if not order:
            raise AppNotFoundError(
                message=f"Order with ID {order_id} not found",
                error_code="order_not_found",
                context={"order_id": order_id},
            )

        # Delete (bindings will cascade delete)
        await self.repo.delete(self.session, order_id)

        logger.info("Order deleted", extra={"order_id": order_id})
