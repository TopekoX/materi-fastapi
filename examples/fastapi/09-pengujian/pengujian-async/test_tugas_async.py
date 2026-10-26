import pytest
from sqlmodel import select

from main import Kategori, Tugas

pytestmark = pytest.mark.anyio  # semua pengujian di berkas ini berjalan secara async


async def test_buat_tugas(client, session):
    response = await client.post("/tugas", json={"judul": "Belajar pengujian async"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "judul": "Belajar pengujian async", "kategori_id": None}

    # Karena pengujian async, kita bisa memeriksa basis data langsung dengan await
    hasil = await session.exec(select(Tugas))
    assert [t.judul for t in hasil.all()] == ["Belajar pengujian async"]


async def test_ambil_tugas_dengan_kategori(client, session):
    session.add(Kategori(nama="Kuliah"))
    await session.commit()
    await client.post("/tugas", json={"judul": "Tugas kuliah", "kategori_id": 1})

    response = await client.get("/tugas/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "judul": "Tugas kuliah", "kategori": "Kuliah"}


async def test_ambil_tugas_tidak_ada(client):
    response = await client.get("/tugas/99")
    assert response.status_code == 404


async def test_validasi_judul(client):
    response = await client.post("/tugas", json={"judul": "ab"})
    assert response.status_code == 422


async def test_basis_data_baru_untuk_setiap_pengujian(client):
    assert (await client.get("/tugas")).json() == []
