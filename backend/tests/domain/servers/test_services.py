"""Unit tests for Server domain service."""


import pytest
from app.domain.servers.exceptions import ServerDuplicateError
from app.domain.servers.services import BulkCreationResult, ServerDomainService


class MockRepository:
    """Mock repository for testing."""

    def __init__(self):
        self.servers = {}

    async def get_by(self, session=None, **filters):
        """Mock get_by method."""
        if "port" in filters:
            return self.servers.get(("port", filters["port"]))
        if "base_url" in filters:
            return self.servers.get(("base_url", filters["base_url"]))
        return None

    async def create(self, session=None, **kwargs):
        """Mock create method."""
        from app.domain.servers.entities import Server
        server = Server.create(**kwargs)
        server.id = len(self.servers) + 1
        self.servers[("port", kwargs["port"])] = server
        self.servers[("base_url", kwargs["base_url"])] = server
        return server


class TestServerDomainService:
    """Test ServerDomainService."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MockRepository()

    @pytest.fixture
    def domain_service(self, mock_repo):
        """Create domain service with mock repository."""
        return ServerDomainService(mock_repo)

    @pytest.mark.asyncio
    async def test_validate_uniqueness_passes(self, domain_service):
        """Test validation passes when no duplicates."""
        existing_by_port, existing_by_url = await domain_service.validate_server_uniqueness(
            port=9900,
            base_url="http://localhost:9900",
        )

        assert existing_by_port is None
        assert existing_by_url is None

    @pytest.mark.asyncio
    async def test_validate_uniqueness_fails_on_duplicate_port(
        self, domain_service, mock_repo
    ):
        """Test validation fails on duplicate port."""
        # Create existing server
        await mock_repo.create(port=9900, base_url="http://localhost:9900")

        with pytest.raises(ServerDuplicateError) as exc_info:
            await domain_service.validate_server_uniqueness(
                port=9900,
                base_url="http://localhost:9901",
            )

        assert exc_info.value.error_code == "server_duplicate"
        assert "9900" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_uniqueness_fails_on_duplicate_url(
        self, domain_service, mock_repo
    ):
        """Test validation fails on duplicate URL."""
        # Create existing server
        await mock_repo.create(port=9900, base_url="http://localhost:9900")

        with pytest.raises(ServerDuplicateError) as exc_info:
            await domain_service.validate_server_uniqueness(
                port=9901,
                base_url="http://localhost:9900",
            )

        assert exc_info.value.error_code == "server_duplicate"
        assert "localhost:9900" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_uniqueness_allows_update_same_server(
        self, domain_service, mock_repo
    ):
        """Test validation allows update of same server."""
        # Create existing server
        server = await mock_repo.create(port=9900, base_url="http://localhost:9900")

        # Should not raise for same server ID
        existing_by_port, existing_by_url = await domain_service.validate_server_uniqueness(
            port=9900,
            base_url="http://localhost:9900",
            server_id=server.id,
        )

        # Returns the same server (not a conflict)
        assert existing_by_port is not None
        assert existing_by_url is not None

    @pytest.mark.asyncio
    async def test_dry_run_bulk_creation_all_new(self, domain_service):
        """Test dry-run with all new servers."""
        results = await domain_service.dry_run_bulk_creation(
            base_host="http://localhost",
            start_port=9900,
            end_port=9902,
        )

        assert len(results) == 3
        assert all(r.status == "would_create" for r in results)
        assert results[0].port == 9900
        assert results[1].port == 9901
        assert results[2].port == 9902

    @pytest.mark.asyncio
    async def test_dry_run_bulk_creation_with_conflicts(
        self, domain_service, mock_repo
    ):
        """Test dry-run with some existing servers."""
        # Create existing server
        await mock_repo.create(port=9900, base_url="http://localhost:9900")

        results = await domain_service.dry_run_bulk_creation(
            base_host="http://localhost",
            start_port=9900,
            end_port=9902,
        )

        assert len(results) == 3
        assert results[0].status == "skipped"  # Port 9900 exists
        assert results[1].status == "would_create"
        assert results[2].status == "would_create"

    @pytest.mark.asyncio
    async def test_execute_bulk_creation_success(self, domain_service):
        """Test executing bulk creation."""
        results, event = await domain_service.execute_bulk_creation(
            base_host="http://localhost",
            start_port=9900,
            end_port=9902,
            server_defaults={
                "timeout": 10,
                "retries": 3,
                "is_active": True,
            },
        )

        assert len(results) == 3
        assert all(r.status == "created" for r in results)
        assert event.total_created == 3
        assert event.total_skipped == 0
        assert event.total_failed == 0
        assert len(event.server_ids) == 3

    @pytest.mark.asyncio
    async def test_execute_bulk_creation_partial_skip(
        self, domain_service, mock_repo
    ):
        """Test bulk creation with partial skips."""
        # Create existing server
        await mock_repo.create(port=9900, base_url="http://localhost:9900")

        results, event = await domain_service.execute_bulk_creation(
            base_host="http://localhost",
            start_port=9900,
            end_port=9902,
            server_defaults={},
        )

        assert len(results) == 3
        assert results[0].status == "skipped"
        assert results[1].status == "created"
        assert results[2].status == "created"
        assert event.total_created == 2
        assert event.total_skipped == 1

    def test_calculate_bulk_summary(self, domain_service):
        """Test calculating bulk summary."""
        results = [
            BulkCreationResult(port=9900, base_url="http://localhost:9900", status="created"),
            BulkCreationResult(port=9901, base_url="http://localhost:9901", status="created"),
            BulkCreationResult(port=9902, base_url="http://localhost:9902", status="skipped"),
            BulkCreationResult(port=9903, base_url="http://localhost:9903", status="failed"),
        ]

        summary = domain_service.calculate_bulk_summary(results)

        assert summary["total_requested"] == 4
        assert summary["total_created"] == 2
        assert summary["total_skipped"] == 1
        assert summary["total_failed"] == 1
        assert summary["total_would_create"] == 0

    def test_validate_port_range_valid(self, domain_service):
        """Test port range validation with valid range."""
        # Should not raise
        domain_service.validate_port_range(9900, 9909)
        domain_service.validate_port_range(1, 500)  # Within max range

    def test_validate_port_range_invalid_start(self, domain_service):
        """Test port range validation with invalid start."""
        with pytest.raises(ValueError, match="start_port must be between"):
            domain_service.validate_port_range(0, 9909)

        with pytest.raises(ValueError, match="start_port must be between"):
            domain_service.validate_port_range(65536, 65536)

    def test_validate_port_range_invalid_end(self, domain_service):
        """Test port range validation with invalid end."""
        with pytest.raises(ValueError, match="end_port must be between"):
            domain_service.validate_port_range(9900, 0)

        with pytest.raises(ValueError, match="end_port must be between"):
            domain_service.validate_port_range(9900, 65536)

    def test_validate_port_range_end_less_than_start(self, domain_service):
        """Test port range validation with end < start."""
        with pytest.raises(ValueError, match="end_port must be greater"):
            domain_service.validate_port_range(9910, 9900)

    def test_validate_port_range_exceeds_max(self, domain_service):
        """Test port range validation with range too large."""
        with pytest.raises(ValueError, match="Port range cannot exceed"):
            domain_service.validate_port_range(9900, 10401, max_range=501)
