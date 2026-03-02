"""API routes for session management.

Thin controller layer that delegates to application services.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.sessions import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusUpdateRequest,
    SessionUpdateRequest,
)
from app.application.sessions.commands import (
    CreateSessionCommand,
    DeleteSessionCommand,
    ToggleSessionStatusCommand,
    UpdateSessionCommand,
)
from app.application.sessions.handlers import SessionCommandHandler
from app.application.sessions.queries import GetSessionQuery, ListSessionsQuery
from app.application.sessions.query_handlers import SessionQueryHandler
from app.database.session import get_db_session
from app.domain.sessions.exceptions import (
    SessionDomainException,
    SessionDuplicateError,
    SessionNotFoundError,
)

router = APIRouter()


def _get_command_handler(session: AsyncSession = Depends(get_db_session)) -> SessionCommandHandler:
    """Get session command handler."""
    return SessionCommandHandler(session)


def _get_query_handler(session: AsyncSession = Depends(get_db_session)) -> SessionQueryHandler:
    """Get session query handler."""
    return SessionQueryHandler(session)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": dict, "description": "Validation error or duplicate email"},
    },
)
@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_session(
    payload: SessionCreateRequest,
    handler: SessionCommandHandler = Depends(_get_command_handler),
) -> SessionResponse:
    """Create a new session.

    A session represents a user/operator context that can have multiple
    server bindings.

    - **name**: Session name (3-100 characters)
    - **email**: Unique email identifier
    - **description**: Optional description
    - **is_active**: Whether session is active (default: true)
    - **notes**: Additional notes (optional)
    """
    command = CreateSessionCommand(
        name=payload.name,
        email=payload.email,
        description=payload.description,
        is_active=payload.is_active,
        notes=payload.notes,
    )

    session = await handler.handle_create(command)
    return SessionResponse.model_validate(session)


@router.get(
    "",
    response_model=list[SessionResponse],
)
@router.get(
    "/",
    response_model=list[SessionResponse],
    include_in_schema=False,
)
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    handler: SessionQueryHandler = Depends(_get_query_handler),
) -> list[SessionResponse]:
    """List sessions with optional filtering and pagination.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **is_active**: Filter by active status (optional)
    """
    query = ListSessionsQuery(skip=skip, limit=limit, is_active=is_active)
    sessions = await handler.handle_list(query)
    return [SessionResponse.model_validate(s) for s in sessions]


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    responses={404: {"description": "Session not found"}},
)
async def get_session(
    session_id: int,
    handler: SessionQueryHandler = Depends(_get_query_handler),
) -> SessionResponse:
    """Get a session by ID."""
    query = GetSessionQuery(session_id=session_id)
    session = await handler.handle_get(query)
    return SessionResponse.model_validate(session)


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    responses={
        404: {"description": "Session not found"},
        400: {"description": "Validation error or duplicate email"},
    },
)
async def update_session(
    session_id: int,
    payload: SessionUpdateRequest,
    handler: SessionCommandHandler = Depends(_get_command_handler),
) -> SessionResponse:
    """Partially update a session.

    Only provided fields will be updated.
    Email must be unique across all sessions.
    """
    command = UpdateSessionCommand(
        session_id=session_id,
        name=payload.name,
        email=payload.email,
        description=payload.description,
        is_active=payload.is_active,
        notes=payload.notes,
    )

    session = await handler.handle_update(command)
    return SessionResponse.model_validate(session)


@router.patch(
    "/{session_id}/status",
    response_model=SessionResponse,
    responses={404: {"description": "Session not found"}},
)
async def toggle_status(
    session_id: int,
    payload: SessionStatusUpdateRequest,
    handler: SessionCommandHandler = Depends(_get_command_handler),
) -> SessionResponse:
    """Toggle session active status.

    - **is_active**: Set to true to activate, false to deactivate
    """
    command = ToggleSessionStatusCommand(session_id=session_id, is_active=payload.is_active)
    session = await handler.handle_toggle_status(command)
    return SessionResponse.model_validate(session)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Session not found"}},
)
async def delete_session(
    session_id: int,
    handler: SessionCommandHandler = Depends(_get_command_handler),
) -> Response:
    """Delete a session.

    This will also remove all associated bindings (future feature).
    """
    command = DeleteSessionCommand(session_id=session_id)
    await handler.handle_delete(command)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
