from pathlib import Path

from sqlmodel import Session, select

from main import Tugas


def test_buat_tugas(client, session: Session):
    response = client.post("/tugas", json={"judul": "Belajar basis data uji"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "judul": "Belajar basis data uji", "selesai": False}
    # Periksa juga langsung di basis data, bukan hanya di response
    tersimpan = session.exec(select(Tugas)).all()
    assert [t.judul for t in tersimpan] == ["Belajar basis data uji"]


def test_id_selalu_mulai_dari_satu(client):
    # Basis data baru untuk tiap pengujian, jadi id dimulai lagi dari 1
    response = client.post("/tugas", json={"judul": "Tugas pertama"})
    assert response.json()["id"] == 1


def test_data_tidak_terbawa_antar_pengujian(client):
    assert client.get("/tugas").json() == []


def test_filter_selesai(client):
    client.post("/tugas", json={"judul": "Tugas satu", "selesai": True})
    client.post("/tugas", json={"judul": "Tugas dua"})
    response = client.get("/tugas", params={"selesai": False})
    assert [t["judul"] for t in response.json()] == ["Tugas dua"]


def test_data_disiapkan_langsung_lewat_session(client, session: Session):
    # Menyiapkan data tanpa lewat API (cepat, dan tidak bergantung pada endpoint POST)
    session.add(Tugas(judul="Disiapkan langsung"))
    session.commit()
    response = client.get("/tugas/1")
    assert response.status_code == 200
    assert response.json()["judul"] == "Disiapkan langsung"


def test_hapus_lalu_404(client):
    client.post("/tugas", json={"judul": "Akan dihapus"})
    assert client.delete("/tugas/1").status_code == 204
    assert client.get("/tugas/1").status_code == 404


def test_validasi_judul(client):
    response = client.post("/tugas", json={"judul": "ab"})
    assert response.status_code == 422


def test_basis_data_produksi_tidak_tersentuh(client):
    client.post("/tugas", json={"judul": "Hanya di memori"})
    assert not Path("database.db").exists()
