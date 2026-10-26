import time
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import main_bg

DATA = {"judul": "Belajar background task", "email": "budi@contoh.id"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Arahkan berkas log ke folder sementara dan hilangkan jeda 2 detik pada pengiriman email
    monkeypatch.setattr(main_bg, "BERKAS_LOG", tmp_path / "notifikasi.log")
    monkeypatch.setattr(main_bg.time, "sleep", lambda detik: None)
    return TestClient(main_bg.app, raise_server_exceptions=False)


def test_tugas_dibuat_dan_tugas_latar_belakang_berjalan(client):
    response = client.post("/tugas", json=DATA)
    assert response.status_code == 201
    log = client.get("/log").json()
    # Dua tugas latar belakang: dari dependency dan dari endpoint
    assert len(log) == 2
    assert "akses: POST /tugas dicatat oleh dependency" in log[0]
    assert "email terkirim ke budi@contoh.id" in log[1]


def test_kirim_notifikasi_dijadwalkan_dengan_argumen_benar(client, monkeypatch):
    pengganti = Mock()
    monkeypatch.setattr(main_bg, "kirim_notifikasi", pengganti)
    client.post("/tugas", json=DATA)
    pengganti.assert_called_once_with("budi@contoh.id", "Belajar background task")


def test_validasi_gagal_tidak_menjadwalkan_tugas(client):
    response = client.post("/tugas", json={"judul": "ab", "email": "budi@contoh.id"})
    assert response.status_code == 422
    assert client.get("/log").json() == []


def test_tugas_gagal_tidak_mengubah_status_response(client):
    response = client.post("/tugas-gagal", json=DATA)
    assert response.status_code == 201  # response sudah dikirim sebelum tugas gagal


def test_testclient_menunggu_tugas_latar_belakang_selesai(tmp_path, monkeypatch):
    # TANPA mengganti time.sleep: kirim_notifikasi sungguhan butuh 2 detik
    monkeypatch.setattr(main_bg, "BERKAS_LOG", tmp_path / "notifikasi.log")
    client = TestClient(main_bg.app)
    mulai = time.perf_counter()
    response = client.post("/tugas", json=DATA)
    lama = time.perf_counter() - mulai
    assert response.status_code == 201
    assert lama >= 2.0  # TestClient baru kembali sesudah tugas latar belakang selesai
