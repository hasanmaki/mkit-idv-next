"""Server command handlers - application service layer."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.servers.commands import (
    CreateServerCommand,
    CreateServersBulkCommand,
    DeleteServerCommand,
    DryRunBulkServersCommand,
    ToggleServerStatusCommand,
    UpdateServerCommand,
)
from app.domain.servers.entities import Server
from app.domain.servers.events import ServerBulkCreatedEvent
from app.domain.servers.exceptions import (
    ServerBulkValidationError,
    ServerDuplicateError,
    ServerNotFoundError,
)
from app.domain.servers.services import ServerDomainService
from app.repos.server_repo import ServerRepository
from app.models.servers import Servers


class ServerCommandHandler:
    """Application service for handling server commands.

    Orchestrates between domain layer and infrastructure.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServerRepository(Servers)
        self.domain_service = ServerDomainService(self.repo)

    async def handle_create(self, command: CreateServerCommand) -> Server:
        """Handle create server command."""
        # Create domain entity
        server = Server.create(
            name=command.name,
            port=command.port,
            base_url=command.base_url,
            description=command.description,
            timeout=command.timeout,
            retries=command.retries,
            wait_between_retries=command.wait_between_retries,
            max_requests_queued=command.max_requests_queued,
            delay_per_hit=command.delay_per_hit,
            is_active=command.is_active,
            notes=command.notes,
            parameters=command.parameters,
            device_id=command.device_id,
        )

        # Validate uniqueness (port and base_url)
        await self.domain_service.validate_server_uniqueness(
            port=command.port,
            base_url=command.base_url,
        )

        # Persist
        server_data = server.model_dump(exclude={"_domain_events"})
        persisted_server = await self.repo.create(self.session, **server_data)

        # Pop and process domain events (could publish to event bus here)
        events = server.pop_events()
        # TODO: Dispatch events to event bus if needed

        return persisted_server

    async def handle_update(self, command: UpdateServerCommand) -> Server:
        """Handle update server command."""
        # Get existing server
        existing = await self.repo.get(self.session, command.server_id)
        if not existing:
            raise ServerNotFoundError(server_id=command.server_id)

        # Load as domain entity
        server = Server.model_validate(existing)

        # Prepare update data (exclude None values)
        update_data = {
            k: v for k, v in command.model_dump().items()
            if v is not None and k != "server_id"
        }

        # Validate port uniqueness if changing port
        if "port" in update_data:
            await self.domain_service.validate_server_uniqueness(
                port=update_data["port"],
                base_url=server.base_url,
                server_id=command.server_id,
            )

        # Apply update
        server.update(**update_data)

        # Persist
        persisted_server = await self.repo.update(
            self.session,
            existing,
            **update_data,
        )

        return persisted_server

    async def handle_delete(self, command: DeleteServerCommand) -> None:
        """Handle delete server command."""
        # Get existing server
        existing = await self.repo.get(self.session, command.server_id)
        if not existing:
            raise ServerNotFoundError(server_id=command.server_id)

        # Load as domain entity and mark for deletion
        server = Server.model_validate(existing)
        server.delete()

        # Deactivate first (business rule)
        if server.is_active:
            await self.repo.update(self.session, existing, is_active=False)

        # Delete
        await self.repo.delete(self.session, command.server_id)

    async def handle_toggle_status(
        self,
        command: ToggleServerStatusCommand,
    ) -> Server:
        """Handle toggle server status command."""
        # Get existing server
        existing = await self.repo.get(self.session, command.server_id)
        if not existing:
            raise ServerNotFoundError(server_id=command.server_id)

        # Load as domain entity and toggle
        server = Server.model_validate(existing)
        server.toggle_status(command.is_active)

        # Persist
        persisted_server = await self.repo.update(
            self.session,
            existing,
            is_active=command.is_active,
        )

        return persisted_server

    async def handle_create_bulk(
        self,
        command: CreateServersBulkCommand,
    ) -> dict[str, Any]:
        """Handle bulk server creation command."""
        # Validate port range
        ServerDomainService.validate_port_range(
            command.start_port,
            command.end_port,
        )

        # Prepare defaults
        server_defaults = {
            "description": command.description,
            "timeout": command.timeout,
            "retries": command.retries,
            "wait_between_retries": command.wait_between_retries,
            "max_requests_queued": command.max_requests_queued,
            "delay_per_hit": command.delay_per_hit,
            "is_active": command.is_active,
            "notes": command.notes,
        }

        # Execute bulk creation with base_name
        results, event = await self.domain_service.execute_bulk_creation(
            base_name=command.base_name,
            base_host=command.base_host,
            start_port=command.start_port,
            end_port=command.end_port,
            server_defaults=server_defaults,
        )

        # Build response
        summary = ServerDomainService.calculate_bulk_summary(results)

        return {
            "dry_run": False,
            "base_host": command.base_host,
            "start_port": command.start_port,
            "end_port": command.end_port,
            **summary,
            "items": [
                {
                    "port": r.port,
                    "base_url": r.base_url,
                    "status": r.status,
                    "reason": r.reason,
                    "server": r.server.model_dump() if r.server else None,
                }
                for r in results
            ],
        }

    async def handle_dry_run_bulk(
        self,
        command: DryRunBulkServersCommand,
    ) -> dict[str, Any]:
        """Handle dry-run bulk server creation command."""
        # Validate port range
        ServerDomainService.validate_port_range(
            command.start_port,
            command.end_port,
        )

        # Execute dry-run
        results = await self.domain_service.dry_run_bulk_creation(
            base_name="Server",  # Default name for dry-run
            base_host=command.base_host,
            start_port=command.start_port,
            end_port=command.end_port,
        )

        # Build response
        summary = ServerDomainService.calculate_bulk_summary(results)

        return {
            "dry_run": True,
            "base_host": command.base_host,
            "start_port": command.start_port,
            "end_port": command.end_port,
            **summary,
            "items": [
                {
                    "port": r.port,
                    "base_url": r.base_url,
                    "status": r.status,
                    "reason": r.reason,
                    "server": None,
                }
                for r in results
            ],
        }
