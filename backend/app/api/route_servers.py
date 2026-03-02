"""API routes for server management.

Simple router layer that delegates to service layer.
"""

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_server_service
from app.api.schemas.servers import (
    ServerBulkCreateRequest,
    ServerBulkCreateResult,
    ServerCreateRequest,
    ServerResponse,
    ServerStatusUpdateRequest,
    ServerUpdateRequest,
)
from app.services.servers.service import ServerService

router = APIRouter()


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
    service: ServerService = Depends(get_server_service),
) -> ServerResponse:
    """Create a new server entry.

    - **name**: User-friendly server name (unique)
    - **port**: Unique port number (1-65535)
    - **base_url**: Full URL including protocol and port
    """
    return await service.create_server(payload)


@router.post(
    "/bulk",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_servers_bulk(
    payload: ServerBulkCreateRequest,
    service: ServerService = Depends(get_server_service),
) -> ServerBulkCreateResult:
    """Create multiple servers from one host and a port range.

    - **base_host**: Host URL without port (e.g., http://10.0.0.3)
    - **start_port**: Range start (inclusive)
    - **end_port**: Range end (inclusive, max 501 ports)
    """
    return await service.create_servers_bulk(payload)


@router.post(
    "/bulk/dry-run",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_200_OK,
)
async def dry_run_servers_bulk(
    payload: ServerBulkCreateRequest,
    service: ServerService = Depends(get_server_service),
) -> ServerBulkCreateResult:
    """Preview bulk server creation without database writes.

    Returns what would be created/skipped without persisting.
    """
    return await service.dry_run_bulk(payload)


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
    service: ServerService = Depends(get_server_service),
) -> list[ServerResponse]:
    """List servers with optional filtering and pagination.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **is_active**: Filter by active status (optional)
    """
    return await service.list_servers(skip=skip, limit=limit, is_active=is_active)


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def get_server(
    server_id: int,
    service: ServerService = Depends(get_server_service),
) -> ServerResponse:
    """Get a server by ID."""
    return await service.get_server(server_id)


@router.patch(
    "/{server_id}",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def update_server(
    server_id: int,
    payload: ServerUpdateRequest,
    service: ServerService = Depends(get_server_service),
) -> ServerResponse:
    """Partially update a server.

    Only provided fields will be updated.
    """
    return await service.update_server(server_id, payload)


@router.patch(
    "/{server_id}/status",
    response_model=ServerResponse,
    responses={404: {"description": "Server not found"}},
)
async def toggle_status(
    server_id: int,
    payload: ServerStatusUpdateRequest,
    service: ServerService = Depends(get_server_service),
) -> ServerResponse:
    """Toggle server active status.

    - **is_active**: Set to true to activate, false to deactivate
    """
    return await service.toggle_server_status(server_id, payload.is_active)


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Server not found"}},
)
async def delete_server(
    server_id: int,
    service: ServerService = Depends(get_server_service),
) -> Response:
    """Delete a server.

    Server will be deactivated before deletion if active.
    """
    await service.delete_server(server_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
