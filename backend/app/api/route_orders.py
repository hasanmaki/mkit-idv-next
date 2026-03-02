"""API routes for order management.

Simple router layer that delegates to service layer.
"""

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_order_service
from app.api.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    OrderUpdateRequest,
)
from app.services.orders.service import OrderService

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": dict, "description": "Validation error or duplicate email"},
    },
)
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_order(
    payload: OrderCreateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create a new order.

    An order represents a customer context that can have multiple server bindings.

    - **name**: Customer name (3-100 characters)
    - **email**: Unique email identifier
    - **description**: Optional description
    - **is_active**: Whether order is active (default: true)
    - **notes**: Additional notes (optional)
    """
    return await service.create_order(payload)


@router.get(
    "",
    response_model=list[OrderResponse],
)
@router.get(
    "/",
    response_model=list[OrderResponse],
    include_in_schema=False,
)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    """List orders with optional filtering and pagination.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **is_active**: Filter by active status (optional)
    """
    return await service.list_orders(skip=skip, limit=limit, is_active=is_active)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"description": "Order not found"}},
)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Get an order by ID."""
    return await service.get_order(order_id)


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    responses={
        404: {"description": "Order not found"},
        400: {"description": "Validation error or duplicate email"},
    },
)
async def update_order(
    order_id: int,
    payload: OrderUpdateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Partially update an order.

    Only provided fields will be updated.
    Email must be unique across all orders.
    """
    return await service.update_order(order_id, payload)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    responses={404: {"description": "Order not found"}},
)
async def toggle_order_status(
    order_id: int,
    payload: OrderStatusUpdateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Toggle order active status.

    - **is_active**: Set to true to activate, false to deactivate
    """
    return await service.toggle_order_status(order_id, payload.is_active)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Order not found"}},
)
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> Response:
    """Delete an order.

    This will also remove all associated bindings.
    """
    await service.delete_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
