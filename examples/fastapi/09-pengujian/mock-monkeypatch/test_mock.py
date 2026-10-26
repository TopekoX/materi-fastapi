from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_mock_mengembalikan_nilai_dan_merekam_pemanggilan():
    pengganti = Mock(return_value=15000.0)
    with patch.object(main, "ambil_kurs", pengganti):
        response = client.get("/kurs", params={"jumlah": 10})
    assert response.json()["hasil"] == 150000.0
    pengganti.assert_called_once_with()  # dipanggil tepat sekali, tanpa argumen


def test_mock_mensimulasikan_kegagalan():
    pengganti = Mock(side_effect=httpx.ConnectError("tidak bisa terhubung"))
    with patch.object(main, "ambil_kurs", pengganti):
        response = client.get("/kurs", params={"jumlah": 10})
    assert response.status_code == 503
    assert response.json() == {"detail": "Layanan kurs tidak tersedia"}


def test_mock_tidak_dipanggil_bila_validasi_gagal():
    pengganti = Mock(return_value=15000.0)
    with patch.object(main, "ambil_kurs", pengganti):
        response = client.get("/kurs", params={"jumlah": "bukan-angka"})
    assert response.status_code == 422
    pengganti.assert_not_called()  # validasi menolak request sebelum fungsi endpoint berjalan


def test_patch_dibatalkan_setelah_blok_with():
    with patch.object(main, "ambil_kurs", Mock(return_value=1.0)):
        pass
    assert client.get("/kurs", params={"jumlah": 1}).status_code == 503  # kembali ke yang asli
