from datetime import datetime
from types import SimpleNamespace

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


class FakeService:
    def __init__(self, session):
        pass

    async def create_server(self, data):
        return SimpleNamespace(
            id=1,
            port=data.port,
            base_url=data.base_url,
            description=data.description,
            timeout=data.timeout,
            retries=data.retries,
            wait_between_retries=data.wait_between_retries,
            max_requests_queued=data.max_requests_queued,
            is_active=data.is_active,
            notes=data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def get_servers(self, skip=0, limit=100, is_active=None):
        _ = skip
        _ = limit
        _ = is_active
        return [
            await self.create_server(
                SimpleNamespace(
                    **{
                        "port": 9900,
                        "base_url": "http://localhost:9900",
                        "description": None,
                        "timeout": 10,
                        "retries": 3,
                        "wait_between_retries": 1,
                        "max_requests_queued": 5,
                        "is_active": True,
                        "notes": None,
                    }
                )
            )
        ]

    async def get_server(self, server_id: int):
        _ = server_id
        return await self.create_server(
            SimpleNamespace(
                **{
                    "port": 9900,
                    "base_url": "http://localhost:9900",
                    "description": None,
                    "timeout": 10,
                    "retries": 3,
                    "wait_between_retries": 1,
                    "max_requests_queued": 5,
                    "is_active": True,
                    "notes": None,
                }
            )
        )

    async def update_server(self, server_id: int, data):
        _ = data
        return await self.get_server(server_id)

    async def toggle_server_status(self, server_id: int, is_active: bool):
        s = await self.get_server(server_id)
        s.is_active = is_active
        return s

    async def delete_server(self, server_id: int):
        _ = server_id
        return True


@pytest.mark.asyncio
async def test_create_server_route(monkeypatch):
    monkeypatch.setattr("app.api.route_servers.ServerService", FakeService)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:  # type: ignore[arg-type]
        payload = {"port": 9900, "base_url": "http://localhost:9900"}
        r = await ac.post("/v1/servers/", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["port"] == 9900


@pytest.mark.asyncio
async def test_list_get_update_delete_routes(monkeypatch):
    monkeypatch.setattr("app.api.route_servers.ServerService", FakeService)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:  # type: ignore[arg-type]
        r = await ac.get("/v1/servers/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        r = await ac.get("/v1/servers/1")
        assert r.status_code == 200

        r = await ac.patch("/v1/servers/1", json={"description": "updated"})
        assert r.status_code == 200

        r = await ac.patch("/v1/servers/1/status", json={"is_active": False})
        assert r.status_code == 200

        r = await ac.delete("/v1/servers/1")
        assert r.status_code == 204
