"""API routes for server management.

Thin controller layer that delegates to application services.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.servers import (
    ServerBulkCreateRequest,
    ServerBulkCreateResult,
    ServerCreateRequest,
    ServerResponse,
    ServerStatusUpdateRequest,
    ServerUpdateRequest,
)
from app.application.servers.commands import (
    CreateServerCommand,
    CreateServersBulkCommand,
    DeleteServerCommand,
    DryRunBulkServersCommand,
    ToggleServerStatusCommand,
    UpdateServerCommand,
)
from app.application.servers.handlers import ServerCommandHandler
from app.application.servers.queries import GetServerQuery, ListServersQuery
from app.application.servers.query_handlers import ServerQueryHandler
from app.database.session import get_db_session
from app.domain.servers.exceptions import (
    ServerDomainException,
    ServerDuplicateError,
    ServerNotFoundError,
)

router = APIRouter()


def _get_command_handler(session: AsyncSession = Depends(get_db_session)) -> ServerCommandHandler:
    """Get server command handler."""
    return ServerCommandHandler(session)


def _get_query_handler(session: AsyncSession = Depends(get_db_session)) -> ServerQueryHandler:
    """Get server query handler."""
    return ServerQueryHandler(session)


@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": dict, "description": "Validation error or duplicate"},
    },
)
@router.post(
    "/",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_server(
    payload: ServerCreateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerResponse:
    """Create a new server entry.

    - **port**: Unique port number (1-65535)
    - **base_url**: Full URL including protocol and port
    - **timeout**: Request timeout in seconds (1-30)
    - **retries**: Number of retry attempts (0-10)
    """
    command = CreateServerCommand(
        port=payload.port,
        base_url=payload.base_url,
        description=payload.description,
        timeout=payload.timeout,
        retries=payload.retries,
        wait_between_retries=payload.wait_between_retries,
        max_requests_queued=payload.max_requests_queued,
        is_active=payload.is_active,
        notes=payload.notes,
    )

    server = await handler.handle_create(command)
    return ServerResponse.model_validate(server)


@router.post(
    "/bulk",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_servers_bulk(
    payload: ServerBulkCreateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerBulkCreateResult:
    """Create multiple servers from one host and a port range.

    - **base_host**: Host URL without port (e.g., http://10.0.0.3)
    - **start_port**: Range start (inclusive)
    - **end_port**: Range end (inclusive, max 501 ports)
    """
    command = CreateServersBulkCommand(
        base_host=payload.base_host,
        start_port=payload.start_port,
        end_port=payload.end_port,
        description=payload.description,
        timeout=payload.timeout,
        retries=payload.retries,
        wait_between_retries=payload.wait_between_retries,
        max_requests_queued=payload.max_requests_queued,
        is_active=payload.is_active,
        notes=payload.notes,
    )

    result = await handler.handle_create_bulk(command)
    return ServerBulkCreateResult.model_validate(result)


@router.post(
    "/bulk/dry-run",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_200_OK,
)
async def dry_run_servers_bulk(
    payload: ServerBulkCreateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerBulkCreateResult:
    """Preview bulk server creation without database writes.

    Returns what would be created/skipped without persisting.
    """
    command = DryRunBulkServersCommand(
        base_host=payload.base_host,
        start_port=payload.start_port,
        end_port=payload.end_port,
    )

    result = await handler.handle_dry_run_bulk(command)
    return ServerBulkCreateResult.model_validate(result)


@router.get(
    "",
    response_model=list[ServerResponse],
)
@router.get(
    "/",
    response_model=list[ServerResponse],
    include_in_schema=False,
)
async def list_servers(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    handler: ServerQueryHandler = Depends(_get_query_handler),
) -> list[ServerResponse]:
    """List servers with optional filtering and pagination.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **is_active**: Filter by active status (optional)
    """
    query = ListServersQuery(skip=skip, limit=limit, is_active=is_active)
    servers = await handler.handle_list(query)
    return [ServerResponse.model_validate(s) for s in servers]


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def get_server(
    server_id: int,
    handler: ServerQueryHandler = Depends(_get_query_handler),
) -> ServerResponse:
    """Get a server by ID."""
    query = GetServerQuery(server_id=server_id)
    server = await handler.handle_get(query)
    return ServerResponse.model_validate(server)


@router.patch(
    "/{server_id}",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def update_server(
    server_id: int,
    payload: ServerUpdateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerResponse:
    """Partially update a server.

    Only provided fields will be updated.
    """
    command = UpdateServerCommand(
        server_id=server_id,
        description=payload.description,
        port=payload.port,
        timeout=payload.timeout,
        retries=payload.retries,
        wait_between_retries=payload.wait_between_retries,
        max_requests_queued=payload.max_requests_queued,
        is_active=payload.is_active,
        notes=payload.notes,
    )

    server = await handler.handle_update(command)
    return ServerResponse.model_validate(server)


@router.patch(
    "/{server_id}/status",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def toggle_status(
    server_id: int,
    payload: ServerStatusUpdateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerResponse:
    """Toggle server active status.

    - **is_active**: Set to true to activate, false to deactivate
    """
    command = ToggleServerStatusCommand(server_id=server_id, is_active=payload.is_active)
    server = await handler.handle_toggle_status(command)
    return ServerResponse.model_validate(server)


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Server not found"}},
)
async def delete_server(
    server_id: int,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> Response:
    """Delete a server.

    Server will be deactivated before deletion if active.
    """
    command = DeleteServerCommand(server_id=server_id)
    await handler.handle_delete(command)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
