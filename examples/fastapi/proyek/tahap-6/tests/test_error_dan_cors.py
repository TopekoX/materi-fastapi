from app.database import get_session
from app.main import app


def test_path_tidak_dikenal_berformat_seragam(client):
    response = client.get("/tidak-ada")
    assert response.status_code == 404
    assert response.json()["galat"]["kode"] == "HTTP_404"


def test_method_salah(client):
    response = client.put("/kategori")
    assert response.status_code == 405
    assert response.json()["galat"]["kode"] == "HTTP_405"


def test_galat_server_tidak_membocorkan_rincian(client, header_budi):
    def sesi_rusak():
        raise RuntimeError("rincian internal yang rahasia")
        yield

    app.dependency_overrides[get_session] = sesi_rusak
    response = client.get("/tugas", headers=header_budi)
    assert response.status_code == 500
    isi = response.json()
    assert isi["galat"]["kode"] == "GALAT_SERVER"
    assert "rahasia" not in response.text


def test_preflight_cors_untuk_origin_yang_diizinkan(client):
    response = client.options(
        "/tugas",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_preflight_cors_untuk_origin_lain_ditolak(client):
    response = client.options(
        "/tugas",
        headers={"Origin": "http://jahat.example.com", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
