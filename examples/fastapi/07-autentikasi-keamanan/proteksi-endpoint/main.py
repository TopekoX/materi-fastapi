import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Variabel environment SECRET_KEY belum diisi. "
        'Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITMA = "HS256"
MENIT_KEDALUWARSA = 30

app = FastAPI()
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")

# nama_pengguna -> {"hash": ..., "aktif": ...}  (sementara, di memori)
pengguna_db: dict[str, dict] = {}

# Memberi tahu FastAPI (dan /docs) bahwa token diambil dari endpoint /token
skema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")


class PenggunaBaru(BaseModel):
    nama_pengguna: str = Field(min_length=3, max_length=30)
    kata_sandi: str = Field(min_length=8, max_length=128)


class PenggunaPublik(BaseModel):
    nama_pengguna: str
    aktif: bool


class Token(BaseModel):
    access_token: str
    token_type: str


def buat_token(nama_pengguna: str, berlaku: timedelta) -> str:
    isi = {"sub": nama_pengguna, "exp": datetime.now(timezone.utc) + berlaku}
    return jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA)


def autentikasi(nama_pengguna: str, kata_sandi: str) -> bool:
    pengguna = pengguna_db.get(nama_pengguna)
    if pengguna is None:
        password_hash.verify(kata_sandi, HASH_TIRUAN)
        return False
    return password_hash.verify(kata_sandi, pengguna["hash"])


# --- Dependency proteksi --------------------------------------------------
def pengguna_saat_ini(token: Annotated[str, Depends(skema_oauth2)]) -> PenggunaPublik:
    gagal = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError:
        raise gagal
    nama_pengguna = isi.get("sub")
    pengguna = pengguna_db.get(nama_pengguna) if nama_pengguna else None
    if pengguna is None:
        raise gagal
    return PenggunaPublik(nama_pengguna=nama_pengguna, aktif=pengguna["aktif"])


def pengguna_aktif(pengguna: Annotated[PenggunaPublik, Depends(pengguna_saat_ini)]) -> PenggunaPublik:
    if not pengguna.aktif:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun tidak aktif")
    return pengguna


PenggunaLogin = Annotated[PenggunaPublik, Depends(pengguna_aktif)]


# --- Endpoint terbuka --------------------------------------------------------
@app.get("/info")
def info():
    return {"nama": "TugasKu", "terbuka": True}


@app.post("/daftar", response_model=PenggunaPublik, status_code=status.HTTP_201_CREATED)
def daftar(data: PenggunaBaru):
    if data.nama_pengguna in pengguna_db:
        raise HTTPException(status_code=409, detail="Nama pengguna sudah dipakai")
    pengguna_db[data.nama_pengguna] = {"hash": password_hash.hash(data.kata_sandi), "aktif": True}
    return PenggunaPublik(nama_pengguna=data.nama_pengguna, aktif=True)


@app.post("/token")
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if not autentikasi(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = buat_token(form.username, timedelta(minutes=MENIT_KEDALUWARSA))
    return Token(access_token=token, token_type="bearer")


# --- Endpoint terlindungi ----------------------------------------------------
@app.get("/saya", response_model=PenggunaPublik)
def profil_saya(pengguna: PenggunaLogin):
    return pengguna


@app.get("/catatan-pribadi")
def catatan_pribadi(pengguna: PenggunaLogin):
    return {"pemilik": pengguna.nama_pengguna, "catatan": ["Belajar proteksi endpoint"]}


# --- Hanya untuk percobaan ------------------------------------------------------
@app.post("/debug/nonaktifkan/{nama_pengguna}")
def nonaktifkan(nama_pengguna: str):
    pengguna_db[nama_pengguna]["aktif"] = False
    return {"nama_pengguna": nama_pengguna, "aktif": False}


@app.delete("/debug/hapus/{nama_pengguna}", status_code=204)
def hapus(nama_pengguna: str):
    pengguna_db.pop(nama_pengguna, None)
