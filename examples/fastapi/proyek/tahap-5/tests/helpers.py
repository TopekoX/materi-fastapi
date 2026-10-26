"""Fungsi bantu yang dipakai banyak pengujian (bukan fixture)."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.keamanan import password_hash
from app.models import Pengguna

KATA_SANDI = {"budi": "sandi-budi-123", "sari": "sandi-sari-456", "rina": "sandi-rina-789"}


def buat_pengguna(session: Session, nama: str, peran: str = "anggota") -> Pengguna:
    pengguna = Pengguna(
        nama_pengguna=nama,
        hash_kata_sandi=password_hash.hash(KATA_SANDI[nama]),
        peran=peran,
    )
    session.add(pengguna)
    session.commit()
    session.refresh(pengguna)
    return pengguna


def header_untuk(client: TestClient, nama: str) -> dict[str, str]:
    """Masuk lewat endpoint /token dan mengembalikan header Authorization."""
    response = client.post("/token", data={"username": nama, "password": KATA_SANDI[nama]})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
