"""API routes for bindings management."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.bindings import Bindings
from app.models.steps import BindingStep
from app.services.bindings import (
    BindingCreate,
    BindingLogout,
    BindingRead,
    BindingService,
    BindingUpdate,
)

router = APIRouter()


@router.post("/", response_model=BindingRead, status_code=status.HTTP_201_CREATED)
async def create_binding(
    payload: BindingCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    service = BindingService(session)
    return await service.create_binding(payload)


@router.get("/", response_model=list[BindingRead])
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


@router.get("/{binding_id}", response_model=BindingRead)
async def get_binding(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    service = BindingService(session)
    return await service.get_binding(binding_id)


@router.patch("/{binding_id}", response_model=BindingRead)
async def update_binding(
    binding_id: int,
    payload: BindingUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    service = BindingService(session)
    return await service.update_binding(binding_id, payload)


@router.post("/{binding_id}/logout", response_model=BindingRead)
async def logout_binding(
    binding_id: int,
    payload: BindingLogout,
    session: AsyncSession = Depends(get_db_session),
) -> Bindings:
    service = BindingService(session)
    return await service.logout_binding(binding_id, payload)


@router.delete("/{binding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_binding(
    binding_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    service = BindingService(session)
    await service.delete_binding(binding_id)
