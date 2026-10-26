from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import layanan
import main
from main import app

client = TestClient(app)


# --- Tanpa penggantian: layanan luar sungguhan dipanggil (dan gagal) -------------------
def test_kurs_tanpa_penggantian_gagal():
    response = client.get("/kurs", params={"jumlah": 100})
    assert response.status_code == 503


# --- 1. monkeypatch.setattr: ganti fungsi di modul yang MEMAKAINYA -------------------------
def test_kurs_dengan_fungsi_pengganti(monkeypatch):
    monkeypatch.setattr(main, "ambil_kurs", lambda: 16000.0)
    response = client.get("/kurs", params={"jumlah": 2})
    assert response.status_code == 200
    assert response.json() == {"jumlah": 2.0, "kurs": 16000.0, "hasil": 32000.0}


# --- Jebakan: mengganti di tempat yang salah ---------------------------------------------------
def test_salah_tempat_penggantian_tidak_berefek(monkeypatch):
    # main sudah menyalin nama ambil_kurs lewat 'from layanan import ambil_kurs',
    # jadi mengganti layanan.ambil_kurs TIDAK mengubah yang dipakai main.
    monkeypatch.setattr(layanan, "ambil_kurs", lambda: 16000.0)
    response = client.get("/kurs", params={"jumlah": 2})
    assert response.status_code == 503  # tetap memanggil layanan asli


# --- 2. Mengganti waktu ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "jam, sapaan",
    [(7, "Selamat pagi"), (12, "Selamat siang"), (16, "Selamat sore"), (21, "Selamat malam")],
)
def test_salam_menurut_jam(monkeypatch, jam, sapaan):
    monkeypatch.setattr(main, "waktu_sekarang", lambda: datetime(2026, 1, 1, jam, 0))
    assert client.get("/salam").json() == {"sapaan": sapaan}


# --- 3. Mengganti variabel environment --------------------------------------------------------
def test_mode_bawaan(monkeypatch):
    monkeypatch.delenv("TUGASKU_MODE", raising=False)
    assert client.get("/mode").json() == {"mode": "produksi"}


def test_mode_dari_environment(monkeypatch):
    monkeypatch.setenv("TUGASKU_MODE", "uji")
    assert client.get("/mode").json() == {"mode": "uji"}


def test_perubahan_environment_dibatalkan_otomatis():
    # monkeypatch dari pengujian sebelumnya sudah dibatalkan
    assert client.get("/mode").json() == {"mode": "produksi"}
