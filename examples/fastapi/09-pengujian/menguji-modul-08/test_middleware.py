import pytest
from fastapi.testclient import TestClient

import main_mw


@pytest.fixture(autouse=True)
def keadaan_awal():
    main_mw.jejak.clear()
    main_mw.status_pemeliharaan["aktif"] = False
    yield
    main_mw.jejak.clear()
    main_mw.status_pemeliharaan["aktif"] = False


@pytest.fixture
def client():
    return TestClient(main_mw.app, raise_server_exceptions=False)


def test_header_ditambahkan_middleware(client):
    response = client.get("/halo")
    assert response.status_code == 200
    assert response.headers["x-waktu-proses"].endswith(" ms")
    assert len(response.headers["x-request-id"]) == 8


def test_request_id_berbeda_setiap_request(client):
    id_1 = client.get("/halo").headers["x-request-id"]
    id_2 = client.get("/halo").headers["x-request-id"]
    assert id_1 != id_2


def test_endpoint_membaca_request_state(client):
    response = client.get("/id")
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_urutan_middleware(client):
    client.get("/halo")
    assert main_mw.jejak == [
        "pemeliharaan: masuk",
        "id: masuk",
        "waktu: masuk",
        "endpoint",
        "waktu: keluar",
        "id: keluar",
        "pemeliharaan: keluar",
    ]


def test_mode_pemeliharaan_menjawab_503_tanpa_menjalankan_endpoint(client):
    client.post("/pemeliharaan/on")
    response = client.get("/halo")
    assert response.status_code == 503
    assert "x-request-id" not in response.headers  # middleware dalam tidak sempat berjalan
    assert "endpoint" not in main_mw.jejak


def test_mode_pemeliharaan_bisa_dimatikan_lagi(client):
    client.post("/pemeliharaan/on")
    assert client.post("/pemeliharaan/off").json() == {"aktif": False}
    assert client.get("/halo").status_code == 200


def test_header_tetap_ada_pada_httpexception_tetapi_tidak_pada_500(client):
    assert "x-request-id" in client.get("/gagal-http").headers
    rusak = client.get("/rusak")
    assert rusak.status_code == 500
    assert "x-request-id" not in rusak.headers
