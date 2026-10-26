import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    """Basis data SQLite DI MEMORI yang baru untuk setiap pengujian."""
    engine_uji = create_engine(
        "sqlite://",  # tanpa nama berkas = di memori
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # semua koneksi memakai satu basis data di memori yang sama
    )
    SQLModel.metadata.create_all(engine_uji)
    with Session(engine_uji) as session:
        yield session
    # Saat engine dilepas, basis data di memori ikut hilang: tidak ada yang perlu dibersihkan


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji  # ganti basis data produksi
    with TestClient(app) as klien:
        yield klien
    app.dependency_overrides.clear()
