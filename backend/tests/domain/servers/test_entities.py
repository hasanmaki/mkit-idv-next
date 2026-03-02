"""Unit tests for Server domain entity."""

import pytest
from app.domain.servers.entities import Server
from app.domain.servers.events import (
    ServerCreatedEvent,
    ServerDeletedEvent,
    ServerStatusToggledEvent,
    ServerUpdatedEvent,
)
from app.domain.servers.exceptions import ServerDuplicateError
from app.domain.servers.value_objects import ServerConfig, ServerUrl


class TestServerEntity:
    """Test Server domain entity."""

    def test_create_server_with_factory_method(self):
        """Test server creation using factory method."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            description="Test Server",
            timeout=15,
            retries=5,
        )

        assert server.port == 9900
        assert server.base_url == "http://localhost:9900"
        assert server.description == "Test Server"
        assert server.timeout == 15
        assert server.retries == 5
        assert server.is_active is True

    def test_create_server_records_domain_event(self):
        """Test that creating server records ServerCreatedEvent."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        events = server.pop_events()
        assert len(events) == 1
        assert isinstance(events[0], ServerCreatedEvent)
        assert events[0].port == 9900
        assert events[0].base_url == "http://localhost:9900"

    def test_update_server(self):
        """Test server update."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            timeout=10,
        )

        updated_fields = server.update(
            timeout=20,
            retries=5,
            description="Updated Server",
        )

        assert server.timeout == 20
        assert server.retries == 5
        assert server.description == "Updated Server"
        assert "timeout" in updated_fields
        assert "retries" in updated_fields
        assert "description" in updated_fields

    def test_update_server_records_event(self):
        """Test that update records ServerUpdatedEvent."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        # Pop the initial ServerCreatedEvent
        server.pop_events()

        server.update(timeout=20)
        events = server.pop_events()

        assert len(events) == 1
        assert isinstance(events[0], ServerUpdatedEvent)
        assert "timeout" in events[0].updated_fields

    def test_toggle_status_activates_server(self):
        """Test toggling server status to active."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            is_active=False,
        )

        server.activate()

        assert server.is_active is True

    def test_toggle_status_deactivates_server(self):
        """Test toggling server status to inactive."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            is_active=True,
        )

        server.deactivate()

        assert server.is_active is False

    def test_toggle_status_records_event(self):
        """Test that toggling status records ServerStatusToggledEvent."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            is_active=True,
        )

        # Pop the initial ServerCreatedEvent
        server.pop_events()

        server.deactivate()
        events = server.pop_events()

        assert len(events) == 1
        assert isinstance(events[0], ServerStatusToggledEvent)
        assert events[0].is_active is False
        assert events[0].previous_status is True

    def test_toggle_status_no_change_if_same_status(self):
        """Test that toggling to same status doesn't record event."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            is_active=True,
        )

        # Pop the initial ServerCreatedEvent
        server.pop_events()

        server.activate()  # Already active
        events = server.pop_events()

        # Should have no new events
        assert len(events) == 0

    def test_delete_server_records_event(self):
        """Test that delete records ServerDeletedEvent."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        # Pop the initial ServerCreatedEvent
        server.pop_events()

        server.delete()
        events = server.pop_events()

        assert len(events) == 1
        assert isinstance(events[0], ServerDeletedEvent)
        assert events[0].server_id == 0  # ID not set yet
        assert events[0].base_url == "http://localhost:9900"

    def test_get_config_returns_value_object(self):
        """Test getting server config as value object."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
            timeout=15,
            retries=5,
            wait_between_retries=2,
            max_requests_queued=10,
        )

        config = server.get_config()

        assert isinstance(config, ServerConfig)
        assert config.timeout == 15
        assert config.retries == 5
        assert config.wait_between_retries == 2
        assert config.max_requests_queued == 10

    def test_get_url_returns_value_object(self):
        """Test getting server URL as value object."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        url = server.get_url()

        assert isinstance(url, ServerUrl)
        assert url.value == "http://localhost:9900"
        assert url.port == 9900
        assert url.host == "http://localhost"

    def test_validate_uniqueness_raises_on_duplicate_port(self):
        """Test that validation raises on duplicate port."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        existing_by_port = Server.create(
            port=9900,
            base_url="http://localhost:9901",
        )
        existing_by_port.id = 1

        with pytest.raises(ServerDuplicateError) as exc_info:
            server.validate_uniqueness(existing_by_port, None)

        assert exc_info.value.error_code == "server_duplicate"
        assert "9900" in str(exc_info.value)

    def test_validate_uniqueness_raises_on_duplicate_url(self):
        """Test that validation raises on duplicate URL."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        existing_by_url = Server.create(
            port=9901,
            base_url="http://localhost:9900",
        )
        existing_by_url.id = 1

        with pytest.raises(ServerDuplicateError) as exc_info:
            server.validate_uniqueness(None, existing_by_url)

        assert exc_info.value.error_code == "server_duplicate"
        assert "localhost:9900" in str(exc_info.value)

    def test_validate_uniqueness_passes_for_same_server(self):
        """Test that validation passes for the same server (update scenario)."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )
        server.id = 1

        # Should not raise - it's the same server
        server.validate_uniqueness(server, server)

    def test_is_same_url_case_insensitive(self):
        """Test URL comparison is case-insensitive."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        assert server.is_same_url("http://localhost:9900")
        assert server.is_same_url("HTTP://LOCALHOST:9900")
        assert not server.is_same_url("http://localhost:9901")

    def test_is_same_port(self):
        """Test port comparison."""
        server = Server.create(
            port=9900,
            base_url="http://localhost:9900",
        )

        assert server.is_same_port(9900)
        assert not server.is_same_port(9901)

    def test_entity_equality(self):
        """Test entity equality based on ID."""
        server1 = Server.create(port=9900, base_url="http://localhost:9900")
        server1.id = 1

        server2 = Server.create(port=9901, base_url="http://localhost:9901")
        server2.id = 1

        server3 = Server.create(port=9902, base_url="http://localhost:9902")
        server3.id = 2

        assert server1 == server2  # Same ID
        assert server1 != server3  # Different ID
        assert server1 != "not a server"  # Different type

    def test_entity_hash(self):
        """Test entity hash based on type and ID."""
        server1 = Server.create(port=9900, base_url="http://localhost:9900")
        server1.id = 1

        server2 = Server.create(port=9901, base_url="http://localhost:9901")
        server2.id = 1

        assert hash(server1) == hash(server2)
