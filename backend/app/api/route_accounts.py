"""API routes for account management.

Simple router layer that delegates to service layer.
"""

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_account_service
from app.api.schemas.accounts import (
    AccountCreateRequest,
    AccountResponse,
    AccountUpdateRequest,
)
from app.services.accounts.service import AccountService

router = APIRouter()


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    payload: AccountCreateRequest,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    """Create a single account."""
    return await service.create_account(payload)


@router.get(
    "",
    response_model=list[AccountResponse],
)
async def list_accounts(
    order_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    service: AccountService = Depends(get_account_service),
) -> list[AccountResponse]:
    """List accounts with optional order filter."""
    return await service.list_accounts(order_id=order_id, skip=skip, limit=limit)


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    responses={404: {"description": "Account not found"}},
)
async def get_account(
    account_id: int,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    """Get an account by ID."""
    return await service.get_account(account_id)


@router.patch(
    "/{account_id}",
    response_model=AccountResponse,
    responses={404: {"description": "Account not found"}},
)
async def update_account(
    account_id: int,
    payload: AccountUpdateRequest,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    """Update an account."""
    return await service.update_account(account_id, payload)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Account not found"}},
)
async def delete_account(
    account_id: int,
    service: AccountService = Depends(get_account_service),
) -> Response:
    """Delete an account."""
    await service.delete_account(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
