import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from main import app, get_session


@pytest.fixture
def anyio_backend():
    """Jalankan pengujian async hanya dengan asyncio (bukan trio)."""
    return "asyncio"


@pytest.fixture
async def session(anyio_backend):
    """Sesi async ke basis data SQLite di memori yang baru untuk setiap pengujian."""
    engine_uji = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine_uji.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine_uji, expire_on_commit=False) as sesi:
        yield sesi
    await engine_uji.dispose()


@pytest.fixture
async def client(session: AsyncSession):
    async def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as klien:
        yield klien
    app.dependency_overrides.clear()
