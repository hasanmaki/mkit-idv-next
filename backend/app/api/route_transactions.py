"""API routes for transaction management."""

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError
from app.database.session import get_db_session
from app.models.transaction_statuses import TransactionStatus
from app.models.transactions import Transactions, TransactionSnapshots
from app.services.idv import IdvService
from app.services.transactions import (
    TransactionCreateRequest,
    TransactionOtpRequest,
    TransactionPauseRequest,
    TransactionRead,
    TransactionResumeRequest,
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
    """Create a transaction and optional snapshot from request payload."""
    service = TransactionService(session)
    return await service.create_transaction(
        payload.transaction, snapshot=payload.snapshot
    )


@router.post("/start", response_model=TransactionRead)
async def start_transaction(
    payload: TransactionStartRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Start a transaction flow: balance -> trx -> status -> snapshot updates."""
    service = TransactionService(session)
    return await service.start_transaction(payload)


@router.post("/{transaction_id}/otp", response_model=TransactionRead)
async def submit_otp(
    transaction_id: int,
    payload: TransactionOtpRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Submit an OTP for a transaction and re-check status/balance."""
    service = TransactionService(session)
    return await service.submit_otp(transaction_id, payload)


@router.post("/{transaction_id}/continue", response_model=TransactionRead)
async def continue_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Continue an in-progress transaction by re-checking status and balance."""
    service = TransactionService(session)
    return await service.continue_transaction(transaction_id)


@router.post("/{transaction_id}/stop", response_model=TransactionRead)
async def stop_transaction(
    transaction_id: int,
    payload: TransactionStopRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Stop a transaction manually with an optional reason."""
    service = TransactionService(session)
    return await service.stop_transaction(transaction_id, payload)


@router.post("/{transaction_id}/pause", response_model=TransactionRead)
async def pause_transaction(
    transaction_id: int,
    payload: TransactionPauseRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Pause an active transaction.

    Can only pause transactions with status PROCESSING or RESUMED.
    """
    service = TransactionService(session)
    return await service.pause_transaction(transaction_id, payload)


@router.post("/{transaction_id}/resume", response_model=TransactionRead)
async def resume_transaction(
    transaction_id: int,
    payload: TransactionResumeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Resume a paused transaction.

    Validates that:
    - Transaction status is PAUSED
    - Current balance is sufficient to continue
    """
    service = TransactionService(session)
    return await service.resume_transaction(transaction_id, payload)


class BalanceCheckResponse(BaseModel):
    """Response for balance check endpoint."""

    transaction: TransactionRead
    action: str
    current_balance: int | None
    threshold: int | None
    checked_at: datetime

    model_config = {"from_attributes": True}


@router.post("/{transaction_id}/check", response_model=BalanceCheckResponse)
async def check_balance_and_continue(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Check balance and auto-decide: continue or stop transaction.

    On-demand check that:
    1. Fetches current balance from IDV service
    2. Compares with product price (limit_harga)
    3. If balance sufficient: continues transaction (re-checks status)
    4. If balance insufficient: stops transaction automatically

    Returns:
        Action taken ("continued" or "stopped") with transaction details
    """
    service = TransactionService(session)
    updated_trx, action = await service.check_balance_and_continue_or_stop(
        transaction_id
    )

    # Fetch balance info for response
    binding, account, server = await service._load_binding_context(
        updated_trx.binding_id
    )
    idv_service = IdvService.from_server(server)
    current_balance = await service._fetch_balance_int(idv_service, account.msisdn)

    return {
        "transaction": updated_trx,
        "action": action,
        "current_balance": current_balance,
        "threshold": updated_trx.limit_harga,
        "checked_at": datetime.utcnow(),
    }


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
    """List transactions with optional filters and pagination."""
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
    """Retrieve a transaction by its ID."""
    service = TransactionService(session)
    return await service.get_transaction(transaction_id)


@router.patch("/{transaction_id}/status", response_model=TransactionRead)
async def update_transaction_status(
    transaction_id: int,
    payload: TransactionStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Transactions:
    """Update the status fields of a transaction."""
    service = TransactionService(session)
    return await service.update_status(transaction_id, payload)


@router.patch("/{transaction_id}/snapshot", response_model=TransactionSnapshotRead)
async def update_transaction_snapshot(
    transaction_id: int,
    payload: TransactionSnapshotUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionSnapshots:
    """Update the snapshot for a transaction and return it."""
    service = TransactionService(session)
    return await service.update_snapshot(transaction_id, payload)


@router.get("/{transaction_id}/snapshot", response_model=TransactionSnapshotRead)
async def get_transaction_snapshot(
    transaction_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionSnapshots:
    """Retrieve a transaction snapshot by transaction ID."""
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
    """Delete a transaction by ID."""
    service = TransactionService(session)
    await service.delete_transaction(transaction_id)
