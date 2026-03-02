"""API routes for binding management."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.bindings import (
    BalanceStartUpdateRequest,
    BindAccountRequest,
    BindingResponse,
    BulkBindRequest,
    ReleaseBindingRequest,
    RequestOTPRequest,
    VerifyOTPRequest,
)
from app.application.bindings.commands import (
    BindAccountCommand,
    BulkBindAccountsCommand,
    ReleaseBindingCommand,
    RequestOTPCommand,
    SetBalanceStartCommand,
    VerifyOTPCommand,
)
from app.application.bindings.handlers import BindingCommandHandler
from app.application.bindings.queries import (
    GetBindingQuery,
    ListActiveBindingsQuery,
    ListBindingsBySessionQuery,
)
from app.application.bindings.query_handlers import BindingQueryHandler
from app.database.session import get_db_session
from app.domain.bindings.exceptions import (
    AccountAlreadyBoundError,
    BindingDomainException,
    BindingNotFoundError,
    InvalidWorkflowTransitionError,
)

router = APIRouter()


def _get_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> BindingCommandHandler:
    """Get binding command handler."""
    return BindingCommandHandler(session)


def _get_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> BindingQueryHandler:
    """Get binding query handler."""
    return BindingQueryHandler(session)


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
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> BindingResponse:
    """Bind a single account to a server for a session.

    - **session_id**: Session that owns this binding
    - **server_id**: Server to bind to
    - **account_id**: Account to bind (must not be already bound)
    - **priority**: Priority for queue management (lower = higher priority)
    """
    command = BindAccountCommand(
        session_id=payload.session_id,
        server_id=payload.server_id,
        account_id=payload.account_id,
        priority=payload.priority,
        description=payload.description,
        notes=payload.notes,
    )

    binding = await handler.handle_bind(command)
    return BindingResponse.model_validate(binding)


@router.post(
    "/bulk",
    response_model=list[BindingResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_bind_accounts(
    payload: BulkBindRequest,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> list[BindingResponse]:
    """Bind multiple accounts to a server for a session.

    All accounts must not be already bound.
    """
    command = BulkBindAccountsCommand(
        session_id=payload.session_id,
        server_id=payload.server_id,
        account_ids=payload.account_ids,
        priority=payload.priority,
        description=payload.description,
        notes=payload.notes,
    )

    bindings = await handler.handle_bulk_bind(command)
    return [BindingResponse.model_validate(b) for b in bindings]


@router.post(
    "/{binding_id}/request-otp",
    response_model=BindingResponse,
)
async def request_otp(
    binding_id: int,
    payload: RequestOTPRequest,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> BindingResponse:
    """Request OTP for a binding.

    Transitions binding from BINDED → REQUEST_OTP.
    """
    command = RequestOTPCommand(binding_id=binding_id, pin=payload.pin)
    binding = await handler.handle_request_otp(command)
    return BindingResponse.model_validate(binding)


@router.post(
    "/{binding_id}/verify-otp",
    response_model=BindingResponse,
)
async def verify_otp(
    binding_id: int,
    payload: VerifyOTPRequest,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> BindingResponse:
    """Verify OTP for a binding.

    Transitions binding from REQUEST_OTP → VERIFY_OTP.
    After this, call mark-verified endpoint when OTP is confirmed successful.
    """
    command = VerifyOTPCommand(binding_id=binding_id, otp=payload.otp)
    binding = await handler.handle_verify_otp(command)
    return BindingResponse.model_validate(binding)


@router.post(
    "/{binding_id}/mark-verified",
    response_model=BindingResponse,
)
async def mark_verified(
    binding_id: int,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> BindingResponse:
    """Mark binding as verified (ready for transactions).

    Transitions binding from VERIFY_OTP → VERIFIED.
    """
    binding = await handler.handle_mark_verified(binding_id)
    return BindingResponse.model_validate(binding)


@router.post(
    "/{binding_id}/release",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def release_binding(
    binding_id: int,
    payload: ReleaseBindingRequest = Depends(lambda: ReleaseBindingRequest()),
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> Response:
    """Release a binding (logout).

    Transitions binding to LOGGED_OUT and sets is_active = false.
    Account becomes available for other sessions.
    """
    command = ReleaseBindingCommand(binding_id=binding_id)
    await handler.handle_release(command)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{binding_id}/balance",
    response_model=BindingResponse,
)
async def set_balance_start(
    binding_id: int,
    payload: BalanceStartUpdateRequest,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> BindingResponse:
    """Set balance start for a binding.

    - **balance_start**: Starting balance amount
    - **source**: 'MANUAL' (user input) or 'AUTO_CHECK' (from IDV provider)
    """
    command = SetBalanceStartCommand(
        binding_id=binding_id,
        balance_start=payload.balance_start,
        source=payload.source,
    )
    binding = await handler.handle_set_balance(command)
    return BindingResponse.model_validate(binding)


@router.get(
    "/{binding_id}",
    response_model=BindingResponse,
)
async def get_binding(
    binding_id: int,
    handler: BindingQueryHandler = Depends(_get_query_handler),
) -> BindingResponse:
    """Get a binding by ID."""
    query = GetBindingQuery(binding_id=binding_id)
    binding = await handler.handle_get(query)
    return BindingResponse.model_validate(binding)


@router.get(
    "",
    response_model=list[BindingResponse],
)
async def list_bindings(
    session_id: int | None = None,
    is_active: bool | None = None,
    handler: BindingQueryHandler = Depends(_get_query_handler),
) -> list[BindingResponse]:
    """List bindings with optional filters.

    - **session_id**: Filter by session ID
    - **is_active**: Filter by active status
    """
    if session_id is not None:
        query = ListBindingsBySessionQuery(session_id=session_id, is_active=is_active)
        bindings = await handler.handle_list_by_session(query)
    elif is_active is not None:
        query = ListActiveBindingsQuery(is_active=is_active)
        bindings = await handler.handle_list_active(query)
    else:
        # List all
        query = ListBindingsBySessionQuery(session_id=0)  # Dummy, will be ignored
        bindings = await handler.handle_list_by_session(query)

    return [BindingResponse.model_validate(b) for b in bindings]


@router.get(
    "/session/{session_id}",
    response_model=list[BindingResponse],
)
async def list_bindings_by_session(
    session_id: int,
    is_active: bool | None = None,
    handler: BindingQueryHandler = Depends(_get_query_handler),
) -> list[BindingResponse]:
    """List all bindings for a session."""
    query = ListBindingsBySessionQuery(session_id=session_id, is_active=is_active)
    bindings = await handler.handle_list_by_session(query)
    return [BindingResponse.model_validate(b) for b in bindings]


@router.delete(
    "/{binding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_binding(
    binding_id: int,
    handler: BindingCommandHandler = Depends(_get_command_handler),
) -> Response:
    """Delete a binding permanently."""
    # First release if active
    try:
        await handler.handle_release(ReleaseBindingCommand(binding_id=binding_id))
    except BindingNotFoundError:
        pass  # Already deleted or not found

    # Then delete
    from app.repos.binding_repo import BindingRepository
    from app.models.bindings import Bindings
    from app.database.session import get_db_session

    async for session in get_db_session():
        repo = BindingRepository(Bindings)
        await repo.delete(session, binding_id)
        break

    return Response(status_code=status.HTTP_204_NO_CONTENT)
