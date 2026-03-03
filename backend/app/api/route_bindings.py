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
    SmartBindRequest,
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
    """Bind a single account to a server for an order."""
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
    """Bind multiple accounts to a single server."""
    return await service.bulk_bind_accounts(payload)


@router.post(
    "/smart",
    response_model=list[BindingResponse],
    status_code=status.HTTP_201_CREATED,
)
async def smart_bind_accounts(
    payload: SmartBindRequest,
    service: BindingService = Depends(get_binding_service),
) -> list[BindingResponse]:
    """Pairwise binding using port:msisdn mapping."""
    return await service.smart_bind_accounts(payload)


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
    """List bindings with optional filtering."""
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
    "/{binding_id}",
    response_model=BindingResponse,
    responses={404: {"description": "Binding not found"}},
)
async def update_binding(
    binding_id: int,
    payload: dict,
    service: BindingService = Depends(get_binding_service),
) -> BindingResponse:
    """Update binding properties."""
    return await service.update_binding(binding_id, payload)


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
    """Manually update workflow step and metadata."""
    return await service.update_workflow_step(binding_id, payload)


@router.post(
    "/{binding_id}/release",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Binding not found"}},
)
async def release_binding(
    binding_id: int,
    payload: ReleaseBindingRequest | None = None,
    service: BindingService = Depends(get_binding_service),
) -> Response:
    """Release (delete) a binding."""
    await service.release_binding(binding_id, payload or ReleaseBindingRequest())
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
