import asyncio
from types import SimpleNamespace
from typing import cast

import pytest
from app.core.exceptions import AppNotFoundError, AppValidationError
from app.models.servers import Servers
from app.services.servers.schemas import ServerCreate, ServerUpdate
from app.services.servers.service import ServerService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_server_port_conflict():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get_by(db, **filters):
        _ = db
        _ = filters
        await asyncio.sleep(0)
        return cast(Servers, SimpleNamespace(id=42))

    svc.repo.get_by = fake_get_by

    payload = ServerCreate(port=9900, base_url="http://localhost:9900")  # type: ignore[arg-type]
    with pytest.raises(AppValidationError):
        await svc.create_server(payload)


@pytest.mark.asyncio
async def test_create_server_url_conflict():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get_by(db, **filters):
        _ = db
        _ = filters
        # emulate when checking base_url conflict
        await asyncio.sleep(0)
        if "base_url" in filters:
            return cast(Servers, SimpleNamespace(id=99))
        return None

    svc.repo.get_by = fake_get_by

    payload = ServerCreate(port=9901, base_url="http://localhost:9901")  # type: ignore[arg-type]
    with pytest.raises(AppValidationError):
        await svc.create_server(payload)


@pytest.mark.asyncio
async def test_update_server_not_found():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get(db, id):
        _ = db
        _ = id
        await asyncio.sleep(0)
        return None

    svc.repo.get = fake_get

    with pytest.raises(AppValidationError):
        await svc.update_server(123, ServerUpdate())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_get_servers_returns_list():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get_multi(db, skip=0, limit=100, **filters):
        _ = db
        _ = skip
        _ = limit
        _ = filters
        await asyncio.sleep(0)
        return [
            cast(Servers, SimpleNamespace(id=1)),
            cast(Servers, SimpleNamespace(id=2)),
        ]

    svc.repo.get_multi = fake_get_multi

    res = await svc.get_servers()
    assert isinstance(res, list)
    assert len(res) == 2


@pytest.mark.asyncio
async def test_delete_server_not_found():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get(db, id):
        _ = db
        _ = id
        await asyncio.sleep(0)
        return None

    svc.repo.get = fake_get

    with pytest.raises(AppNotFoundError):
        await svc.delete_server(1)


@pytest.mark.asyncio
async def test_delete_server_success():
    svc = ServerService(session=cast(AsyncSession, None))

    async def fake_get(db, id):
        _ = db
        _ = id
        await asyncio.sleep(0)
        return cast(Servers, SimpleNamespace(id=id))

    async def fake_delete(db, id):
        _ = db
        _ = id
        await asyncio.sleep(0)
        return True

    svc.repo.get = fake_get
    svc.repo.delete = fake_delete

    # should not raise
    await svc.delete_server(5)
