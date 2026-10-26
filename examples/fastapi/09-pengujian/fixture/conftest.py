import pytest
from fastapi.testclient import TestClient

from main import TOKEN_RAHASIA, app, tugas_db


@pytest.fixture(autouse=True)
def data_bersih():
    """Dijalankan otomatis untuk setiap pengujian: data kosong sebelum dan sesudah."""
    tugas_db.clear()
    yield
    tugas_db.clear()


@pytest.fixture
def client():
    """Klien pengujian. Memakai 'with' agar lifespan aplikasi (bila ada) ikut berjalan."""
    with TestClient(app) as klien:
        yield klien


@pytest.fixture
def header_token():
    return {"X-Token": TOKEN_RAHASIA}


@pytest.fixture
def tugas_contoh(client):
    """Fixture yang memakai fixture lain: membuat satu tugas dan mengembalikannya."""
    response = client.post("/tugas", json={"judul": "Tugas contoh"})
    return response.json()


@pytest.fixture(params=["Belajar", "Menulis kode", "Membaca dokumentasi"])
def judul_valid(request):
    """Fixture berparameter: pengujian yang memakainya dijalankan sekali per nilai."""
    return request.param
