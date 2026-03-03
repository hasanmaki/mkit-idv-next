"""API routes for account management.

Simple router layer that delegates to service layer.
"""

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_account_service
from app.api.schemas.accounts import (
    AccountCreateRequest,
    AccountResponse,
    AccountUpdateRequest,
    BulkAccountCreateRequest,
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


@router.post(
    "/bulk",
    response_model=list[AccountResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_accounts(
    payload: BulkAccountCreateRequest,
    service: AccountService = Depends(get_account_service),
) -> list[AccountResponse]:
    """Create multiple accounts for an order at once.

    - **order_id**: Order ID these accounts belong to (must exist)
    - **accounts**: List of accounts to create with msisdn, email, pin (optional), is_reseller

    All accounts are created in a single transaction. If any validation fails,
    no accounts will be created.
    """
    return await service.bulk_create_accounts(payload)


@router.get(
    "",
    response_model=list[AccountResponse],
)
async def list_accounts(
    order_id: int | None = None,
    msisdn: str | None = None,
    email: str | None = None,
    is_active: bool | None = None,
    is_processed: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    service: AccountService = Depends(get_account_service),
) -> list[AccountResponse]:
    """List accounts with comprehensive filtering."""
    accounts_data = await service.list_accounts(
        order_id=order_id,
        msisdn=msisdn,
        email=email,
        is_active=is_active,
        is_processed=is_processed,
        skip=skip,
        limit=limit,
    )
    return [AccountResponse(**account_data) for account_data in accounts_data]



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
