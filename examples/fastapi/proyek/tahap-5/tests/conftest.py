import os

# Konfigurasi aplikasi dibaca saat modul app diimpor, jadi kunci uji harus diisi LEBIH DULU.
# Kunci ini hanya untuk pengujian. Jangan dipakai di tempat lain.
os.environ.setdefault("TUGASKU_SECRET_KEY", "kunci-khusus-pengujian-yang-cukup-panjang-123456")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from helpers import buat_pengguna, header_untuk


@pytest.fixture(name="session")
def session_fixture():
    """Basis data SQLite di memori yang baru untuk setiap pengujian."""
    engine_uji = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine_uji)
    with Session(engine_uji) as session:
        yield session
    engine_uji.dispose()  # tutup koneksi memori agar tidak ada peringatan 'unclosed database'


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    with TestClient(app, raise_server_exceptions=False) as klien:
        yield klien
    app.dependency_overrides.clear()


@pytest.fixture
def header_budi(client, session):
    buat_pengguna(session, "budi")
    return header_untuk(client, "budi")


@pytest.fixture
def header_sari(client, session):
    buat_pengguna(session, "sari")
    return header_untuk(client, "sari")


@pytest.fixture
def header_pengelola(client, session):
    buat_pengguna(session, "rina", peran="pengelola")
    return header_untuk(client, "rina")


@pytest.fixture
def kategori_kuliah(client, header_pengelola):
    response = client.post("/kategori", json={"nama": "Kuliah"}, headers=header_pengelola)
    assert response.status_code == 201
    return response.json()
