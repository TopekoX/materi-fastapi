"""Contoh yang SALAH: override tidak dilepas, sehingga bocor ke pengujian lain.

Dijalankan terpisah dengan conftest.py yang tidak membersihkan override
(lihat catatan di halaman). Berkas ini sengaja tidak memakai fixture 'bersihkan'.
"""

from fastapi.testclient import TestClient

from main import Settings, app, get_settings

client = TestClient(app)


def test_ubah_konfigurasi_tanpa_melepas():
    app.dependency_overrides[get_settings] = lambda: Settings(nama_aplikasi="PALSU", batas_tugas=1)
    assert client.get("/info").json()["nama_aplikasi"] == "PALSU"
    # lupa: app.dependency_overrides.clear()


def test_mengira_konfigurasi_asli():
    assert client.get("/info").json()["nama_aplikasi"] == "TugasKu"
