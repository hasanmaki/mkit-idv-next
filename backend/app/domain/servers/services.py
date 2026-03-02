"""Server domain service for domain-level business logic."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.servers.entities import Server
from app.domain.servers.events import ServerBulkCreatedEvent
from app.domain.servers.exceptions import ServerDuplicateError


class ServerRepositoryProtocol(Protocol):
    """Protocol for server repository (dependency inversion)."""

    async def get_by(self, session: object, **filters) -> Server | None:
        """Get server by filters."""
        ...

    async def create(self, session: object, **kwargs) -> Server:
        """Create a new server."""
        ...


@dataclass
class BulkCreationResult:
    """Result of bulk server creation."""

    port: int
    base_url: str
    status: str  # "created", "skipped", "failed", "would_create"
    reason: str | None = None
    server: Server | None = None


class ServerDomainService:
    """Domain service for server operations.

    Contains business logic that doesn't naturally fit within a single entity.
    Works with the Server entity but doesn't hold state.
    """

    def __init__(self, repository: ServerRepositoryProtocol | None = None):
        self.repository = repository

    async def validate_server_uniqueness(
        self,
        port: int,
        base_url: str,
        server_id: int | None = None,
    ) -> tuple[Server | None, Server | None]:
        """Validate that port and URL are unique.

        Returns tuple of (existing_by_port, existing_by_url).
        Raises ServerDuplicateError if duplicates found.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        existing_by_port = await self.repository.get_by(port=port)
        existing_by_url = await self.repository.get_by(base_url=base_url)

        # Check port conflict
        if existing_by_port and (not server_id or existing_by_port.id != server_id):
            raise ServerDuplicateError(
                field="port",
                value=port,
                existing_id=existing_by_port.id,
            )

        # Check URL conflict
        if existing_by_url and (not server_id or existing_by_url.id != server_id):
            raise ServerDuplicateError(
                field="base_url",
                value=base_url,
                existing_id=existing_by_url.id,
            )

        return existing_by_port, existing_by_url

    async def dry_run_bulk_creation(
        self,
        base_name: str,
        base_host: str,
        start_port: int,
        end_port: int,
    ) -> list[BulkCreationResult]:
        """Preview bulk server creation without persisting.

        Returns list of results showing what would be created/skipped.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        results: list[BulkCreationResult] = []

        for port in range(start_port, end_port + 1):
            base_url = f"{base_host}:{port}"

            # Check port conflict
            existing_by_port = await self.repository.get_by(port=port)
            if existing_by_port:
                results.append(
                    BulkCreationResult(
                        port=port,
                        base_url=base_url,
                        status="skipped",
                        reason="port already in use",
                    )
                )
                continue

            # Check URL conflict
            existing_by_url = await self.repository.get_by(base_url=base_url)
            if existing_by_url:
                results.append(
                    BulkCreationResult(
                        port=port,
                        base_url=base_url,
                        status="skipped",
                        reason="base_url already in use",
                    )
                )
                continue

            # Would be created
            results.append(
                BulkCreationResult(
                    port=port,
                    base_url=base_url,
                    status="would_create",
                )
            )

        return results

    async def execute_bulk_creation(
        self,
        base_name: str,
        base_host: str,
        start_port: int,
        end_port: int,
        server_defaults: dict,
    ) -> tuple[list[BulkCreationResult], ServerBulkCreatedEvent]:
        """Execute bulk server creation.

        Returns tuple of (results, domain_event).
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        results: list[BulkCreationResult] = []
        created_ids: list[int] = []
        created_count = 0
        skipped_count = 0
        failed_count = 0

        for port in range(start_port, end_port + 1):
            base_url = f"{base_host}:{port}"
            server_name = f"{base_name} {port}"

            try:
                # Check port conflict
                existing_by_port = await self.repository.get_by(port=port)
                if existing_by_port:
                    skipped_count += 1
                    results.append(
                        BulkCreationResult(
                            port=port,
                            base_url=base_url,
                            status="skipped",
                            reason="port already in use",
                        )
                    )
                    continue

                # Check URL conflict
                existing_by_url = await self.repository.get_by(base_url=base_url)
                if existing_by_url:
                    skipped_count += 1
                    results.append(
                        BulkCreationResult(
                            port=port,
                            base_url=base_url,
                            status="skipped",
                            reason="base_url already in use",
                        )
                    )
                    continue

                # Create server
                server = await self.repository.create(
                    name=server_name,
                    port=port,
                    base_url=base_url,
                    **server_defaults,
                )
                created_count += 1
                created_ids.append(server.id)
                results.append(
                    BulkCreationResult(
                        port=port,
                        base_url=base_url,
                        status="created",
                        server=server,
                    )
                )

            except Exception as e:
                failed_count += 1
                results.append(
                    BulkCreationResult(
                        port=port,
                        base_url=base_url,
                        status="failed",
                        reason=str(e),
                    )
                )

        total_requested = (end_port - start_port) + 1

        # Create domain event
        event = ServerBulkCreatedEvent(
            total_requested=total_requested,
            total_created=created_count,
            total_skipped=skipped_count,
            total_failed=failed_count,
            server_ids=created_ids,
            base_host=base_host,
            start_port=start_port,
            end_port=end_port,
        )

        return results, event

    @staticmethod
    def calculate_bulk_summary(
        results: list[BulkCreationResult],
    ) -> dict:
        """Calculate summary statistics from bulk creation results."""
        total_requested = len(results)
        total_created = sum(1 for r in results if r.status == "created")
        total_skipped = sum(1 for r in results if r.status == "skipped")
        total_failed = sum(1 for r in results if r.status == "failed")
        total_would_create = sum(1 for r in results if r.status == "would_create")

        return {
            "total_requested": total_requested,
            "total_created": total_created,
            "total_skipped": total_skipped,
            "total_failed": total_failed,
            "total_would_create": total_would_create,
        }

    @staticmethod
    def validate_port_range(
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
