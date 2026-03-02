"""Order service layer - business logic with Pydantic DTOs."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.orders import Orders
from app.repos.order_repo import OrderRepository

logger = get_logger("service.orders")


class OrderService:
    """Service for order management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    No redundant command/query objects.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = OrderRepository(Orders)

    async def create_order(self, data: OrderCreateRequest) -> OrderResponse:
        """Create a new order."""
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
            description=data.description,
            is_active=data.is_active,
            notes=data.notes,
        )

        logger.info("Order created successfully", extra={"order_id": order.id})
        return OrderResponse.model_validate(order)

    async def get_order(self, order_id: int) -> OrderResponse:
        """Get an order by ID."""
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
    ) -> list[OrderResponse]:
        """List orders with optional filtering."""
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        orders = await self.repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        return [OrderResponse.model_validate(o) for o in orders]

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
