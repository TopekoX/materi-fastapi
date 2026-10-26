from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config import get_settings
from sqlmodel import select

from app.models import Pengguna
from helpers import buat_pengguna


def test_daftar_berhasil(client):
    response = client.post("/daftar", json={"nama_pengguna": "budi", "kata_sandi": "sandi-budi-123"})
    assert response.status_code == 201
    isi = response.json()
    assert isi["nama_pengguna"] == "budi"
    assert isi["peran"] == "anggota"  # pendaftaran lewat API selalu anggota
    assert "kata_sandi" not in isi and "hash_kata_sandi" not in isi


def test_daftar_menyimpan_hash_bukan_kata_sandi(client, session):
    client.post("/daftar", json={"nama_pengguna": "budi", "kata_sandi": "sandi-budi-123"})
    pengguna = session.exec(select(Pengguna)).one()
    assert pengguna.hash_kata_sandi != "sandi-budi-123"
    assert pengguna.hash_kata_sandi.startswith("$argon2")


def test_daftar_nama_kembar(client):
    data = {"nama_pengguna": "budi", "kata_sandi": "sandi-budi-123"}
    client.post("/daftar", json=data)
    response = client.post("/daftar", json=data)
    assert response.status_code == 409
    assert response.json()["galat"]["kode"] == "NAMA_PENGGUNA_SUDAH_ADA"


@pytest.mark.parametrize(
    "data, field",
    [
        ({"nama_pengguna": "bu", "kata_sandi": "sandi-budi-123"}, "body.nama_pengguna"),
        ({"nama_pengguna": "budi", "kata_sandi": "pendek"}, "body.kata_sandi"),
    ],
)
def test_daftar_data_tidak_valid(client, data, field):
    response = client.post("/daftar", json=data)
    assert response.status_code == 422
    galat = response.json()["galat"]
    assert galat["kode"] == "VALIDASI_GAGAL"
    assert field in [r["field"] for r in galat["rincian"]]


def test_masuk_berhasil(client, header_budi):
    assert header_budi["Authorization"].startswith("Bearer ")


def test_masuk_kata_sandi_salah(client, session):
    buat_pengguna(session, "budi")
    response = client.post("/token", data={"username": "budi", "password": "salah-sekali-9"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_masuk_pengguna_tidak_ada_pesan_sama(client, session):
    buat_pengguna(session, "budi")
    salah_sandi = client.post("/token", data={"username": "budi", "password": "salah-sekali-9"})
    tidak_ada = client.post("/token", data={"username": "hantu", "password": "salah-sekali-9"})
    assert salah_sandi.status_code == tidak_ada.status_code == 401
    assert salah_sandi.json() == tidak_ada.json()  # tidak membocorkan nama yang terdaftar


def test_saya(client, header_budi):
    response = client.get("/saya", headers=header_budi)
    assert response.status_code == 200
    assert response.json()["nama_pengguna"] == "budi"


def test_saya_tanpa_token(client):
    response = client.get("/saya")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_token_sembarang_ditolak(client):
    response = client.get("/saya", headers={"Authorization": "Bearer bukan-token"})
    assert response.status_code == 401


def _token(nama: str, **ubahan) -> str:
    settings = get_settings()
    isi = {"sub": nama, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)} | ubahan
    return jwt.encode(isi, settings.secret_key.get_secret_value(), algorithm=settings.algoritma)


def test_token_kedaluwarsa_ditolak(client, header_budi):
    token = _token("budi", exp=datetime.now(timezone.utc) - timedelta(seconds=5))
    response = client.get("/saya", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_token_untuk_pengguna_yang_tidak_ada_ditolak(client):
    response = client.get("/saya", headers={"Authorization": f"Bearer {_token('hantu')}"})
    assert response.status_code == 401


def test_token_dengan_kunci_lain_ditolak(client, header_budi):
    token = jwt.encode(
        {"sub": "budi", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "kunci-lain-yang-tidak-sama-dengan-aplikasi-1234",
        algorithm="HS256",
    )
    response = client.get("/saya", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_token_tanpa_klaim_sub_ditolak(client):
    settings = get_settings()
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.secret_key.get_secret_value(),
        algorithm=settings.algoritma,
    )
    response = client.get("/saya", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
