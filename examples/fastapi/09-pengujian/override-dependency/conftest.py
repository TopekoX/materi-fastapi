import pytest
from fastapi.testclient import TestClient

from main import app, tugas_db


@pytest.fixture(autouse=True)
def bersihkan():
    """Sebelum dan sesudah setiap pengujian: kosongkan data dan lepas semua override."""
    tugas_db.clear()
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    tugas_db.clear()


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as klien:
        yield klien
