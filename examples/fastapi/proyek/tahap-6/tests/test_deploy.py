import importlib
import io
import logging

import pytest
from pydantic import ValidationError

from app import main
from app.config import KUNCI_CONTOH, Settings
from app.pengaturan_log import atur_logging

KUNCI = "k" * 40


# --- Endpoint operasional -----------------------------------------------------------------
def test_kesehatan_tanpa_login(client):
    respons = client.get("/kesehatan")
    assert respons.status_code == 200
    assert respons.json() == {"status": "ok"}


def test_siap_menyentuh_basis_data(client):
    respons = client.get("/siap")
    assert respons.status_code == 200
    assert respons.json() == {"status": "siap"}


def test_siap_gagal_503_bila_basis_data_bermasalah(client):
    from app.database import get_session

    class SesiRusak:
        def exec(self, *_):
            raise RuntimeError("basis data mati")

    main.app.dependency_overrides[get_session] = lambda: SesiRusak()
    respons = client.get("/siap")
    assert respons.status_code == 503
    assert client.get("/kesehatan").status_code == 200  # proses tetap hidup


# --- Konfigurasi produksi -------------------------------------------------------------------
def test_produksi_dengan_konfigurasi_aman_diterima():
    s = Settings(secret_key=KUNCI, lingkungan="produksi", origin_diizinkan=["https://tugasku.contoh"])
    assert s.lingkungan == "produksi"


@pytest.mark.parametrize(
    "argumen, pesan",
    [
        ({"origin_diizinkan": ["*"]}, "tidak boleh berisi '*'"),
        ({"secret_key": KUNCI_CONTOH + "-" + "x" * 20}, "masih kunci contoh"),
    ],
)
def test_produksi_menolak_konfigurasi_berbahaya(argumen, pesan):
    dasar = {"secret_key": KUNCI, "lingkungan": "produksi"}
    with pytest.raises(ValidationError) as galat:
        Settings(**{**dasar, **argumen})
    assert pesan in str(galat.value)


def test_pengembangan_boleh_longgar():
    Settings(secret_key=KUNCI_CONTOH + "-" + "x" * 20, origin_diizinkan=["*"])  # tanpa galat


def test_level_log_yang_tidak_dikenal_ditolak():
    with pytest.raises(ValidationError):
        Settings(secret_key=KUNCI, log_level="CERewET")


# --- Dokumentasi dibuka/ditutup menurut lingkungan -----------------------------------------
def test_docs_terbuka_di_pengembangan(client):
    assert client.get("/docs").status_code == 200


def test_docs_ditutup_di_produksi(monkeypatch):
    from fastapi.testclient import TestClient

    from app import config

    monkeypatch.setenv("TUGASKU_LINGKUNGAN", "produksi")
    config.get_settings.cache_clear()
    try:
        modul = importlib.reload(main)
        with TestClient(modul.app) as klien:
            assert klien.get("/docs").status_code == 404
            assert klien.get("/openapi.json").status_code == 404
            assert klien.get("/kesehatan").status_code == 200
    finally:
        monkeypatch.delenv("TUGASKU_LINGKUNGAN")
        config.get_settings.cache_clear()
        importlib.reload(main)


# --- Logging -----------------------------------------------------------------------------------
@pytest.fixture
def keluaran_log():
    atur_logging(level="INFO", format_log="teks")
    wadah = io.StringIO()
    logging.getLogger("tugasku").handlers[0].setStream(wadah)
    return wadah


def test_request_dicatat_dengan_request_id(client, keluaran_log):
    respons = client.get("/kesehatan", headers={"X-Request-ID": "abc123"})
    assert respons.headers["x-request-id"] == "abc123"
    teks = keluaran_log.getvalue()
    assert "[abc123]" in teks
    assert "GET /kesehatan -> 200" in teks


def test_request_id_dibuat_bila_tidak_ada(client):
    a = client.get("/kesehatan").headers["x-request-id"]
    b = client.get("/kesehatan").headers["x-request-id"]
    assert len(a) == 8 and a != b


def test_kata_sandi_tidak_muncul_di_log_masuk(client, keluaran_log):
    respons = client.post("/token", data={"username": "tidak-ada", "password": "RAHASIA-123"})
    assert respons.status_code == 401  # jalur memang ada dan ditolak
    teks = keluaran_log.getvalue()
    assert "POST /token -> 401" in teks
    assert "RAHASIA-123" not in teks
