"""API routes for accounts management."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.accounts import Accounts
from app.models.statuses import AccountStatus
from app.services.accounts import (
    AccountCreateBulk,
    AccountCreateSingle,
    AccountDelete,
    AccountRead,
    AccountUpdate,
    AccountsService,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AccountRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    payload: AccountCreateSingle,
    session: AsyncSession = Depends(get_db_session),
) -> Accounts:
    service = AccountsService(session)
    return await service.create_single(payload)


@router.post(
    "/bulk",
    response_model=list[AccountRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_accounts_bulk(
    payload: AccountCreateBulk,
    session: AsyncSession = Depends(get_db_session),
) -> list[Accounts]:
    service = AccountsService(session)
    return await service.create_bulk(payload)


@router.get(
    "/",
    response_model=list[AccountRead],
)
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    status_filter: AccountStatus | None = None,
    is_reseller: bool | None = None,
    batch_id: str | None = None,
    email: str | None = None,
    msisdn: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[Accounts]:
    service = AccountsService(session)
    return list(
        await service.list_accounts(
            skip=skip,
            limit=limit,
            status=status_filter,
            is_reseller=is_reseller,
            batch_id=batch_id,
            email=email,
            msisdn=msisdn,
        )
    )


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Accounts:
    service = AccountsService(session)
    return await service.get_account(account_id)


@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: int,
    payload: AccountUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Accounts:
    service = AccountsService(session)
    return await service.update_account(account_id, payload)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    payload: AccountDelete,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    service = AccountsService(session)
    await service.delete_account(payload)
