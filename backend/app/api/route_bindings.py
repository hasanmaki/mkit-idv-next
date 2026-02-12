"""API routes for bindings management."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.bindings import Bindings
from app.models.steps import BindingStep
from app.services.bindings import (
    BindingBulkRequest,
    BindingBulkResult,
    BindingCreate,
    BindingLogout,
    BindingRead,
    BindingRequestLogin,
    BindingService,
    BindingUpdate,
    BindingViewRead,
    BindingVerifyLogin,
)

router = APIRouter()


@router.post(
    "/bulk/dry-run",
    response_model=BindingBulkResult,
    status_code=status.HTTP_200_OK,
)
async def bulk_dry_run_bindings(
    payload: BindingBulkRequest,
    session: AsyncSession = Depends(get_db_session),
) -> BindingBulkResult:
    """Dry-run bulk binding creation without database writes."""
    service = BindingService(session)
    return await service.bulk_dry_run_bindings(payload)


@router.post("/bulk", response_model=BindingBulkResult, status_code=status.HTTP_201_CREATED)
async def bulk_create_bindings(
    payload: BindingBulkRequest,
    session: AsyncSession = Depends(get_db_session),
) -> BindingBulkResult:
    """Create bindings in bulk mode."""
    service = BindingService(session)
    return await service.bulk_create_bindings(payload)


@router.post("", response_model=BindingRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=BindingRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_binding(
    payload: BindingCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Create a binding between an account and a server."""
    service = BindingService(session)
    return await service.create_binding(payload)


@router.get("", response_model=list[BindingRead])
@router.get("/", response_model=list[BindingRead], include_in_schema=False)
async def list_bindings(
    skip: int = 0,
    limit: int = 100,
    server_id: int | None = None,
    account_id: int | None = None,
    batch_id: str | None = None,
    step: BindingStep | None = None,
    active_only: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[Bindings]:
    """List bindings with optional filters and pagination."""
    service = BindingService(session)
    return await service.list_bindings(
        skip=skip,
        limit=limit,
        server_id=server_id,
        account_id=account_id,
        batch_id=batch_id,
        step=step,
        active_only=active_only,
    )


@router.get("/view", response_model=list[BindingViewRead])
async def list_bindings_view(
    skip: int = 0,
    limit: int = 100,
    server_id: int | None = None,
    account_id: int | None = None,
    batch_id: str | None = None,
    step: BindingStep | None = None,
    active_only: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[BindingViewRead]:
    """List bindings with joined server/account display fields."""
    service = BindingService(session)
    return await service.list_bindings_view(
        skip=skip,
        limit=limit,
        server_id=server_id,
        account_id=account_id,
        batch_id=batch_id,
        step=step,
        active_only=active_only,
    )


@router.get("/{binding_id}", response_model=BindingRead)
async def get_binding(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Get a binding by ID."""
    service = BindingService(session)
    return await service.get_binding(binding_id)


@router.patch("/{binding_id}", response_model=BindingRead)
async def update_binding(
    binding_id: int,
    payload: BindingUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Update fields of an existing binding and return the updated binding."""
    service = BindingService(session)
    return await service.update_binding(binding_id, payload)


@router.post("/{binding_id}/logout", response_model=BindingRead)
async def logout_binding(
    binding_id: int,
    payload: BindingLogout,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Logout/unbind a binding and return the updated binding."""
    service = BindingService(session)
    return await service.logout_binding(binding_id, payload)


@router.post("/{binding_id}/request-login")
async def request_login(
    binding_id: int,
    payload: BindingRequestLogin,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Request OTP login for a binding."""
    service = BindingService(session)
    return await service.request_login(binding_id, payload)


@router.post("/{binding_id}/check-balance", response_model=BindingRead)
async def check_balance(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Check latest balance for a binding and persist it."""
    service = BindingService(session)
    return await service.check_balance(binding_id)


@router.post("/{binding_id}/refresh-token-location", response_model=BindingRead)
async def refresh_token_location(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    """Refresh token_location for a binding and persist it."""
    service = BindingService(session)
    return await service.refresh_token_location(binding_id)


@router.post("/{binding_id}/verify-login")
async def verify_login(
    binding_id: int,
    payload: BindingVerifyLogin,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Verify login OTP and reseller status for a binding."""
    service = BindingService(session)
    return await service.verify_login_and_reseller(binding_id, payload)


@router.delete("/{binding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binding(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a binding by ID."""
    service = BindingService(session)
    await service.delete_binding(binding_id)
