import pytest

from main import simpan_ringkasan, tugas_db


def test_daftar_awal_kosong(client):
    response = client.get("/tugas")
    assert response.json() == []


def test_buat_tugas(client):
    response = client.post("/tugas", json={"judul": "Belajar fixture"})
    assert response.status_code == 201
    assert response.json()["id"] == 1  # selalu 1, karena data dibersihkan sebelum setiap tes


def test_ambil_tugas_contoh(client, tugas_contoh):
    response = client.get(f"/tugas/{tugas_contoh['id']}")
    assert response.status_code == 200
    assert response.json() == tugas_contoh


def test_hapus_tugas_contoh(client, tugas_contoh, header_token):
    response = client.delete(f"/tugas/{tugas_contoh['id']}", headers=header_token)
    assert response.status_code == 204
    assert client.get(f"/tugas/{tugas_contoh['id']}").status_code == 404


def test_judul_valid_diterima(client, judul_valid):
    # Dijalankan 3 kali, sekali untuk tiap nilai judul_valid
    response = client.post("/tugas", json={"judul": judul_valid})
    assert response.status_code == 201
    assert response.json()["judul"] == judul_valid


@pytest.mark.parametrize(
    "judul, status_diharapkan",
    [("abc", 201), ("ab", 422), ("", 422), ("x" * 100, 201), ("x" * 101, 422)],
)
def test_batas_panjang_judul(client, judul, status_diharapkan):
    response = client.post("/tugas", json={"judul": judul})
    assert response.status_code == status_diharapkan


def test_simpan_ringkasan(tmp_path, client):
    client.post("/tugas", json={"judul": "Satu"})
    client.post("/tugas", json={"judul": "Dua"})
    jalur = simpan_ringkasan(tmp_path, list(tugas_db.values()))
    assert (tmp_path / "ringkasan.txt").read_text(encoding="utf-8") == "Satu\nDua"
    assert jalur.endswith("ringkasan.txt")
