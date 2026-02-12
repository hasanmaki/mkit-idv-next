"""API routes for server management."""

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.servers import Servers
from app.services.servers import (
    ServerBulkCreateResult,
    ServerCreate,
    ServerCreateBulk,
    ServerResponse,
    ServerService,
    ServerUpdate,
)

router = APIRouter()


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_server(
    payload: ServerCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Servers:
    """Create a new server entry."""
    service = ServerService(session)
    return await service.create_server(payload)


@router.post(
    "/bulk",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_servers_bulk(
    payload: ServerCreateBulk,
    session: AsyncSession = Depends(get_db_session),
) -> ServerBulkCreateResult:
    """Create multiple servers from one host and a port range."""
    service = ServerService(session)
    return await service.create_servers_bulk(payload)


@router.post(
    "/bulk/dry-run",
    response_model=ServerBulkCreateResult,
    status_code=status.HTTP_200_OK,
)
async def dry_run_servers_bulk(
    payload: ServerCreateBulk,
    session: AsyncSession = Depends(get_db_session),
) -> ServerBulkCreateResult:
    """Preview bulk server creation without database writes."""
    service = ServerService(session)
    return await service.dry_run_servers_bulk(payload)


@router.get("", response_model=list[ServerResponse])
@router.get("/", response_model=list[ServerResponse], include_in_schema=False)
async def list_servers(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[Servers]:
    """List servers with optional filtering and pagination."""
    service = ServerService(session)
    return await service.get_servers(skip=skip, limit=limit, is_active=is_active)


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Servers:
    """Get a server by ID."""
    service = ServerService(session)
    return await service.get_server(server_id)


@router.patch("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    payload: ServerUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Servers:
    """Partially update a server."""
    service = ServerService(session)
    return await service.update_server(server_id, payload)


class ServerStatusUpdate(BaseModel):
    """DTO for updating the 'is_active' status of a server."""

    is_active: bool


@router.patch("/{server_id}/status", response_model=ServerResponse)
async def toggle_status(
    server_id: int,
    payload: ServerStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Servers:
    """Toggle server active status."""
    service = ServerService(session)
    return await service.toggle_server_status(server_id, payload.is_active)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete a server."""
    service = ServerService(session)
    await service.delete_server(server_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
