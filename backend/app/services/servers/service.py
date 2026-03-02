"""Server service layer - business logic with Pydantic DTOs."""

from app.api.schemas.servers import (
    ServerBulkCreateRequest,
    ServerBulkCreateResult,
    ServerBulkItemResult,
    ServerCreateRequest,
    ServerResponse,
    ServerUpdateRequest,
)
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.core.log_config import get_logger
from app.models.servers import Servers
from app.repos.server_repo import ServerRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("service.servers")


class ServerService:
    """Service for server management - business logic layer.

    Uses Pydantic schemas as DTOs (Data Transfer Objects).
    No redundant command/query objects.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServerRepository(Servers)

    async def create_server(self, data: ServerCreateRequest) -> ServerResponse:
        """Create a new server."""
        log_ctx = {"port": data.port, "base_url": data.base_url}
        logger.info("Creating server", extra=log_ctx)

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
        server = await self.repo.create(
            self.session,
            name=data.name.strip(),
            port=data.port,
            base_url=data.base_url,
            description=data.description,
            timeout=data.timeout,
            retries=data.retries,
            wait_between_retries=data.wait_between_retries,
            max_requests_queued=data.max_requests_queued,
            delay_per_hit=data.delay_per_hit,
            is_active=data.is_active,
            notes=data.notes,
        )

        logger.info("Server created successfully", extra={"server_id": server.id})
        return ServerResponse.model_validate(server)

    async def get_server(self, server_id: int) -> ServerResponse:
        """Get a server by ID."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )
        return ServerResponse.model_validate(server)

    async def list_servers(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[ServerResponse]:
        """List servers with optional filtering."""
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        servers = await self.repo.get_multi(
            self.session, skip=skip, limit=limit, **filters
        )
        return [ServerResponse.model_validate(s) for s in servers]

    async def update_server(
        self,
        server_id: int,
        data: ServerUpdateRequest,
    ) -> ServerResponse:
        """Update a server."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

        # Prepare update data (exclude None values)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Validate port uniqueness if changing port
        if "port" in update_data:
            existing_by_port = await self.repo.get_by(
                self.session, port=update_data["port"]
            )
            if existing_by_port and existing_by_port.id != server_id:
                raise AppValidationError(
                    message=f"Port {update_data['port']} is already in use",
                    error_code="server_port_duplicate",
                    context={
                        "port": update_data["port"],
                        "existing_id": existing_by_port.id,
                    },
                )

        # Update server
        updated_server = await self.repo.update(self.session, server, **update_data)

        logger.info("Server updated", extra={"server_id": server_id})
        return ServerResponse.model_validate(updated_server)

    async def toggle_server_status(
        self,
        server_id: int,
        is_active: bool,
    ) -> ServerResponse:
        """Toggle server active status."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

        updated_server = await self.repo.update(
            self.session, server, is_active=is_active
        )

        logger.info(
            "Server status toggled",
            extra={"server_id": server_id, "is_active": is_active},
        )
        return ServerResponse.model_validate(updated_server)

    async def delete_server(self, server_id: int) -> None:
        """Delete a server."""
        server = await self.repo.get(self.session, server_id)
        if not server:
            raise AppNotFoundError(
                message=f"Server with ID {server_id} not found",
                error_code="server_not_found",
                context={"server_id": server_id},
            )

        # Deactivate first (business rule)
        if server.is_active:
            await self.repo.update(self.session, server, is_active=False)

        # Delete
        await self.repo.delete(self.session, server_id)

        logger.info("Server deleted", extra={"server_id": server_id})

    async def create_servers_bulk(
        self,
        data: ServerBulkCreateRequest,
    ) -> ServerBulkCreateResult:
        """Create multiple servers from one host and port range."""
        # Validate port range
        self._validate_port_range(data.start_port, data.end_port)

        items: list[ServerBulkItemResult] = []
        created_count = 0
        skipped_count = 0
        failed_count = 0
        total_requested = (data.end_port - data.start_port) + 1

        # Prepare defaults
        server_defaults = {
            "description": data.description,
            "timeout": data.timeout,
            "retries": data.retries,
            "wait_between_retries": data.wait_between_retries,
            "max_requests_queued": data.max_requests_queued,
            "delay_per_hit": data.delay_per_hit,
            "is_active": data.is_active,
            "notes": data.notes,
        }

        for port in range(data.start_port, data.end_port + 1):
            base_url = f"{data.base_host}:{port}"
            server_name = f"{data.base_name} {port}"

            try:
                # Check port conflict
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

                # Check URL conflict
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

                # Create server
                server = await self.repo.create(
                    self.session,
                    name=server_name,
                    port=port,
                    base_url=base_url,
                    description=server_defaults["description"],
                    timeout=server_defaults["timeout"],
                    retries=server_defaults["retries"],
                    wait_between_retries=server_defaults["wait_between_retries"],
                    max_requests_queued=server_defaults["max_requests_queued"],
                    delay_per_hit=server_defaults["delay_per_hit"],
                    is_active=server_defaults["is_active"],
                    notes=server_defaults["notes"],
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

            except Exception as e:
                failed_count += 1
                items.append(
                    ServerBulkItemResult(
                        port=port,
                        base_url=base_url,
                        status="failed",
                        reason=str(e),
                        server=None,
                    )
                )

        logger.info(
            "Bulk server creation completed",
            extra={
                "total_requested": total_requested,
                "created": created_count,
                "skipped": skipped_count,
                "failed": failed_count,
            },
        )

        return ServerBulkCreateResult(
            dry_run=False,
            base_host=data.base_host,
            start_port=data.start_port,
            end_port=data.end_port,
            total_requested=total_requested,
            total_created=created_count,
            total_skipped=skipped_count,
            total_failed=failed_count,
            items=items,
        )

    async def dry_run_bulk(
        self,
        data: ServerBulkCreateRequest,
    ) -> ServerBulkCreateResult:
        """Preview bulk server creation without persisting."""
        # Validate port range
        self._validate_port_range(data.start_port, data.end_port)

        items: list[ServerBulkItemResult] = []
        skipped_count = 0

        for port in range(data.start_port, data.end_port + 1):
            base_url = f"{data.base_host}:{port}"

            # Check port conflict
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

            # Check URL conflict
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

            # Would be created
            items.append(
                ServerBulkItemResult(
                    port=port,
                    base_url=base_url,
                    status="would_create",
                    reason=None,
                    server=None,
                )
            )

        total_requested = (data.end_port - data.start_port) + 1
        would_create_count = total_requested - skipped_count

        logger.info(
            "Bulk dry-run completed",
            extra={
                "total_requested": total_requested,
                "would_create": would_create_count,
                "skipped": skipped_count,
            },
        )

        return ServerBulkCreateResult(
            dry_run=True,
            base_host=data.base_host,
            start_port=data.start_port,
            end_port=data.end_port,
            total_requested=total_requested,
            total_created=would_create_count,
            total_skipped=skipped_count,
            total_failed=0,
            items=items,
        )

    @staticmethod
    def _validate_port_range(
        start_port: int,
        end_port: int,
        max_range: int = 501,
    ) -> None:
        """Validate port range constraints.

        Raises ValueError if range is invalid.
        """
        if start_port < 1 or start_port > 65535:
            raise ValueError("start_port must be between 1 and 65535")

        if end_port < 1 or end_port > 65535:
            raise ValueError("end_port must be between 1 and 65535")

        if end_port < start_port:
            raise ValueError("end_port must be greater than or equal to start_port")

        if (end_port - start_port) >= max_range:
            raise ValueError(f"Port range cannot exceed {max_range} ports")
