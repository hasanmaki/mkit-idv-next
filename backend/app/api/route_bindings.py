"""API routes for binding management.

Simple router layer that delegates to service layer.
"""

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_binding_service
from app.api.schemas.bindings import (
    BalanceStartUpdateRequest,
    BindAccountRequest,
    BindingResponse,
    BulkBindRequest,
    ReleaseBindingRequest,
    RequestOTPRequest,
    VerifyOTPRequest,
    WorkflowStepUpdateRequest,
)
from app.services.bindings.service import BindingService

router = APIRouter()


@router.get(
    "/accounts/by-order/{order_id}",
    response_model=list[dict],
)
async def list_accounts_by_order(
    order_id: int,
    service: BindingService = Depends(get_binding_service),
) -> list[dict]:
    """List accounts for a specific order (for dropdown)."""
    return await service.list_accounts_by_order(order_id)


@router.get(
    "/servers/active",
    response_model=list[dict],
)
async def list_active_servers(
    service: BindingService = Depends(get_binding_service),
) -> list[dict]:
    """List active servers (for dropdown)."""
    return await service.list_active_servers()


@router.post(
    "",
    response_model=BindingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Account already bound"},
    },
)
async def bind_account(
    payload: BindAccountRequest,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Bind a single account to a server for an order.

    - **order_id**: Order that owns this binding
    - **server_id**: Server to bind to
    - **account_id**: Account to bind (must not be already bound)
    - **is_reseller**: Whether it's a reseller account
    - **priority**: Priority for queue management (lower = higher priority)
    """
    return await service.bind_account(payload)


@router.post(
    "/bulk",
    response_model=list[BindingResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_bind_accounts(
    payload: BulkBindRequest,
    service: BindingService = Depends(get_binding_service),
) -> list[BindingResponse]:
    """Bind multiple accounts to a server for an order.

    - **order_id**: Order that owns these bindings
    - **server_id**: Server to bind to
    - **account_ids**: List of account IDs to bind
    - **is_reseller**: Whether they are reseller accounts
    - **priority**: Priority for all bindings
    """
    return await service.bulk_bind_accounts(payload)


@router.get(
    "",
    response_model=list[BindingResponse],
)
async def list_bindings(
    skip: int = 0,
    limit: int = 100,
    order_id: int | None = None,
    is_active: bool | None = None,
    service: BindingService = Depends(get_binding_service),
) -> list[BindingResponse]:
    """List bindings with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **order_id**: Filter by order ID (optional)
    - **is_active**: Filter by active status (optional)
    """
    return await service.list_bindings(
        skip=skip, limit=limit, order_id=order_id, is_active=is_active
    )


@router.get(
    "/active",
    response_model=list[BindingResponse],
)
async def list_active_bindings(
    service: BindingService = Depends(get_binding_service),
) -> list[BindingResponse]:
    """List all active bindings."""
    return await service.list_active_bindings()


@router.get(
    "/{binding_id}",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def get_binding(
    binding_id: int,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Get a binding by ID."""
    return await service.get_binding(binding_id)


@router.patch(
    "/{binding_id}/step",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def update_workflow_step(
    binding_id: int,
    payload: WorkflowStepUpdateRequest,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Manually update workflow step and metadata.

    This is a generic endpoint for any workflow transition like:
    - BINDED -> REQUEST_OTP
    - VERIFIED -> CHECK_BALANCE
    - CHECK_BALANCE -> COMPLETED
    """
    return await service.update_workflow_step(binding_id, payload)


@router.post(
    "/{binding_id}/release",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Binding not found"}},
)
async def release_binding(
    binding_id: int,
    payload: ReleaseBindingRequest,
    service: BindingService = Depends(get_binding_service),
) -> Response:
    """Release (deactivate) a binding."""
    await service.release_binding(binding_id, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{binding_id}/balance",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def set_balance_start(
    binding_id: int,
    payload: BalanceStartUpdateRequest,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Set balance start for a binding."""
    return await service.set_balance_start(binding_id, payload)


@router.post(
    "/{binding_id}/otp/request",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def request_otp(
    binding_id: int,
    payload: RequestOTPRequest,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Request OTP for a binding."""
    return await service.request_otp(binding_id, payload)


@router.post(
    "/{binding_id}/otp/verify",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def verify_otp(
    binding_id: int,
    payload: VerifyOTPRequest,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Verify OTP for a binding."""
    return await service.verify_otp(binding_id, payload)


@router.delete(
    "/{binding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Binding not found"}},
)
async def delete_binding(
    binding_id: int,
    service: BindingService = Depends(get_binding_service),
) -> Response:
    """Delete a binding."""
    await service.delete_binding(binding_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
