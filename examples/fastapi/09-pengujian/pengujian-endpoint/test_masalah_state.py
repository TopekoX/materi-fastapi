"""Contoh pengujian yang SALAH: hasilnya bergantung pada pengujian lain.

Jalankan terpisah (pytest test_masalah_state.py) untuk melihat masalahnya.
"""

from fastapi.testclient import TestClient

from main import app, tugas_db

client = TestClient(app)


def test_a_membuat_tugas():
    tugas_db.clear()
    response = client.post("/tugas", json={"judul": "Tugas dari tes A"})
    assert response.status_code == 201


def test_b_mengira_daftar_kosong():
    # Lolos bila dijalankan sendirian, gagal bila test_a berjalan lebih dulu
    response = client.get("/tugas")
    assert response.json() == []
