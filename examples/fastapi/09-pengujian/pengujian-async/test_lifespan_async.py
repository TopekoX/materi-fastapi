from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import main
from main import app

pytestmark = pytest.mark.anyio


async def test_asyncclient_tidak_menjalankan_lifespan():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/status")
    assert response.json() == {"siap": False}  # lifespan belum berjalan


async def test_dengan_lifespanmanager_lifespan_berjalan(monkeypatch):
    # lifespan membuat tabel di main.engine. Ganti engine itu dengan basis data di memori
    # selama pengujian, supaya berkas database.db tidak terbentuk.
    engine_uji = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(main, "engine", engine_uji)

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/status")
    assert response.json() == {"siap": True}
    assert not Path("database.db").exists()
