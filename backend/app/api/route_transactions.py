"""API routes for transaction management."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError
from app.database.session import get_db_session
from app.models.transaction_statuses import TransactionStatus
from app.models.transactions import Transactions, TransactionSnapshots
from app.services.transactions import (
    TransactionCreateRequest,
    TransactionOtpRequest,
    TransactionRead,
    TransactionService,
    TransactionSnapshotRead,
    TransactionSnapshotUpdate,
    TransactionStartRequest,
    TransactionStatusUpdate,
    TransactionStopRequest,
)

router = APIRouter()


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.create_transaction(
        payload.transaction, snapshot=payload.snapshot
    )


@router.post("/start", response_model=TransactionRead)
async def start_transaction(
    payload: TransactionStartRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.start_transaction(payload)


@router.post("/{transaction_id}/otp", response_model=TransactionRead)
async def submit_otp(
    transaction_id: int,
    payload: TransactionOtpRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.submit_otp(transaction_id, payload)


@router.post("/{transaction_id}/continue", response_model=TransactionRead)
async def continue_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.continue_transaction(transaction_id)


@router.post("/{transaction_id}/stop", response_model=TransactionRead)
async def stop_transaction(
    transaction_id: int,
    payload: TransactionStopRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.stop_transaction(transaction_id, payload)


@router.get("/", response_model=list[TransactionRead])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    status_filter: TransactionStatus | None = None,
    binding_id: int | None = None,
    account_id: int | None = None,
    server_id: int | None = None,
    batch_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[Transactions]:
    service = TransactionService(session)
    return list(
        await service.list_transactions(
            skip=skip,
            limit=limit,
            status=status_filter,
            binding_id=binding_id,
            account_id=account_id,
            server_id=server_id,
            batch_id=batch_id,
        )
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.get_transaction(transaction_id)


@router.patch("/{transaction_id}/status", response_model=TransactionRead)
async def update_transaction_status(
    transaction_id: int,
    payload: TransactionStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    service = TransactionService(session)
    return await service.update_status(transaction_id, payload)


@router.patch("/{transaction_id}/snapshot", response_model=TransactionSnapshotRead)
async def update_transaction_snapshot(
    transaction_id: int,
    payload: TransactionSnapshotUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionSnapshots:
    service = TransactionService(session)
    return await service.update_snapshot(transaction_id, payload)


@router.get("/{transaction_id}/snapshot", response_model=TransactionSnapshotRead)
async def get_transaction_snapshot(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionSnapshots:
    service = TransactionService(session)
    snapshot = await service.snapshots.get_by(session, transaction_id=transaction_id)
    if not snapshot:
        raise AppNotFoundError(
            message="Snapshot tidak ditemukan.",
            error_code="transaction_snapshot_not_found",
            context={"transaction_id": transaction_id},
        )
    return snapshot


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    service = TransactionService(session)
    await service.delete_transaction(transaction_id)
