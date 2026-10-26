"""Versi yang diperbaiki dari test_masalah_state.py di halaman sebelumnya.

Berkat fixture data_bersih (autouse), kedua pengujian lolos dalam urutan apa pun.
"""


def test_a_membuat_tugas(client):
    response = client.post("/tugas", json={"judul": "Tugas dari tes A"})
    assert response.status_code == 201


def test_b_daftar_kosong(client):
    assert client.get("/tugas").json() == []
