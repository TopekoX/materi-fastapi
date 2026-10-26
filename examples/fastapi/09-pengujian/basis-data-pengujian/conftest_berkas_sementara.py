"""Alternatif: basis data uji berupa BERKAS SEMENTARA, bukan di memori.

Untuk mencobanya, ganti isi conftest.py dengan berkas ini.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture(tmp_path):
    # tmp_path: folder sementara unik per pengujian (dibahas di halaman Fixture)
    engine_uji = create_engine(
        f"sqlite:///{tmp_path / 'uji.db'}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine_uji)
    with Session(engine_uji) as session:
        yield session
    engine_uji.dispose()  # tutup koneksi agar berkas bisa dihapus (penting di Windows)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    with TestClient(app) as klien:
        yield klien
    app.dependency_overrides.clear()
