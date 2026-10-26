import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Variabel environment SECRET_KEY belum diisi. "
        'Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITMA = "HS256"
# Masa berlaku bisa diubah lewat environment agar mudah diuji (nilai bawaan: 15 menit dan 7 hari)
DETIK_AKSES = int(os.environ.get("DETIK_AKSES", 15 * 60))
DETIK_REFRESH = int(os.environ.get("DETIK_REFRESH", 7 * 24 * 3600))

app = FastAPI()
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")
skema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")

# Data contoh (sementara, di memori). Kata sandi hanya untuk demo.
pengguna_db = {"budi": password_hash.hash("sandi-budi-123")}

# Penyimpanan di sisi server (di memori; hilang saat server dimulai ulang):
refresh_aktif: dict[str, str] = {}  # jti refresh token yang masih sah -> nama pengguna
akses_dicabut: set[str] = set()  # jti access token yang sudah dicabut (daftar blokir)


class TokenPasangan(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class PermintaanRefresh(BaseModel):
    refresh_token: str


def buat_token(nama: str, jenis: str, detik: int) -> tuple[str, str]:
    """Mengembalikan (token, jti). jti = pengenal unik token, dipakai untuk mencabutnya."""
    jti = uuid.uuid4().hex
    isi = {
        "sub": nama,
        "jenis": jenis,
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=detik),
    }
    return jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA), jti


def terbitkan_pasangan(nama: str) -> TokenPasangan:
    akses, _ = buat_token(nama, "akses", DETIK_AKSES)
    refresh, jti_refresh = buat_token(nama, "refresh", DETIK_REFRESH)
    refresh_aktif[jti_refresh] = nama
    return TokenPasangan(access_token=akses, refresh_token=refresh, token_type="bearer")


def decode(token: str, jenis_diharapkan: str) -> dict:
    gagal = HTTPException(
        status_code=401,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError:
        raise gagal
    if isi.get("jenis") != jenis_diharapkan or not isi.get("sub") or not isi.get("jti"):
        raise gagal
    return isi


def isi_token_akses(token: Annotated[str, Depends(skema_oauth2)]) -> dict:
    isi = decode(token, "akses")
    if isi["jti"] in akses_dicabut:
        raise HTTPException(
            status_code=401,
            detail="Token sudah dicabut",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return isi


@app.post("/token", response_model=TokenPasangan)
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    hash_tersimpan = pengguna_db.get(form.username)
    if hash_tersimpan is None:
        password_hash.verify(form.password, HASH_TIRUAN)
        sah = False
    else:
        sah = password_hash.verify(form.password, hash_tersimpan)
    if not sah:
        raise HTTPException(
            status_code=401,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return terbitkan_pasangan(form.username)


@app.post("/refresh", response_model=TokenPasangan)
def perbarui(data: PermintaanRefresh):
    isi = decode(data.refresh_token, "refresh")
    # Refresh token hanya boleh dipakai sekali (rotasi): hapus dari daftar sah
    if refresh_aktif.pop(isi["jti"], None) is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token sudah dipakai atau dicabut",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return terbitkan_pasangan(isi["sub"])


@app.post("/keluar", status_code=status.HTTP_204_NO_CONTENT)
def keluar(data: PermintaanRefresh, isi_akses: Annotated[dict, Depends(isi_token_akses)]):
    """Mencabut access token yang sedang dipakai dan refresh token yang dikirim."""
    akses_dicabut.add(isi_akses["jti"])
    try:
        isi_refresh = decode(data.refresh_token, "refresh")
        refresh_aktif.pop(isi_refresh["jti"], None)
    except HTTPException:
        pass  # refresh token tidak valid: tetap anggap keluar berhasil


@app.get("/saya")
def saya(isi: Annotated[dict, Depends(isi_token_akses)]):
    return {"nama": isi["sub"]}
