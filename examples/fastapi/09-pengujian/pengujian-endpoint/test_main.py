from fastapi.testclient import TestClient

from main import TOKEN_RAHASIA, app, tugas_db

client = TestClient(app)


def test_beranda():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"pesan": "TugasKu API"}


def test_buat_tugas():
    tugas_db.clear()  # mulai dari keadaan kosong (cara yang lebih rapi dibahas di halaman Fixture)
    response = client.post("/tugas", json={"judul": "Belajar pytest"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "judul": "Belajar pytest", "selesai": False}


def test_buat_tugas_judul_terlalu_pendek():
    response = client.post("/tugas", json={"judul": "ab"})
    assert response.status_code == 422
    galat = response.json()["detail"][0]
    assert galat["type"] == "string_too_short"
    assert galat["loc"] == ["body", "judul"]


def test_ambil_tugas_tidak_ada():
    tugas_db.clear()
    response = client.get("/tugas/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tugas tidak ditemukan"}


def test_filter_selesai():
    tugas_db.clear()
    client.post("/tugas", json={"judul": "Tugas satu", "selesai": True})
    client.post("/tugas", json={"judul": "Tugas dua"})
    response = client.get("/tugas", params={"selesai": True})
    assert response.status_code == 200
    judul = [t["judul"] for t in response.json()]
    assert judul == ["Tugas satu"]


def test_hapus_butuh_token():
    tugas_db.clear()
    client.post("/tugas", json={"judul": "Akan dihapus"})
    tanpa_token = client.delete("/tugas/1")
    assert tanpa_token.status_code == 422  # header X-Token wajib
    token_salah = client.delete("/tugas/1", headers={"X-Token": "salah"})
    assert token_salah.status_code == 401
    benar = client.delete("/tugas/1", headers={"X-Token": TOKEN_RAHASIA})
    assert benar.status_code == 204
    assert client.get("/tugas/1").status_code == 404
