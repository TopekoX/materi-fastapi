"""Contoh yang SALAH: SQLite di memori TANPA StaticPool.

Untuk mencobanya, ganti isi conftest.py dengan berkas ini.
Setiap koneksi baru ke 'sqlite://' mendapat basis data memori yang KOSONG dan terpisah.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine_uji = create_engine("sqlite://", connect_args={"check_same_thread": False})  # tanpa StaticPool
    SQLModel.metadata.create_all(engine_uji)
    with Session(engine_uji) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    with TestClient(app) as klien:
        yield klien
    app.dependency_overrides.clear()
