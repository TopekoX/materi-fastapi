import io
import json
import logging

import pytest
from fastapi.testclient import TestClient

import main
from pengaturan_log import atur_logging


@pytest.fixture(autouse=True)
def keluaran():
    """Pasang ulang logging dan arahkan keluarannya ke StringIO agar isinya bisa diperiksa."""
    atur_logging(level="INFO", format_log="teks")
    return arahkan()


def arahkan() -> io.StringIO:
    wadah = io.StringIO()
    logging.getLogger("tugasku").handlers[0].setStream(wadah)
    return wadah


@pytest.fixture
def klien():
    with TestClient(main.app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def tangkap(caplog):
    """Logger 'tugasku' tidak meneruskan (propagate=False), jadi caplog dipasang langsung."""
    logger = logging.getLogger("tugasku")
    logger.addHandler(caplog.handler)
    caplog.set_level(logging.DEBUG, logger="tugasku")
    yield caplog
    logger.removeHandler(caplog.handler)


def test_request_dicatat_dengan_status_dan_durasi(klien, tangkap):
    klien.get("/kerja")
    pesan = [r.getMessage() for r in tangkap.records]
    assert any(p.startswith("GET /kerja -> 200 (") and p.endswith(" ms)") for p in pesan)


def test_request_id_dari_header_dipakai_dan_dikembalikan(klien, tangkap):
    respons = klien.get("/kerja", headers={"X-Request-ID": "abc123"})
    assert respons.headers["x-request-id"] == "abc123"
    assert {r.request_id for r in tangkap.records} == {"abc123"}


def test_request_id_dibuat_bila_tidak_ada(klien):
    r1 = klien.get("/kerja").headers["x-request-id"]
    r2 = klien.get("/kerja").headers["x-request-id"]
    assert len(r1) == 8 and r1 != r2


def test_level_warning_tercatat(klien, tangkap):
    klien.get("/kerja")
    assert any(r.levelno == logging.WARNING for r in tangkap.records)


def test_kata_sandi_disamarkan_di_keluaran(klien, keluaran):
    klien.post("/masuk", params={"nama_pengguna": "budi", "kata_sandi": "RAHASIA-123"})
    teks = keluaran.getvalue()
    assert "RAHASIA-123" not in teks
    assert "kata_sandi=***" in teks
    assert "nama_pengguna=budi" in teks


def test_exception_mencatat_jejak_stack(klien, keluaran):
    respons = klien.get("/gagal-tertangani")
    assert respons.status_code == 400
    assert "ZeroDivisionError" in keluaran.getvalue()


def test_galat_tak_terduga_dicatat_dan_menjadi_500(klien, keluaran):
    respons = klien.get("/gagal-tak-terduga")
    assert respons.status_code == 500
    teks = keluaran.getvalue()
    assert "request gagal: GET /gagal-tak-terduga" in teks
    assert "ZeroDivisionError" in teks


def test_format_json_satu_baris_valid(klien):
    atur_logging(level="INFO", format_log="json")
    keluaran = arahkan()
    try:
        klien.get("/kerja", headers={"X-Request-ID": "xyz"})
        baris = [b for b in keluaran.getvalue().splitlines() if b.strip()]
        data = [json.loads(b) for b in baris]  # setiap baris harus JSON valid
        assert {"waktu", "level", "logger", "request_id", "pesan"} <= set(data[0])
        assert all(d["request_id"] == "xyz" for d in data)
    finally:
        atur_logging(level="INFO", format_log="teks")


def test_level_warning_menyembunyikan_info(klien):
    atur_logging(level="WARNING", format_log="teks")
    keluaran = arahkan()
    try:
        klien.get("/kerja")
        teks = keluaran.getvalue()
        assert "sumber daya hampir penuh" in teks
        assert "pekerjaan sedang berjalan" not in teks
    finally:
        atur_logging(level="INFO", format_log="teks")
