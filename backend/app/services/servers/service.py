"""Service layer for server management."""
# app/services/servers/service.py

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.servers import Servers
from app.repos.server_repo import ServerRepository
from app.services.servers.schemas import (
    ServerBulkCreateResult,
    ServerBulkItemResult,
    ServerCreate,
    ServerCreateBulk,
    ServerResponse,
    ServerUpdate,
)

logger = get_logger("service.servers")


class ServerService:
    """Service for managing server instances with full auditability."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServerRepository(Servers)

    async def create_server(self, data: ServerCreate) -> Servers:
        """Create a new server with validation and logging."""
        log_ctx = {"port": data.port, "base_url": data.base_url}
        logger.info("Initiating server creation", extra=log_ctx)

        # Check for port conflict
        existing_by_port = await self.repo.get_by(self.session, port=data.port)
        if existing_by_port:
            err_ctx = {"port": data.port, "existing_id": existing_by_port.id}
            logger.warning("Port already in use", extra=err_ctx)
            raise AppValidationError(
                message=f"Port {data.port} is already assigned to server ID {existing_by_port.id}",
                error_code="server_port_duplicate",
                context=err_ctx,
            )

        # Check for base_url conflict
        existing_by_url = await self.repo.get_by(self.session, base_url=data.base_url)
        if existing_by_url:
            err_ctx = {"base_url": data.base_url, "existing_id": existing_by_url.id}
            logger.warning("Base URL already registered", extra=err_ctx)
            raise AppValidationError(
                message=f"Base URL '{data.base_url}' is already in use",
                error_code="server_url_duplicate",
                context=err_ctx,
            )

        # Create server
        server = await self.repo.create(self.session, **data.model_dump())
        logger.info("Server created successfully", extra={"server_id": server.id})
        return server

    async def create_servers_bulk(
        self, data: ServerCreateBulk
    ) -> ServerBulkCreateResult:
        """Create many servers from one host and a port range."""
        items: list[ServerBulkItemResult] = []
        created_count = 0
        skipped_count = 0
        failed_count = 0
        total_requested = (data.end_port - data.start_port) + 1

        for port in range(data.start_port, data.end_port + 1):
            base_url = f"{data.base_host}:{port}"
            try:
                existing_by_port = await self.repo.get_by(self.session, port=port)
                if existing_by_port:
                    skipped_count += 1
                    items.append(
                        ServerBulkItemResult(
                            port=port,
                            base_url=base_url,
                            status="skipped",
                            reason="port already in use",
                            server=None,
                        )
                    )
                    continue

                existing_by_url = await self.repo.get_by(
                    self.session, base_url=base_url
                )
                if existing_by_url:
                    skipped_count += 1
                    items.append(
                        ServerBulkItemResult(
                            port=port,
                            base_url=base_url,
                            status="skipped",
                            reason="base_url already in use",
                            server=None,
                        )
                    )
                    continue

                server = await self.repo.create(
                    self.session,
                    port=port,
                    base_url=base_url,
                    description=data.description,
                    timeout=data.timeout,
                    retries=data.retries,
                    wait_between_retries=data.wait_between_retries,
                    max_requests_queued=data.max_requests_queued,
                    is_active=data.is_active,
                    notes=data.notes,
                    device_id=data.device_id,
                )
                created_count += 1
                items.append(
                    ServerBulkItemResult(
                        port=port,
                        base_url=base_url,
                        status="created",
                        reason=None,
                        server=ServerResponse.model_validate(server),
                    )
                )

            except Exception as exc:
                failed_count += 1
                items.append(
                    ServerBulkItemResult(
                        port=port,
                        base_url=base_url,
                        status="failed",
                        reason=str(exc),
                        server=None,
                    )
                )

        result = ServerBulkCreateResult(
            base_host=data.base_host,
            start_port=data.start_port,
            end_port=data.end_port,
            total_requested=total_requested,
            total_created=created_count,
            total_skipped=skipped_count,
            total_failed=failed_count,
            items=items,
        )
        logger.info(
            "Bulk server creation completed",
            extra={
                "total_requested": total_requested,
                "total_created": created_count,
                "total_skipped": skipped_count,
                "total_failed": failed_count,
            },
        )
        return result

    async def dry_run_servers_bulk(
        self, data: ServerCreateBulk
    ) -> ServerBulkCreateResult:
        """Preview bulk creation without inserting records."""
        items: list[ServerBulkItemResult] = []
        created_count = 0
        skipped_count = 0
        total_requested = (data.end_port - data.start_port) + 1

        for port in range(data.start_port, data.end_port + 1):
            base_url = f"{data.base_host}:{port}"
            existing_by_port = await self.repo.get_by(self.session, port=port)
            if existing_by_port:
                skipped_count += 1
                items.append(
                    ServerBulkItemResult(
                        port=port,
                        base_url=base_url,
                        status="skipped",
                        reason="port already in use",
                        server=None,
                    )
                )
                continue

            existing_by_url = await self.repo.get_by(self.session, base_url=base_url)
            if existing_by_url:
                skipped_count += 1
                items.append(
                    ServerBulkItemResult(
                        port=port,
                        base_url=base_url,
                        status="skipped",
                        reason="base_url already in use",
                        server=None,
                    )
                )
                continue

            created_count += 1
            items.append(
                ServerBulkItemResult(
                    port=port,
                    base_url=base_url,
                    status="would_create",
                    reason=None,
                    server=None,
                )
            )

        return ServerBulkCreateResult(
            base_host=data.base_host,
            start_port=data.start_port,
            end_port=data.end_port,
            total_requested=total_requested,
            total_created=created_count,
            total_skipped=skipped_count,
            total_failed=0,
            items=items,
        )

    async def update_server(self, server_id: int, data: ServerUpdate) -> Servers:
        """Update an existing server."""
        logger.info("Initiating server update", extra={"server_id": server_id})

        server = await self.repo.get(self.session, server_id)
        if not server:
            logger.warning(
                "Server not found for update", extra={"server_id": server_id}
            )
            raise AppValidationError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            logger.debug("No fields to update", extra={"server_id": server_id})
            return server

        # Special handling for port change
        if "port" in update_data:
            new_port = update_data["port"]
            existing = await self.repo.get_by(self.session, port=new_port)
            if existing and existing.id != server_id:
                err_ctx = {"new_port": new_port, "conflict_id": existing.id}
                logger.warning("Port conflict during update", extra=err_ctx)
                raise AppValidationError(
                    message=f"Port {new_port} is already in use",
                    error_code="server_port_conflict",
                    context=err_ctx,
                )

        updated_server = await self.repo.update(self.session, server, **update_data)
        logger.info("Server updated successfully", extra={"server_id": server_id})
        return updated_server

    async def get_active_servers(self) -> Sequence[Servers]:
        """Get all active servers."""
        servers = await self.repo.get_multi(self.session, is_active=True)
        logger.debug("Retrieved active servers", extra={"count": len(servers)})
        return servers

    async def toggle_server_status(self, server_id: int, is_active: bool) -> Servers:
        """Enable or disable a server."""
        action = "enabling" if is_active else "disabling"
        logger.info(f"Initiating {action} server", extra={"server_id": server_id})

        server = await self.repo.get(self.session, server_id)
        if not server:
            logger.warning(
                "Server not found for status toggle", extra={"server_id": server_id}
            )
            raise AppValidationError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

        updated = await self.repo.update(self.session, server, is_active=is_active)
        status_str = "enabled" if is_active else "disabled"
        logger.info(f"Server {status_str} successfully", extra={"server_id": server_id})
        return updated

    async def get_server(self, server_id: int) -> Servers:
        """Retrieve a server by ID or raise AppNotFoundError."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            logger.warning("Server not found", extra={"server_id": server_id})
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )
        return server

    async def get_servers(
        self, skip: int = 0, limit: int = 100, is_active: bool | None = None
    ) -> list[Servers]:
        """List servers with optional filtering and pagination."""
        filters: dict = {}
        if is_active is not None:
            filters["is_active"] = is_active
        servers = await self.repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        servers_list = list(servers)
        logger.debug(
            "Retrieved servers",
            extra={"count": len(servers_list), "is_active": is_active},
        )
        return servers_list

    async def delete_server(self, server_id: int) -> None:
        """Delete a server by ID or raise AppNotFoundError."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            logger.warning(
                "Server not found for delete", extra={"server_id": server_id}
            )
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )
        await self.repo.delete(self.session, server_id)
        logger.info("Server deleted successfully", extra={"server_id": server_id})
